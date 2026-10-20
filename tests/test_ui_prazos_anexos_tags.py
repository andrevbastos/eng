"""Prazos, anexos e tags na interface: RS019, RF015, RF004, RS022, RF011, RS020, RNF007, RF005.

Pulado sem display.
"""
import datetime
import tkinter

import customtkinter as ctk
import pytest

from tests.dados import DADOS_DEMANDA, DADOS_PARECER

ui = pytest.importorskip("src.ui.app")
HOJE = datetime.date.today()


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
def principal(app):
    return app.current_view


@pytest.fixture
def demandas(principal):
    return principal.abas["demandas"]


@pytest.fixture
def avisos(demandas, monkeypatch):
    registrados = []
    monkeypatch.setattr(demandas, "avisar", lambda titulo, mensagem: registrados.append((titulo, mensagem)))
    return registrados


@pytest.fixture
def abertos(monkeypatch):
    from src.ui import sistema

    chamadas = []
    monkeypatch.setattr(sistema, "abrir_arquivo", lambda caminho: chamadas.append(("arquivo", caminho)))
    monkeypatch.setattr(sistema, "abrir_url", lambda url: chamadas.append(("url", url)))
    return chamadas


def nova(app, dias: int, **campos):
    dados = {**DADOS_DEMANDA, "data_entrada": HOJE - datetime.timedelta(days=60),
             "data_limite": HOJE + datetime.timedelta(days=dias), **campos}
    return app.servicos.demandas.criar(**dados)


def botoes(widget, texto: str) -> list[ctk.CTkButton]:
    encontrados = []
    for filho in widget.winfo_children():
        if isinstance(filho, ctk.CTkButton) and filho.cget("text") == texto:
            encontrados.append(filho)
        encontrados.extend(botoes(filho, texto))
    return encontrados


def textos(widget) -> list[str]:
    encontrados = []
    for filho in widget.winfo_children():
        if isinstance(filho, ctk.CTkLabel):
            encontrados.append(filho.cget("text"))
        encontrados.extend(textos(filho))
    return encontrados


# --- Prazos (RS019, RF015) ----------------------------------------------------------

def test_rs019_cores_na_lista(app, demandas):
    vencida = nova(app, -1)
    hoje = nova(app, 0)
    limite = nova(app, 4)
    folgada = nova(app, 5)
    concluida = nova(app, -3, status="Concluída")
    demandas.atualizar_lista()
    assert demandas.lista.item(str(vencida.id), "tags") == ("vencida",)
    assert demandas.lista.item(str(hoje.id), "tags") == ("proxima",)
    assert demandas.lista.item(str(limite.id), "tags") == ("proxima",)
    assert demandas.lista.item(str(folgada.id), "tags") == ""
    assert demandas.lista.item(str(concluida.id), "tags") == ""


def test_rf015_total_ao_abrir_e_fechar_alerta(app, tmp_path):
    nova(app, -2)
    nova(app, -1)
    nova(app, 3)
    app.usar_banco_existente(app.servicos.caminho_db)  # reabre, como ao iniciar
    principal = app.current_view
    assert principal.alerta.winfo_manager() == "pack"
    assert (principal.contagem_prazos.vencidas, principal.contagem_prazos.proximas) == (2, 1)
    assert "2 vencida(s)" in principal.lbl_vencidas.cget("text")
    assert "1 vencendo em até 5 dias" in principal.lbl_proximas.cget("text")
    principal.fechar_alerta()
    assert principal.alerta.winfo_manager() == ""


def test_sem_prazos_criticos_nao_ha_alerta(app, principal):
    nova(app, 30)
    principal.abas["demandas"].atualizar_lista()
    assert principal.alerta.winfo_manager() == ""


def test_alerta_acompanha_alteracoes(app, principal, demandas):
    demanda = nova(app, 30)
    demandas.atualizar_lista()
    app.servicos.demandas.editar(demanda.id, data_limite=HOJE - datetime.timedelta(days=1))
    demandas.atualizar_lista()
    assert principal.contagem_prazos.vencidas == 1


def test_badge_de_prazo_nos_detalhes(app, demandas):
    demanda = nova(app, 2)
    demandas.mostrar_detalhe(demanda.id)
    assert "  Vence em 2 dias  " in textos(demandas.conteudo_painel)


# --- Anexos (RF004, RS022) ----------------------------------------------------------

def test_rf004_anexar_e_remover(app, demandas, monkeypatch, arquivo, avisos):
    demanda = nova(app, 30)
    demandas.mostrar_detalhe(demanda.id)
    caminho = arquivo("oficio.pdf")
    monkeypatch.setattr(demandas, "escolher_arquivo", lambda: caminho)
    botoes(demandas.conteudo_painel, "+ Anexar")[0].invoke()
    [documento] = app.servicos.demandas.buscar(demanda.id).documentos
    assert documento.caminho_arquivo == caminho
    assert "oficio.pdf" in textos(demandas.conteudo_painel)
    assert avisos == []

    monkeypatch.setattr(demandas, "confirmar", lambda *_: True)
    monkeypatch.setattr(demandas, "perguntar", lambda *_: False)  # mantém o arquivo no disco
    botoes(demandas.conteudo_painel, "Remover")[0].invoke()
    assert app.servicos.demandas.buscar(demanda.id).documentos == []
    assert demandas.registro_aberto == demanda.id


@pytest.mark.parametrize("nome, tamanho, trecho", [
    ("programa.exe", 10, "Formato não aceito"),
    ("enorme.pdf", 50 * 1024 * 1024 + 1, "50 MB"),
])
def test_rs022_arquivo_recusado_com_mensagem(app, demandas, monkeypatch, arquivo, avisos, nome, tamanho, trecho):
    demanda = nova(app, 30)
    demandas.mostrar_detalhe(demanda.id)
    monkeypatch.setattr(demandas, "escolher_arquivo", lambda: arquivo(nome, tamanho))
    demandas.anexar(demanda_id=demanda.id)
    assert app.servicos.demandas.buscar(demanda.id).documentos == []
    [(titulo, mensagem)] = avisos
    assert titulo == "Documento recusado" and trecho in mensagem


def test_anexar_cancelado_nao_faz_nada(app, demandas, monkeypatch, avisos):
    demanda = nova(app, 30)
    monkeypatch.setattr(demandas, "escolher_arquivo", lambda: "")
    demandas.anexar(demanda_id=demanda.id)
    assert app.servicos.demandas.buscar(demanda.id).documentos == [] and avisos == []


def test_rf004_anexo_no_parecer_e_no_subsidio(app, principal, monkeypatch, arquivo):
    pareceres = principal.abas["pareceres"]
    parecer = app.servicos.pareceres.criar(**DADOS_PARECER)
    monkeypatch.setattr(pareceres, "escolher_arquivo", lambda: arquivo("parecer.pdf"))
    pareceres.mostrar_detalhe(parecer.id)
    botoes(pareceres.conteudo_painel, "+ Anexar")[0].invoke()
    assert len(app.servicos.pareceres.buscar(parecer.id).documentos) == 1

    demandas = principal.abas["demandas"]
    demanda = nova(app, 30)
    subsidio = app.servicos.subsidios.criar(demanda_id=demanda.id, setor_fonte="Proad",
                                            data_aquisicao=HOJE, resposta="ok")
    monkeypatch.setattr(demandas, "escolher_arquivo", lambda: arquivo("planilha.xlsx"))
    demandas.mostrar_detalhe(demanda.id)
    botoes(demandas.conteudo_painel, "Anexar")[0].invoke()
    assert len(app.servicos.subsidios.buscar(subsidio.id).documentos) == 1
    assert "planilha.xlsx" in textos(demandas.conteudo_painel)


# --- Abrir (RF011, RS020, RNF007) -----------------------------------------------------

def test_rnf007_abrir_documento_em_3_interacoes(app, demandas, abertos, arquivo):
    demanda = nova(app, 30, titulo="Ofício MPF sobre acessibilidade")
    nova(app, 30, titulo="Outra demanda")
    caminho = arquivo("notificacao.pdf")
    app.servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=caminho)
    demandas.atualizar_lista()

    demandas.busca.definir("acessibilidade")         # 1. pesquisar
    demandas.pesquisar()
    demandas.lista.selection_set(demandas.lista.get_children()[0])
    demandas._abrir_selecionado()                     # 2. clique duplo na demanda
    botoes(demandas.conteudo_painel, "Abrir")[0].invoke()  # 3. "Abrir"
    assert abertos == [("arquivo", caminho)]


def test_rs020_abrir_no_drive_so_com_link(app, demandas, abertos, arquivo):
    demanda = nova(app, 30)
    documento = app.servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo())
    demandas.mostrar_detalhe(demanda.id)
    assert botoes(demandas.conteudo_painel, "Abrir no Drive") == []

    url = "https://drive.google.com/file/d/abc/view"
    demandas.editar_link(app.servicos.documentos.buscar(documento.id))
    form = demandas.conteudo_painel
    form.campos["url_drive"].definir(url)
    form.salvar()
    assert app.servicos.documentos.buscar(documento.id).url_drive == url
    botoes(demandas.conteudo_painel, "Abrir no Drive")[0].invoke()
    assert abertos == [("url", url)]


def test_rs020_link_invalido_fica_no_formulario(app, demandas, arquivo):
    demanda = nova(app, 30)
    documento = app.servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo())
    demandas.mostrar_detalhe(demanda.id)
    demandas.editar_link(documento)
    form = demandas.conteudo_painel
    form.campos["url_drive"].definir("drive.google.com/sem-https")
    form.salvar()
    assert demandas.conteudo_painel is form
    assert "https://" in form.campos["url_drive"].lbl_erro.cget("text")


def test_rf011_arquivo_sumido_avisa(app, demandas, avisos, arquivo):
    import os

    demanda = nova(app, 30)
    caminho = arquivo("sumiu.pdf")
    documento = app.servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=caminho)
    os.remove(caminho)
    demandas.abrir_documento(documento)
    [(titulo, mensagem)] = avisos
    assert titulo == "Arquivo não encontrado" and caminho in mensagem


# --- Tags (RF005) ----------------------------------------------------------------------

def test_rf005_seletor_associa_desassocia_e_cria(app, demandas):
    tag = app.servicos.tags.criar(nome="MPF", cor="#EF5350")
    demanda = nova(app, 30)
    demandas.mostrar_detalhe(demanda.id)
    botoes(demandas.conteudo_painel, "Editar tags")[0].invoke()
    seletor = demandas.conteudo_painel
    assert type(seletor).__name__ == "SeletorTags"

    seletor.caixas[tag.id].toggle()  # marca
    assert [t.id for t in app.servicos.demandas.buscar(demanda.id).tags] == [tag.id]
    seletor.caixas[tag.id].toggle()  # desmarca
    assert app.servicos.demandas.buscar(demanda.id).tags == []

    seletor.nome_nova.definir("Urgente")
    seletor.criar_e_marcar()
    assert [t.nome for t in app.servicos.demandas.buscar(demanda.id).tags] == ["Urgente"]

    seletor.nome_nova.definir("mpf")  # nome repetido
    seletor.criar_e_marcar()
    assert "Já existe" in seletor.lbl_mensagem.cget("text")

    botoes(seletor, "Concluir")[0].invoke()
    assert " Urgente " in textos(demandas.conteudo_painel)


def test_rf005_tags_de_subsidio_e_documento(app, demandas, arquivo):
    tag = app.servicos.tags.criar(nome="Proad", cor="#3A7BD5")
    demanda = nova(app, 30)
    subsidio = app.servicos.subsidios.criar(demanda_id=demanda.id, setor_fonte="Proad",
                                            data_aquisicao=HOJE, resposta="ok")
    documento = app.servicos.documentos.criar(demanda_id=demanda.id, caminho_arquivo=arquivo())
    demandas.mostrar_detalhe(demanda.id)

    demandas.editar_tags(app.servicos.subsidios, app.servicos.subsidios.buscar(subsidio.id), "Tags")
    demandas.conteudo_painel.caixas[tag.id].toggle()
    demandas.editar_tags_documento(app.servicos.documentos.buscar(documento.id))
    demandas.conteudo_painel.caixas[tag.id].toggle()
    assert app.servicos.tags.usos(tag.id) == 2


def test_rf005_tela_de_tags_crud(app, principal, monkeypatch):
    principal.mostrar_aba("tags")
    tela = principal.abas["tags"]
    form = tela.formulario
    form.campos["nome"].definir("Licitação")
    form.campos["cor"].definir("#66bb6a")
    form.salvar()
    [tag] = app.servicos.tags.listar()
    assert (tag.nome, tag.cor) == ("Licitação", "#66BB6A")
    assert tela.lbl_lista.cget("text") == "TAGS (1)"

    tela.mostrar_formulario(tag)
    tela.formulario.campos["nome"].definir("Licitações")
    tela.formulario.salvar()
    assert app.servicos.tags.buscar(tag.id).nome == "Licitações"

    # Cor inválida: "Salvar" continua habilitado (campo preenchido), mas o serviço recusa.
    tela.mostrar_formulario(app.servicos.tags.buscar(tag.id))
    tela.formulario.campos["cor"].definir("verde")
    tela.formulario.salvar()
    assert "#RRGGBB" in tela.formulario.campos["cor"].lbl_erro.cget("text")

    demanda = nova(app, 30)
    app.servicos.demandas.associar_tag(demanda.id, tag.id)
    perguntas = []
    monkeypatch.setattr(tela, "confirmar", lambda titulo, mensagem: perguntas.append(mensagem) or True)
    tela.excluir(app.servicos.tags.buscar(tag.id), app.servicos.tags.usos(tag.id))
    assert app.servicos.tags.listar() == []
    assert "1 registro(s)" in perguntas[0]
    assert app.servicos.demandas.buscar(demanda.id).tags == []


def test_paleta_preenche_a_cor(principal):
    principal.mostrar_aba("tags")
    campo = principal.abas["tags"].formulario.campos["cor"]
    [amarelo] = [b for b in campo.winfo_children()[1].winfo_children()
                 if isinstance(b, ctk.CTkButton) and b.cget("fg_color") == "#FACC15"]
    amarelo.invoke()
    assert campo.valor() == "#FACC15"
    assert campo.previa.cget("text").strip() == "Prévia"
