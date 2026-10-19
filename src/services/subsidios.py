"""SubsidioService (RS015, RF003)."""
from typing import Any

from sqlalchemy.orm import Session, selectinload

from src.models import Demanda, Documento, Subsidio
from src.services import historico
from src.services.base import ComTags, ServicoBase, exigir, exigir_data

OBRIGATORIOS_SUBSIDIO = ("demanda_id", "setor_fonte", "data_aquisicao", "resposta")


class SubsidioService(ComTags, ServicoBase):
    modelo = Subsidio
    tabela = "subsidios"
    campos = ("demanda_id", "setor_fonte", "data_aquisicao", "resposta")
    campos_fixos = ("demanda_id",)
    carregar = (
        selectinload(Subsidio.tags),
        selectinload(Subsidio.documentos).selectinload(Documento.tags),
    )

    def _validar(self, sessao: Session, dados: dict[str, Any], registro_id: int | None) -> dict[str, str]:
        erros = exigir(dados, OBRIGATORIOS_SUBSIDIO)
        exigir_data(erros, dados, "data_aquisicao")
        if "demanda_id" not in erros and sessao.get(Demanda, dados["demanda_id"]) is None:
            erros["demanda_id"] = "Demanda não encontrada."
        return erros

    def _apos_criar(self, sessao: Session, subsidio: Subsidio) -> None:
        historico.registrar(sessao, "demandas", subsidio.demanda_id, "subsidios", None, self._descricao(subsidio))

    def _antes_excluir(self, sessao: Session, subsidio: Subsidio) -> None:
        historico.registrar(sessao, "demandas", subsidio.demanda_id, "subsidios", self._descricao(subsidio), None)

    def _descricao(self, subsidio: Subsidio) -> str:
        return f"{subsidio.setor_fonte} (#{subsidio.id})"

    def _documentos_de(self, subsidio: Subsidio) -> list[Documento]:
        return list(subsidio.documentos)

