import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.base import engine
from models.pareceres import ParecerTable
from models.demandas import DemandaTable
from models.subsidios import SubsidioTable
from models.documentos import DocumentoTable
from models.tags import TagTable, TagDemandaTable, TagParecerTable, TagSubsidioTable, TagDocumentoTable

def get_demanda(
    alvo_motivo: str = None,
    data_entrada: datetime.date = None,
    data_limite: datetime.date = None,
    origem_canal: str = None,
    origem_remetente: str = None,
    origem_destinatario: str = None,
    origem_documento: str = None,
    obs: str = None,
    tag: str = None
) -> list:
    with Session(engine) as session:
        query = select(DemandaTable)
        
        if alvo_motivo:
            query = query.where(DemandaTable.alvo_motivo == alvo_motivo)
        if data_entrada:
            query = query.where(DemandaTable.data_entrada == data_entrada)
        if data_limite:
            query = query.where(DemandaTable.data_limite == data_limite)
        if origem_canal:
            query = query.where(DemandaTable.origem_canal == origem_canal)
        if origem_remetente:
            query = query.where(DemandaTable.origem_remetente == origem_remetente)
        if origem_destinatario:
            query = query.where(DemandaTable.origem_destinatario == origem_destinatario)
        if origem_documento:
            query = query.where(DemandaTable.origem_documento == origem_documento)
        if obs:
            query = query.where(DemandaTable.obs == obs)
        if tag:
            query = query.join(TagDemandaTable).join(TagTable).where(TagTable.nome == tag)
        
        result = session.execute(query).scalars().all()
        return result
    
def get_parecer(
    assunto: str = None,
    conclusao: str = None,
    tag: str = None
) -> list:
    with Session(engine) as session:
        query = select(ParecerTable)
        
        if assunto:
            query = query.where(ParecerTable.assunto == assunto)
        if conclusao:
            query = query.where(ParecerTable.conclusao == conclusao)
        if tag:
            query = query.join(TagParecerTable).join(TagTable).where(TagTable.nome == tag)
        
        result = session.execute(query).scalars().all()
        return result
    
def get_subsidio(
    demanda_id: int = None,
    setor_fonte: str = None,
    tag: str = None
) -> list:
    with Session(engine) as session:
        query = select(SubsidioTable)
        
        if demanda_id:
            query = query.where(SubsidioTable.demanda_id == demanda_id)
        if setor_fonte:
            query = query.where(SubsidioTable.setor_fonte == setor_fonte)
        if tag:
            query = query.join(TagSubsidioTable).join(TagTable).where(TagTable.nome == tag)
        
        result = session.execute(query).scalars().all()
        return result
    
def get_documento(
    parecer_id: int = None,
    demanda_id: int = None,
    subsidio_id: int = None,
    caminho_arquivo: str = None,
    tipo_arquivo: str = None,
    tag: str = None
) -> list:
    with Session(engine) as session:
        query = select(DocumentoTable)
        
        if parecer_id:
            query = query.where(DocumentoTable.parecer_id == parecer_id)
        if demanda_id:
            query = query.where(DocumentoTable.demanda_id == demanda_id)
        if subsidio_id:
            query = query.where(DocumentoTable.subsidio_id == subsidio_id)
        if caminho_arquivo:
            query = query.where(DocumentoTable.caminho_arquivo == caminho_arquivo)
        if tipo_arquivo:
            query = query.where(DocumentoTable.tipo_arquivo == tipo_arquivo)
        if tag:
            query = query.join(TagDocumentoTable).join(TagTable).where(TagTable.nome == tag)
        
        result = session.execute(query).scalars().all()
        return result
    
def get_tag(
    nome: str = None,
    cor: str = None
) -> list:
    with Session(engine) as session:
        query = select(TagTable)
        
        if nome:
            query = query.where(TagTable.nome == nome)
        if cor:
            query = query.where(TagTable.cor == cor)
        
        result = session.execute(query).scalars().all()
        return result