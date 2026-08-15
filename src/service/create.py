import datetime
from sqlalchemy.orm import Session

from database.base import engine
from models.pareceres import ParecerTable
from models.demandas import DemandaTable, StatusDemanda
from models.subsidios import SubsidioTable
from models.documentos import DocumentoTable
from models.tags import TagTable, TagDemandaTable, TagParecerTable, TagSubsidioTable, TagDocumentoTable

def add_demanda(
    alvo_motivo: str,
    data_entrada: datetime.date,
    data_limite: datetime.date,
    caminho_pasta: str,
    origem_canal: str,
    origem_remetente: str, 
    origem_destinatario: str, 
    status: StatusDemanda = StatusDemanda.PENDENTE,
    origem_documento: str = None, 
    obs: str = None
) -> int:
    with Session(engine) as session:
        demanda = DemandaTable(
            alvo_motivo=alvo_motivo,
            data_entrada=data_entrada,
            data_limite=data_limite,
            caminho_pasta=caminho_pasta,
            origem_canal=origem_canal,
            origem_remetente=origem_remetente,
            origem_destinatario=origem_destinatario,
            status=status,
            origem_documento=origem_documento,
            obs=obs
        )
        session.add(demanda)
        session.commit()
        return demanda.id
    
def add_parecer(
    assunto: str,
    conclusao: str,
    data: datetime.date,
    obs: str = None
) -> int:
    with Session(engine) as session:
        parecer = ParecerTable(
            assunto=assunto,
            conclusao=conclusao,
            data=data,
            obs=obs
        )
        session.add(parecer)
        session.commit()
        return parecer.id
    
def add_subsidio(
    demanda_id: int,
    setor_fonte: str,
    data_aquisicao: datetime.date,
    resposta: str
) -> int:
    with Session(engine) as session:
        subsidio = SubsidioTable(
            demanda_id=demanda_id,
            setor_fonte=setor_fonte,
            data_aquisicao=data_aquisicao,
            resposta=resposta
        )
        session.add(subsidio)
        session.commit()
        return subsidio.id

def add_documento(
    parecer_id: int = None,
    demanda_id: int = None,
    subsidio_id: int = None,
    caminho_arquivo: str = None,
    tipo_arquivo: str = None
) -> int:
    with Session(engine) as session:
        documento = DocumentoTable(
            parecer_id=parecer_id,
            demanda_id=demanda_id,
            subsidio_id=subsidio_id,
            caminho_arquivo=caminho_arquivo,
            tipo_arquivo=tipo_arquivo,
            data_sincronizacao=datetime.datetime.now()
        )
        session.add(documento)
        session.commit()
        return documento.id
    
def add_tag(
    nome: str,
    cor: str = None
) -> int:
    with Session(engine) as session:
        tag = TagTable(
            nome=nome,
            cor=cor
        )
        session.add(tag)
        session.commit()
        return tag.id
    
def add_tag_demanda(
    tag_id: int,
    demanda_id: int
) -> tuple:
    with Session(engine) as session:
        tag_demanda = TagDemandaTable(
            tag_id=tag_id,
            demanda_id=demanda_id
        )
        session.add(tag_demanda)
        session.commit()

        return (tag_demanda.tag_id, tag_demanda.demanda_id)
    
def add_tag_parecer(
    tag_id: int,
    parecer_id: int
) -> tuple:
    with Session(engine) as session:
        tag_parecer = TagParecerTable(
            tag_id=tag_id,
            parecer_id=parecer_id
        )
        session.add(tag_parecer)
        session.commit()
        return (tag_parecer.tag_id, tag_parecer.parecer_id)
    
def add_tag_subsidio(
    tag_id: int,
    subsidio_id: int
) -> tuple:
    with Session(engine) as session:
        tag_subsidio = TagSubsidioTable(
            tag_id=tag_id,
            subsidio_id=subsidio_id
        )
        session.add(tag_subsidio)
        session.commit()
        return (tag_subsidio.tag_id, tag_subsidio.subsidio_id)
    
def add_tag_documento(
    tag_id: int,
    documento_id: int
) -> tuple:
    with Session(engine) as session:
        tag_documento = TagDocumentoTable(
            tag_id=tag_id,
            documento_id=documento_id
        )
        session.add(tag_documento)
        session.commit()
        return (tag_documento.tag_id, tag_documento.documento_id)