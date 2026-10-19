"""
Janela principal em abas (RS012): cada aba tem a lista de resultados à
esquerda e o painel de detalhes à direita, na mesma janela.

Esqueleto da sessão 3: a lista, a pesquisa e o painel de detalhes são
preenchidos nas sessões 4 e 5.
"""
import customtkinter as ctk

from src.ui.theme import Colors, Fonts

ABAS = (("demandas", "Demandas"), ("pareceres", "Pareceres"))
MAX_CARACTERES_CAMINHO = 60


def encurtar_meio(texto: str, maximo: int = MAX_CARACTERES_CAMINHO) -> str:
    """Encurta caminhos longos mantendo o início e o nome do arquivo."""
    if len(texto) <= maximo:
        return texto
    metade = (maximo - 1) // 2
    return f"{texto[:metade]}…{texto[-(maximo - 1 - metade):]}"


class PrincipalView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.botoes_aba: dict[str, ctk.CTkButton] = {}
        self.abas: dict[str, AbaView] = {}
        self.aba_ativa: str | None = None

        self._build_header()
        self.conteudo = ctk.CTkFrame(self, fg_color=Colors.BG_APP, corner_radius=0)
        self.conteudo.pack(fill="both", expand=True, padx=16, pady=12)

        self.abas["demandas"] = AbaView(self.conteudo, titulo_lista="DEMANDAS CADASTRADAS", servico=app.servicos.demandas)
        self.abas["pareceres"] = AbaView(self.conteudo, titulo_lista="PARECERES CADASTRADOS", servico=app.servicos.pareceres)
        self.mostrar_aba("demandas")

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            corner_radius=0,
            height=56,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
        )
        header.pack(fill="x", side="top")

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=10)

        ctk.CTkLabel(
            inner,
            text="ASSESSORIA JURÍDICA IFC",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_MAIN,
        ).pack(side="left", padx=(0, 20))

        tabs_frame = ctk.CTkFrame(
            inner,
            fg_color=Colors.BG_HEADER,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
            corner_radius=8,
        )
        tabs_frame.pack(side="left")

        for chave, rotulo in ABAS:
            botao = ctk.CTkButton(
                tabs_frame,
                text=rotulo,
                font=Fonts.BODY,
                fg_color="transparent",
                text_color=Colors.TEXT_MUTED,
                hover_color=Colors.BG_BTN_SEC_HOVER,
                corner_radius=6,
                height=32,
                width=120,
                command=lambda chave=chave: self.mostrar_aba(chave),
            )
            botao.pack(side="left", padx=3, pady=3)
            self.botoes_aba[chave] = botao

        ctk.CTkButton(
            inner,
            text="Trocar banco...",
            font=Fonts.SMALL,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            height=30,
            width=120,
            corner_radius=6,
            command=self.app.mostrar_configuracao,
        ).pack(side="right")

        self.lbl_banco = ctk.CTkLabel(
            inner,
            text=f"Banco: {encurtar_meio(str(self.app.servicos.caminho_db))}",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_MUTED,
        )
        self.lbl_banco.pack(side="right", padx=(0, 12))

    def mostrar_aba(self, chave: str) -> None:
        if self.aba_ativa:
            self.abas[self.aba_ativa].pack_forget()
        self.aba_ativa = chave
        self.abas[chave].pack(fill="both", expand=True)
        self.abas[chave].atualizar()
        for outra, botao in self.botoes_aba.items():
            ativa = outra == chave
            botao.configure(
                fg_color=Colors.BG_INPUT if ativa else "transparent",
                text_color=Colors.TEXT_MAIN if ativa else Colors.TEXT_MUTED,
                font=Fonts.BODY_BOLD if ativa else Fonts.BODY,
            )


class AbaView(ctk.CTkFrame):
    """Lista à esquerda e painel de detalhes à direita (RS012)."""

    def __init__(self, parent, titulo_lista: str, servico):
        super().__init__(parent, fg_color="transparent")
        self.titulo_lista = titulo_lista
        self.servico = servico

        self.grid_columnconfigure(0, weight=5, uniform="colunas")
        self.grid_columnconfigure(1, weight=6, uniform="colunas")
        self.grid_rowconfigure(0, weight=1)

        self.lista = _cartao(self)
        self.lista.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.lbl_lista = ctk.CTkLabel(
            self.lista, text="", font=Fonts.SECTION_HEADER, text_color=Colors.TEXT_MUTED
        )
        self.lbl_lista.pack(anchor="w", padx=14, pady=(12, 6))

        self.detalhes = _cartao(self)
        self.detalhes.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(
            self.detalhes,
            text="Selecione um item na lista para ver os detalhes.",
            font=Fonts.BODY,
            text_color=Colors.TEXT_MUTED,
        ).place(relx=0.5, rely=0.5, anchor="center")

    def atualizar(self) -> None:
        self.lbl_lista.configure(text=f"{self.titulo_lista} ({len(self.servico.listar())})")


def _cartao(parent) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=Colors.BG_CARD,
        border_color=Colors.BORDER_SUBTLE,
        border_width=1,
        corner_radius=8,
    )
