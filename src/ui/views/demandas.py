"""
Aba Demandas (RF001, RF003, RF010, RF014, RS012, RS017).
"""
import datetime

import customtkinter as ctk

from src.models import CANAIS_ORIGEM, STATUS_DEMANDA, STATUS_PADRAO
from src.ui.formatos import data_br, sim_nao
from src.ui.theme import Colors, Fonts
from src.ui.views.aba import AbaBase, Coluna
from src.ui.views.detalhe import LARGURA_TEXTO, DetalheBase
from src.ui.views.formulario import Especificacao as E
from src.ui.views.formulario import FormularioView
from src.ui.widgets import botao

LINHAS_DEMANDA = [
    [E("titulo", obrigatorio=True)],
    [E("alvo_motivo", "longo", obrigatorio=True, extras={"altura": 56})],
    [
        E("data_entrada", "data", obrigatorio=True),
        E("data_limite", "data", obrigatorio=True),
        E("status", "opcoes", obrigatorio=True, extras={"opcoes": STATUS_DEMANDA}),
    ],
    [
        E("origem_canal", "opcoes", obrigatorio=True, extras={"opcoes": CANAIS_ORIGEM}),
        E("origem_remetente", obrigatorio=True, rotulo="Remetente (quem enviou)"),
        E("origem_destinatario", obrigatorio=True, rotulo="Destinatário (quem recebeu)"),
    ],
    [
        E("origem_documento", rotulo="Documento de origem (título do e-mail, nº do ofício...)"),
        E("segredo_justica", "booleano", extras={"texto_opcao": "Processo em segredo de justiça"}),
    ],
    [E("caminho_pasta", "pasta", rotulo="Pasta local dos documentos")],
    [E("observacoes", "longo", extras={"altura": 72})],
]

LINHAS_SUBSIDIO = [
    [E("setor_fonte", obrigatorio=True), E("data_aquisicao", "data", obrigatorio=True)],
    [E("resposta", "longo", obrigatorio=True, extras={"altura": 110})],
]


class AbaDemandas(AbaBase):
    colunas = [
        Coluna("id", "ID", 50, alinhar="center"),
        Coluna("titulo", "Título", 240, esticar=True),
        Coluna("status", "Status", 190),
        Coluna("data_limite", "Data limite", 100, alinhar="center"),
    ]
    titulo_lista = "DEMANDAS"
    texto_novo = "+ Nova demanda"

    def registros(self) -> list:
        return self.servicos.demandas.listar()

    def valores_linha(self, demanda) -> tuple:
        return (demanda.id, demanda.titulo, demanda.status, data_br(demanda.data_limite))

    # --- Formulários -----------------------------------------------------------

    def criar_formulario(self, demanda_id: int | None):
        if demanda_id is None:
            valores = {"data_entrada": datetime.date.today(), "status": STATUS_PADRAO}
            titulo = "Nova demanda"
        else:
            demanda = self.servicos.demandas.buscar(demanda_id)
            valores = {e.nome: getattr(demanda, e.nome) for linha in LINHAS_DEMANDA for e in linha}
            titulo = f"Editar demanda #{demanda_id}"

        def salvar(dados):
            if demanda_id is None:
                salvo = self.servicos.demandas.criar(**dados)
            else:
                salvo = self.servicos.demandas.editar(demanda_id, **dados)
            self.atualizar_lista(selecionar=salvo.id)
            self.mostrar_detalhe(salvo.id)

        return FormularioView(self.painel, titulo, LINHAS_DEMANDA, salvar, self.voltar, valores,
                              texto_salvar="Salvar demanda")

    def formulario_subsidio(self, demanda_id: int, subsidio=None) -> None:
        if subsidio is None:
            valores = {"data_aquisicao": datetime.date.today()}
            titulo = f"Novo subsídio · demanda #{demanda_id}"
        else:
            valores = {"setor_fonte": subsidio.setor_fonte, "data_aquisicao": subsidio.data_aquisicao,
                       "resposta": subsidio.resposta}
            titulo = f"Editar subsídio #{subsidio.id} · demanda #{demanda_id}"

        def salvar(dados):
            if subsidio is None:
                self.servicos.subsidios.criar(demanda_id=demanda_id, **dados)
            else:
                self.servicos.subsidios.editar(subsidio.id, **dados)
            self.mostrar_detalhe(demanda_id)

        self.trocar_painel(FormularioView(self.painel, titulo, LINHAS_SUBSIDIO, salvar,
                                          lambda: self.mostrar_detalhe(demanda_id), valores,
                                          texto_salvar="Salvar subsídio"))

    # --- Detalhes (RF010) -------------------------------------------------------

    def criar_detalhe(self, demanda_id: int):
        demanda = self.servicos.demandas.buscar(demanda_id)
        historico = self.servicos.demandas.listar_historico(demanda_id)
        return DetalheDemanda(self.painel, self, demanda, historico)

    def excluir_demanda(self, demanda) -> None:
        n_documentos = len(demanda.documentos) + sum(len(s.documentos) for s in demanda.subsidios)
        dependentes = []
        if demanda.subsidios:
            dependentes.append(f"{len(demanda.subsidios)} subsídio(s)")
        if n_documentos:
            dependentes.append(f"{n_documentos} documento(s)")
        aviso = f"Também serão removidos do sistema: {', '.join(dependentes)}." if dependentes else ""
        self.excluir(self.servicos.demandas, demanda.id, f"a demanda #{demanda.id} \"{demanda.titulo}\"",
                     aviso, n_documentos)

    def excluir_subsidio(self, demanda_id: int, subsidio) -> None:
        n_documentos = len(subsidio.documentos)
        aviso = f"Também serão removidos do sistema: {n_documentos} documento(s)." if n_documentos else ""
        self.excluir(self.servicos.subsidios, subsidio.id, f"o subsídio de {subsidio.setor_fonte}",
                     aviso, n_documentos, depois=lambda: self.mostrar_detalhe(demanda_id))


class DetalheDemanda(DetalheBase):
    def __init__(self, parent, aba: AbaDemandas, demanda, historico):
        super().__init__(parent)
        etiquetas = [demanda.status]
        if demanda.segredo_justica:
            etiquetas.append("Segredo de justiça")
        self.cabecalho(
            demanda.titulo,
            f"#{demanda.id} · Entrada {data_br(demanda.data_entrada)} · Limite {data_br(demanda.data_limite)}",
            etiquetas,
            ao_editar=lambda: aba.mostrar_formulario(demanda.id),
            ao_excluir=lambda: aba.excluir_demanda(demanda),
        )

        info = self.secao("Informações")
        self.pares(info, [("Alvo / motivo", demanda.alvo_motivo)], colunas=1)
        self.pares(info, [
            ("Canal de origem", demanda.origem_canal),
            ("Documento de origem", demanda.origem_documento),
            ("Remetente", demanda.origem_remetente),
            ("Destinatário", demanda.origem_destinatario),
            ("Segredo de justiça", sim_nao(demanda.segredo_justica)),
            ("Pasta local", demanda.caminho_pasta),
        ])

        self.texto(self.secao("Observações"), demanda.observacoes)
        self.tags(self.secao("Tags"), demanda.tags)

        subsidios = self.secao("Subsídios", ("+ Adicionar", lambda: aba.formulario_subsidio(demanda.id)))
        if not demanda.subsidios:
            self.texto(subsidios, "Nenhum subsídio registrado.")
        for subsidio in sorted(demanda.subsidios, key=lambda s: (s.data_aquisicao, s.id)):
            self._subsidio(subsidios, aba, demanda.id, subsidio)

        self.documentos(self.secao("Documentos"), demanda.documentos)
        self.historico(self.secao("Histórico de alterações"), "demandas", historico)

    def _subsidio(self, conteudo, aba: AbaDemandas, demanda_id: int, subsidio) -> None:
        caixa = ctk.CTkFrame(conteudo, fg_color=Colors.BG_INPUT, corner_radius=6)
        caixa.pack(fill="x", pady=(0, 6))
        topo = ctk.CTkFrame(caixa, fg_color="transparent")
        topo.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            topo, text=f"{subsidio.setor_fonte} · {data_br(subsidio.data_aquisicao)}",
            font=Fonts.BODY_BOLD, text_color=Colors.TEXT_MAIN, anchor="w",
        ).pack(side="left")
        botao(topo, "Excluir", lambda: aba.excluir_subsidio(demanda_id, subsidio), tipo="perigo",
              width=64, height=24, font=Fonts.SMALL).pack(side="right")
        botao(topo, "Editar", lambda: aba.formulario_subsidio(demanda_id, subsidio),
              width=64, height=24, font=Fonts.SMALL).pack(side="right", padx=(0, 6))
        ctk.CTkLabel(
            caixa, text=subsidio.resposta, font=Fonts.BODY, text_color=Colors.TEXT_MAIN,
            anchor="w", justify="left", wraplength=LARGURA_TEXTO - 40,
        ).pack(fill="x", padx=10, pady=(0, 6))
        if subsidio.tags:
            self.tags(_subframe(caixa), subsidio.tags)
        if subsidio.documentos:
            self.documentos(_subframe(caixa), subsidio.documentos)


def _subframe(parent) -> ctk.CTkFrame:
    moldura = ctk.CTkFrame(parent, fg_color="transparent")
    moldura.pack(fill="x", padx=10, pady=(0, 8))
    return moldura

