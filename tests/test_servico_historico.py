"""Histórico de alterações e transações: RS016, RF014, RU010, RS015."""
import datetime
import sqlite3

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.base import criar_engine, criar_fabrica_sessoes, criar_tabelas
from src.models import HistoricoAlteracao
from src.services import BancoOcupadoError, DemandaService, ValidacaoError
from tests.dados import DADOS_DEMANDA, DADOS_PARECER


def _linhas(historico):
    return [(h.tabela, h.campo, h.valor_anterior, h.valor_novo) for h in historico]


def test_rs016_criacao_registra_campos_preenchidos(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    linhas = {h.campo: (h.valor_anterior, h.valor_novo) for h in servicos.demandas.listar_historico(demanda.id)}
    assert linhas["titulo"] == (None, "Ofício MPF 12/2026")
    assert linhas["data_entrada"] == (None, "2026-08-10")
    assert linhas["status"] == (None, "Em análise")
    assert linhas["segredo_justica"] == (None, "False")
    assert "observacoes" not in linhas  # campos vazios não geram linha


def test_rs016_edicao_registra_apenas_campos_alterados(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    servicos.demandas.editar(demanda.id, status="Em andamento", titulo=DADOS_DEMANDA["titulo"])
    recente = servicos.demandas.listar_historico(demanda.id)[0]
    assert (recente.campo, recente.valor_anterior, recente.valor_novo) == ("status", "Em análise", "Em andamento")
    assert isinstance(recente.data_hora, datetime.datetime)
    assert sum(h.campo == "titulo" for h in servicos.demandas.listar_historico(demanda.id)) == 1


def test_rs016_edicao_recusada_nao_gera_historico(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    antes = len(servicos.demandas.listar_historico(demanda.id))
    with pytest.raises(ValidacaoError):
        servicos.demandas.editar(demanda.id, titulo="")
    assert len(servicos.demandas.listar_historico(demanda.id)) == antes


def test_rf014_historico_da_demanda_inclui_tags_subsidios_e_anexos(servicos, arquivo):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    tag = servicos.tags.criar(nome="MPF", cor="#EF5350")
    servicos.demandas.associar_tag(demanda.id, tag.id)
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, setor_fonte="Proad",
                                        data_aquisicao=datetime.date(2026, 8, 12), resposta="Ok")
    servicos.subsidios.editar(subsidio.id, resposta="Revisada")
    caminho = arquivo()
    servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=caminho)
    servicos.demandas.desassociar_tag(demanda.id, tag.id)

    linhas = _linhas(servicos.demandas.listar_historico(demanda.id))
    assert ("demandas", "tags", None, "MPF") in linhas
    assert ("demandas", "tags", "MPF", None) in linhas
    assert ("demandas", "subsidios", None, f"Proad (#{subsidio.id})") in linhas
    assert ("subsidios", "resposta", "Ok", "Revisada") in linhas
    assert ("demandas", "documentos", None, caminho) in linhas
    assert linhas[0] == ("demandas", "tags", "MPF", None)  # mais recente primeiro


def test_rf014_historico_do_parecer(servicos, arquivo):
    parecer = servicos.pareceres.criar(**DADOS_PARECER)
    documento = servicos.documentos.criar(parecer_id=parecer.id, caminho_arquivo=arquivo())
    servicos.documentos.excluir(documento.id)
    linhas = _linhas(servicos.pareceres.listar_historico(parecer.id))
    assert ("pareceres", "numero", None, "PJ-042/2026") in linhas
    assert ("pareceres", "documentos", documento.caminho_arquivo, None) in linhas


def test_rs016_exclusao_registra_registro_e_dependentes(servicos, engine, arquivo):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, setor_fonte="Proad",
                                        data_aquisicao=datetime.date(2026, 8, 12), resposta="Ok")
    documento = servicos.documentos.criar(subsidio_id=subsidio.id, caminho_arquivo=arquivo())
    servicos.demandas.excluir(demanda.id)

    with Session(engine) as sessao:
        exclusoes = sessao.execute(
            select(HistoricoAlteracao.tabela, HistoricoAlteracao.registro_id, HistoricoAlteracao.valor_anterior)
            .where(HistoricoAlteracao.campo == "*")
        ).all()
    assert set(exclusoes) == {
        ("demandas", demanda.id, "Ofício MPF 12/2026"),
        ("subsidios", subsidio.id, "Proad"),
        ("documentos", documento.id, documento.caminho_arquivo),
    }


def test_rs016_excluir_tag_registra_nos_registros_afetados(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    tag = servicos.tags.criar(nome="Urgente", cor="#FFB74D")
    servicos.demandas.associar_tag(demanda.id, tag.id)
    servicos.tags.excluir(tag.id)
    assert _linhas(servicos.demandas.listar_historico(demanda.id))[0] == ("demandas", "tags", "Urgente", None)


# --- Transação e banco bloqueado ---------------------------------------------

def test_banco_bloqueado_informa_e_nao_grava(tmp_path):
    caminho = tmp_path / "assessoria.db"
    engine = criar_engine(caminho, espera_bloqueio_s=0.1)
    criar_tabelas(engine)
    servico = DemandaService(criar_fabrica_sessoes(engine))

    bloqueio = sqlite3.connect(caminho, isolation_level=None)
    bloqueio.execute("BEGIN EXCLUSIVE")
    try:
        with pytest.raises(BancoOcupadoError):
            servico.criar(**DADOS_DEMANDA)
    finally:
        bloqueio.execute("ROLLBACK")
        bloqueio.close()

    assert servico.listar() == []
    servico.criar(**DADOS_DEMANDA)  # liberado o bloqueio, a escrita funciona
    assert len(servico.listar()) == 1
    engine.dispose()
