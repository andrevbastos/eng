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


# --- Serviços (RS015) --------------------------------------------------------

@pytest.fixture
def fabrica(engine):
    from src.database.base import criar_fabrica_sessoes

    return criar_fabrica_sessoes(engine)


@pytest.fixture
def servicos(fabrica):
    from types import SimpleNamespace

    from src.services import (
        DemandaService, DocumentoService, ParecerService, SubsidioService, TagService,
    )

    return SimpleNamespace(
        demandas=DemandaService(fabrica),
        pareceres=ParecerService(fabrica),
        subsidios=SubsidioService(fabrica),
        documentos=DocumentoService(fabrica),
        tags=TagService(fabrica),
    )


@pytest.fixture
def arquivo(tmp_path):
    """Fábrica de arquivo real no disco, para anexos (RF004)."""

    def _arquivo(nome="notificacao_mpf.pdf", tamanho=128):
        caminho = tmp_path / nome
        with open(caminho, "wb") as f:
            f.truncate(tamanho)
        return str(caminho)

    return _arquivo
