"""TagService (RS015, RF005, RS006)."""
import re
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Tag, tags_demandas, tags_documentos, tags_pareceres, tags_subsidios
from src.services import historico
from src.services.base import ServicoBase, exigir

COR_HEX = re.compile(r"#[0-9A-Fa-f]{6}")
COR_INVALIDA = "Use uma cor hexadecimal no formato #RRGGBB."
NOME_REPETIDO = "Já existe uma tag com este nome."

# Associação -> (tabela do registro, coluna do registro).
ASSOCIACOES = (
    (tags_demandas, "demandas", "demanda_id"),
    (tags_pareceres, "pareceres", "parecer_id"),
    (tags_subsidios, "subsidios", "subsidio_id"),
    (tags_documentos, "documentos", "documento_id"),
)


class TagService(ServicoBase):
    modelo = Tag
    tabela = "tags"
    campos = ("nome", "cor")

    def listar(self) -> list[Tag]:
        with self._transacao() as sessao:
            return list(sessao.scalars(select(Tag).order_by(func.lower(Tag.nome))))

    def _completar(self, dados: dict[str, Any], criando: bool) -> dict[str, Any]:
        if isinstance(dados.get("cor"), str):
            dados["cor"] = dados["cor"].upper()
        return dados

    def _validar(self, sessao: Session, dados: dict[str, Any], registro_id: int | None) -> dict[str, str]:
        erros = exigir(dados, self.campos)
        if "cor" not in erros and not COR_HEX.fullmatch(dados["cor"]):
            erros["cor"] = COR_INVALIDA
        if "nome" not in erros and self._nome_em_uso(sessao, dados["nome"], registro_id):
            erros["nome"] = NOME_REPETIDO
        return erros

    def _nome_em_uso(self, sessao: Session, nome: str, registro_id: int | None) -> bool:
        consulta = select(Tag.id).where(func.lower(Tag.nome) == nome.lower())
        if registro_id is not None:
            consulta = consulta.where(Tag.id != registro_id)
        return sessao.scalar(consulta) is not None

    def _antes_excluir(self, sessao: Session, tag: Tag) -> None:
        # As associações caem em cascata; cada registro afetado guarda no seu
        # histórico que perdeu a tag.
        for associacao, tabela, coluna in ASSOCIACOES:
            consulta = select(associacao.c[coluna]).where(associacao.c.tag_id == tag.id)
            for registro_id in sessao.scalars(consulta):
                historico.registrar(sessao, tabela, registro_id, "tags", tag.nome, None)

    def _descricao(self, tag: Tag) -> str:
        return tag.nome
