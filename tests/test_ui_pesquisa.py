"""Pesquisa na interface: RF006, RF007, RF008, RF009, RS011, RS018. Pulado sem display."""
import datetime
import tkinter

import pytest
from sqlalchemy import insert

from src.models import Demanda
from src.ui.views.aba import NENHUM_RESULTADO
from tests.dados import DADOS_DEMANDA, DADOS_PARECER

ui = pytest.importorskip("src.ui.app")


@pytest.fixture
def app(tmp_path):
    try:
        app = ui.App(arquivo_config=tmp_path / "config.json")
    except tkinter.TclError as erro:
        pytest.skip(f"sem display: {erro}")
    app.usar_novo_banco(tmp_path / "assessoria.db")
    app.update()
    yield app
    app.fechar()


@pytest.fixture
def demandas(app):
    return app.current_view.abas["demandas"]


@pytest.fixture
def pareceres(app):
    principal = app.current_view
    principal.mostrar_aba("pareceres")
    return principal.abas["pareceres"]


def linhas(aba) -> list[int]:
    return [int(iid) for iid in aba.lista.get_children()]


def aviso_visivel(aba) -> bool:
    return aba.aviso_vazio.winfo_manager() == "place"


def nova(app, **campos):
    neutros = dict(alvo_motivo="Análise jurídica", origem_remetente="Gabinete")
    return app.servicos.demandas.criar(**{**DADOS_DEMANDA, **neutros, **campos})


def test_rf006_digitar_agenda_a_pesquisa_e_filtra_a_lista(app, demandas):
    edital = nova(app, titulo="Esclarecimento Edital nº 04/2026")
    nova(app, titulo="Defesa trabalhista")
    demandas.atualizar_lista()
    assert len(linhas(demandas)) == 2

    demandas.busca.definir("editl")  # com erro de digitação
    assert demandas._pesquisa_agendada is not None  # espera a pausa na digitação
    app.after(400)
    app.update()
    assert linhas(demandas) == [edital.id]
    assert demandas.lbl_lista.cget("text") == "DEMANDAS (1)"


def test_rf008_localizar_por_id(app, demandas):
    criadas = [nova(app, titulo=f"Demanda {letra}") for letra in "ABC"]
    demandas.busca.definir(f"#{criadas[1].id}")
    demandas.pesquisar()
    assert linhas(demandas) == [criadas[1].id]


def test_rf007_filtros_combinados_e_data_invalida(app, demandas):
    a = nova(app, titulo="Edital A", status="Concluída", origem_canal="SIGAA",
             data_entrada=datetime.date(2026, 1, 5), data_limite=datetime.date(2026, 1, 9))
    b = nova(app, titulo="Edital B", status="Concluída")
    tag = app.servicos.tags.criar(nome="MPF", cor="#EF5350")
    app.servicos.demandas.associar_tag(b.id, tag.id)
    demandas.atualizar_lista()

    demandas.f_status.escolher("Concluída")
    assert linhas(demandas) == [b.id, a.id]
    demandas.f_tag.escolher("MPF")
    assert linhas(demandas) == [b.id]
    demandas.f_tag.escolher("Todas as tags")
    demandas.f_canal.escolher("SIGAA")
    assert linhas(demandas) == [a.id]

    demandas.f_canal.escolher("Todos os canais")
    demandas.f_campo_data.escolher("Data limite")
    demandas.f_ate.definir("31/01/2026")
    demandas.pesquisar()
    assert linhas(demandas) == [a.id]

    # Data incompleta ou inválida: borda destacada e a lista não muda.
    demandas.f_ate.definir("31/02/2026")
    demandas.pesquisar()
    assert demandas.f_ate.invalida()
    assert linhas(demandas) == [a.id]


def test_rf009_nenhum_resultado_e_limpar_filtros(app, demandas):
    unica = nova(app, titulo="Edital")
    demandas.busca.definir("xyzwq")
    demandas.f_status.escolher("Concluída")
    assert linhas(demandas) == []
    assert aviso_visivel(demandas)
    assert demandas.lbl_vazio.cget("text") == NENHUM_RESULTADO == "Nenhum resultado encontrado"
    assert demandas.btn_limpar_vazio.winfo_manager() == "pack"

    demandas.btn_limpar_vazio.invoke()
    assert linhas(demandas) == [unica.id]
    assert not aviso_visivel(demandas)
    assert demandas.busca.texto() == "" and demandas.f_status.get() == "Todos os status"


def test_lista_vazia_sem_filtros_nao_oferece_limpar(demandas):
    demandas.atualizar_lista()
    assert aviso_visivel(demandas)
    assert demandas.lbl_vazio.cget("text") == "Nenhuma demanda cadastrada."
    assert demandas.btn_limpar_vazio.winfo_manager() == ""


def test_rs018_paginacao_de_50(app, demandas):
    entrada = datetime.date(2026, 1, 1)
    with app.servicos.engine.begin() as conexao:
        conexao.execute(insert(Demanda), [
            dict(titulo=f"Processo {i}", alvo_motivo="x", data_entrada=entrada, data_limite=entrada,
                 status="Em análise", segredo_justica=False, origem_canal="E-mail",
                 origem_remetente="r", origem_destinatario="d")
            for i in range(120)
        ])
    demandas.atualizar_lista()
    assert len(linhas(demandas)) == 50
    assert demandas.lbl_pagina.cget("text") == "Página 1 de 3"
    assert demandas.btn_anterior.cget("state") == "disabled"

    demandas.btn_proxima.invoke()
    demandas.btn_proxima.invoke()
    assert len(linhas(demandas)) == 20 and linhas(demandas)[-1] == 1
    assert demandas.lbl_pagina.cget("text") == "Página 3 de 3"
    assert demandas.btn_proxima.cget("state") == "disabled"

    # Nova pesquisa volta à primeira página.
    demandas.busca.definir("processo")
    demandas.pesquisar()
    assert demandas.lbl_pagina.cget("text") == "Página 1 de 3"


def test_opcoes_de_tag_acompanham_o_banco(app, demandas):
    tag = app.servicos.tags.criar(nome="Urgente", cor="#FFB74D")
    demandas.atualizar_lista()
    assert "Urgente" in demandas.f_tag.cget("values")
    demandas.f_tag.escolher("Urgente")
    app.servicos.tags.excluir(tag.id)
    demandas.atualizar_lista()
    assert demandas.f_tag.get() == "Todas as tags"


def test_rf008_pareceres_por_numero_e_ano(app, pareceres):
    p25 = app.servicos.pareceres.criar(**{**DADOS_PARECER, "numero": "PJ-010/2025",
                                          "data": datetime.date(2025, 6, 1)})
    p26 = app.servicos.pareceres.criar(**DADOS_PARECER)
    pareceres.atualizar_lista()
    assert linhas(pareceres) == [p26.id, p25.id]
    assert list(pareceres.f_ano.cget("values")) == ["Todos os anos", "2026", "2025"]

    pareceres.f_ano.escolher("2025")
    assert linhas(pareceres) == [p25.id]
    pareceres.f_ano.escolher("Todos os anos")
    pareceres.busca.definir("042/2026")
    pareceres.pesquisar()
    assert linhas(pareceres) == [p26.id]
