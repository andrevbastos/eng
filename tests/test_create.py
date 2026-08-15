import datetime

from service.create import (
    add_demanda, add_tag, add_parecer, add_subsidio, add_documento,
    add_tag_demanda, add_tag_parecer, add_tag_subsidio, add_tag_documento
)
from models.demandas import DemandaTable, StatusDemanda
from models.tags import TagTable, TagDemandaTable, TagParecerTable, TagSubsidioTable, TagDocumentoTable
from models.pareceres import ParecerTable
from models.subsidios import SubsidioTable
from models.documentos import DocumentoTable

def test_add_demanda_service(db_session):
    demanda_id = add_demanda(
        alvo_motivo="Investigação de Fraude Financeira",
        data_entrada=datetime.date(2026, 8, 12),
        data_limite=datetime.date(2026, 8, 20),
        caminho_pasta="/docs/demandas/002",
        origem_canal="Portal",
        origem_remetente="sistema@portal.com",
        origem_destinatario="analise@empresa.com",
        status=StatusDemanda.EM_ANDAMENTO
    )
    demanda_salva = db_session.query(DemandaTable).filter_by(id=demanda_id).first()
    assert demanda_salva is not None
    assert demanda_salva.alvo_motivo == "Investigação de Fraude Financeira"
    assert demanda_salva.status == StatusDemanda.EM_ANDAMENTO

def test_add_tag_service(db_session):
    tag_id = add_tag(nome="Prioridade Alta", cor="red")
    tag_salva = db_session.query(TagTable).filter_by(id=tag_id).first()
    assert tag_salva is not None
    assert tag_salva.nome == "Prioridade Alta"

def test_add_parecer_service(db_session):
    parecer_id = add_parecer(
        assunto="Análise Tributária",
        conclusao="Regular",
        data=datetime.date(2026, 8, 12)
    )
    parecer_salvo = db_session.query(ParecerTable).filter_by(id=parecer_id).first()
    assert parecer_salvo is not None
    assert parecer_salvo.assunto == "Análise Tributária"

def test_add_subsidio_service(db_session):
    # Precisamos de uma demanda primeiro para atrelar
    demanda_id = add_demanda(
        alvo_motivo="Subsidio Teste", data_entrada=datetime.date.today(),
        data_limite=datetime.date.today(), caminho_pasta="/docs",
        origem_canal="Web", origem_remetente="X", origem_destinatario="Y"
    )
    
    sub_id = add_subsidio(
        demanda_id=demanda_id,
        setor_fonte="TI",
        data_aquisicao=datetime.date.today(),
        resposta="Sistemas operantes"
    )
    sub_salvo = db_session.query(SubsidioTable).filter_by(id=sub_id).first()
    assert sub_salvo is not None
    assert sub_salvo.demanda_id == demanda_id
    assert sub_salvo.setor_fonte == "TI"

def test_add_documento_service(db_session):
    demanda_id = add_demanda(
        alvo_motivo="Documento Teste", data_entrada=datetime.date.today(),
        data_limite=datetime.date.today(), caminho_pasta="/docs",
        origem_canal="Web", origem_remetente="X", origem_destinatario="Y"
    )
    
    doc_id = add_documento(
        demanda_id=demanda_id,
        caminho_arquivo="/var/files/relatorio.pdf",
        tipo_arquivo="pdf"
    )
    doc_salvo = db_session.query(DocumentoTable).filter_by(id=doc_id).first()
    assert doc_salvo is not None
    assert doc_salvo.demanda_id == demanda_id
    assert doc_salvo.caminho_arquivo == "/var/files/relatorio.pdf"

def test_add_tags_associacoes(db_session):
    tag_id = add_tag(nome="Revisão")
    
    demanda_id = add_demanda(alvo_motivo="A", data_entrada=datetime.date.today(), data_limite=datetime.date.today(), caminho_pasta="/a", origem_canal="A", origem_remetente="A", origem_destinatario="A")
    parecer_id = add_parecer(assunto="A", conclusao="A", data=datetime.date.today())
    subsidio_id = add_subsidio(demanda_id=demanda_id, setor_fonte="A", data_aquisicao=datetime.date.today(), resposta="A")
    doc_id = add_documento(demanda_id=demanda_id, caminho_arquivo="/a.pdf")
    
    add_tag_demanda(tag_id, demanda_id)
    add_tag_parecer(tag_id, parecer_id)
    add_tag_subsidio(tag_id, subsidio_id)
    add_tag_documento(tag_id, doc_id)
    
    assert db_session.query(TagDemandaTable).filter_by(tag_id=tag_id, demanda_id=demanda_id).first() is not None
    assert db_session.query(TagParecerTable).filter_by(tag_id=tag_id, parecer_id=parecer_id).first() is not None
    assert db_session.query(TagSubsidioTable).filter_by(tag_id=tag_id, subsidio_id=subsidio_id).first() is not None
    assert db_session.query(TagDocumentoTable).filter_by(tag_id=tag_id, documento_id=doc_id).first() is not None
