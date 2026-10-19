"""Camada de serviços (RS015). A interface acessa o banco apenas por aqui."""
from src.services.demandas import DemandaService
from src.services.documentos import DocumentoService
from src.services.erros import BancoOcupadoError, NaoEncontradoError, ServicoError, ValidacaoError
from src.services.pareceres import ParecerService
from src.services.subsidios import SubsidioService
from src.services.tags import TagService

__all__ = [
    "BancoOcupadoError",
    "DemandaService",
    "DocumentoService",
    "NaoEncontradoError",
    "ParecerService",
    "ServicoError",
    "SubsidioService",
    "TagService",
    "ValidacaoError",
]
