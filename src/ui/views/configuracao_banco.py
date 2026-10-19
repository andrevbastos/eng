"""
Escolha do arquivo .db (RS001), exibida na própria janela principal (NR002).
"""
from tkinter import filedialog

import customtkinter as ctk

from src.ui.theme import Colors, Fonts

TIPOS_DB = [("Banco de dados", "*.db"), ("Todos os arquivos", "*.*")]


class ConfiguracaoBancoView(ctk.CTkFrame):
    def __init__(self, parent, app, mensagem: str | None = None, pode_voltar: bool = False):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        card = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=10,
        )
        card.place(relx=0.5, rely=0.45, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=36, pady=30)

        ctk.CTkLabel(
            inner,
            text="Banco de dados",
            font=Fonts.TITLE,
            text_color=Colors.TEXT_MAIN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text=(
                "Escolha onde fica o arquivo .db com as demandas e pareceres.\n"
                "Crie um banco novo na primeira utilização ou abra um banco existente."
            ),
            font=Fonts.BODY,
            text_color=Colors.TEXT_MUTED,
            justify="left",
        ).pack(anchor="w", pady=(6, 18))

        self.lbl_erro = ctk.CTkLabel(
            inner,
            text=mensagem or "",
            font=Fonts.BODY,
            text_color=Colors.ERRO_FG,
            justify="left",
            wraplength=520,
        )
        if mensagem:
            self.lbl_erro.pack(anchor="w", pady=(0, 14))

        botoes = ctk.CTkFrame(inner, fg_color="transparent")
        botoes.pack(fill="x")

        self.btn_novo = ctk.CTkButton(
            botoes,
            text="Criar novo banco...",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color=Colors.TEXT_ON_ACCENT,
            height=36,
            width=190,
            corner_radius=7,
            command=self._escolher_novo,
        )
        self.btn_novo.pack(side="left", padx=(0, 10))

        self.btn_existente = ctk.CTkButton(
            botoes,
            text="Abrir banco existente...",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            height=36,
            width=190,
            corner_radius=7,
            command=self._escolher_existente,
        )
        self.btn_existente.pack(side="left", padx=(0, 10))

        if pode_voltar:
            ctk.CTkButton(
                botoes,
                text="Cancelar",
                font=Fonts.BODY,
                fg_color="transparent",
                hover_color=Colors.BG_BTN_SEC_HOVER,
                text_color=Colors.TEXT_MUTED,
                height=36,
                width=100,
                corner_radius=7,
                command=self.app.mostrar_principal,
            ).pack(side="left")

    def mostrar_erro(self, mensagem: str) -> None:
        self.lbl_erro.configure(text=mensagem)
        if not self.lbl_erro.winfo_ismapped():
            self.lbl_erro.pack(anchor="w", pady=(0, 14), before=self.btn_novo.master)

    def _escolher_novo(self):
        caminho = filedialog.asksaveasfilename(
            title="Criar novo banco de dados",
            defaultextension=".db",
            initialfile="assessoria_juridica.db",
            filetypes=TIPOS_DB,
            confirmoverwrite=False,
        )
        if caminho:
            self.app.usar_novo_banco(caminho)

    def _escolher_existente(self):
        caminho = filedialog.askopenfilename(title="Abrir banco de dados", filetypes=TIPOS_DB)
        if caminho:
            self.app.usar_banco_existente(caminho)
