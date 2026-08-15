import datetime

from service.create import add_demanda, add_tag, add_tag_demanda
from service.update import update_demanda, change_tag_demanda
from models.demandas import DemandaTable, StatusDemanda
from models.tags import TagDemandaTable

def test_update_demanda(db_session):
    demanda_id = add_demanda(
        alvo_motivo="Antigo Motivo", data_entrada=datetime.date.today(),
        data_limite=datetime.date.today(), caminho_pasta="/a",
        origem_canal="Email", origem_remetente="X", origem_destinatario="Y"
    )
    
    # Atualiza o motivo e o status
    sucesso = update_demanda(demanda_id, alvo_motivo="Novo Motivo", status=StatusDemanda.CONCLUIDA)
    assert sucesso is True
    
    # Valida no banco
    demanda = db_session.get(DemandaTable, demanda_id)
    assert demanda.alvo_motivo == "Novo Motivo"
    assert demanda.status == StatusDemanda.CONCLUIDA

def test_change_tag_demanda(db_session):
    demanda_id = add_demanda(alvo_motivo="Teste", data_entrada=datetime.date.today(), data_limite=datetime.date.today(), caminho_pasta="/", origem_canal="Email", origem_remetente="X", origem_destinatario="Y")
    old_tag_id = add_tag("Tag Antiga")
    new_tag_id = add_tag("Tag Nova")
    
    add_tag_demanda(old_tag_id, demanda_id)
    
    # Troca a tag velha pela nova
    sucesso = change_tag_demanda(demanda_id, old_tag_id, new_tag_id)
    assert sucesso is True
    
    # Valida
    velha_assoc = db_session.get(TagDemandaTable, (old_tag_id, demanda_id))
    nova_assoc = db_session.get(TagDemandaTable, (new_tag_id, demanda_id))
    
    assert velha_assoc is None
    assert nova_assoc is not None
