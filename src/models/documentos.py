import datetime 
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey

from database.base import Base

class DocumentoTable(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    parecer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pareceres.id"), nullable=True)
    demanda_id: Mapped[Optional[int]] = mapped_column(ForeignKey("demandas.id"), nullable=True)
    subsidio_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subsidios.id"), nullable=True)
    caminho_arquivo: Mapped[str] = mapped_column(nullable=False)
    tipo_arquivo: Mapped[Optional[str]] = mapped_column(nullable=True)
    data_sincronizacao: Mapped[datetime.datetime] = mapped_column(DateTime)