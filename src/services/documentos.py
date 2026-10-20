"""DocumentoService (RS015, RF004, RS022, RD001, RNF010).

Só o caminho local é registrado; o arquivo não é copiado (decisão da sessão 0).
"""
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from sqlalchemy.orm import Session, selectinload

from src.models import EXTENSOES_PERMITIDAS, TAMANHO_MAXIMO_BYTES, Demanda, Documento, Parecer, Subsidio
from src.services import historico
from src.services.base import ComTags, ServicoBase, exigir

DONOS = {"demanda_id": Demanda, "parecer_id": Parecer, "subsidio_id": Subsidio}
TABELA_DO_DONO = {"demanda_id": "demandas", "parecer_id": "pareceres", "subsidio_id": "subsidios"}

ARQUIVO_NAO_ENCONTRADO = "Arquivo não encontrado."
ARQUIVO_GRANDE = "O arquivo ultrapassa o limite de 50 MB."
UM_DONO = "Informe exatamente um entre demanda, parecer ou subsídio."
URL_INVALIDA = "Informe um link completo, começando com http:// ou https://."


def formato_nao_aceito(extensao: str) -> str:
    aceitos = ", ".join(e.upper() for e in EXTENSOES_PERMITIDAS)
    return f"Formato não aceito ({extensao or 'sem extensão'}). Formatos aceitos: {aceitos}."


def extensao_de(caminho: str) -> str:
    return Path(caminho).suffix.lower().lstrip(".")


def url_valida(url: str) -> bool:
    """RS020: link do Drive colado manualmente (decisão da sessão 6)."""
    partes = urlparse(url)
    return partes.scheme in ("http", "https") and bool(partes.netloc) and " " not in url


class DocumentoService(ComTags, ServicoBase):
    modelo = Documento
    tabela = "documentos"
    campos = ("demanda_id", "parecer_id", "subsidio_id", "caminho_arquivo", "tipo_arquivo", "url_drive")
    # Trocar o arquivo é remover o anexo e anexar outro; só o link do Drive é editável.
    campos_fixos = ("demanda_id", "parecer_id", "subsidio_id", "caminho_arquivo")
    carregar = (selectinload(Documento.tags),)

    def _normalizar(self, dados: dict[str, Any]) -> dict[str, Any]:
        if "tipo_arquivo" in dados:
            raise TypeError("tipo_arquivo é derivado da extensão do arquivo.")
        return super()._normalizar(dados)

    def _completar(self, dados: dict[str, Any], criando: bool) -> dict[str, Any]:
        caminho = dados.get("caminho_arquivo")
        dados["tipo_arquivo"] = extensao_de(caminho) if caminho else None
        return dados

    def _validar(self, sessao: Session, dados: dict[str, Any], registro_id: int | None) -> dict[str, str]:
        erros = exigir(dados, ("caminho_arquivo",))
        # O arquivo é conferido ao anexar; depois ele pode ter sido movido, e
        # isso não deve impedir a edição do link do Drive.
        if "caminho_arquivo" not in erros and registro_id is None:
            erro_arquivo = self._validar_arquivo(dados["caminho_arquivo"])
            if erro_arquivo:
                erros["caminho_arquivo"] = erro_arquivo

        if dados.get("url_drive") is not None and not url_valida(dados["url_drive"]):
            erros["url_drive"] = URL_INVALIDA

        donos = [campo for campo in DONOS if dados.get(campo) is not None]
        if len(donos) != 1:
            erros["dono"] = UM_DONO
        elif sessao.get(DONOS[donos[0]], dados[donos[0]]) is None:
            erros[donos[0]] = "Registro não encontrado."
        return erros

    def _validar_arquivo(self, caminho: str) -> str | None:
        """RS022: recusa formato fora do RD001 e arquivo acima de 50 MB."""
        extensao = extensao_de(caminho)
        if extensao not in EXTENSOES_PERMITIDAS:
            return formato_nao_aceito(extensao)
        arquivo = Path(caminho)
        if not arquivo.is_file():
            return ARQUIVO_NAO_ENCONTRADO
        if arquivo.stat().st_size > TAMANHO_MAXIMO_BYTES:
            return ARQUIVO_GRANDE
        return None

    def _dono(self, documento: Documento) -> tuple[str, int]:
        for campo, tabela in TABELA_DO_DONO.items():
            if getattr(documento, campo) is not None:
                return tabela, getattr(documento, campo)
        raise AssertionError("documento sem dono")  # impedido pelo CHECK do banco

    def _apos_criar(self, sessao: Session, documento: Documento) -> None:
        historico.registrar(sessao, *self._dono(documento), "documentos", None, documento.caminho_arquivo)

    def _antes_excluir(self, sessao: Session, documento: Documento) -> None:
        historico.registrar(sessao, *self._dono(documento), "documentos", documento.caminho_arquivo, None)

    def _descricao(self, documento: Documento) -> str:
        return documento.caminho_arquivo

    def _documentos_de(self, documento: Documento) -> list[Documento]:
        return [documento]
