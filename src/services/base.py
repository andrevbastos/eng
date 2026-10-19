"""Base da camada de serviços (RS015): transação, validação (RS017) e histórico (RS016)."""
import datetime
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ClassVar, Iterator

from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from src.models import Tag
from src.services import historico
from src.services.erros import BancoOcupadoError, NaoEncontradoError, ValidacaoError

OBRIGATORIO = "Campo obrigatório."
DATA_INVALIDA = "Data inválida."


def _banco_bloqueado(erro: OperationalError) -> bool:
    return "locked" in str(erro.orig).lower() or "busy" in str(erro.orig).lower()


class ServicoBase:
    modelo: ClassVar[type]
    tabela: ClassVar[str]
    # Campos aceitos em criar/editar e registrados no histórico.
    campos: ClassVar[tuple[str, ...]]
    # Campos que só podem ser definidos na criação.
    campos_fixos: ClassVar[tuple[str, ...]] = ()
    # Opções de carregamento (relacionamentos) usadas em buscar().
    carregar: ClassVar[tuple] = ()

    def __init__(self, fabrica_sessoes: sessionmaker):
        self._fabrica = fabrica_sessoes

    # --- Operações (RS015) ---------------------------------------------------

    def criar(self, **dados: Any):
        dados = self._completar(self._normalizar(dados), criando=True)
        with self._transacao() as sessao:
            self._verificar(sessao, dados, None)
            registro = self.modelo(**dados)
            sessao.add(registro)
            sessao.flush()
            historico.registrar_criacao(sessao, self.tabela, registro.id, self._valores(registro))
            self._apos_criar(sessao, registro)
        return registro

    def editar(self, registro_id: int, **alteracoes: Any):
        alteracoes = self._normalizar(alteracoes)
        fixos = sorted(set(alteracoes) & set(self.campos_fixos))
        if fixos:
            raise ValidacaoError({campo: "Não pode ser alterado." for campo in fixos})
        with self._transacao() as sessao:
            registro = self._obter(sessao, registro_id)
            antes = self._valores(registro)
            depois = self._completar({**antes, **alteracoes}, criando=False)
            self._verificar(sessao, depois, registro_id)
            for campo in self.campos:
                setattr(registro, campo, depois[campo])
            historico.registrar_edicao(sessao, self.tabela, registro_id, antes, depois)
        return registro

    def buscar(self, registro_id: int):
        with self._transacao() as sessao:
            return self._obter(sessao, registro_id, self.carregar)

    def listar(self) -> list:
        with self._transacao() as sessao:
            return list(sessao.scalars(select(self.modelo).order_by(self.modelo.id)))

    def excluir(self, registro_id: int, apagar_arquivos: bool = False) -> list[str]:
        """Exclui o registro e, em cascata, seus dependentes no banco.

        Os arquivos anexados só são apagados do disco com apagar_arquivos=True
        (decisão da sessão 0). Devolve os caminhos que não puderam ser apagados.
        """
        with self._transacao() as sessao:
            registro = self._obter(sessao, registro_id)
            documentos = self._documentos_de(registro)
            self._antes_excluir(sessao, registro)
            for documento in documentos:
                if documento is not registro:
                    historico.registrar_exclusao(sessao, "documentos", documento.id, documento.caminho_arquivo)
            historico.registrar_exclusao(sessao, self.tabela, registro_id, self._descricao(registro))
            sessao.delete(registro)
        if not apagar_arquivos:
            return []
        return apagar_do_disco([documento.caminho_arquivo for documento in documentos])

    # --- Ganchos para as subclasses -----------------------------------------

    def _completar(self, dados: dict[str, Any], criando: bool) -> dict[str, Any]:
        """Preenche padrões (na criação) e campos derivados antes da validação."""
        return dados

    def _validar(self, sessao: Session, dados: dict[str, Any], registro_id: int | None) -> dict[str, str]:
        return {}

    def _descricao(self, registro) -> str:
        return f"{self.tabela} #{registro.id}"

    def _apos_criar(self, sessao: Session, registro) -> None:
        pass

    def _antes_excluir(self, sessao: Session, registro) -> None:
        pass

    def _documentos_de(self, registro) -> list:
        """Documentos que deixam de existir junto com o registro."""
        return []

    # --- Utilitários ---------------------------------------------------------

    @contextmanager
    def _transacao(self) -> Iterator[Session]:
        """Toda escrita acontece numa transação; se o .db seguir bloqueado após a
        espera do engine, nada é gravado e a interface recebe BancoOcupadoError."""
        try:
            with self._fabrica() as sessao, sessao.begin():
                yield sessao
        except OperationalError as erro:
            if _banco_bloqueado(erro):
                raise BancoOcupadoError() from erro
            raise

    def _obter(self, sessao: Session, registro_id: int, opcoes: tuple = ()):
        registro = sessao.get(self.modelo, registro_id, options=list(opcoes))
        if registro is None:
            raise NaoEncontradoError(self.tabela, registro_id)
        return registro

    def _valores(self, registro) -> dict[str, Any]:
        return {campo: getattr(registro, campo) for campo in self.campos}

    def _normalizar(self, dados: dict[str, Any]) -> dict[str, Any]:
        desconhecidos = sorted(set(dados) - set(self.campos))
        if desconhecidos:
            raise TypeError(f"Campos desconhecidos para {self.tabela}: {', '.join(desconhecidos)}")
        normalizados = {}
        for campo, valor in dados.items():
            if isinstance(valor, str):
                valor = valor.strip() or None
            normalizados[campo] = valor
        return normalizados

    def _verificar(self, sessao: Session, dados: dict[str, Any], registro_id: int | None) -> None:
        erros = self._validar(sessao, dados, registro_id)
        if erros:
            raise ValidacaoError(erros)


class ComTags:
    """Associação de tags a um registro (RF005), registrada no histórico do registro."""

    def associar_tag(self: ServicoBase, registro_id: int, tag_id: int) -> None:
        with self._transacao() as sessao:
            registro = self._obter(sessao, registro_id)
            tag = _obter_tag(sessao, tag_id)
            if tag not in registro.tags:
                registro.tags.append(tag)
                historico.registrar(sessao, self.tabela, registro_id, "tags", None, tag.nome)

    def desassociar_tag(self: ServicoBase, registro_id: int, tag_id: int) -> None:
        with self._transacao() as sessao:
            registro = self._obter(sessao, registro_id)
            tag = _obter_tag(sessao, tag_id)
            if tag in registro.tags:
                registro.tags.remove(tag)
                historico.registrar(sessao, self.tabela, registro_id, "tags", tag.nome, None)


def _obter_tag(sessao: Session, tag_id: int) -> Tag:
    tag = sessao.get(Tag, tag_id)
    if tag is None:
        raise NaoEncontradoError("tags", tag_id)
    return tag


def apagar_do_disco(caminhos: list[str]) -> list[str]:
    """Apaga os arquivos; ignora os que já não existem e devolve os que falharam."""
    falhas = []
    for caminho in caminhos:
        try:
            Path(caminho).unlink(missing_ok=True)
        except OSError:
            falhas.append(caminho)
    return falhas


# --- Validações reutilizáveis (RS017) -----------------------------------------

def exigir(dados: dict[str, Any], campos: tuple[str, ...]) -> dict[str, str]:
    return {campo: OBRIGATORIO for campo in campos if dados.get(campo) is None}


def exigir_data(erros: dict[str, str], dados: dict[str, Any], campo: str) -> None:
    valor = dados.get(campo)
    if valor is not None and campo not in erros:
        # datetime é subclasse de date, mas aqui só datas puras são aceitas.
        if not isinstance(valor, datetime.date) or isinstance(valor, datetime.datetime):
            erros[campo] = DATA_INVALIDA


def exigir_opcao(erros: dict[str, str], dados: dict[str, Any], campo: str, opcoes: tuple[str, ...]) -> None:
    valor = dados.get(campo)
    if valor is not None and campo not in erros and valor not in opcoes:
        erros[campo] = f"Valor inválido. Opções: {', '.join(opcoes)}."
