import datetime

from service.create import add_demanda, add_tag, add_tag_demanda
from service.remove import remove_demanda, remove_tag
from models.demandas import DemandaTable
from models.tags import TagTable, TagDemandaTable

def test_remove_demanda(db_session):
    demanda_id = add_demanda(
        alvo_motivo="Para Remover", data_entrada=datetime.date.today(),
        data_limite=datetime.date.today(), caminho_pasta="/",
        origem_canal="X", origem_remetente="Y", origem_destinatario="Z"
    )
    
    sucesso = remove_demanda(demanda_id)
    assert sucesso is True
    
    # Valida que não existe mais
    demanda = db_session.get(DemandaTable, demanda_id)
    assert demanda is None

def test_remove_tag_cascade(db_session):
    demanda_id = add_demanda(
        alvo_motivo="A", data_entrada=datetime.date.today(),
        data_limite=datetime.date.today(), caminho_pasta="/",
        origem_canal="X", origem_remetente="Y", origem_destinatario="Z"
    )
    tag_id = add_tag("Tag de Risco")
    add_tag_demanda(tag_id, demanda_id)
    
    # Remove a tag, o que deve deletar a associação também
    sucesso = remove_tag(tag_id)
    assert sucesso is True
    
    tag = db_session.get(TagTable, tag_id)
    assoc = db_session.get(TagDemandaTable, (tag_id, demanda_id))
    
    assert tag is None
    assert assoc is None
