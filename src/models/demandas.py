import enum
import datetime 
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, Enum

from database.base import Base

class StatusDemanda(enum.Enum):
    PENDENTE = "Pendente"
    EM_ANDAMENTO = "Em andamento"
    CONCLUIDA = "Concluída"

class DemandaTable(Base):
    __tablename__ = "demandas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    alvo_motivo: Mapped[str] = mapped_column(nullable=False)
    data_entrada: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    data_limite: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[StatusDemanda] = mapped_column(
        Enum(StatusDemanda), 
        nullable=False, 
        default=StatusDemanda.PENDENTE
    )
    caminho_pasta: Mapped[str] = mapped_column(nullable=False)
    origem_canal: Mapped[str] = mapped_column(nullable=False)
    origem_remetente: Mapped[str] = mapped_column(nullable=False)
    origem_destinatario: Mapped[str] = mapped_column(nullable=False)
    origem_documento: Mapped[Optional[str]] = mapped_column(nullable=True)
    obs: Mapped[Optional[str]] = mapped_column(nullable=True)