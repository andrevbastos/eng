"""Documentos anexados (RS005, RS022, RD001)."""
import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.tags import Tag, tags_documentos

if TYPE_CHECKING:
    from src.models.demandas import Demanda
    from src.models.pareceres import Parecer
    from src.models.subsidios import Subsidio

# Formatos aceitos (RD001), comparados com a extensão do arquivo em minúsculas.
EXTENSOES_PERMITIDAS = ("pdf", "doc", "docx", "odt", "xlsx", "txt", "eml", "jpg", "png")
TAMANHO_MAXIMO_BYTES = 50 * 1024 * 1024  # 50 MB (RS022, RNF010)


class Documento(Base):
    __tablename__ = "documentos"
    __table_args__ = (
        # Cada documento pertence a exatamente um dono: demanda, parecer ou subsídio.
        CheckConstraint(
            "(parecer_id IS NOT NULL) + (demanda_id IS NOT NULL) + (subsidio_id IS NOT NULL) = 1",
            name="ck_documentos_um_dono",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    parecer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pareceres.id", ondelete="CASCADE"))
    demanda_id: Mapped[Optional[int]] = mapped_column(ForeignKey("demandas.id", ondelete="CASCADE"))
    subsidio_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subsidios.id", ondelete="CASCADE"))
    caminho_arquivo: Mapped[str] = mapped_column(String)
    url_drive: Mapped[Optional[str]] = mapped_column(String)
    tipo_arquivo: Mapped[str] = mapped_column(String)
    data_sincronizacao: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    parecer: Mapped[Optional["Parecer"]] = relationship(back_populates="documentos")
    demanda: Mapped[Optional["Demanda"]] = relationship(back_populates="documentos")
    subsidio: Mapped[Optional["Subsidio"]] = relationship(back_populates="documentos")
    tags: Mapped[list[Tag]] = relationship(secondary=tags_documentos)
