import datetime

from service.create import add_demanda, add_parecer, add_tag, add_tag_demanda
from service.read import get_demanda, get_parecer, get_tag

def test_get_demanda(db_session):
    add_demanda(alvo_motivo="Investigação A", data_entrada=datetime.date.today(), data_limite=datetime.date.today(), caminho_pasta="/a", origem_canal="Email", origem_remetente="x", origem_destinatario="y")
    add_demanda(alvo_motivo="Investigação B", data_entrada=datetime.date.today(), data_limite=datetime.date.today(), caminho_pasta="/b", origem_canal="Portal", origem_remetente="x", origem_destinatario="y")
    
    resultados = get_demanda(alvo_motivo="Investigação A")
    assert len(resultados) == 1
    assert resultados[0].alvo_motivo == "Investigação A"
    
    resultados_canal = get_demanda(origem_canal="Portal")
    assert len(resultados_canal) == 1
    assert resultados_canal[0].alvo_motivo == "Investigação B"

def test_get_parecer_corrigido(db_session):
    add_parecer(assunto="Parecer Financeiro", conclusao="Aprovado", data=datetime.date.today())
    add_parecer(assunto="Parecer Tecnico", conclusao="Rejeitado", data=datetime.date.today())
    
    resultados = get_parecer(conclusao="Aprovado")
    assert len(resultados) == 1
    assert resultados[0].assunto == "Parecer Financeiro"

def test_get_demanda_por_tag(db_session):
    demanda_id = add_demanda(alvo_motivo="Urgente", data_entrada=datetime.date.today(), data_limite=datetime.date.today(), caminho_pasta="/a", origem_canal="Email", origem_remetente="x", origem_destinatario="y")
    tag_id = add_tag(nome="Prioridade")
    add_tag_demanda(tag_id, demanda_id)
    
    resultados = get_demanda(tag="Prioridade")
    assert len(resultados) == 1
    assert resultados[0].alvo_motivo == "Urgente"