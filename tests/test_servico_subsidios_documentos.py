"""SubsidioService e DocumentoService: RF003, RF004, RS015, RS022, RD001, RNF010."""
import datetime
from pathlib import Path

import pytest

from src.models import EXTENSOES_PERMITIDAS, TAMANHO_MAXIMO_BYTES
from src.services import NaoEncontradoError, ValidacaoError
from src.services.documentos import ARQUIVO_GRANDE, ARQUIVO_NAO_ENCONTRADO, UM_DONO
from tests.dados import DADOS_DEMANDA, DADOS_PARECER

DADOS_SUBSIDIO = dict(setor_fonte="Proad", data_aquisicao=datetime.date(2026, 8, 12),
                      resposta="Subsídios orçamentários validados.")


@pytest.fixture
def demanda(servicos):
    return servicos.demandas.criar(**DADOS_DEMANDA)


# --- Subsídios (RF003) -------------------------------------------------------

def test_rf003_crud_de_subsidio(servicos, demanda):
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, **DADOS_SUBSIDIO)
    assert [s.id for s in servicos.demandas.buscar(demanda.id).subsidios] == [subsidio.id]
    servicos.subsidios.editar(subsidio.id, resposta="Resposta revisada.")
    assert servicos.subsidios.buscar(subsidio.id).resposta == "Resposta revisada."
    servicos.subsidios.excluir(subsidio.id)
    assert servicos.demandas.buscar(demanda.id).subsidios == []


def test_rf003_subsidio_exige_demanda_existente(servicos):
    with pytest.raises(ValidacaoError) as erro:
        servicos.subsidios.criar(demanda_id=999, **DADOS_SUBSIDIO)
    assert erro.value.erros == {"demanda_id": "Demanda não encontrada."}


def test_rf003_subsidio_nao_muda_de_demanda(servicos, demanda):
    outra = servicos.demandas.criar(**DADOS_DEMANDA)
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, **DADOS_SUBSIDIO)
    with pytest.raises(ValidacaoError):
        servicos.subsidios.editar(subsidio.id, demanda_id=outra.id)


# --- Documentos (RF004, RS022, RD001) -----------------------------------------

@pytest.mark.parametrize("extensao", EXTENSOES_PERMITIDAS)
def test_rd001_aceita_formatos(servicos, demanda, arquivo, extensao):
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo(f"a.{extensao}"))
    assert documento.tipo_arquivo == extensao


def test_rd001_extensao_em_maiusculas(servicos, demanda, arquivo):
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo("OFICIO.PDF"))
    assert documento.tipo_arquivo == "pdf"


@pytest.mark.parametrize("nome", ["planilha.xls", "video.mp4", "sem_extensao"])
def test_rs022_recusa_formato_fora_do_rd001(servicos, demanda, arquivo, nome):
    with pytest.raises(ValidacaoError) as erro:
        servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo(nome))
    assert erro.value.erros["caminho_arquivo"].startswith("Formato não aceito")


def test_rs022_rnf010_limite_de_50_mb(servicos, demanda, arquivo):
    no_limite = arquivo("limite.pdf", TAMANHO_MAXIMO_BYTES)
    servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=no_limite)
    with pytest.raises(ValidacaoError) as erro:
        servicos.documentos.criar(demanda_id=demanda.id,
                                  caminho_arquivo=arquivo("grande.pdf", TAMANHO_MAXIMO_BYTES + 1))
    assert erro.value.erros == {"caminho_arquivo": ARQUIVO_GRANDE}


def test_rf004_arquivo_inexistente(servicos, demanda, tmp_path):
    with pytest.raises(ValidacaoError) as erro:
        servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=str(tmp_path / "x.pdf"))
    assert erro.value.erros == {"caminho_arquivo": ARQUIVO_NAO_ENCONTRADO}


def test_rf004_anexa_a_demanda_parecer_ou_subsidio(servicos, demanda, arquivo):
    parecer = servicos.pareceres.criar(**DADOS_PARECER)
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, **DADOS_SUBSIDIO)
    servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo("d.pdf"))
    servicos.documentos.criar(parecer_id=parecer.id, caminho_arquivo=arquivo("p.pdf"))
    servicos.documentos.criar(subsidio_id=subsidio.id, caminho_arquivo=arquivo("s.pdf"))
    assert len(servicos.pareceres.buscar(parecer.id).documentos) == 1
    lida = servicos.demandas.buscar(demanda.id)
    assert len(lida.documentos) == 1 and len(lida.subsidios[0].documentos) == 1


@pytest.mark.parametrize("donos", [{}, {"demanda_id": "D", "parecer_id": "P"}])
def test_rf004_exatamente_um_dono(servicos, demanda, arquivo, donos):
    parecer = servicos.pareceres.criar(**DADOS_PARECER)
    ids = {"D": demanda.id, "P": parecer.id}
    with pytest.raises(ValidacaoError) as erro:
        servicos.documentos.criar(caminho_arquivo=arquivo(), **{k: ids[v] for k, v in donos.items()})
    assert erro.value.erros == {"dono": UM_DONO}


def test_rf004_tipo_arquivo_nao_e_informado_pelo_chamador(servicos, demanda, arquivo):
    with pytest.raises(TypeError):
        servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo(), tipo_arquivo="pdf")


def test_rf004_remover_anexo_mantem_arquivo_por_padrao(servicos, demanda, arquivo):
    caminho = arquivo()
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=caminho)
    assert servicos.documentos.excluir(documento.id) == []
    assert Path(caminho).is_file()
    assert servicos.demandas.buscar(demanda.id).documentos == []


def test_rf004_remover_anexo_apagando_arquivo(servicos, demanda, arquivo):
    caminho = arquivo()
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=caminho)
    servicos.documentos.excluir(documento.id, apagar_arquivos=True)
    assert not Path(caminho).exists()


def test_excluir_demanda_remove_dependentes_e_opcionalmente_arquivos(servicos, demanda, arquivo):
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, **DADOS_SUBSIDIO)
    c1, c2 = arquivo("d.pdf"), arquivo("s.docx")
    servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=c1)
    servicos.documentos.criar(subsidio_id=subsidio.id, caminho_arquivo=c2)

    assert servicos.demandas.excluir(demanda.id, apagar_arquivos=True) == []

    assert servicos.documentos.listar() == [] and servicos.subsidios.listar() == []
    assert not Path(c1).exists() and not Path(c2).exists()
    with pytest.raises(NaoEncontradoError):
        servicos.subsidios.buscar(subsidio.id)
