"""ParecerService (RS015, RF002, RS017, RD004, RS011)."""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.models import Documento, Parecer, tags_pareceres
from src.services import historico, pesquisa
from src.services.base import ComTags, ServicoBase, exigir, exigir_data

OBRIGATORIOS_PARECER = ("numero", "assunto", "conclusao", "data")
NUMERO_REPETIDO = "Já existe um parecer com este número."


class ParecerService(ComTags, ServicoBase):
    modelo = Parecer
    tabela = "pareceres"
    campos = ("numero", "assunto", "conclusao", "data", "observacoes")
    carregar = (
        selectinload(Parecer.tags),
        selectinload(Parecer.documentos).selectinload(Documento.tags),
    )

    # RS011: campos comparados por similaridade; o número só por trecho exato.
    campos_pesquisa = ("assunto", "observacoes")

    def pesquisar(
        self,
        texto: str | None = None,
        *,
        tag_id: int | None = None,
        ano: int | None = None,
        pagina: int = 1,
    ) -> pesquisa.Pagina:
        """Pesquisa por texto, tag e ano de emissão (decisão da sessão 0), paginada (RS018)."""
        condicoes = []
        if tag_id is not None:
            condicoes.append(Parecer.id.in_(
                select(tags_pareceres.c.parecer_id).where(tags_pareceres.c.tag_id == tag_id)
            ))
        if ano is not None:
            condicoes.append(func.strftime("%Y", Parecer.data) == f"{ano:04d}")
        with self._transacao() as sessao:
            return pesquisa.pesquisar(
                sessao, Parecer, condicoes, texto, pagina, self.campos_pesquisa,
                tags_pareceres, "parecer_id", campo_numero="numero",
            )

    def anos(self) -> list[int]:
        """Anos com pareceres emitidos, do mais recente ao mais antigo (filtro por ano)."""
        with self._transacao() as sessao:
            ano = func.strftime("%Y", Parecer.data)
            return [int(valor) for valor in sessao.scalars(select(ano).distinct().order_by(ano.desc()))]

    def listar_historico(self, parecer_id: int) -> list:
        """Histórico do parecer e dos seus documentos atuais (RF014)."""
        with self._transacao() as sessao:
            parecer = self._obter(sessao, parecer_id, self.carregar)
            registros = [("pareceres", parecer.id)] + [("documentos", d.id) for d in parecer.documentos]
            return historico.consultar(sessao, registros)

    def _validar(self, sessao: Session, dados: dict[str, Any], registro_id: int | None) -> dict[str, str]:
        erros = exigir(dados, OBRIGATORIOS_PARECER)
        exigir_data(erros, dados, "data")
        if "numero" not in erros and self._numero_em_uso(sessao, dados["numero"], registro_id):
            erros["numero"] = NUMERO_REPETIDO
        return erros

    def _numero_em_uso(self, sessao: Session, numero: str, registro_id: int | None) -> bool:
        # Comparação sem diferenciar maiúsculas: "pj-042/2026" repete "PJ-042/2026".
        consulta = select(Parecer.id).where(func.lower(Parecer.numero) == numero.lower())
        if registro_id is not None:
            consulta = consulta.where(Parecer.id != registro_id)
        return sessao.scalar(consulta) is not None

    def _descricao(self, parecer: Parecer) -> str:
        return parecer.numero

    def _documentos_de(self, parecer: Parecer) -> list[Documento]:
        return list(parecer.documentos)
