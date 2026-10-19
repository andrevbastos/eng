"""
Base das abas Demandas e Pareceres (RS012): lista de resultados à esquerda e
painel à direita, que mostra os detalhes (RF010) ou um formulário, sem abrir
nova janela (NR002).

A pesquisa, os filtros e a paginação entram na sessão 5.
"""
from dataclasses import dataclass
from typing import Callable
from tkinter import messagebox, ttk

import customtkinter as ctk

from src.services import ServicoError
from src.ui.theme import Colors, Fonts
from src.ui.widgets import ESTILO_LISTA, botao


@dataclass
class Coluna:
    nome: str
    titulo: str
    largura: int
    esticar: bool = False
    alinhar: str = "w"


class AbaBase(ctk.CTkFrame):
    colunas: list[Coluna] = []
    titulo_lista = ""
    texto_novo = ""
    mensagem_vazio = "Clique duas vezes em um item da lista para ver os detalhes."

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.servicos = app.servicos
        self.registro_aberto: int | None = None

        self.grid_columnconfigure(0, weight=5, uniform="colunas")
        self.grid_columnconfigure(1, weight=6, uniform="colunas")
        self.grid_rowconfigure(0, weight=1)

        self._build_lista()
        self.painel = _cartao(self)
        self.painel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.conteudo_painel = None
        self.mostrar_vazio()

    # --- Lista -----------------------------------------------------------------

    def _build_lista(self):
        cartao = _cartao(self)
        cartao.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        topo = ctk.CTkFrame(cartao, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 8))
        self.lbl_lista = ctk.CTkLabel(topo, text="", font=Fonts.SECTION_HEADER, text_color=Colors.TEXT_MUTED)
        self.lbl_lista.pack(side="left")
        botao(topo, self.texto_novo, lambda: self.mostrar_formulario(None), tipo="primario", width=140).pack(side="right")

        moldura = ctk.CTkFrame(cartao, fg_color=Colors.BG_CARD, corner_radius=0)
        moldura.pack(fill="both", expand=True, padx=(10, 6), pady=(0, 8))
        self.lista = ttk.Treeview(
            moldura,
            columns=[c.nome for c in self.colunas],
            show="headings",
            selectmode="browse",
            style=ESTILO_LISTA,
        )
        for coluna in self.colunas:
            self.lista.heading(coluna.nome, text=coluna.titulo.upper(), anchor=coluna.alinhar)
            self.lista.column(coluna.nome, width=coluna.largura, minwidth=40, stretch=coluna.esticar,
                              anchor=coluna.alinhar)
        barra = ctk.CTkScrollbar(moldura, orientation="vertical", command=self.lista.yview,
                                 button_color=Colors.BG_BTN_SEC, button_hover_color=Colors.BG_BTN_SEC_HOVER)
        self.lista.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lista.pack(side="left", fill="both", expand=True)

        # RF010: clique duplo abre os detalhes; Enter faz o mesmo pelo teclado.
        self.lista.bind("<Double-1>", self._abrir_selecionado)
        self.lista.bind("<Return>", self._abrir_selecionado)

        ctk.CTkLabel(
            cartao,
            text="Clique duas vezes para abrir.",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 8))

    def registros(self) -> list:
        raise NotImplementedError

    def valores_linha(self, registro) -> tuple:
        raise NotImplementedError

    def atualizar_lista(self, selecionar: int | None = None) -> None:
        try:
            registros = self.registros()
        except ServicoError as erro:
            self.mostrar_aviso(str(erro))
            return
        self.lista.delete(*self.lista.get_children())
        for registro in registros:
            self.lista.insert("", "end", iid=str(registro.id), values=self.valores_linha(registro))
        self.lbl_lista.configure(text=f"{self.titulo_lista} ({len(registros)})")
        if selecionar is not None and self.lista.exists(str(selecionar)):
            self.lista.selection_set(str(selecionar))
            self.lista.see(str(selecionar))

    def _abrir_selecionado(self, _evento=None):
        selecao = self.lista.selection()
        if selecao:
            self.mostrar_detalhe(int(selecao[0]))

    # --- Painel da direita ----------------------------------------------------

    def trocar_painel(self, widget) -> None:
        if self.conteudo_painel is not None:
            self.conteudo_painel.destroy()
        self.conteudo_painel = widget
        widget.pack(fill="both", expand=True, padx=2, pady=2)

    def mostrar_vazio(self, mensagem: str | None = None) -> None:
        self.registro_aberto = None
        moldura = ctk.CTkFrame(self.painel, fg_color="transparent")
        ctk.CTkLabel(
            moldura,
            text=mensagem or self.mensagem_vazio,
            font=Fonts.BODY,
            text_color=Colors.TEXT_MUTED,
            wraplength=480,
        ).place(relx=0.5, rely=0.5, anchor="center")
        self.trocar_painel(moldura)

    def mostrar_aviso(self, mensagem: str) -> None:
        self.mostrar_vazio(mensagem)

    def mostrar_detalhe(self, registro_id: int) -> None:
        try:
            widget = self.criar_detalhe(registro_id)
        except ServicoError as erro:
            self.mostrar_aviso(str(erro))
            return
        self.registro_aberto = registro_id
        self.trocar_painel(widget)

    def mostrar_formulario(self, registro_id: int | None) -> None:
        try:
            widget = self.criar_formulario(registro_id)
        except ServicoError as erro:
            self.mostrar_aviso(str(erro))
            return
        self.trocar_painel(widget)

    def voltar(self) -> None:
        """Depois de cancelar um formulário: volta ao registro aberto, se houver."""
        if self.registro_aberto is not None:
            self.mostrar_detalhe(self.registro_aberto)
        else:
            self.mostrar_vazio()

    def criar_detalhe(self, registro_id: int):
        raise NotImplementedError

    def criar_formulario(self, registro_id: int | None):
        raise NotImplementedError

    # --- Confirmações (substituíveis nos testes) -------------------------------

    def confirmar(self, titulo: str, mensagem: str) -> bool:
        return messagebox.askyesno(titulo, mensagem, icon="warning", parent=self)

    def perguntar(self, titulo: str, mensagem: str) -> bool | None:
        """Sim, Não ou Cancelar (None)."""
        return messagebox.askyesnocancel(titulo, mensagem, icon="warning", parent=self)

    def avisar(self, titulo: str, mensagem: str) -> None:
        messagebox.showwarning(titulo, mensagem, parent=self)

    def excluir(
        self,
        servico,
        registro_id: int,
        descricao: str,
        dependentes: str,
        n_documentos: int,
        depois: Callable[[], None] | None = None,
    ) -> None:
        """Confirma e exclui; pergunta se os arquivos anexados também saem do disco."""
        mensagem = f"Excluir {descricao}?"
        if dependentes:
            mensagem += f"\n\n{dependentes}"
        if not self.confirmar("Confirmar exclusão", mensagem):
            return
        apagar_arquivos = False
        if n_documentos:
            resposta = self.perguntar(
                "Arquivos anexados",
                f"Há {n_documentos} arquivo(s) anexado(s). Apagar também os arquivos do disco?\n\n"
                "Sim: apaga os arquivos.  Não: mantém os arquivos e remove só o registro.",
            )
            if resposta is None:
                return
            apagar_arquivos = resposta
        try:
            falhas = servico.excluir(registro_id, apagar_arquivos=apagar_arquivos)
        except ServicoError as erro:
            self.avisar("Não foi possível excluir", str(erro))
            return
        if falhas:
            self.avisar("Arquivos mantidos", "Não foi possível apagar:\n" + "\n".join(falhas))
        if depois:
            depois()
        else:
            self.atualizar_lista()
            self.mostrar_vazio()


def _cartao(parent) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=Colors.BG_CARD,
        border_color=Colors.BORDER_SUBTLE,
        border_width=1,
        corner_radius=8,
    )
