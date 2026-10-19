"""Dados válidos reutilizados nos testes dos serviços."""
import datetime

DADOS_DEMANDA = dict(
    titulo="Ofício MPF 12/2026",
    alvo_motivo="Esclarecimento sobre o Edital nº 04/2026",
    data_entrada=datetime.date(2026, 8, 10),
    data_limite=datetime.date(2026, 8, 20),
    origem_canal="E-mail",
    origem_remetente="Proj. MPF Joinville",
    origem_destinatario="Assessoria Jurídica IFC",
)

DADOS_PARECER = dict(
    numero="PJ-042/2026",
    assunto="Dispensa de licitação para insumos de pesquisa",
    conclusao="Deferido",
    data=datetime.date(2026, 5, 15),
)
