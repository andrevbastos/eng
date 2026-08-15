from colour import Color
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy_utils import ColorType

from database.base import Base

class TagTable(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    cor: Mapped[Color] = mapped_column(ColorType, nullable=True)
    
class TagDemandaTable(Base):
    __tablename__ = "tag_demanda"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    demanda_id: Mapped[int] = mapped_column(ForeignKey("demandas.id"), primary_key=True)
    
class TagParecerTable(Base):
    __tablename__ = "tag_parecer"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    parecer_id: Mapped[int] = mapped_column(ForeignKey("pareceres.id"), primary_key=True)

class TagSubsidioTable(Base):
    __tablename__ = "tag_subsidio"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    subsidio_id: Mapped[int] = mapped_column(ForeignKey("subsidios.id"), primary_key=True)
    
class TagDocumentoTable(Base):
    __tablename__ = "tag_documento"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"), primary_key=True)