import datetime
from colour import Color

from models.tags import TagTable
from models.demandas import DemandaTable, StatusDemanda
from models.pareceres import ParecerTable
from models.subsidios import SubsidioTable
from models.documentos import DocumentoTable

def test_criar_documento(db_session):
    demanda = DemandaTable(
        alvo_motivo="Auditoria",
        data_entrada=datetime.date.today(),
        data_limite=datetime.date.today(),
        status=StatusDemanda.EM_ANDAMENTO,
        caminho_pasta="/docs",
        origem_canal="Sistema",
        origem_remetente="Admin",
        origem_destinatario="Setor"
    )
    db_session.add(demanda)
    db_session.commit()

    novo_documento = DocumentoTable(
        demanda_id=demanda.id,
        caminho_arquivo="/docs/audit_report.pdf",
        tipo_arquivo="pdf",
        data_sincronizacao=datetime.datetime(2026, 8, 12, 10, 0, 0)
    )
    
    db_session.add(novo_documento)
    db_session.commit()
    
    doc_salvo = db_session.query(DocumentoTable).filter_by(caminho_arquivo="/docs/audit_report.pdf").first()
    
    assert doc_salvo is not None
    assert doc_salvo.id is not None
    assert doc_salvo.demanda_id == demanda.id
    assert doc_salvo.tipo_arquivo == "pdf"

def test_criar_parecer(db_session):
    novo_parecer = ParecerTable(
        assunto="Viabilidade Técnica",
        conclusao="Aprovado com ressalvas",
        data=datetime.date(2026, 8, 12),
        obs="Falta revisar orçamento"
    )
    
    db_session.add(novo_parecer)
    db_session.commit()
    
    parecer_salvo = db_session.query(ParecerTable).filter_by(assunto="Viabilidade Técnica").first()
    
    assert parecer_salvo is not None
    assert parecer_salvo.id is not None
    assert parecer_salvo.conclusao == "Aprovado com ressalvas"
    assert parecer_salvo.data.year == 2026

def test_criar_demanda(db_session):
    nova_demanda = DemandaTable(
        alvo_motivo="Investigação de Fraude",
        data_entrada=datetime.date(2026, 8, 12),
        data_limite=datetime.date(2026, 8, 20),
        status=StatusDemanda.PENDENTE,
        caminho_pasta="/docs/demandas/001",
        origem_canal="Email",
        origem_remetente="joao@email.com",
        origem_destinatario="setor.fraudes@empresa.com",
        obs="Anexos pendentes"
    )
    
    db_session.add(nova_demanda)
    db_session.commit()
    
    demanda_salva = db_session.query(DemandaTable).filter_by(alvo_motivo="Investigação de Fraude").first()
    
    assert demanda_salva is not None
    assert demanda_salva.id is not None
    assert demanda_salva.status == StatusDemanda.PENDENTE
    assert demanda_salva.caminho_pasta == "/docs/demandas/001"

def test_criar_subsidio(db_session):
    demanda = DemandaTable(
        alvo_motivo="Revisão Contratual",
        data_entrada=datetime.date.today(),
        data_limite=datetime.date.today(),
        status=StatusDemanda.PENDENTE,
        caminho_pasta="/docs",
        origem_canal="Sistema",
        origem_remetente="Admin",
        origem_destinatario="Setor"
    )
    db_session.add(demanda)
    db_session.commit()

    novo_subsidio = SubsidioTable(
        demanda_id=demanda.id,
        setor_fonte="Jurídico",
        data_aquisicao=datetime.date(2026, 8, 12),
        resposta="Contrato validado segundo a nova lei."
    )
    
    db_session.add(novo_subsidio)
    db_session.commit()
    
    sub_salvo = db_session.query(SubsidioTable).filter_by(setor_fonte="Jurídico").first()
    
    assert sub_salvo is not None
    assert sub_salvo.id is not None
    assert sub_salvo.demanda_id == demanda.id
    assert "nova lei" in sub_salvo.resposta

def test_criar_tag(db_session):
    nova_tag = TagTable(nome="Urgente", cor=Color("red"))
    
    db_session.add(nova_tag)
    db_session.commit()
    
    tag_buscada = db_session.query(TagTable).filter_by(nome="Urgente").first()
    
    assert tag_buscada is not None
    assert tag_buscada.id is not None
    assert tag_buscada.nome == "Urgente"
    assert tag_buscada.cor == Color("red")

def test_nome_tag_unico(db_session):
    import pytest
    from sqlalchemy.exc import IntegrityError
    
    tag1 = TagTable(nome="Unico")
    db_session.add(tag1)
    db_session.commit()
    
    tag2 = TagTable(nome="Unico")
    db_session.add(tag2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
