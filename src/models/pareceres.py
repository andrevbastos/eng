import datetime 
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date

from database.base import Base

class ParecerTable(Base):
    __tablename__ = "pareceres"

    id: Mapped[int] = mapped_column(primary_key=True)
    assunto: Mapped[str] = mapped_column(nullable=False)
    conclusao: Mapped[str] = mapped_column(nullable=False)
    data: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    obs: Mapped[Optional[str]] = mapped_column(nullable=True)