"""ParecerService: RF002, RS015, RS017, RD004."""
import pytest

from src.services import ValidacaoError
from src.services.pareceres import NUMERO_REPETIDO, OBRIGATORIOS_PARECER
from tests.dados import DADOS_PARECER


def test_rf002_criar_buscar_editar_excluir(servicos):
    parecer = servicos.pareceres.criar(**DADOS_PARECER)
    assert servicos.pareceres.buscar(parecer.id).numero == "PJ-042/2026"
    servicos.pareceres.editar(parecer.id, conclusao="Indeferido", observacoes="Referência")
    lido = servicos.pareceres.buscar(parecer.id)
    assert (lido.conclusao, lido.observacoes) == ("Indeferido", "Referência")
    servicos.pareceres.excluir(parecer.id)
    assert servicos.pareceres.listar() == []


@pytest.mark.parametrize("campo", OBRIGATORIOS_PARECER)
def test_rs017_campos_obrigatorios(servicos, campo):
    with pytest.raises(ValidacaoError) as erro:
        servicos.pareceres.criar(**{**DADOS_PARECER, campo: None})
    assert erro.value.erros == {campo: "Campo obrigatório."}


@pytest.mark.parametrize("numero", ["PJ-042/2026", " PJ-042/2026 ", "pj-042/2026"])
def test_rs017_rd004_rejeita_numero_repetido(servicos, numero):
    servicos.pareceres.criar(**DADOS_PARECER)
    with pytest.raises(ValidacaoError) as erro:
        servicos.pareceres.criar(**{**DADOS_PARECER, "numero": numero})
    assert erro.value.erros == {"numero": NUMERO_REPETIDO}


def test_rd004_editar_mantendo_o_proprio_numero(servicos):
    parecer = servicos.pareceres.criar(**DADOS_PARECER)
    servicos.pareceres.editar(parecer.id, numero="PJ-042/2026", assunto="Novo assunto")


def test_rd004_editar_para_numero_de_outro_parecer(servicos):
    servicos.pareceres.criar(**DADOS_PARECER)
    outro = servicos.pareceres.criar(**{**DADOS_PARECER, "numero": "PJ-043/2026"})
    with pytest.raises(ValidacaoError) as erro:
        servicos.pareceres.editar(outro.id, numero="PJ-042/2026")
    assert erro.value.erros == {"numero": NUMERO_REPETIDO}
