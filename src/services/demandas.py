"""DemandaService (RS015, RF001, RS017)."""
from typing import Any

from sqlalchemy.orm import Session, selectinload

from src.models import CANAIS_ORIGEM, STATUS_DEMANDA, STATUS_PADRAO, Demanda, Documento, Subsidio
from src.services import historico
from src.services.base import ComTags, ServicoBase, exigir, exigir_data, exigir_opcao

OBRIGATORIOS_DEMANDA = (
    "titulo", "alvo_motivo", "data_entrada", "data_limite", "status",
    "origem_canal", "origem_remetente", "origem_destinatario",
)
DATA_LIMITE_ANTERIOR = "A data limite não pode ser anterior à data de entrada."


class DemandaService(ComTags, ServicoBase):
    modelo = Demanda
    tabela = "demandas"
    campos = (
        "titulo", "alvo_motivo", "data_entrada", "data_limite", "status", "segredo_justica",
        "observacoes", "caminho_pasta", "origem_canal", "origem_remetente",
        "origem_destinatario", "origem_documento",
    )
    carregar = (
        selectinload(Demanda.tags),
        selectinload(Demanda.documentos).selectinload(Documento.tags),
        selectinload(Demanda.subsidios).selectinload(Subsidio.tags),
        selectinload(Demanda.subsidios).selectinload(Subsidio.documentos).selectinload(Documento.tags),
    )

    def listar_historico(self, demanda_id: int) -> list:
        """Histórico da demanda e dos seus subsídios e documentos atuais (RF014)."""
        with self._transacao() as sessao:
            demanda = self._obter(sessao, demanda_id, self.carregar)
            registros = [("demandas", demanda.id)]
            registros += [("subsidios", s.id) for s in demanda.subsidios]
            registros += [("documentos", d.id) for d in self._documentos_de(demanda)]
            return historico.consultar(sessao, registros)

    def _completar(self, dados: dict[str, Any], criando: bool) -> dict[str, Any]:
        # Padrões do RS003: status "Em análise" (decisão da sessão 0) e segredo_justica falso.
        if criando:
            if dados.get("status") is None:
                dados["status"] = STATUS_PADRAO
            if dados.get("segredo_justica") is None:
                dados["segredo_justica"] = False
        return dados

    def _validar(self, sessao: Session, dados: dict[str, Any], registro_id: int | None) -> dict[str, str]:
        erros = exigir(dados, OBRIGATORIOS_DEMANDA)
        exigir_data(erros, dados, "data_entrada")
        exigir_data(erros, dados, "data_limite")
        # RD005 não é imposto: o status é escolhido livremente e pode ser reaberto.
        exigir_opcao(erros, dados, "status", STATUS_DEMANDA)
        exigir_opcao(erros, dados, "origem_canal", CANAIS_ORIGEM)
        if not isinstance(dados.get("segredo_justica"), bool):
            erros["segredo_justica"] = "Valor inválido."
        if "data_entrada" not in erros and "data_limite" not in erros:
            if dados["data_limite"] < dados["data_entrada"]:
                erros["data_limite"] = DATA_LIMITE_ANTERIOR
        return erros

    def _descricao(self, demanda: Demanda) -> str:
        return demanda.titulo

    def _antes_excluir(self, sessao: Session, demanda: Demanda) -> None:
        for subsidio in demanda.subsidios:
            historico.registrar_exclusao(sessao, "subsidios", subsidio.id, subsidio.setor_fonte)

    def _documentos_de(self, demanda: Demanda) -> list[Documento]:
        return list(demanda.documentos) + [d for s in demanda.subsidios for d in s.documentos]
