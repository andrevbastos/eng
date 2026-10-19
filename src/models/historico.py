"""Histórico de alterações (RS016, RF014, RU010)."""
import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class HistoricoAlteracao(Base):
    __tablename__ = "historico_alteracoes"
    __table_args__ = (Index("ix_historico_registro", "tabela", "registro_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tabela: Mapped[str] = mapped_column(String)
    # Sem FK: o histórico precisa sobreviver à exclusão do registro.
    registro_id: Mapped[int]
    campo: Mapped[str] = mapped_column(String)
    valor_anterior: Mapped[Optional[str]] = mapped_column(String)
    valor_novo: Mapped[Optional[str]] = mapped_column(String)
    data_hora: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
