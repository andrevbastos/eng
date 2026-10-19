"""TagService e associações: RF005, RS006–RS010."""
import datetime

import pytest

from src.services import NaoEncontradoError, ValidacaoError
from src.services.tags import COR_INVALIDA, NOME_REPETIDO
from tests.dados import DADOS_DEMANDA, DADOS_PARECER


def test_rf005_crud_de_tag(servicos):
    tag = servicos.tags.criar(nome="MPF", cor="#ef5350")
    assert tag.cor == "#EF5350"  # normalizada em maiúsculas
    servicos.tags.editar(tag.id, nome="Ministério Público")
    assert servicos.tags.buscar(tag.id).nome == "Ministério Público"
    servicos.tags.excluir(tag.id)
    assert servicos.tags.listar() == []


def test_rf005_listar_em_ordem_alfabetica(servicos):
    for nome in ("Urgente", "edital", "MPF"):
        servicos.tags.criar(nome=nome, cor="#3A7BD5")
    assert [t.nome for t in servicos.tags.listar()] == ["edital", "MPF", "Urgente"]


@pytest.mark.parametrize("cor", ["red", "#FFF", "3A7BD5", "#3A7BDZ", None])
def test_rs006_cor_hexadecimal(servicos, cor):
    with pytest.raises(ValidacaoError) as erro:
        servicos.tags.criar(nome="Edital", cor=cor)
    assert erro.value.erros == {"cor": COR_INVALIDA if cor else "Campo obrigatório."}


@pytest.mark.parametrize("nome", ["MPF", "mpf", " MPF "])
def test_rs006_nome_unico(servicos, nome):
    servicos.tags.criar(nome="MPF", cor="#EF5350")
    with pytest.raises(ValidacaoError) as erro:
        servicos.tags.criar(nome=nome, cor="#3A7BD5")
    assert erro.value.erros == {"nome": NOME_REPETIDO}


def test_rf005_associar_e_desassociar_em_todas_as_entidades(servicos, arquivo):
    tag = servicos.tags.criar(nome="Urgente", cor="#FFB74D")
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    parecer = servicos.pareceres.criar(**DADOS_PARECER)
    subsidio = servicos.subsidios.criar(demanda_id=demanda.id, setor_fonte="Proad",
                                        data_aquisicao=datetime.date(2026, 8, 12), resposta="Ok")
    documento = servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo())
    alvos = [(servicos.demandas, demanda.id), (servicos.pareceres, parecer.id),
             (servicos.subsidios, subsidio.id), (servicos.documentos, documento.id)]

    for servico, registro_id in alvos:
        servico.associar_tag(registro_id, tag.id)
        servico.associar_tag(registro_id, tag.id)  # idempotente
        assert [t.nome for t in servico.buscar(registro_id).tags] == ["Urgente"]

    for servico, registro_id in alvos:
        servico.desassociar_tag(registro_id, tag.id)
        assert servico.buscar(registro_id).tags == []


def test_rf005_associar_tag_inexistente(servicos):
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    with pytest.raises(NaoEncontradoError):
        servicos.demandas.associar_tag(demanda.id, 999)


def test_rf005_excluir_tag_desassocia_registros(servicos):
    tag = servicos.tags.criar(nome="MPF", cor="#EF5350")
    demanda = servicos.demandas.criar(**DADOS_DEMANDA)
    servicos.demandas.associar_tag(demanda.id, tag.id)
    servicos.tags.excluir(tag.id)
    assert servicos.demandas.buscar(demanda.id).tags == []
