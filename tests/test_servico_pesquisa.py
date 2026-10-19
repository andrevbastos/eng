"""Pesquisa: RS011, RS018, RF006, RF007, RF008, RF009, RNF003, RNF006."""
import datetime
import time

import pytest
from sqlalchemy import insert

from src.models import Demanda, Parecer, tags_demandas
from src.services.pesquisa import LIMIAR, POR_PAGINA, Pagina, normalizar, similaridade
from tests.dados import DADOS_DEMANDA, DADOS_PARECER


def demanda(servicos, **campos):
    # Textos neutros, para que só o campo de cada teste coincida com a pesquisa.
    neutros = dict(titulo="Sem título", alvo_motivo="Análise jurídica", origem_remetente="Gabinete")
    return servicos.demandas.criar(**{**DADOS_DEMANDA, **neutros, **campos})


def parecer(servicos, **campos):
    return servicos.pareceres.criar(**{**DADOS_PARECER, "assunto": "Consulta", **campos})


def ids(pagina: Pagina) -> list[int]:
    return [item.id for item in pagina.itens]


# --- Similaridade (RNF003) -----------------------------------------------------

def test_rnf003_limiar_e_normalizacao():
    assert LIMIAR == 70
    assert normalizar("Notificação Recomendatória") == "notificacao recomendatoria"
    assert similaridade(normalizar("notificacao"), normalizar("Notificação MPF")) == 100
    # Erro de digitação ainda passa do limiar; termo sem relação não.
    assert similaridade(normalizar("acessibilidde"), normalizar("Acessibilidade campus Araquari")) >= LIMIAR
    assert similaridade(normalizar("orçamento"), normalizar("Acessibilidade campus Araquari")) == 0
    # Texto curto (nome de tag) é comparado inteiro, não como trecho da pesquisa.
    assert similaridade(normalizar("urgente reitoria"), normalizar("Urgente")) == 0


# --- Demandas (RS011, RF006, RF008) --------------------------------------------

def test_rf006_pesquisa_por_campos_de_texto_da_demanda(servicos):
    titulo = demanda(servicos, titulo="Esclarecimento Edital nº 04/2026")
    motivo = demanda(servicos, titulo="Outro assunto", alvo_motivo="Contratação de terceirizados")
    remetente = demanda(servicos, titulo="Item C", origem_remetente="Procuradoria Federal")
    obs = demanda(servicos, titulo="Item D", observacoes="Aguardando assinatura do Reitor")
    demanda(servicos, titulo="Sem relação")

    assert ids(servicos.demandas.pesquisar("edital")) == [titulo.id]
    assert ids(servicos.demandas.pesquisar("terceirizado")) == [motivo.id]
    assert ids(servicos.demandas.pesquisar("procuradoria")) == [remetente.id]
    assert ids(servicos.demandas.pesquisar("assinatura reitor")) == [obs.id]


def test_rf006_tolera_erro_de_digitacao_e_acentos(servicos):
    alvo = demanda(servicos, titulo="Notificação Recomendatória da Reitoria")
    demanda(servicos, titulo="Defesa em processo trabalhista")
    assert ids(servicos.demandas.pesquisar("notificacao recomendatoria")) == [alvo.id]
    assert ids(servicos.demandas.pesquisar("recomendatoira")) == [alvo.id]


def test_rs011_pesquisa_pelo_nome_da_tag(servicos):
    marcada = demanda(servicos, titulo="Primeira")
    demanda(servicos, titulo="Segunda")
    tag = servicos.tags.criar(nome="Ministério Público", cor="#EF5350")
    servicos.demandas.associar_tag(marcada.id, tag.id)
    assert ids(servicos.demandas.pesquisar("ministerio publico")) == [marcada.id]


def test_rf008_id_exato(servicos):
    criadas = [demanda(servicos, titulo=f"Demanda {letra}") for letra in "ABCDEFGHIJKL"]
    alvo = criadas[10]
    assert (criadas[0].id, alvo.id) == (1, 11)
    assert ids(servicos.demandas.pesquisar("11")) == [alvo.id]
    assert ids(servicos.demandas.pesquisar("#11")) == [alvo.id]
    # O id não é comparado por similaridade: "1" não encontra a demanda 11.
    assert ids(servicos.demandas.pesquisar("1")) == [1]


def test_rf006_ordem_por_semelhanca_e_mais_recente_no_empate(servicos):
    parcial = demanda(servicos, titulo="Edital de pesquisa")
    exata1 = demanda(servicos, titulo="Edital 04/2026")
    exata2 = demanda(servicos, titulo="Edital 04/2026")
    assert ids(servicos.demandas.pesquisar("edital 04/2026"))[:2] == [exata2.id, exata1.id]
    assert parcial.id not in ids(servicos.demandas.pesquisar("edital 04/2026"))[:2]


def test_sem_texto_lista_tudo_do_mais_recente(servicos):
    criadas = [demanda(servicos, titulo=f"D{i}") for i in range(3)]
    assert ids(servicos.demandas.pesquisar()) == [d.id for d in reversed(criadas)]
    assert ids(servicos.demandas.pesquisar("   ")) == [d.id for d in reversed(criadas)]


# --- Filtros (RF007) -------------------------------------------------------------

def test_rf007_filtros_de_status_canal_e_tag(servicos):
    a = demanda(servicos, titulo="Edital A", status="Concluída", origem_canal="SIGAA")
    b = demanda(servicos, titulo="Edital B", status="Concluída", origem_canal="E-mail")
    c = demanda(servicos, titulo="Edital C")
    tag = servicos.tags.criar(nome="MPF", cor="#EF5350")
    servicos.demandas.associar_tag(b.id, tag.id)
    servicos.demandas.associar_tag(c.id, tag.id)

    assert ids(servicos.demandas.pesquisar(status="Concluída")) == [b.id, a.id]
    assert ids(servicos.demandas.pesquisar(canal="SIGAA")) == [a.id]
    assert ids(servicos.demandas.pesquisar(tag_id=tag.id)) == [c.id, b.id]
    assert ids(servicos.demandas.pesquisar(status="Concluída", tag_id=tag.id)) == [b.id]
    # Combinados com o texto.
    assert ids(servicos.demandas.pesquisar("edital c", tag_id=tag.id))[0] == c.id
    assert ids(servicos.demandas.pesquisar("edital", canal="Presencial")) == []


def test_rf007_intervalos_de_data_de_entrada_e_limite(servicos):
    d = datetime.date
    jan = demanda(servicos, data_entrada=d(2026, 1, 10), data_limite=d(2026, 1, 20))
    mar = demanda(servicos, data_entrada=d(2026, 3, 10), data_limite=d(2026, 4, 30))

    assert ids(servicos.demandas.pesquisar(entrada_de=d(2026, 3, 1))) == [mar.id]
    assert ids(servicos.demandas.pesquisar(entrada_ate=d(2026, 1, 10))) == [jan.id]
    assert ids(servicos.demandas.pesquisar(limite_de=d(2026, 1, 20), limite_ate=d(2026, 1, 20))) == [jan.id]
    assert ids(servicos.demandas.pesquisar(limite_de=d(2026, 5, 1))) == []


# --- Paginação (RS018, RF009) ----------------------------------------------------

def test_rs018_paginas_de_50(servicos):
    for i in range(POR_PAGINA * 2 + 5):
        demanda(servicos, titulo=f"Edital {i}")
    primeira = servicos.demandas.pesquisar("edital")
    assert POR_PAGINA == 50
    assert (len(primeira.itens), primeira.total, primeira.total_paginas) == (50, 105, 3)
    terceira = servicos.demandas.pesquisar("edital", pagina=3)
    assert len(terceira.itens) == 5 and terceira.pagina == 3
    # Página fora do intervalo vira a última (ex.: depois de excluir itens).
    assert servicos.demandas.pesquisar("edital", pagina=9).pagina == 3
    todas = {i for p in (1, 2, 3) for i in ids(servicos.demandas.pesquisar(pagina=p))}
    assert len(todas) == 105


def test_rf009_sem_resultados(servicos):
    demanda(servicos)
    vazia = servicos.demandas.pesquisar("xyzwq")
    assert (vazia.itens, vazia.total, vazia.pagina, vazia.total_paginas) == ([], 0, 1, 1)


# --- Pareceres (RS011, RF008) ----------------------------------------------------

def test_rf008_parecer_por_numero_e_assunto(servicos):
    p42 = parecer(servicos, numero="PJ-042/2026", assunto="Dispensa para obra")
    p43 = parecer(servicos, numero="PJ-043/2026", assunto="Contrato de limpeza")
    assert ids(servicos.pareceres.pesquisar("PJ-042/2026")) == [p42.id]
    assert ids(servicos.pareceres.pesquisar("pj-042")) == [p42.id]
    assert ids(servicos.pareceres.pesquisar("042/2026")) == [p42.id]
    assert ids(servicos.pareceres.pesquisar("limpeza")) == [p43.id]
    # Número sem similaridade: "PJ-044" não encontra os vizinhos.
    assert ids(servicos.pareceres.pesquisar("PJ-044")) == []


def test_rf007_parecer_filtros_de_tag_e_ano(servicos):
    antigo = parecer(servicos, numero="PJ-001/2025", data=datetime.date(2025, 3, 1))
    novo = parecer(servicos, numero="PJ-001/2026", data=datetime.date(2026, 3, 1))
    tag = servicos.tags.criar(nome="Licitação", cor="#3A7BD5")
    servicos.pareceres.associar_tag(antigo.id, tag.id)

    assert servicos.pareceres.anos() == [2026, 2025]
    assert ids(servicos.pareceres.pesquisar(ano=2025)) == [antigo.id]
    assert ids(servicos.pareceres.pesquisar(tag_id=tag.id)) == [antigo.id]
    assert ids(servicos.pareceres.pesquisar("licitacao")) == [antigo.id]
    assert ids(servicos.pareceres.pesquisar(ano=2026, tag_id=tag.id)) == []
    assert ids(servicos.pareceres.pesquisar()) == [novo.id, antigo.id]


# --- Desempenho (RNF006) -----------------------------------------------------------

PALAVRAS = (
    "edital ofício notificação recomendatória defesa processo trabalhista terceirizados "
    "acessibilidade campus araquari denúncia seletivo bolsistas ação civil pública obras "
    "bloco licitação contrato dispensa pesquisa reitoria procuradoria orçamento servidores"
).split()


def _texto(i: int, n: int) -> str:
    return " ".join(PALAVRAS[(i * 7 + k * 3) % len(PALAVRAS)] for k in range(n)) + f" {i}"


@pytest.fixture
def dez_mil(servicos, fabrica):
    entrada = datetime.date(2026, 1, 1)
    linhas = [
        dict(
            titulo=_texto(i, 6),
            alvo_motivo=_texto(i + 1, 40),
            data_entrada=entrada,
            data_limite=entrada + datetime.timedelta(days=i % 300),
            status="Em análise",
            segredo_justica=False,
            observacoes=_texto(i + 2, 25) if i % 2 else None,
            origem_canal="E-mail",
            origem_remetente=f"Remetente {i % 97}",
            origem_destinatario="Assessoria Jurídica IFC",
        )
        for i in range(10_000)
    ]
    tags = [servicos.tags.criar(nome=f"Tag {i}", cor="#3A7BD5") for i in range(10)]
    with fabrica.begin() as sessao:
        sessao.execute(insert(Demanda), linhas)
        sessao.execute(insert(tags_demandas), [
            dict(tag_id=tags[i % 10].id, demanda_id=i + 1) for i in range(0, 10_000, 3)
        ])
        sessao.execute(insert(Parecer), [
            dict(numero=f"PJ-{i:05d}/2026", assunto=_texto(i, 8), conclusao="Deferido",
                 data=entrada, observacoes=_texto(i, 20))
            for i in range(10_000)
        ])
    return tags


@pytest.mark.parametrize("texto", ["", "acessibilidade araquari", "notifcação", "5000", "zzz qqq"])
def test_rnf006_primeira_pagina_em_ate_1s_com_10_mil_demandas(servicos, dez_mil, texto):
    servicos.demandas.pesquisar("aquecimento")  # o primeiro acesso carrega bibliotecas e caches
    inicio = time.perf_counter()
    pagina = servicos.demandas.pesquisar(texto)
    decorrido = time.perf_counter() - inicio
    assert decorrido < 1.0, f"{decorrido:.2f} s"
    if texto == "5000":
        # Outros registros citam "5000" no texto, mas o id exato vem primeiro (RF008).
        assert pagina.itens[0].id == 5000 and pagina.total > 1


def test_rnf006_pareceres_e_filtros_em_ate_1s(servicos, dez_mil):
    servicos.pareceres.pesquisar("aquecimento")
    inicio = time.perf_counter()
    servicos.pareceres.pesquisar("dispensa licitacao")
    servicos.demandas.pesquisar("edital", tag_id=dez_mil[3].id, limite_de=datetime.date(2026, 3, 1))
    assert (time.perf_counter() - inicio) / 2 < 1.0


def test_rnf006_detalhes_em_ate_2s_com_10_mil_demandas(servicos, dez_mil):
    inicio = time.perf_counter()
    servicos.demandas.buscar(7_777)
    servicos.demandas.listar_historico(7_777)
    assert time.perf_counter() - inicio < 2.0
