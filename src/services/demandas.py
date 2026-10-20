"""DemandaService (RS015, RF001, RS017, RS011)."""
import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.models import (
    CANAIS_ORIGEM, STATUS_CONCLUIDA, STATUS_DEMANDA, STATUS_PADRAO, Demanda, Documento, Subsidio, tags_demandas,
)
from src.services import historico, pesquisa, prazos
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

    # RS011: campos comparados por similaridade (além do id e dos nomes das tags).
    campos_pesquisa = ("titulo", "alvo_motivo", "origem_remetente", "observacoes")

    def pesquisar(
        self,
        texto: str | None = None,
        *,
        status: str | None = None,
        tag_id: int | None = None,
        canal: str | None = None,
        entrada_de: datetime.date | None = None,
        entrada_ate: datetime.date | None = None,
        limite_de: datetime.date | None = None,
        limite_ate: datetime.date | None = None,
        pagina: int = 1,
    ) -> pesquisa.Pagina:
        """Pesquisa por texto combinada com filtros (RS011, RF006–RF008), paginada (RS018)."""
        condicoes = []
        if status:
            condicoes.append(Demanda.status == status)
        if canal:
            condicoes.append(Demanda.origem_canal == canal)
        if tag_id is not None:
            condicoes.append(Demanda.id.in_(
                select(tags_demandas.c.demanda_id).where(tags_demandas.c.tag_id == tag_id)
            ))
        for coluna, inicio, fim in (
            (Demanda.data_entrada, entrada_de, entrada_ate),
            (Demanda.data_limite, limite_de, limite_ate),
        ):
            if inicio:
                condicoes.append(coluna >= inicio)
            if fim:
                condicoes.append(coluna <= fim)
        with self._transacao() as sessao:
            return pesquisa.pesquisar(
                sessao, Demanda, condicoes, texto, pagina, self.campos_pesquisa,
                tags_demandas, "demanda_id",
            )

    def contar_prazos(self, hoje: datetime.date | None = None) -> prazos.ContagemPrazos:
        """Total de demandas próximas do prazo e vencidas, exibido ao abrir (RS019, RF015)."""
        hoje = hoje or datetime.date.today()
        abertas = Demanda.status != STATUS_CONCLUIDA
        with self._transacao() as sessao:
            proximas = sessao.scalar(select(func.count()).where(
                abertas, Demanda.data_limite >= hoje, Demanda.data_limite <= prazos.ultimo_dia_alerta(hoje),
            ))
            vencidas = sessao.scalar(select(func.count()).where(abertas, Demanda.data_limite < hoje))
        return prazos.ContagemPrazos(proximas, vencidas)

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
