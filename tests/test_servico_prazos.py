"""Prazos (RS019, RF015), link do Drive (RS020) e uso de tags (RF005) nos serviços."""
import datetime
import os

import pytest

from src.services import ValidacaoError
from src.services.documentos import URL_INVALIDA
from src.services.prazos import PROXIMA, VENCIDA, descrever, situacao
from tests.dados import DADOS_DEMANDA, DADOS_PARECER

HOJE = datetime.date(2026, 10, 19)


def dia(n: int) -> datetime.date:
    return HOJE + datetime.timedelta(days=n)


@pytest.mark.parametrize("dias, esperado", [
    (-30, VENCIDA), (-1, VENCIDA), (0, PROXIMA), (4, PROXIMA), (5, None), (40, None),
])
def test_rs019_cinco_dias_corridos_contando_hoje(dias, esperado):
    assert situacao(dia(dias), concluida=False, hoje=HOJE) == esperado


def test_rs019_concluida_nunca_e_destacada():
    assert situacao(dia(-3), concluida=True, hoje=HOJE) is None
    assert situacao(dia(1), concluida=True, hoje=HOJE) is None


def test_descricao_do_prazo():
    assert descrever(dia(-1), HOJE) == "Vencida há 1 dia"
    assert descrever(dia(-3), HOJE) == "Vencida há 3 dias"
    assert descrever(HOJE, HOJE) == "Vence hoje"
    assert descrever(dia(1), HOJE) == "Vence em 1 dia"
    assert descrever(dia(4), HOJE) == "Vence em 4 dias"


def test_rf015_contagem_ao_iniciar(servicos):
    def criar(limite, status="Em análise"):
        servicos.demandas.criar(**{**DADOS_DEMANDA, "data_entrada": dia(-60), "data_limite": limite,
                                   "status": status})

    criar(dia(-2))
    criar(dia(-1))
    criar(dia(-5), status="Concluída")
    criar(dia(0))
    criar(dia(4))
    criar(dia(2), status="Concluída")
    criar(dia(5))
    contagem = servicos.demandas.contar_prazos(hoje=HOJE)
    assert (contagem.proximas, contagem.vencidas) == (2, 2)


# --- Link do Drive (RS020, decisão da sessão 6) --------------------------------

def test_rs020_link_do_drive_editavel_e_validado(servicos, arquivo):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo())
    assert documento.url_drive is None

    url = "https://drive.google.com/file/d/abc123/view"
    servicos.documentos.editar(documento.id, url_drive=url)
    assert servicos.documentos.buscar(documento.id).url_drive == url

    for invalida in ("drive.google.com/abc", "ftp://x/y", "https://", "javascript:alert(1)"):
        with pytest.raises(ValidacaoError) as erro:
            servicos.documentos.editar(documento.id, url_drive=invalida)
        assert erro.value.erros == {"url_drive": URL_INVALIDA}

    servicos.documentos.editar(documento.id, url_drive="  ")
    assert servicos.documentos.buscar(documento.id).url_drive is None
    historico = servicos.demandas.listar_historico(demanda.id)
    # Histórico do mais recente ao mais antigo.
    assert [h.valor_novo for h in historico if h.campo == "url_drive"] == [None, url]


def test_link_editavel_mesmo_com_arquivo_movido(servicos, arquivo):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    caminho = arquivo()
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=caminho)

    os.remove(caminho)
    servicos.documentos.editar(documento.id, url_drive="https://drive.google.com/x")


def test_caminho_do_anexo_nao_e_editavel(servicos, arquivo):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo())
    with pytest.raises(ValidacaoError) as erro:
        servicos.documentos.editar(documento.id, caminho_arquivo=arquivo("outro.pdf"))
    assert "caminho_arquivo" in erro.value.erros


# --- Uso de tags (RF005) ---------------------------------------------------------

def test_rf005_usos_da_tag(servicos, arquivo):
    tag = servicos.tags.criar(nome="MPF", cor="#EF5350")
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    parecer = servicos.pareceres.criar(**DADOS_PARECER)
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, setor_fonte="Proad",
                                        data_aquisicao=HOJE, resposta="ok")
    documento = servicos.documentos.criar(subsidio_id=subsidio.id, caminho_arquivo=arquivo())
    assert servicos.tags.usos(tag.id) == 0
    servicos.demandas.associar_tag(demanda.id, tag.id)
    servicos.pareceres.associar_tag(parecer.id, tag.id)
    servicos.subsidios.associar_tag(subsidio.id, tag.id)
    servicos.documentos.associar_tag(documento.id, tag.id)
    assert servicos.tags.usos(tag.id) == 4
