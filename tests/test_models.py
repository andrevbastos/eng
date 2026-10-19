"""Testes do esquema do banco (RS001–RS010, RS016, RD001, RD002, RD004, NR006)."""
import datetime

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from src.database.base import criar_engine, criar_tabelas
from src.models import (
    CANAIS_ORIGEM,
    EXTENSOES_PERMITIDAS,
    STATUS_DEMANDA,
    Demanda,
    Documento,
    HistoricoAlteracao,
    Subsidio,
    Tag,
    tags_demandas,
    tags_documentos,
    tags_subsidios,
)

COLUNAS_ESPERADAS = {
    "pareceres": {"id", "numero", "assunto", "conclusao", "data", "observacoes"},  # RS002
    "demandas": {  # RS003
        "id", "titulo", "alvo_motivo", "data_entrada", "data_limite", "status",
        "segredo_justica", "observacoes", "caminho_pasta", "origem_canal",
        "origem_remetente", "origem_destinatario", "origem_documento",
    },
    "subsidios": {"id", "demanda_id", "setor_fonte", "data_aquisicao", "resposta"},  # RS004
    "documentos": {  # RS005
        "id", "parecer_id", "demanda_id", "subsidio_id", "caminho_arquivo",
        "url_drive", "tipo_arquivo", "data_sincronizacao",
    },
    "tags": {"id", "nome", "cor"},  # RS006
    "tags_demandas": {"tag_id", "demanda_id"},  # RS007
    "tags_pareceres": {"tag_id", "parecer_id"},  # RS008
    "tags_subsidios": {"tag_id", "subsidio_id"},  # RS009
    "tags_documentos": {"tag_id", "documento_id"},  # RS010
    "historico_alteracoes": {  # RS016 (sem usuario_id)
        "id", "tabela", "registro_id", "campo", "valor_anterior", "valor_novo", "data_hora",
    },
}

OPCIONAIS = {
    "pareceres": {"observacoes"},
    "demandas": {"observacoes", "caminho_pasta", "origem_documento"},
    "documentos": {"parecer_id", "demanda_id", "subsidio_id", "url_drive", "data_sincronizacao"},
    "historico_alteracoes": {"valor_anterior", "valor_novo"},
}


# --- Esquema -----------------------------------------------------------------

def test_rs001_cria_banco_em_arquivo_escolhido(tmp_path):
    caminho = tmp_path / "pasta escolhida" / "assessoria.db"
    caminho.parent.mkdir()
    engine = criar_engine(caminho)
    criar_tabelas(engine)
    engine.dispose()
    assert caminho.is_file()


def test_tabelas_da_spec_e_sem_usuarios(engine):
    """RS002–RS010, RS016; NR006/RS014 removido: não há tabela de usuários."""
    assert set(inspect(engine).get_table_names()) == set(COLUNAS_ESPERADAS)


@pytest.mark.parametrize("tabela", sorted(COLUNAS_ESPERADAS))
def test_colunas_e_opcionais_conforme_spec(engine, tabela):
    colunas = {c["name"]: c for c in inspect(engine).get_columns(tabela)}
    assert set(colunas) == COLUNAS_ESPERADAS[tabela]
    anulaveis = {nome for nome, c in colunas.items() if c["nullable"] and not c.get("primary_key")}
    assert anulaveis == OPCIONAIS.get(tabela, set())


def test_chaves_estrangeiras_ativas(sessao):
    sessao.add(Subsidio(demanda_id=999, setor_fonte="Proad",
                        data_aquisicao=datetime.date(2026, 8, 12), resposta="Ok"))
    with pytest.raises(IntegrityError):
        sessao.commit()


# --- Demandas (RS003, RD002) -------------------------------------------------

def test_rs003_valores_padrao(sessao, nova_demanda):
    demanda = nova_demanda()
    sessao.add(demanda)
    sessao.commit()
    assert demanda.status == "Em análise"  # decisão da sessão 0
    assert demanda.segredo_justica is False


def test_rs003_listas_de_status_e_canais():
    assert STATUS_DEMANDA == (
        "Em análise", "Em andamento", "Aguardando subsídios", "Aguardando Procuradoria",
        "Aguardando assinatura do Reitor", "Concluída",
    )
    assert CANAIS_ORIGEM == ("E-mail", "SIGAA", "Presencial", "Ofício", "Outro")


@pytest.mark.parametrize("status", STATUS_DEMANDA)
def test_rs003_aceita_todos_os_status(sessao, nova_demanda, status):
    sessao.add(nova_demanda(status=status))
    sessao.commit()


@pytest.mark.parametrize("campo, valor", [("status", "Pendente"), ("origem_canal", "Pessoalmente")])
def test_rs003_rejeita_status_e_canal_fora_da_lista(sessao, nova_demanda, campo, valor):
    sessao.add(nova_demanda(**{campo: valor}))
    with pytest.raises(IntegrityError):
        sessao.commit()


def test_rd002_data_limite_obrigatoria(sessao, nova_demanda):
    sessao.add(nova_demanda(data_limite=None))
    with pytest.raises(IntegrityError):
        sessao.commit()


def test_rs017_rejeita_data_limite_anterior_a_entrada(sessao, nova_demanda):
    sessao.add(nova_demanda(data_entrada=datetime.date(2026, 8, 10),
                            data_limite=datetime.date(2026, 8, 9)))
    with pytest.raises(IntegrityError):
        sessao.commit()


def test_rs017_aceita_data_limite_igual_a_entrada(sessao, nova_demanda):
    hoje = datetime.date(2026, 8, 10)
    sessao.add(nova_demanda(data_entrada=hoje, data_limite=hoje))
    sessao.commit()


# --- Pareceres (RS002, RD004) ------------------------------------------------

def test_rd004_numero_do_parecer_unico(sessao, novo_parecer):
    sessao.add(novo_parecer(numero="PJ-001/2026"))
    sessao.commit()
    sessao.add(novo_parecer(numero="PJ-001/2026", assunto="Outro assunto"))
    with pytest.raises(IntegrityError):
        sessao.commit()


# --- Tags (RS006) ------------------------------------------------------------

def test_rs006_nome_da_tag_unico(sessao):
    sessao.add(Tag(nome="MPF", cor="#EF5350"))
    sessao.commit()
    sessao.add(Tag(nome="MPF", cor="#3A7BD5"))
    with pytest.raises(IntegrityError):
        sessao.commit()


@pytest.mark.parametrize("cor", ["#3A7BD5", "#ffb74d"])
def test_rs006_aceita_cor_hexadecimal(sessao, cor):
    sessao.add(Tag(nome="Urgente", cor=cor))
    sessao.commit()


@pytest.mark.parametrize("cor", ["red", "#FFF", "3A7BD5", "#3A7BDZ", "#3A7BD55"])
def test_rs006_rejeita_cor_invalida(sessao, cor):
    sessao.add(Tag(nome="Edital", cor=cor))
    with pytest.raises(IntegrityError):
        sessao.commit()


# --- Documentos (RS005, RD001) -----------------------------------------------

def test_rd001_extensoes_permitidas():
    assert set(EXTENSOES_PERMITIDAS) == {"pdf", "doc", "docx", "odt", "xlsx", "txt", "eml", "jpg", "png"}


def test_rs005_documento_sem_dono_e_rejeitado(sessao):
    sessao.add(Documento(caminho_arquivo="C:/docs/a.pdf", tipo_arquivo="pdf"))
    with pytest.raises(IntegrityError):
        sessao.commit()


def test_rs005_documento_com_dois_donos_e_rejeitado(sessao, nova_demanda, novo_parecer):
    demanda, parecer = nova_demanda(), novo_parecer()
    sessao.add_all([demanda, parecer])
    sessao.flush()
    sessao.add(Documento(demanda_id=demanda.id, parecer_id=parecer.id,
                         caminho_arquivo="C:/docs/a.pdf", tipo_arquivo="pdf"))
    with pytest.raises(IntegrityError):
        sessao.commit()


def test_rs005_campos_do_drive_sao_opcionais(sessao, novo_parecer):
    parecer = novo_parecer()
    parecer.documentos.append(Documento(caminho_arquivo="C:/docs/p.pdf", tipo_arquivo="pdf"))
    sessao.add(parecer)
    sessao.commit()
    documento = parecer.documentos[0]
    assert documento.url_drive is None
    assert documento.data_sincronizacao is None


# --- Exclusão em cascata (decisão da sessão 0: só registros do banco) --------

def test_excluir_demanda_remove_dependentes_e_mantem_tags(sessao, nova_demanda):
    tag = Tag(nome="MPF", cor="#EF5350")
    demanda = nova_demanda(tags=[tag])
    subsidio = Subsidio(setor_fonte="Proad", data_aquisicao=datetime.date(2026, 8, 12),
                        resposta="Subsídios orçamentários validados", tags=[tag])
    subsidio.documentos.append(Documento(caminho_arquivo="C:/docs/s.pdf", tipo_arquivo="pdf", tags=[tag]))
    demanda.subsidios.append(subsidio)
    demanda.documentos.append(Documento(caminho_arquivo="C:/docs/d.docx", tipo_arquivo="docx"))
    sessao.add(demanda)
    sessao.commit()

    sessao.delete(demanda)
    sessao.commit()

    assert sessao.scalars(select(Subsidio)).all() == []
    assert sessao.scalars(select(Documento)).all() == []
    for associacao in (tags_demandas, tags_subsidios, tags_documentos):
        assert sessao.execute(select(associacao)).all() == []
    assert sessao.scalars(select(Tag)).one().nome == "MPF"


def test_excluir_tag_remove_associacoes(sessao, nova_demanda):
    tag = Tag(nome="Urgente", cor="#FFB74D")
    demanda = nova_demanda(tags=[tag])
    sessao.add(demanda)
    sessao.commit()

    sessao.delete(tag)
    sessao.commit()
    sessao.refresh(demanda)

    assert demanda.tags == []
    assert sessao.execute(select(tags_demandas)).all() == []


# --- Histórico (RS016) -------------------------------------------------------

def test_rs016_historico_sobrevive_a_exclusao(sessao, nova_demanda):
    demanda = nova_demanda()
    sessao.add(demanda)
    sessao.commit()
    registro_id = demanda.id
    sessao.add(HistoricoAlteracao(tabela="demandas", registro_id=registro_id, campo="*",
                                  valor_anterior="Ofício MPF 12/2026"))
    sessao.delete(demanda)
    sessao.commit()

    historico = sessao.scalars(select(HistoricoAlteracao)).one()
    assert historico.registro_id == registro_id
    assert historico.valor_novo is None
    assert isinstance(historico.data_hora, datetime.datetime)
