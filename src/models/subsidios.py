import datetime 
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, ForeignKey

from database.base import Base

class SubsidioTable(Base):
    __tablename__ = "subsidios"

    id: Mapped[int] = mapped_column(primary_key=True)
    demanda_id: Mapped[int] = mapped_column(ForeignKey("demandas.id"), nullable=False)
    setor_fonte: Mapped[str] = mapped_column(nullable=False)
    data_aquisicao: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    resposta: Mapped[str] = mapped_column(nullable=False)