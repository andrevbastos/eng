"""DemandaService: RF001, RS015, RS016, RS017, RD002 (RD005 não imposto — sessão 0)."""
import datetime

import pytest

from src.models import STATUS_DEMANDA
from src.services import NaoEncontradoError, ValidacaoError
from src.services.demandas import DATA_LIMITE_ANTERIOR, OBRIGATORIOS_DEMANDA
from tests.dados import DADOS_DEMANDA


def test_rf001_criar_e_buscar(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA, observacoes="  Aguardando parecer  ")
    lida = servicos.demandas.buscar(demanda.id)
    assert lida.titulo == "Ofício MPF 12/2026"
    assert lida.status == "Em análise"
    assert lida.segredo_justica is False
    assert lida.observacoes == "Aguardando parecer"  # espaços removidos
    assert lida.subsidios == [] and lida.documentos == [] and lida.tags == []


def test_rf001_texto_vazio_em_campo_opcional_vira_nulo(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA, caminho_pasta="   ", origem_documento="")
    assert demanda.caminho_pasta is None
    assert demanda.origem_documento is None


@pytest.mark.parametrize("campo", OBRIGATORIOS_DEMANDA)
def test_rs017_campos_obrigatorios(servicos, campo):
    dados = {**DADOS_DEMANDA, campo: "   " if campo not in ("data_entrada", "data_limite") else None}
    if campo == "status":
        # status vazio na criação recebe o padrão; vazio na edição é recusado.
        demanda = servicos.demandas.criar(**DADOS_DEMANDA)
        with pytest.raises(ValidacaoError) as erro:
            servicos.demandas.editar(demanda.id, status="")
    else:
        with pytest.raises(ValidacaoError) as erro:
            servicos.demandas.criar(**dados)
    assert erro.value.erros == {campo: "Campo obrigatório."}


def test_rs017_rejeita_varios_campos_de_uma_vez(servicos):
    with pytest.raises(ValidacaoError) as erro:
        servicos.demandas.criar(titulo="Só o título")
    assert set(erro.value.erros) == set(OBRIGATORIOS_DEMANDA) - {"titulo", "status"}


def test_rs017_rd002_data_limite_anterior_a_entrada(servicos):
    with pytest.raises(ValidacaoError) as erro:
        servicos.demandas.criar(**{**DADOS_DEMANDA, "data_limite": datetime.date(2026, 8, 9)})
    assert erro.value.erros == {"data_limite": DATA_LIMITE_ANTERIOR}


def test_rs017_data_limite_igual_a_entrada_e_aceita(servicos):
    dia = datetime.date(2026, 8, 10)
    servicos.demandas.criar(**{**DADOS_DEMANDA, "data_entrada": dia, "data_limite": dia})


def test_rs017_data_precisa_ser_date(servicos):
    with pytest.raises(ValidacaoError) as erro:
        servicos.demandas.criar(**{**DADOS_DEMANDA, "data_entrada": "10/08/2026"})
    assert erro.value.erros == {"data_entrada": "Data inválida."}


@pytest.mark.parametrize("campo, valor", [("status", "Pendente"), ("origem_canal", "Pessoalmente")])
def test_rs003_rejeita_opcao_fora_da_lista(servicos, campo, valor):
    with pytest.raises(ValidacaoError) as erro:
        servicos.demandas.criar(**{**DADOS_DEMANDA, campo: valor})
    assert list(erro.value.erros) == [campo]


def test_rd005_nao_imposto_status_livre_e_reabertura(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    servicos.demandas.editar(demanda.id, status="Concluída")  # sem passar pelo Reitor
    reaberta = servicos.demandas.editar(demanda.id, status="Em andamento")
    assert reaberta.status == "Em andamento"


def test_rf001_editar_altera_apenas_campos_informados(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA, observacoes="Antes")
    servicos.demandas.editar(demanda.id, titulo="Novo título", observacoes=None)
    lida = servicos.demandas.buscar(demanda.id)
    assert lida.titulo == "Novo título"
    assert lida.observacoes is None
    assert lida.alvo_motivo == DADOS_DEMANDA["alvo_motivo"]


def test_rf001_editar_com_erro_nao_grava_nada(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    with pytest.raises(ValidacaoError):
        servicos.demandas.editar(demanda.id, titulo="Outro", data_limite=datetime.date(2026, 1, 1))
    assert servicos.demandas.buscar(demanda.id).titulo == DADOS_DEMANDA["titulo"]


def test_campo_desconhecido_e_erro_de_programacao(servicos):
    with pytest.raises(TypeError):
        servicos.demandas.criar(**DADOS_DEMANDA, relator="Dr. Carlos")


def test_rf001_listar_e_excluir(servicos):
    a = servicos.demandas.criar(**DADOS_DEMANDA)
    b = servicos.demandas.criar(**{**DADOS_DEMANDA, "titulo": "Segunda"})
    assert [d.id for d in servicos.demandas.listar()] == [a.id, b.id]
    servicos.demandas.excluir(a.id)
    assert [d.id for d in servicos.demandas.listar()] == [b.id]
    with pytest.raises(NaoEncontradoError):
        servicos.demandas.buscar(a.id)


@pytest.mark.parametrize("operacao", ["buscar", "excluir", "editar"])
def test_registro_inexistente(servicos, operacao):
    with pytest.raises(NaoEncontradoError):
        getattr(servicos.demandas, operacao)(999)


@pytest.mark.parametrize("status", STATUS_DEMANDA)
def test_rs003_todos_os_status_aceitos(servicos, status):
    assert servicos.demandas.criar(**DADOS_DEMANDA, status=status).status == status
