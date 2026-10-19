"""Abas, formulários e detalhes: RF001–RF003, RF010, RF014, RS012, RS017. Pulado sem display."""
import datetime
import tkinter
from pathlib import Path

import customtkinter as ctk
import pytest

from src.services import BancoOcupadoError
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


def textos(widget) -> list[str]:
    """Todos os textos de rótulos visíveis dentro de um widget."""
    encontrados = []
    for filho in widget.winfo_children():
        if isinstance(filho, ctk.CTkLabel):
            encontrados.append(filho.cget("text"))
        encontrados.extend(textos(filho))
    return encontrados


def preencher(formulario, **valores):
    for nome, valor in valores.items():
        formulario.campos[nome].definir(valor)
    formulario.atualizar_estado()


def abrir_pela_lista(aba, registro_id):
    """Seleciona a linha e dispara o mesmo tratador do clique duplo e do Enter."""
    aba.lista.selection_set(str(registro_id))
    aba._abrir_selecionado()


def nome_painel(aba):
    return type(aba.conteudo_painel).__name__


# --- Formulário de demanda (RS017, RF001) ---------------------------------------

def test_rs017_salvar_desabilitado_ate_preencher_obrigatorios(demandas):
    demandas.mostrar_formulario(None)
    form = demandas.conteudo_painel
    assert form.btn_salvar.cget("state") == "disabled"
    assert form.campos["titulo"].widget.cget("border_color") != form.campos["observacoes"].widget.cget("border_color")

    preencher(form, **{k: v for k, v in DADOS_DEMANDA.items()})
    assert form.btn_salvar.cget("state") == "normal"

    form.campos["data_limite"].var.set("31/02/2026")
    form.atualizar_estado()
    assert form.btn_salvar.cget("state") == "disabled"
    assert "DD/MM/AAAA" in form.campos["data_limite"].lbl_erro.cget("text")


def test_rf001_nova_demanda_padroes_e_cadastro(app, demandas):
    demandas.mostrar_formulario(None)
    form = demandas.conteudo_painel
    assert form.campos["status"].valor() == "Em análise"
    assert form.campos["data_entrada"].valor() == datetime.date.today()

    preencher(form, **DADOS_DEMANDA)
    form.campos["observacoes"].definir("Aguardando parecer")
    form.salvar()

    [demanda] = app.servicos.demandas.listar()
    assert demanda.titulo == DADOS_DEMANDA["titulo"] and demanda.observacoes == "Aguardando parecer"
    assert nome_painel(demandas) == "DetalheDemanda"
    assert demandas.lista.get_children() == (str(demanda.id),)
    assert demandas.lbl_lista.cget("text") == "DEMANDAS (1)"


def test_rs017_erro_do_servico_aparece_no_campo_e_mantem_formulario(app, demandas):
    demandas.mostrar_formulario(None)
    form = demandas.conteudo_painel
    preencher(form, **{**DADOS_DEMANDA, "data_limite": datetime.date(2026, 8, 1)})
    form.salvar()
    assert demandas.conteudo_painel is form
    assert "anterior" in form.campos["data_limite"].lbl_erro.cget("text")
    assert app.servicos.demandas.listar() == []


def test_banco_ocupado_mantem_formulario_preenchido(app, demandas, monkeypatch):
    def ocupado(**_):
        raise BancoOcupadoError()

    monkeypatch.setattr(app.servicos.demandas, "criar", ocupado)
    demandas.mostrar_formulario(None)
    form = demandas.conteudo_painel
    preencher(form, **DADOS_DEMANDA)
    form.salvar()
    assert demandas.conteudo_painel is form
    assert "ocupado" in form.lbl_mensagem.cget("text")
    assert form.campos["titulo"].valor() == DADOS_DEMANDA["titulo"]


def test_rf001_editar_e_cancelar(app, demandas):
    demanda = app.servicos.demandas.criar(**DADOS_DEMANDA)
    demandas.atualizar_lista()
    abrir_pela_lista(demandas, demanda.id)

    demandas.mostrar_formulario(demanda.id)
    form = demandas.conteudo_painel
    assert form.campos["titulo"].valor() == DADOS_DEMANDA["titulo"]
    form.campos["status"].definir("Concluída")
    form.salvar()
    assert app.servicos.demandas.buscar(demanda.id).status == "Concluída"

    demandas.mostrar_formulario(demanda.id)
    demandas.voltar()  # Cancelar volta aos detalhes do registro aberto
    assert nome_painel(demandas) == "DetalheDemanda"


# --- Detalhes (RF010, RF014, RS012) ----------------------------------------------

def test_rf010_rf014_detalhes_completos_na_mesma_tela(app, demandas, tmp_path):
    s = app.servicos
    demanda = s.demandas.criar(**DADOS_DEMANDA, segredo_justica=True)
    tag = s.tags.criar(nome="MPF", cor="#EF5350")
    s.demandas.associar_tag(demanda.id, tag.id)
    subsidio = s.subsidios.criar(demanda_id=demanda.id, setor_fonte="Proad",
                                 data_aquisicao=datetime.date(2026, 8, 12), resposta="Orçamento validado.")
    arquivo = tmp_path / "notificacao_mpf.pdf"
    arquivo.write_bytes(b"%PDF")
    s.documentos.criar(demanda_id=demanda.id, caminho_arquivo=str(arquivo))
    s.demandas.editar(demanda.id, status="Em andamento")
    demandas.atualizar_lista()

    abrir_pela_lista(demandas, demanda.id)
    assert nome_painel(demandas) == "DetalheDemanda"
    visiveis = textos(demandas.conteudo_painel)
    for esperado in [DADOS_DEMANDA["titulo"], DADOS_DEMANDA["alvo_motivo"], "Segredo de justiça",
                     " MPF ", f"Proad · 12/08/2026", "Orçamento validado.", "notificacao_mpf.pdf",
                     "Status: Em análise → Em andamento", f"Subsídios: adicionado Proad (#{subsidio.id})"]:
        assert any(esperado in t for t in visiveis), esperado


def test_rf010_clique_duplo_e_enter_abrem_os_detalhes(app, demandas):
    demanda = app.servicos.demandas.criar(**DADOS_DEMANDA)
    demandas.atualizar_lista()
    assert {"<Double-Button-1>", "<Key-Return>"} <= set(demandas.lista.bind())
    abrir_pela_lista(demandas, demanda.id)
    assert demandas.registro_aberto == demanda.id


# --- Subsídios (RF003) -----------------------------------------------------------

def test_rf003_adicionar_editar_e_excluir_subsidio(app, demandas, monkeypatch):
    demanda = app.servicos.demandas.criar(**DADOS_DEMANDA)
    demandas.mostrar_detalhe(demanda.id)

    demandas.formulario_subsidio(demanda.id)
    form = demandas.conteudo_painel
    preencher(form, setor_fonte="ProPessoas", resposta="Lista de servidores enviada.")
    form.salvar()
    [subsidio] = app.servicos.demandas.buscar(demanda.id).subsidios
    assert subsidio.data_aquisicao == datetime.date.today()
    assert nome_painel(demandas) == "DetalheDemanda"

    demandas.formulario_subsidio(demanda.id, subsidio)
    form = demandas.conteudo_painel
    form.campos["resposta"].definir("Lista revisada.")
    form.salvar()
    assert app.servicos.subsidios.buscar(subsidio.id).resposta == "Lista revisada."

    monkeypatch.setattr(demandas, "confirmar", lambda *_: True)
    demandas.excluir_subsidio(demanda.id, app.servicos.subsidios.buscar(subsidio.id))
    assert app.servicos.demandas.buscar(demanda.id).subsidios == []
    assert demandas.registro_aberto == demanda.id


# --- Exclusão ----------------------------------------------------------------------

def test_excluir_demanda_cancelado_nao_exclui(app, demandas, monkeypatch):
    demanda = app.servicos.demandas.criar(**DADOS_DEMANDA)
    monkeypatch.setattr(demandas, "confirmar", lambda *_: False)
    demandas.excluir_demanda(app.servicos.demandas.buscar(demanda.id))
    assert len(app.servicos.demandas.listar()) == 1


@pytest.mark.parametrize("apagar, existe_depois", [(False, True), (True, False)])
def test_excluir_demanda_pergunta_sobre_arquivos(app, demandas, monkeypatch, tmp_path, apagar, existe_depois):
    demanda = app.servicos.demandas.criar(**DADOS_DEMANDA)
    arquivo = tmp_path / "oficio.pdf"
    arquivo.write_bytes(b"%PDF")
    app.servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=str(arquivo))
    perguntas = []
    monkeypatch.setattr(demandas, "confirmar", lambda *_: True)
    monkeypatch.setattr(demandas, "perguntar", lambda *a: perguntas.append(a) or apagar)

    demandas.excluir_demanda(app.servicos.demandas.buscar(demanda.id))

    assert app.servicos.demandas.listar() == []
    assert len(perguntas) == 1
    assert Path(arquivo).exists() is existe_depois
    assert nome_painel(demandas) == "CTkFrame"  # painel vazio


# --- Pareceres (RF002, RD004) -------------------------------------------------------

def test_rf002_rd004_parecer_cadastro_e_numero_repetido(app, pareceres):
    pareceres.mostrar_formulario(None)
    form = pareceres.conteudo_painel
    preencher(form, **DADOS_PARECER)
    form.salvar()
    assert nome_painel(pareceres) == "DetalheParecer"

    pareceres.mostrar_formulario(None)
    form = pareceres.conteudo_painel
    preencher(form, **{**DADOS_PARECER, "numero": "pj-042/2026"})
    form.salvar()
    assert "Já existe" in form.campos["numero"].lbl_erro.cget("text")
    assert len(app.servicos.pareceres.listar()) == 1
