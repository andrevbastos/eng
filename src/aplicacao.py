"""Montagem da aplicação: abre o .db configurado e entrega os serviços à interface (RS001, RS015)."""
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.exc import DatabaseError, OperationalError

from src.config import ConfiguracaoError
from src.database.base import criar_engine, criar_fabrica_sessoes, criar_tabelas
from src.services import DemandaService, DocumentoService, ParecerService, SubsidioService, TagService


@dataclass
class Servicos:
    caminho_db: Path
    engine: Engine
    demandas: DemandaService
    pareceres: ParecerService
    subsidios: SubsidioService
    documentos: DocumentoService
    tags: TagService

    def fechar(self) -> None:
        self.engine.dispose()


def abrir_banco(caminho_db: Path) -> Servicos:
    """Abre (ou cria) o .db e garante que as tabelas existam."""
    engine = criar_engine(caminho_db)
    try:
        criar_tabelas(engine)
    except (OperationalError, DatabaseError) as erro:
        engine.dispose()
        raise ConfiguracaoError(f"Não foi possível abrir o banco {caminho_db}: {erro.orig}") from erro
    fabrica = criar_fabrica_sessoes(engine)
    return Servicos(
        caminho_db=Path(caminho_db),
        engine=engine,
        demandas=DemandaService(fabrica),
        pareceres=ParecerService(fabrica),
        subsidios=SubsidioService(fabrica),
        documentos=DocumentoService(fabrica),
        tags=TagService(fabrica),
    )
