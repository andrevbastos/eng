from sqlalchemy.orm import Session

from database.base import engine
from models.pareceres import ParecerTable
from models.demandas import DemandaTable
from models.subsidios import SubsidioTable
from models.documentos import DocumentoTable
from models.tags import TagTable, TagDemandaTable, TagParecerTable, TagSubsidioTable, TagDocumentoTable

def remove_demanda(demanda_id: int) -> bool:
    with Session(engine) as session:
        demanda = session.get(DemandaTable, demanda_id)
        if not demanda:
            return False
        
        session.delete(demanda)
        session.commit()
        return True
    
def remove_parecer(parecer_id: int) -> bool:
    with Session(engine) as session:
        parecer = session.get(ParecerTable, parecer_id)
        if not parecer:
            return False
        
        session.delete(parecer)
        session.commit()
        return True
    
def remove_subsidio(subsidio_id: int) -> bool:
    with Session(engine) as session:
        subsidio = session.get(SubsidioTable, subsidio_id)
        if not subsidio:
            return False
        
        session.delete(subsidio)
        session.commit()
        return True
    
def remove_documento(documento_id: int) -> bool:
    with Session(engine) as session:
        documento = session.get(DocumentoTable, documento_id)
        if not documento:
            return False
        
        session.delete(documento)
        session.commit()
        return True
    
def remove_tag(tag_id: int) -> bool:
    with Session(engine) as session:
        tag = session.get(TagTable, tag_id)
        if not tag:
            return False
        
        associations = session.query(TagDemandaTable).filter_by(tag_id=tag_id).all()
        for association in associations:
            session.delete(association)
        associations = session.query(TagParecerTable).filter_by(tag_id=tag_id).all()
        for association in associations:
            session.delete(association)
        associations = session.query(TagSubsidioTable).filter_by(tag_id=tag_id).all()
        for association in associations:
            session.delete(association)
        associations = session.query(TagDocumentoTable).filter_by(tag_id=tag_id).all()
        for association in associations:
            session.delete(association)
        
        session.delete(tag)
        session.commit()
        return True