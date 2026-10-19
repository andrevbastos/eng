"""Subsídios vinculados a uma Demanda (RS004)."""
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.tags import Tag, tags_subsidios

if TYPE_CHECKING:
    from src.models.demandas import Demanda
    from src.models.documentos import Documento


class Subsidio(Base):
    __tablename__ = "subsidios"

    id: Mapped[int] = mapped_column(primary_key=True)
    demanda_id: Mapped[int] = mapped_column(ForeignKey("demandas.id", ondelete="CASCADE"))
    setor_fonte: Mapped[str] = mapped_column(String)
    data_aquisicao: Mapped[datetime.date] = mapped_column(Date)
    resposta: Mapped[str] = mapped_column(String)

    demanda: Mapped["Demanda"] = relationship(back_populates="subsidios")
    documentos: Mapped[list["Documento"]] = relationship(
        back_populates="subsidio", cascade="all, delete-orphan", passive_deletes=True
    )
    tags: Mapped[list[Tag]] = relationship(secondary=tags_subsidios)
