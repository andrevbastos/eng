"""Formatos da interface: datas DD/MM/AAAA (sessão 0) e histórico (RF014)."""
import datetime
from types import SimpleNamespace

import pytest

from src.ui.formatos import data_br, descrever_alteracao, ler_data_br, valor_historico


def test_data_br():
    assert data_br(datetime.date(2026, 8, 5)) == "05/08/2026"
    assert data_br(None) == ""


@pytest.mark.parametrize("texto, esperado", [
    ("05/08/2026", datetime.date(2026, 8, 5)),
    ("5/8/2026", datetime.date(2026, 8, 5)),
    (" 29/02/2028 ", datetime.date(2028, 2, 29)),
    ("", None),
    ("   ", None),
])
def test_ler_data_br(texto, esperado):
    assert ler_data_br(texto) == esperado


@pytest.mark.parametrize("texto", ["2026-08-05", "31/02/2026", "05/08/26", "05/08", "aa/bb/cccc", "05/13/2026"])
def test_ler_data_br_invalida(texto):
    with pytest.raises(ValueError):
        ler_data_br(texto)


@pytest.mark.parametrize("valor, esperado", [
    (None, "—"), ("2026-08-10", "10/08/2026"), ("True", "Sim"), ("False", "Não"), ("Proad", "Proad"),
])
def test_valor_historico(valor, esperado):
    assert valor_historico(valor) == esperado


def _h(tabela="demandas", campo="status", anterior=None, novo=None, registro_id=1):
    return SimpleNamespace(tabela=tabela, registro_id=registro_id, campo=campo,
                           valor_anterior=anterior, valor_novo=novo)


@pytest.mark.parametrize("item, esperado", [
    (_h(campo="data_limite", novo="2026-08-20"), "Data limite: 20/08/2026"),
    (_h(anterior="Em análise", novo="Concluída"), "Status: Em análise → Concluída"),
    (_h(campo="tags", novo="MPF"), "Tags: adicionado MPF"),
    (_h(campo="tags", anterior="MPF"), "Tags: removido MPF"),
    (_h(tabela="subsidios", registro_id=3, campo="resposta", anterior="a", novo="b"),
     "Subsídio #3 · Resposta: a → b"),
    (_h(tabela="documentos", registro_id=7, campo="*", anterior="C:/a.pdf"), "Documento #7 · excluído (C:/a.pdf)"),
])
def test_rf014_descrever_alteracao(item, esperado):
    assert descrever_alteracao("demandas", item) == esperado
