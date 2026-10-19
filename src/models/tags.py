"""Tags e tabelas de associação (RS006–RS010, RU004)."""
from sqlalchemy import CheckConstraint, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base

# "#" seguido de exatamente 6 dígitos hexadecimais, ex.: #3A7BD5 (RS006).
_HEX = "[0-9A-Fa-f]"
_COR_HEX_GLOB = "#" + _HEX * 6


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        CheckConstraint(f"cor GLOB '{_COR_HEX_GLOB}'", name="ck_tags_cor_hex"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String, unique=True)
    cor: Mapped[str] = mapped_column(String(7))


def _tabela_associacao(nome: str, coluna: str, tabela_alvo: str) -> Table:
    return Table(
        nome,
        Base.metadata,
        Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
        Column(coluna, ForeignKey(f"{tabela_alvo}.id", ondelete="CASCADE"), primary_key=True),
    )


tags_demandas = _tabela_associacao("tags_demandas", "demanda_id", "demandas")        # RS007
tags_pareceres = _tabela_associacao("tags_pareceres", "parecer_id", "pareceres")     # RS008
tags_subsidios = _tabela_associacao("tags_subsidios", "subsidio_id", "subsidios")    # RS009
tags_documentos = _tabela_associacao("tags_documentos", "documento_id", "documentos")  # RS010
