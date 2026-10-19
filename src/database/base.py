"""
Configuração do banco SQLite (RS001, RNF001).

O caminho do arquivo .db é escolhido pelo usuário (RS001), por isso o engine
não é global: ele é criado a partir do caminho informado.
"""
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

MEMORIA = ":memory:"


class Base(DeclarativeBase):
    pass


def criar_engine(caminho_db: str | Path) -> Engine:
    """Cria o engine para o arquivo .db informado (ou ":memory:", nos testes)."""
    if str(caminho_db) == MEMORIA:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(f"sqlite:///{Path(caminho_db)}")

    @event.listens_for(engine, "connect")
    def _ativar_chaves_estrangeiras(conexao_dbapi, _registro):
        # O SQLite só aplica FKs (e ON DELETE CASCADE) com este PRAGMA ligado.
        cursor = conexao_dbapi.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def criar_tabelas(engine: Engine) -> None:
    # Importa os modelos para registrá-los em Base.metadata.
    import src.models  # noqa: F401

    Base.metadata.create_all(engine)
