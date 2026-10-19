"""Pareceres da Procuradoria (RS002, RD004)."""
import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.tags import Tag, tags_pareceres

if TYPE_CHECKING:
    from src.models.documentos import Documento


class Parecer(Base):
    __tablename__ = "pareceres"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String, unique=True)
    assunto: Mapped[str] = mapped_column(String)
    conclusao: Mapped[str] = mapped_column(String)
    data: Mapped[datetime.date] = mapped_column(Date)
    observacoes: Mapped[Optional[str]] = mapped_column(String)

    documentos: Mapped[list["Documento"]] = relationship(
        back_populates="parecer", cascade="all, delete-orphan", passive_deletes=True
    )
    tags: Mapped[list[Tag]] = relationship(secondary=tags_pareceres)
