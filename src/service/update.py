import datetime
from colour import Color
from sqlalchemy.orm import Session

from database.base import engine
from models.pareceres import ParecerTable
from models.demandas import DemandaTable, StatusDemanda
from models.subsidios import SubsidioTable
from models.documentos import DocumentoTable
from models.tags import TagTable, TagDemandaTable, TagParecerTable, TagSubsidioTable, TagDocumentoTable

def update_demanda(
    demanda_id: int,
    alvo_motivo: str = None,
    data_entrada: datetime.date = None,
    data_limite: datetime.date = None,
    status: StatusDemanda = None,
    caminho_pasta: str = None,
    origem_canal: str = None,
    origem_remetente: str = None, 
    origem_destinatario: str = None, 
    origem_documento: str = None, 
    obs: str = None
) -> bool:
    with Session(engine) as session:
        demanda = session.get(DemandaTable, demanda_id)
        if not demanda:
            return False
        
        if alvo_motivo is not None:
            demanda.alvo_motivo = alvo_motivo
        if data_entrada is not None:
            demanda.data_entrada = data_entrada
        if data_limite is not None:
            demanda.data_limite = data_limite
        if status is not None:
            demanda.status = status
        if caminho_pasta is not None:
            demanda.caminho_pasta = caminho_pasta
        if origem_canal is not None:
            demanda.origem_canal = origem_canal
        if origem_remetente is not None:
            demanda.origem_remetente = origem_remetente
        if origem_destinatario is not None:
            demanda.origem_destinatario = origem_destinatario
        if origem_documento is not None:
            demanda.origem_documento = origem_documento
        if obs is not None:
            demanda.obs = obs
        
        session.commit()
        return True
    
def update_parecer(
    parecer_id: int,
    assunto: str = None,
    conclusao: str = None,
    data: datetime.date = None,
    obs: str = None
) -> bool:
    with Session(engine) as session:
        parecer = session.get(ParecerTable, parecer_id)
        if not parecer:
            return False
        
        if assunto is not None:
            parecer.assunto = assunto
        if conclusao is not None:
            parecer.conclusao = conclusao
        if data is not None:
            parecer.data = data
        if obs is not None:
            parecer.obs = obs
        
        session.commit()
        return True
    
def update_subsidio(
    subsidio_id: int,
    demanda_id: int = None,
    setor_fonte: str = None,
    data_aquisicao: datetime.date = None,
    resposta: str = None
) -> bool:
    with Session(engine) as session:
        subsidio = session.get(SubsidioTable, subsidio_id)
        if not subsidio:
            return False
        
        if demanda_id is not None:
            subsidio.demanda_id = demanda_id
        if setor_fonte is not None:
            subsidio.setor_fonte = setor_fonte
        if data_aquisicao is not None:
            subsidio.data_aquisicao = data_aquisicao
        if resposta is not None:
            subsidio.resposta = resposta
        
        session.commit()
        return True
    
def update_documento(
    documento_id: int,
    parecer_id: int = None,
    demanda_id: int = None,
    subsidio_id: int = None,
    caminho_arquivo: str = None,
    tipo_arquivo: str = None
) -> bool:
    with Session(engine) as session:
        documento = session.get(DocumentoTable, documento_id)
        if not documento:
            return False
        
        if parecer_id is not None:
            documento.parecer_id = parecer_id
        if demanda_id is not None:
            documento.demanda_id = demanda_id
        if subsidio_id is not None:
            documento.subsidio_id = subsidio_id
        if caminho_arquivo is not None:
            documento.caminho_arquivo = caminho_arquivo
        if tipo_arquivo is not None:
            documento.tipo_arquivo = tipo_arquivo
        
        session.commit()
        return True
    
def update_tag(
    tag_id: int,
    nome: str = None,
    cor: Color = None
) -> bool:
    with Session(engine) as session:
        tag = session.get(TagTable, tag_id)
        if not tag:
            return False
        
        if nome is not None:
            tag.nome = nome
        if cor is not None:
            tag.cor = cor

        session.commit()
        return True
    
def change_tag_demanda(
    demanda_id: int,
    old_tag_id: int,
    new_tag_id: int = None
) -> bool:
    with Session(engine) as session:
        old_association = session.get(TagDemandaTable, (old_tag_id, demanda_id))
        
        if not old_association:
            return False
        
        session.delete(old_association)
        
        if new_tag_id is not None:
            new_association = TagDemandaTable(tag_id=new_tag_id, demanda_id=demanda_id)
            session.add(new_association)
        
        session.commit()
        return True
    
def change_tag_parecer(
    parecer_id: int,
    old_tag_id: int,
    new_tag_id: int = None
) -> bool:
    with Session(engine) as session:
        old_association = session.get(TagParecerTable, (old_tag_id, parecer_id))
        
        if not old_association:
            return False
        
        session.delete(old_association)
        
        if new_tag_id is not None:
            new_association = TagParecerTable(tag_id=new_tag_id, parecer_id=parecer_id)
            session.add(new_association)
        
        session.commit()
        return True
    
def change_tag_subsidio(
    subsidio_id: int,
    old_tag_id: int,
    new_tag_id: int = None
) -> bool:
    with Session(engine) as session:
        old_association = session.get(TagSubsidioTable, (old_tag_id, subsidio_id))
        
        if not old_association:
            return False
        
        session.delete(old_association)
        
        if new_tag_id is not None:
            new_association = TagSubsidioTable(tag_id=new_tag_id, subsidio_id=subsidio_id)
            session.add(new_association)
        
        session.commit()
        return True
    
def change_tag_documento(
    documento_id: int,
    old_tag_id: int,
    new_tag_id: int = None
) -> bool:
    with Session(engine) as session:
        old_association = session.get(TagDocumentoTable, (old_tag_id, documento_id))
        
        if not old_association:
            return False
        
        session.delete(old_association)
        
        if new_tag_id is not None:
            new_association = TagDocumentoTable(tag_id=new_tag_id, documento_id=documento_id)
            session.add(new_association)
        
        session.commit()
        return True