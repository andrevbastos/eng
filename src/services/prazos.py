"""Alertas de prazo das demandas (RS019, RF015).

Decisão da sessão 0: dias corridos, contando hoje. "Próxima do prazo" é a
demanda não concluída cuja data limite cai entre hoje e hoje + 4 dias (5 dias
no total); "vencida" é a não concluída com data limite anterior a hoje.
"""
import datetime
from dataclasses import dataclass

DIAS_ALERTA = 5
PROXIMA = "proxima"
VENCIDA = "vencida"


@dataclass(frozen=True)
class ContagemPrazos:
    proximas: int
    vencidas: int


def ultimo_dia_alerta(hoje: datetime.date) -> datetime.date:
    return hoje + datetime.timedelta(days=DIAS_ALERTA - 1)


def situacao(data_limite: datetime.date, concluida: bool, hoje: datetime.date | None = None) -> str | None:
    """PROXIMA, VENCIDA ou None (demanda concluída ou com prazo folgado)."""
    hoje = hoje or datetime.date.today()
    if concluida:
        return None
    if data_limite < hoje:
        return VENCIDA
    if data_limite <= ultimo_dia_alerta(hoje):
        return PROXIMA
    return None


def descrever(data_limite: datetime.date, hoje: datetime.date | None = None) -> str:
    """Texto curto para o painel de detalhes, ex.: "Vence em 2 dias"."""
    hoje = hoje or datetime.date.today()
    dias = (data_limite - hoje).days
    if dias < 0:
        return f"Vencida há {-dias} dia{'s' if dias < -1 else ''}"
    if dias == 0:
        return "Vence hoje"
    return f"Vence em {dias} dia{'s' if dias > 1 else ''}"
