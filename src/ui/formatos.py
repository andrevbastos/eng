"""Conversões entre os valores dos serviços e o texto exibido na interface.

Datas na interface em DD/MM/AAAA (decisão da sessão 0); no banco e no
histórico, em ISO (AAAA-MM-DD).
"""
import datetime

FORMATO_DATA = "%d/%m/%Y"
FORMATO_DATA_HORA = "%d/%m/%Y %H:%M"

ROTULOS_CAMPOS = {
    "titulo": "Título",
    "alvo_motivo": "Alvo / motivo",
    "data_entrada": "Data de entrada",
    "data_limite": "Data limite",
    "status": "Status",
    "segredo_justica": "Segredo de justiça",
    "observacoes": "Observações",
    "caminho_pasta": "Pasta local",
    "origem_canal": "Canal de origem",
    "origem_remetente": "Remetente",
    "origem_destinatario": "Destinatário",
    "origem_documento": "Documento de origem",
    "numero": "Número",
    "assunto": "Assunto",
    "conclusao": "Conclusão",
    "data": "Data",
    "demanda_id": "Demanda",
    "parecer_id": "Parecer",
    "subsidio_id": "Subsídio",
    "setor_fonte": "Setor fonte",
    "data_aquisicao": "Data de aquisição",
    "resposta": "Resposta",
    "caminho_arquivo": "Arquivo",
    "tipo_arquivo": "Tipo",
    "url_drive": "Link do Drive",
    "nome": "Nome",
    "cor": "Cor",
    "tags": "Tags",
    "subsidios": "Subsídios",
    "documentos": "Documentos",
}

ROTULOS_TABELAS = {
    "demandas": "Demanda",
    "pareceres": "Parecer",
    "subsidios": "Subsídio",
    "documentos": "Documento",
    "tags": "Tag",
}


def data_br(valor: datetime.date | None) -> str:
    return valor.strftime(FORMATO_DATA) if valor else ""


def data_hora_br(valor: datetime.datetime | None) -> str:
    return valor.strftime(FORMATO_DATA_HORA) if valor else ""


def ler_data_br(texto: str) -> datetime.date | None:
    """Converte DD/MM/AAAA (dia e mês podem ter um dígito). Vazio -> None.

    Levanta ValueError se o texto não for uma data válida.
    """
    texto = texto.strip()
    if not texto:
        return None
    partes = texto.split("/")
    if len(partes) != 3 or len(partes[2]) != 4 or not all(p.isdigit() for p in partes):
        raise ValueError(texto)
    dia, mes, ano = (int(p) for p in partes)
    return datetime.date(ano, mes, dia)


def sim_nao(valor: bool) -> str:
    return "Sim" if valor else "Não"


def valor_historico(valor: str | None) -> str:
    """Valor gravado no histórico (ISO, True/False) no formato da interface."""
    if valor is None:
        return "—"
    if valor in ("True", "False"):
        return sim_nao(valor == "True")
    try:
        return data_br(datetime.date.fromisoformat(valor)) if len(valor) == 10 else valor
    except ValueError:
        return valor


def descrever_alteracao(tabela_principal: str, item) -> str:
    """Texto de uma linha de historico_alteracoes para o painel de detalhes (RF014)."""
    prefixo = ""
    if item.tabela != tabela_principal:
        prefixo = f"{ROTULOS_TABELAS.get(item.tabela, item.tabela)} #{item.registro_id} · "

    if item.campo == "*":
        return f"{prefixo}excluído ({item.valor_anterior})"

    campo = ROTULOS_CAMPOS.get(item.campo, item.campo)
    if item.campo in ("tags", "subsidios", "documentos"):
        if item.valor_anterior is None:
            return f"{prefixo}{campo}: adicionado {item.valor_novo}"
        return f"{prefixo}{campo}: removido {item.valor_anterior}"
    if item.valor_anterior is None:
        return f"{prefixo}{campo}: {valor_historico(item.valor_novo)}"
    return f"{prefixo}{campo}: {valor_historico(item.valor_anterior)} → {valor_historico(item.valor_novo)}"
