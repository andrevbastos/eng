"""Configuração local do usuário (RS001): onde fica o arquivo .db.

O caminho escolhido é guardado num JSON na pasta de dados do usuário
(%APPDATA% no Windows), fora do .db, para que a escolha sobreviva a
atualizações do executável.
"""
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

NOME_PASTA = "AssessoriaJuridicaIFC"
NOME_ARQUIVO = "config.json"
CABECALHO_SQLITE = b"SQLite format 3\x00"
EXTENSAO_DB = ".db"


class ConfiguracaoError(Exception):
    """Caminho de banco recusado; a mensagem é exibível ao usuário."""


@dataclass
class Configuracao:
    caminho_db: Path | None = None


def arquivo_padrao() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / NOME_PASTA / NOME_ARQUIVO


def carregar(arquivo: Path | None = None) -> Configuracao:
    """Lê a configuração; arquivo ausente ou corrompido equivale a não configurado."""
    arquivo = arquivo or arquivo_padrao()
    try:
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Configuracao()
    caminho = dados.get("caminho_db") if isinstance(dados, dict) else None
    return Configuracao(Path(caminho) if isinstance(caminho, str) and caminho else None)


def salvar(configuracao: Configuracao, arquivo: Path | None = None) -> None:
    arquivo = arquivo or arquivo_padrao()
    dados = {"caminho_db": str(configuracao.caminho_db) if configuracao.caminho_db else None}
    try:
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as erro:
        raise ConfiguracaoError(f"Não foi possível salvar a configuração em {arquivo}: {erro.strerror}") from erro


def validar_novo_banco(caminho: Path) -> Path:
    """Caminho para criar um .db novo, numa pasta existente e sem sobrescrever outro arquivo."""
    caminho = Path(caminho)
    if caminho.suffix.lower() != EXTENSAO_DB:
        caminho = caminho.with_name(caminho.name + EXTENSAO_DB)
    if not caminho.parent.is_dir():
        raise ConfiguracaoError(f"A pasta não existe: {caminho.parent}")
    if caminho.exists():
        raise ConfiguracaoError(
            f"Já existe um arquivo em {caminho}. Use \"Abrir banco existente\" ou escolha outro nome."
        )
    return caminho


def validar_banco_existente(caminho: Path) -> Path:
    """Caminho de um .db já existente; recusa arquivos que não sejam SQLite."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise ConfiguracaoError(f"Arquivo não encontrado: {caminho}")
    try:
        with open(caminho, "rb") as arquivo:
            cabecalho = arquivo.read(len(CABECALHO_SQLITE))
    except OSError as erro:
        raise ConfiguracaoError(f"Não foi possível ler {caminho}: {erro.strerror}") from erro
    # Arquivo vazio é um SQLite válido (ainda sem páginas).
    if cabecalho and cabecalho != CABECALHO_SQLITE:
        raise ConfiguracaoError(f"O arquivo não é um banco de dados do sistema: {caminho}")
    return caminho
