"""
Tags (RF005, RS006–RS010): tela para criar, editar e excluir tags e o seletor
que associa ou desassocia tags de um registro, no próprio painel (NR002).
"""
from tkinter import messagebox
from typing import Callable

import customtkinter as ctk

from src.services import ServicoError
from src.ui.theme import Colors, Fonts
from src.ui.views.formulario import Especificacao as E
from src.ui.views.formulario import FormularioView
from src.ui.widgets import PALETA_TAGS, Entrada, botao, chip_tag

LINHAS_TAG = [
    [E("nome", obrigatorio=True)],
    [E("cor", "cor", obrigatorio=True)],
]


def _cartao(parent) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, border_color=Colors.BORDER_SUBTLE,
                        border_width=1, corner_radius=8)


class SeletorTags(ctk.CTkFrame):
    """Marca e desmarca as tags de um registro; cada clique é gravado na hora."""

    def __init__(self, parent, titulo: str, servicos, servico_registro, registro_id: int,
                 marcadas: set[int], ao_concluir: Callable[[], None]):
        super().__init__(parent, fg_color="transparent")
        self.servicos = servicos
        self.servico_registro = servico_registro
        self.registro_id = registro_id
        self.marcadas = set(marcadas)
        self.caixas: dict[int, ctk.CTkCheckBox] = {}

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(14, 4))
        ctk.CTkLabel(topo, text=titulo, font=Fonts.SUBTITLE, text_color=Colors.TEXT_MAIN).pack(side="left")
        botao(topo, "Concluir", ao_concluir, tipo="primario", width=110).pack(side="right")
        ctk.CTkLabel(self, text="Marque ou desmarque; cada alteração é salva na hora.", font=Fonts.SMALL,
                     text_color=Colors.TEXT_MUTED, anchor="w").pack(fill="x", padx=16)
        self.lbl_mensagem = ctk.CTkLabel(self, text="", font=Fonts.SMALL, text_color=Colors.ERRO_FG, anchor="w")
        self.lbl_mensagem.pack(fill="x", padx=16)

        nova = ctk.CTkFrame(self, fg_color="transparent")
        nova.pack(fill="x", side="bottom", padx=16, pady=(6, 14))
        self.nome_nova = Entrada(nova, placeholder_text="Nome da nova tag", width=240)
        self.nome_nova.pack(side="left", padx=(0, 8))
        self.nome_nova.bind("<Return>", lambda _e: self.criar_e_marcar())
        botao(nova, "Criar e marcar", self.criar_e_marcar, width=120).pack(side="left")

        self.lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista.pack(fill="both", expand=True, padx=8, pady=(4, 0))
        self._preencher()

    def _preencher(self) -> None:
        for filho in self.lista.winfo_children():
            filho.destroy()
        self.caixas.clear()
        tags = self.servicos.tags.listar()
        if not tags:
            ctk.CTkLabel(self.lista, text="Nenhuma tag cadastrada. Crie uma abaixo.", font=Fonts.BODY,
                         text_color=Colors.TEXT_MUTED).pack(anchor="w", padx=8)
        for tag in tags:
            linha = ctk.CTkFrame(self.lista, fg_color="transparent")
            linha.pack(fill="x", padx=8, pady=3)
            caixa = ctk.CTkCheckBox(
                linha, text="", width=24, fg_color=Colors.ACCENT_BLUE, hover_color=Colors.ACCENT_BLUE_HOVER,
                command=lambda tag_id=tag.id: self.alternar(tag_id),
            )
            if tag.id in self.marcadas:
                caixa.select()
            caixa.pack(side="left")
            chip_tag(linha, tag.nome, tag.cor).pack(side="left")
            self.caixas[tag.id] = caixa

    def alternar(self, tag_id: int) -> None:
        caixa = self.caixas[tag_id]
        marcar = bool(caixa.get())
        self.lbl_mensagem.configure(text="")
        try:
            if marcar:
                self.servico_registro.associar_tag(self.registro_id, tag_id)
                self.marcadas.add(tag_id)
            else:
                self.servico_registro.desassociar_tag(self.registro_id, tag_id)
                self.marcadas.discard(tag_id)
        except ServicoError as erro:
            # Nada foi gravado: a caixa volta ao estado anterior.
            caixa.deselect() if marcar else caixa.select()
            self.lbl_mensagem.configure(text=str(erro))

    def criar_e_marcar(self) -> None:
        nome = self.nome_nova.texto().strip()
        if not nome:
            self.lbl_mensagem.configure(text="Digite o nome da nova tag.")
            return
        try:
            existentes = self.servicos.tags.listar()
            # Cor inicial da paleta, em rodízio; pode ser trocada na tela Tags.
            cor = PALETA_TAGS[len(existentes) % len(PALETA_TAGS)]
            tag = self.servicos.tags.criar(nome=nome, cor=cor)
            self.servico_registro.associar_tag(self.registro_id, tag.id)
        except ServicoError as erro:
            mensagens = getattr(erro, "erros", None)
            self.lbl_mensagem.configure(text=" ".join(mensagens.values()) if mensagens else str(erro))
            return
        self.marcadas.add(tag.id)
        self.nome_nova.definir("")
        self.lbl_mensagem.configure(text="")
        self._preencher()


class TelaTags(ctk.CTkFrame):
    """Cadastro de tags: lista à esquerda, formulário à direita."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.servicos = app.servicos
        self.grid_columnconfigure(0, weight=5, uniform="colunas")
        self.grid_columnconfigure(1, weight=6, uniform="colunas")
        self.grid_rowconfigure(0, weight=1)

        cartao = _cartao(self)
        cartao.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        topo = ctk.CTkFrame(cartao, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 8))
        self.lbl_lista = ctk.CTkLabel(topo, text="", font=Fonts.SECTION_HEADER, text_color=Colors.TEXT_MUTED)
        self.lbl_lista.pack(side="left")
        botao(topo, "+ Nova tag", lambda: self.mostrar_formulario(None), tipo="primario", width=120).pack(side="right")
        self.lista = ctk.CTkScrollableFrame(cartao, fg_color="transparent")
        self.lista.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        self.painel = _cartao(self)
        self.painel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.formulario: FormularioView | None = None

    def atualizar_lista(self) -> None:
        for filho in self.lista.winfo_children():
            filho.destroy()
        tags = self.servicos.tags.listar()
        self.lbl_lista.configure(text=f"TAGS ({len(tags)})")
        if not tags:
            ctk.CTkLabel(self.lista, text="Nenhuma tag cadastrada.", font=Fonts.BODY,
                         text_color=Colors.TEXT_MUTED).pack(pady=20)
        for tag in tags:
            usos = self.servicos.tags.usos(tag.id)
            linha = ctk.CTkFrame(self.lista, fg_color=Colors.BG_INPUT, corner_radius=6)
            linha.pack(fill="x", padx=6, pady=3)
            chip_tag(linha, tag.nome, tag.cor).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(linha, text=f"{tag.cor} · {usos} uso{'s' if usos != 1 else ''}", font=Fonts.SMALL,
                         text_color=Colors.TEXT_MUTED).pack(side="left")
            botao(linha, "Excluir", lambda t=tag, u=usos: self.excluir(t, u), tipo="perigo", width=64,
                  height=24, font=Fonts.SMALL).pack(side="right", padx=(4, 10))
            botao(linha, "Editar", lambda t=tag: self.mostrar_formulario(t), width=64, height=24,
                  font=Fonts.SMALL).pack(side="right")
        if self.formulario is None:
            self.mostrar_formulario(None)

    def mostrar_formulario(self, tag) -> None:
        if self.formulario is not None:
            self.formulario.destroy()
        if tag is None:
            titulo, valores = "Nova tag", {"cor": PALETA_TAGS[6]}
        else:
            titulo, valores = f"Editar tag \"{tag.nome}\"", {"nome": tag.nome, "cor": tag.cor}

        def salvar(dados):
            if tag is None:
                self.servicos.tags.criar(**dados)
            else:
                self.servicos.tags.editar(tag.id, **dados)
            self.formulario.destroy()
            self.formulario = None
            self.atualizar_lista()

        self.formulario = FormularioView(self.painel, titulo, LINHAS_TAG, salvar,
                                         lambda: self.mostrar_formulario(None), valores,
                                         texto_salvar="Salvar tag")
        self.formulario.pack(fill="both", expand=True, padx=2, pady=2)

    def excluir(self, tag, usos: int) -> None:
        mensagem = f"Excluir a tag \"{tag.nome}\"?"
        if usos:
            mensagem += f"\n\nEla será retirada de {usos} registro(s); os registros continuam."
        if not self.confirmar("Confirmar exclusão", mensagem):
            return
        try:
            self.servicos.tags.excluir(tag.id)
        except ServicoError as erro:
            self.avisar("Não foi possível excluir", str(erro))
            return
        self.mostrar_formulario(None)
        self.atualizar_lista()

    def confirmar(self, titulo: str, mensagem: str) -> bool:
        return messagebox.askyesno(titulo, mensagem, icon="warning", parent=self)

    def avisar(self, titulo: str, mensagem: str) -> None:
        messagebox.showwarning(titulo, mensagem, parent=self)
