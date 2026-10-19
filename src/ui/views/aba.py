"""
Base das abas Demandas e Pareceres (RS012): lista de resultados à esquerda e
painel à direita, que mostra os detalhes (RF010) ou um formulário, sem abrir
nova janela (NR002).

Acima da lista ficam a pesquisa por texto e os filtros (RF006–RF008); abaixo,
a paginação de 50 itens (RS018, RF009).
"""
from dataclasses import dataclass
from typing import Callable
from tkinter import messagebox, ttk

import customtkinter as ctk

from src.services import ServicoError
from src.services.pesquisa import Pagina
from src.ui.theme import Colors, Fonts
from src.ui.widgets import ESTILO_LISTA, Entrada, botao

NENHUM_RESULTADO = "Nenhum resultado encontrado"
ESPERA_DIGITACAO_MS = 250


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
    texto_busca = ""
    texto_sem_registros = ""
    mensagem_vazio = "Clique duas vezes em um item da lista para ver os detalhes."

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.servicos = app.servicos
        self.registro_aberto: int | None = None
        self.pagina = 1
        self.filtros: list = []
        self._pesquisa_agendada = None

        self.grid_columnconfigure(0, weight=5, uniform="colunas")
        self.grid_columnconfigure(1, weight=6, uniform="colunas")
        self.grid_rowconfigure(0, weight=1)

        self._build_lista()
        self.painel = _cartao(self)
        self.painel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.conteudo_painel = None
        self.mostrar_vazio()

    # --- Lista, pesquisa e filtros ----------------------------------------------

    def _build_lista(self):
        cartao = _cartao(self)
        cartao.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        topo = ctk.CTkFrame(cartao, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 8))
        self.lbl_lista = ctk.CTkLabel(topo, text="", font=Fonts.SECTION_HEADER, text_color=Colors.TEXT_MUTED)
        self.lbl_lista.pack(side="left")
        botao(topo, self.texto_novo, lambda: self.mostrar_formulario(None), tipo="primario", width=140).pack(side="right")

        # RF006: um único campo de texto; a lista atualiza logo depois de cada termo digitado.
        self.busca = Entrada(cartao, ao_mudar=self._agendar_pesquisa, placeholder_text=self.texto_busca, height=34)
        self.busca.pack(fill="x", padx=14, pady=(0, 6))
        self.busca.bind("<Return>", lambda _e: self.pesquisar())

        # RF007: filtros combinados com o texto; "Limpar filtros" remove todos.
        filtros = ctk.CTkFrame(cartao, fg_color="transparent")
        filtros.pack(fill="x", padx=14, pady=(0, 8))
        self._build_filtros(filtros)

        moldura = ctk.CTkFrame(cartao, fg_color=Colors.BG_CARD, corner_radius=0)
        moldura.pack(fill="both", expand=True, padx=(10, 6), pady=(0, 4))
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

        # RF009: aviso sobre a lista quando não há resultados.
        self.aviso_vazio = ctk.CTkFrame(moldura, fg_color="transparent")
        self.lbl_vazio = ctk.CTkLabel(self.aviso_vazio, text="", font=Fonts.BODY, text_color=Colors.TEXT_MUTED)
        self.lbl_vazio.pack(pady=(0, 8))
        self.btn_limpar_vazio = botao(self.aviso_vazio, "Limpar filtros", self.limpar_filtros, width=130)

        rodape = ctk.CTkFrame(cartao, fg_color="transparent")
        rodape.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(rodape, text="Clique duas vezes para abrir.", font=Fonts.SMALL,
                     text_color=Colors.TEXT_MUTED).pack(side="left")
        # RS018: 50 itens por página.
        self.btn_proxima = botao(rodape, "Próxima ›", lambda: self.ir_para_pagina(self.pagina + 1),
                                 width=86, height=26, font=Fonts.SMALL)
        self.btn_proxima.pack(side="right")
        self.lbl_pagina = ctk.CTkLabel(rodape, text="", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        self.lbl_pagina.pack(side="right", padx=8)
        self.btn_anterior = botao(rodape, "‹ Anterior", lambda: self.ir_para_pagina(self.pagina - 1),
                                  width=86, height=26, font=Fonts.SMALL)
        self.btn_anterior.pack(side="right")

    def _build_filtros(self, parent) -> None:
        """Cria os filtros da aba e preenche self.filtros."""
        raise NotImplementedError

    def botao_limpar(self, parent) -> ctk.CTkButton:
        return botao(parent, "Limpar filtros", self.limpar_filtros, width=110, height=30, font=Fonts.SMALL)

    def consultar(self, texto: str, pagina: int, **filtros) -> Pagina:
        raise NotImplementedError

    def valores_filtros(self) -> dict | None:
        """Argumentos dos filtros para consultar(); None se algum estiver inválido."""
        raise NotImplementedError

    def atualizar_opcoes_filtros(self) -> None:
        """Atualiza opções que dependem do banco (tags, anos)."""

    def filtros_ativos(self) -> bool:
        return bool(self.busca.texto().strip()) or any(f.ativo() for f in self.filtros)

    def limpar_filtros(self) -> None:
        for filtro in self.filtros:
            filtro.limpar()
        self.busca.definir("")
        self.pesquisar()

    def _agendar_pesquisa(self) -> None:
        # Espera uma pausa curta na digitação para não pesquisar a cada tecla.
        if self._pesquisa_agendada is not None:
            self.after_cancel(self._pesquisa_agendada)
        self._pesquisa_agendada = self.after(ESPERA_DIGITACAO_MS, self.pesquisar)

    def pesquisar(self) -> None:
        """Texto ou filtro mudou: volta à primeira página."""
        self.atualizar_lista(pagina=1)

    def ir_para_pagina(self, pagina: int) -> None:
        self.atualizar_lista(pagina=pagina)

    def atualizar_lista(self, selecionar: int | None = None, pagina: int | None = None) -> None:
        if self._pesquisa_agendada is not None:
            self.after_cancel(self._pesquisa_agendada)
            self._pesquisa_agendada = None
        try:
            self.atualizar_opcoes_filtros()
            filtros = self.valores_filtros()
            if filtros is None:
                return  # data de filtro incompleta ou inválida: mantém a lista atual
            resultado = self.consultar(self.busca.texto(), pagina or self.pagina, **filtros)
        except ServicoError as erro:
            self.mostrar_aviso(str(erro))
            return
        self.pagina = resultado.pagina
        self.lista.delete(*self.lista.get_children())
        for registro in resultado.itens:
            self.lista.insert("", "end", iid=str(registro.id), values=self.valores_linha(registro))
        self.lbl_lista.configure(text=f"{self.titulo_lista} ({resultado.total})")
        self.lbl_pagina.configure(text=f"Página {resultado.pagina} de {resultado.total_paginas}")
        self.btn_anterior.configure(state="normal" if resultado.pagina > 1 else "disabled")
        self.btn_proxima.configure(state="normal" if resultado.pagina < resultado.total_paginas else "disabled")
        self._mostrar_aviso_vazio(not resultado.itens)
        if selecionar is not None and self.lista.exists(str(selecionar)):
            self.lista.selection_set(str(selecionar))
            self.lista.see(str(selecionar))

    def _mostrar_aviso_vazio(self, vazio: bool) -> None:
        if not vazio:
            self.aviso_vazio.place_forget()
            return
        if self.filtros_ativos():
            self.lbl_vazio.configure(text=NENHUM_RESULTADO)
            self.btn_limpar_vazio.pack()
        else:
            self.lbl_vazio.configure(text=self.texto_sem_registros)
            self.btn_limpar_vazio.pack_forget()
        self.aviso_vazio.place(relx=0.5, rely=0.4, anchor="center")

    def valores_linha(self, registro) -> tuple:
        raise NotImplementedError

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
