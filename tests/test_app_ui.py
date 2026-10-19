"""Fluxo de abertura da janela: RS001, RS012, NR006. Pulado sem display."""
import tkinter

import pytest

from src import config
from src.config import Configuracao

ui = pytest.importorskip("src.ui.app")


@pytest.fixture
def criar_app(tmp_path):
    apps = []

    def _criar(caminho_db=None):
        arquivo_config = tmp_path / "config.json"
        if caminho_db is not None:
            config.salvar(Configuracao(caminho_db), arquivo_config)
        try:
            app = ui.App(arquivo_config=arquivo_config)
        except tkinter.TclError as erro:
            pytest.skip(f"sem display: {erro}")
        app.update()
        apps.append(app)
        return app

    yield _criar
    for app in apps:
        app.fechar()


def _tela(app):
    return type(app.current_view).__name__


def test_nr006_rs001_primeira_execucao_pede_o_banco_sem_login(criar_app):
    app = criar_app()
    assert _tela(app) == "ConfiguracaoBancoView"


def test_rs001_criar_banco_abre_a_janela_principal_e_salva(criar_app, tmp_path):
    app = criar_app()
    app.usar_novo_banco(tmp_path / "assessoria")
    assert _tela(app) == "PrincipalView"
    assert (tmp_path / "assessoria.db").is_file()
    assert config.carregar(app.arquivo_config).caminho_db == tmp_path / "assessoria.db"


def test_rs001_banco_configurado_abre_direto(criar_app, tmp_path):
    criar_app().usar_novo_banco(tmp_path / "assessoria.db")
    app = criar_app(tmp_path / "assessoria.db")
    assert _tela(app) == "PrincipalView"


def test_rs001_banco_configurado_sumiu(criar_app, tmp_path):
    app = criar_app(tmp_path / "removido.db")
    assert _tela(app) == "ConfiguracaoBancoView"
    assert "não encontrado" in app.current_view.lbl_erro.cget("text")


def test_rs001_escolha_invalida_mostra_erro_e_continua_na_tela(criar_app, tmp_path):
    app = criar_app()
    falso = tmp_path / "falso.db"
    falso.write_text("texto")
    app.usar_banco_existente(falso)
    assert _tela(app) == "ConfiguracaoBancoView"
    assert "não é um banco" in app.current_view.lbl_erro.cget("text")


def test_rs012_abas_demandas_e_pareceres(criar_app, tmp_path):
    app = criar_app()
    app.usar_novo_banco(tmp_path / "a.db")
    principal = app.current_view
    assert principal.aba_ativa == "demandas"
    principal.mostrar_aba("pareceres")
    app.update()
    assert principal.aba_ativa == "pareceres"
    assert principal.abas["pareceres"].winfo_ismapped()
    assert not principal.abas["demandas"].winfo_ismapped()


def test_trocar_banco_e_cancelar_volta_para_o_mesmo(criar_app, tmp_path):
    app = criar_app()
    app.usar_novo_banco(tmp_path / "a.db")
    app.mostrar_configuracao()
    assert _tela(app) == "ConfiguracaoBancoView"
    app.mostrar_principal()
    assert app.servicos.caminho_db == tmp_path / "a.db"
