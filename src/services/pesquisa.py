"""
Pesquisa por texto com fuzzy matching e paginação (RS011, RS018, RF006, RF008,
RF009, RNF003, RNF006).

Cada registro recebe a maior similaridade (0 a 100, rapidfuzz) entre o texto
pesquisado e os seus campos; entram no resultado os que atingem LIMIAR.
Decisão da sessão 0: id e número do parecer não são comparados por
similaridade. O id precisa ser igual ao digitado; o número precisa conter o
texto digitado, sem diferenciar maiúsculas (assim "042/2026" encontra
"PJ-042/2026", mas "PJ-043" não encontra "PJ-042").
"""
import math
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

from rapidfuzz import fuzz
from rapidfuzz.utils import default_process
from sqlalchemy import Table, func, select
from sqlalchemy.orm import Session

from src.models import Tag

LIMIAR = 70
POR_PAGINA = 50


@dataclass(frozen=True)
class Pagina:
    """Uma página de resultados (RS018)."""

    itens: list
    total: int
    pagina: int
    por_pagina: int = POR_PAGINA

    @property
    def total_paginas(self) -> int:
        return max(1, math.ceil(self.total / self.por_pagina))


@dataclass(frozen=True)
class Candidato:
    id: int
    textos: tuple[str | None, ...]
    numero: str | None = None


@lru_cache(maxsize=200_000)
def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos e sem pontuação: "Notificação" ~ "notificacao"."""
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return default_process(sem_acentos)


def similaridade(consulta: str, texto: str) -> float:
    """Ambos já normalizados. Texto longo: melhor trecho; texto curto (ex.: tag): inteiro."""
    if not texto:
        return 0.0
    if len(consulta) <= len(texto):
        return fuzz.partial_ratio(consulta, texto, score_cutoff=LIMIAR)
    return fuzz.ratio(consulta, texto, score_cutoff=LIMIAR)


def _id_digitado(texto: str) -> int | None:
    texto = texto.strip().removeprefix("#")
    return int(texto) if texto.isdigit() else None


def pontuar(texto: str, candidatos: Iterable[Candidato]) -> list[tuple[int, float]]:
    """(id, pontuação) dos candidatos que atingem o limiar, do mais ao menos parecido."""
    consulta = normalizar(texto)
    id_digitado = _id_digitado(texto)
    trecho_numero = texto.strip().casefold()
    encontrados = []
    exato = None
    for candidato in candidatos:
        if candidato.id == id_digitado:
            exato = (candidato.id, 100.0)
            continue
        if trecho_numero and candidato.numero and trecho_numero in candidato.numero.casefold():
            encontrados.append((candidato.id, 100.0))
            continue
        if not consulta:
            continue
        melhor = 0.0
        for campo in candidato.textos:
            if campo:
                melhor = max(melhor, similaridade(consulta, normalizar(campo)))
                if melhor == 100:
                    break
        if melhor >= LIMIAR:
            encontrados.append((candidato.id, melhor))
    # Empate: o mais recente primeiro, como na lista sem pesquisa.
    encontrados.sort(key=lambda par: (-par[1], -par[0]))
    # O id digitado vem primeiro, à frente de textos que apenas o citam (RF008).
    return [exato, *encontrados] if exato else encontrados


def limitar_pagina(pagina: int, total: int, por_pagina: int = POR_PAGINA) -> int:
    """Página pedida, dentro do intervalo existente (a última se passar do fim)."""
    return min(max(1, pagina), max(1, math.ceil(total / por_pagina)))


def pesquisar(
    sessao: Session,
    modelo: type,
    condicoes: list,
    texto: str | None,
    pagina: int,
    campos_texto: tuple[str, ...],
    associacao: Table,
    coluna_associacao: str,
    campo_numero: str | None = None,
    carregar: tuple = (),
) -> Pagina:
    """Filtra no SQL (RF007), pontua em Python (RF006) e carrega só a página pedida.

    Sem texto, a lista vem do mais recente ao mais antigo e a paginação fica no SQL.
    """
    texto = (texto or "").strip()
    if not texto:
        total = sessao.scalar(select(func.count()).select_from(modelo).where(*condicoes))
        pagina = limitar_pagina(pagina, total)
        ids = list(sessao.scalars(
            select(modelo.id).where(*condicoes).order_by(modelo.id.desc())
            .limit(POR_PAGINA).offset((pagina - 1) * POR_PAGINA)
        ))
    else:
        colunas = [getattr(modelo, campo) for campo in campos_texto]
        if campo_numero:
            colunas.append(getattr(modelo, campo_numero))
        linhas = sessao.execute(select(modelo.id, *colunas).where(*condicoes)).all()
        nomes_tags: dict[int, list[str]] = {}
        coluna = associacao.c[coluna_associacao]
        for registro_id, nome in sessao.execute(
            select(coluna, Tag.nome).join(Tag, Tag.id == associacao.c.tag_id)
        ):
            nomes_tags.setdefault(registro_id, []).append(nome)
        n = len(campos_texto)
        candidatos = (
            Candidato(
                id=linha[0],
                textos=(*linha[1:n + 1], *nomes_tags.get(linha[0], ())),
                numero=linha[n + 1] if campo_numero else None,
            )
            for linha in linhas
        )
        encontrados = pontuar(texto, candidatos)
        total = len(encontrados)
        pagina = limitar_pagina(pagina, total)
        inicio = (pagina - 1) * POR_PAGINA
        ids = [registro_id for registro_id, _ in encontrados[inicio:inicio + POR_PAGINA]]
    por_id = {
        registro.id: registro
        for registro in sessao.scalars(select(modelo).where(modelo.id.in_(ids)).options(*carregar))
    }
    return Pagina([por_id[registro_id] for registro_id in ids], total, pagina)
