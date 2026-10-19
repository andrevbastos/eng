"""Demandas (RS003, RD002, RD006)."""
import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.tags import Tag, tags_demandas

if TYPE_CHECKING:
    from src.models.documentos import Documento
    from src.models.subsidios import Subsidio

STATUS_DEMANDA = (
    "Em análise",
    "Em andamento",
    "Aguardando subsídios",
    "Aguardando Procuradoria",
    "Aguardando assinatura do Reitor",
    "Concluída",
)
# Decisão do usuário na sessão 0: o padrão é "Em análise".
STATUS_PADRAO = "Em análise"
STATUS_CONCLUIDA = "Concluída"

CANAIS_ORIGEM = ("E-mail", "SIGAA", "Presencial", "Ofício", "Outro")


def _em(coluna: str, valores: tuple[str, ...]) -> str:
    lista = ", ".join(f"'{valor}'" for valor in valores)
    return f"{coluna} IN ({lista})"


class Demanda(Base):
    __tablename__ = "demandas"
    __table_args__ = (
        CheckConstraint(_em("status", STATUS_DEMANDA), name="ck_demandas_status"),
        CheckConstraint(_em("origem_canal", CANAIS_ORIGEM), name="ck_demandas_origem_canal"),
        CheckConstraint("data_limite >= data_entrada", name="ck_demandas_datas"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String)
    alvo_motivo: Mapped[str] = mapped_column(String)
    data_entrada: Mapped[datetime.date] = mapped_column(Date)
    data_limite: Mapped[datetime.date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String, default=STATUS_PADRAO)
    # Apenas informativo nesta versão (RD003).
    segredo_justica: Mapped[bool] = mapped_column(default=False)
    observacoes: Mapped[Optional[str]] = mapped_column(String)
    caminho_pasta: Mapped[Optional[str]] = mapped_column(String)
    origem_canal: Mapped[str] = mapped_column(String)
    origem_remetente: Mapped[str] = mapped_column(String)
    origem_destinatario: Mapped[str] = mapped_column(String)
    origem_documento: Mapped[Optional[str]] = mapped_column(String)

    subsidios: Mapped[list["Subsidio"]] = relationship(
        back_populates="demanda", cascade="all, delete-orphan", passive_deletes=True
    )
    documentos: Mapped[list["Documento"]] = relationship(
        back_populates="demanda", cascade="all, delete-orphan", passive_deletes=True
    )
    tags: Mapped[list[Tag]] = relationship(secondary=tags_demandas)
