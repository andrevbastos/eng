"""Configuração do banco e montagem dos serviços: RS001, RS015, NR006."""
import sqlite3
from pathlib import Path

import pytest

from src import config
from src.aplicacao import abrir_banco
from src.config import Configuracao, ConfiguracaoError
from tests.dados import DADOS_DEMANDA


@pytest.fixture
def arquivo_config(tmp_path):
    return tmp_path / "cfg" / "config.json"


def test_rs001_sem_configuracao(arquivo_config):
    assert config.carregar(arquivo_config) == Configuracao()


def test_rs001_salvar_e_carregar(arquivo_config, tmp_path):
    caminho = tmp_path / "Pasta Assessoria" / "assessoria.db"
    config.salvar(Configuracao(caminho), arquivo_config)
    assert config.carregar(arquivo_config).caminho_db == caminho


@pytest.mark.parametrize("conteudo", ["{corrompido", "[]", '{"caminho_db": 5}', '{"caminho_db": ""}'])
def test_rs001_configuracao_invalida_equivale_a_nao_configurado(arquivo_config, conteudo):
    arquivo_config.parent.mkdir()
    arquivo_config.write_text(conteudo, encoding="utf-8")
    assert config.carregar(arquivo_config).caminho_db is None


def test_rs001_falha_ao_salvar_vira_erro_exibivel(tmp_path):
    bloqueio = tmp_path / "arquivo"
    bloqueio.write_text("x")
    with pytest.raises(ConfiguracaoError):
        config.salvar(Configuracao(tmp_path / "a.db"), bloqueio / "config.json")


def test_arquivo_padrao_fica_na_pasta_do_usuario(monkeypatch, tmp_path):
    monkeypatch.setattr(config.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert config.arquivo_padrao() == tmp_path / "AssessoriaJuridicaIFC" / "config.json"


# --- Validação do caminho escolhido ------------------------------------------

def test_rs001_novo_banco_recebe_extensao_db(tmp_path):
    assert config.validar_novo_banco(tmp_path / "assessoria") == tmp_path / "assessoria.db"


def test_rs001_novo_banco_nao_sobrescreve(tmp_path):
    existente = tmp_path / "assessoria.db"
    existente.write_bytes(b"")
    with pytest.raises(ConfiguracaoError, match="Já existe"):
        config.validar_novo_banco(existente)


def test_rs001_novo_banco_em_pasta_inexistente(tmp_path):
    with pytest.raises(ConfiguracaoError, match="pasta não existe"):
        config.validar_novo_banco(tmp_path / "nao_existe" / "a.db")


def test_rs001_banco_existente_inexistente(tmp_path):
    with pytest.raises(ConfiguracaoError, match="não encontrado"):
        config.validar_banco_existente(tmp_path / "a.db")


def test_rs001_banco_existente_que_nao_e_sqlite(tmp_path):
    falso = tmp_path / "planilha.db"
    falso.write_text("isto não é um banco")
    with pytest.raises(ConfiguracaoError, match="não é um banco"):
        config.validar_banco_existente(falso)


def test_rs001_banco_existente_valido(tmp_path):
    caminho = tmp_path / "a.db"
    sqlite3.connect(caminho).execute("CREATE TABLE t (x)").connection.close()
    assert config.validar_banco_existente(caminho) == caminho


# --- Abertura do banco -------------------------------------------------------

def test_rs001_rs015_abrir_banco_cria_tabelas_e_servicos(tmp_path):
    caminho = tmp_path / "assessoria.db"
    servicos = abrir_banco(caminho)
    servicos.demandas.criar(**DADOS_DEMANDA)
    servicos.fechar()

    reaberto = abrir_banco(caminho)
    assert [d.titulo for d in reaberto.demandas.listar()] == [DADOS_DEMANDA["titulo"]]
    assert reaberto.caminho_db == Path(caminho)
    reaberto.fechar()
