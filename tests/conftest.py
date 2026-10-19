import datetime

import pytest
from sqlalchemy.orm import Session

from src.database.base import MEMORIA, criar_engine, criar_tabelas
from src.models import Demanda, Parecer


@pytest.fixture
def engine():
    engine = criar_engine(MEMORIA)
    criar_tabelas(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sessao(engine):
    with Session(engine) as sessao:
        yield sessao


@pytest.fixture
def nova_demanda():
    """Fábrica de Demanda válida; os campos podem ser sobrescritos por kwargs."""

    def _nova(**campos) -> Demanda:
        dados = dict(
            titulo="Ofício MPF 12/2026",
            alvo_motivo="Esclarecimento sobre o Edital nº 04/2026",
            data_entrada=datetime.date(2026, 8, 10),
            data_limite=datetime.date(2026, 8, 20),
            origem_canal="E-mail",
            origem_remetente="Proj. MPF Joinville",
            origem_destinatario="Assessoria Jurídica IFC",
        )
        dados.update(campos)
        return Demanda(**dados)

    return _nova


@pytest.fixture
def novo_parecer():
    def _novo(**campos) -> Parecer:
        dados = dict(
            numero="PJ-042/2026",
            assunto="Dispensa de licitação para insumos de pesquisa",
            conclusao="Deferido",
            data=datetime.date(2026, 5, 15),
        )
        dados.update(campos)
        return Parecer(**dados)

    return _novo
