"""
Configuração do banco SQLite (RS001, RNF001).

O caminho do arquivo .db é escolhido pelo usuário (RS001), por isso o engine
não é global: ele é criado a partir do caminho informado.
"""
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

MEMORIA = ":memory:"
# Tempo (s) que o SQLite aguarda um bloqueio de escrita antes de desistir.
ESPERA_BLOQUEIO_S = 5.0


class Base(DeclarativeBase):
    pass


def criar_engine(caminho_db: str | Path, espera_bloqueio_s: float = ESPERA_BLOQUEIO_S) -> Engine:
    """Cria o engine para o arquivo .db informado (ou ":memory:", nos testes)."""
    if str(caminho_db) == MEMORIA:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            f"sqlite:///{Path(caminho_db)}",
            connect_args={"timeout": espera_bloqueio_s},
        )

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


def criar_fabrica_sessoes(engine: Engine) -> sessionmaker:
    # expire_on_commit=False: os objetos devolvidos à interface continuam legíveis.
    return sessionmaker(engine, expire_on_commit=False)
