"""Registro em historico_alteracoes (RS016, RF014).

Convenções (decididas na sessão 0):
- criação: uma linha por campo preenchido, com valor_anterior nulo;
- edição: uma linha por campo alterado;
- exclusão: uma linha com campo "*" e a descrição do registro em valor_anterior;
- associação de tags, anexos e subsídios: uma linha no registro pai, com o campo
  "tags", "documentos" ou "subsidios".
"""
import datetime
from typing import Any, Iterable

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from src.models import HistoricoAlteracao

CAMPO_EXCLUSAO = "*"


def serializar(valor: Any) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, (datetime.date, datetime.datetime)):
        return valor.isoformat()
    return str(valor)


def registrar(
    sessao: Session,
    tabela: str,
    registro_id: int,
    campo: str,
    anterior: Any = None,
    novo: Any = None,
) -> None:
    sessao.add(
        HistoricoAlteracao(
            tabela=tabela,
            registro_id=registro_id,
            campo=campo,
            valor_anterior=serializar(anterior),
            valor_novo=serializar(novo),
            data_hora=datetime.datetime.now(),
        )
    )


def registrar_criacao(sessao: Session, tabela: str, registro_id: int, valores: dict[str, Any]) -> None:
    for campo, valor in valores.items():
        if valor is not None:
            registrar(sessao, tabela, registro_id, campo, None, valor)


def registrar_edicao(
    sessao: Session, tabela: str, registro_id: int, antes: dict[str, Any], depois: dict[str, Any]
) -> None:
    for campo, novo in depois.items():
        anterior = antes.get(campo)
        if serializar(anterior) != serializar(novo):
            registrar(sessao, tabela, registro_id, campo, anterior, novo)


def registrar_exclusao(sessao: Session, tabela: str, registro_id: int, descricao: str) -> None:
    registrar(sessao, tabela, registro_id, CAMPO_EXCLUSAO, descricao, None)


def consultar(sessao: Session, registros: Iterable[tuple[str, int]]) -> list[HistoricoAlteracao]:
    """Histórico dos pares (tabela, registro_id), do mais recente ao mais antigo."""
    condicoes = [
        and_(HistoricoAlteracao.tabela == tabela, HistoricoAlteracao.registro_id == registro_id)
        for tabela, registro_id in registros
    ]
    if not condicoes:
        return []
    consulta = (
        select(HistoricoAlteracao)
        .where(or_(*condicoes))
        .order_by(HistoricoAlteracao.data_hora.desc(), HistoricoAlteracao.id.desc())
    )
    return list(sessao.scalars(consulta))
