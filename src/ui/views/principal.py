"""
Janela principal em abas (RS012): cada aba tem a lista de resultados à
esquerda e o painel de detalhes à direita, na mesma janela.

A aba Tags reúne o cadastro de tags (RF005). Ao abrir, uma faixa abaixo do
cabeçalho mostra o total de demandas próximas do prazo e vencidas (RS019, RF015).
"""
import customtkinter as ctk

from src.services import ServicoError
from src.ui.theme import Colors, Fonts
from src.ui.views.demandas import AbaDemandas
from src.ui.views.pareceres import AbaPareceres
from src.ui.views.tags import TelaTags
from src.ui.widgets import badge_prazo, botao, configurar_estilo_lista

ABAS = (("demandas", "Demandas"), ("pareceres", "Pareceres"), ("tags", "Tags"))
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
        self.abas: dict[str, ctk.CTkFrame] = {}
        self.aba_ativa: str | None = None
        self.alerta_fechado = False

        configurar_estilo_lista(self)
        self._build_header()
        # A faixa de prazos só ocupa espaço quando há o que avisar.
        self.area_alerta = ctk.CTkFrame(self, fg_color="transparent", height=1)
        self.area_alerta.pack(fill="x")
        self.alerta = ctk.CTkFrame(self.area_alerta, fg_color=Colors.BG_HEADER, corner_radius=0)
        self.conteudo = ctk.CTkFrame(self, fg_color=Colors.BG_APP, corner_radius=0)
        self.conteudo.pack(fill="both", expand=True, padx=16, pady=12)

        self.abas["demandas"] = AbaDemandas(self.conteudo, app)
        self.abas["pareceres"] = AbaPareceres(self.conteudo, app)
        self.abas["tags"] = TelaTags(self.conteudo, app)
        # Salvar, editar ou excluir uma demanda atualiza a lista e, com ela, a contagem.
        self.abas["demandas"].ao_atualizar = self.atualizar_alerta
        self.mostrar_aba("demandas")

    # --- Alerta de prazos (RS019, RF015) ------------------------------------------

    def atualizar_alerta(self) -> None:
        for filho in self.alerta.winfo_children():
            filho.destroy()
        try:
            contagem = self.app.servicos.demandas.contar_prazos()
        except ServicoError:
            return
        self.contagem_prazos = contagem
        if self.alerta_fechado or not (contagem.vencidas or contagem.proximas):
            self.alerta.pack_forget()
            return
        interno = ctk.CTkFrame(self.alerta, fg_color="transparent")
        interno.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(interno, text="Prazos:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_MAIN).pack(side="left", padx=(0, 8))
        self.lbl_vencidas = badge_prazo(interno, "vencida", f"{contagem.vencidas} vencida(s)")
        self.lbl_proximas = badge_prazo(interno, "proxima", f"{contagem.proximas} vencendo em até 5 dias")
        self.lbl_vencidas.pack(side="left", padx=(0, 6))
        self.lbl_proximas.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(interno, text="Demandas destacadas na lista com as mesmas cores.", font=Fonts.SMALL,
                     text_color=Colors.TEXT_MUTED).pack(side="left")
        botao(interno, "Fechar", self.fechar_alerta, width=70, height=24, font=Fonts.SMALL).pack(side="right")
        self.alerta.pack(fill="x")

    def fechar_alerta(self) -> None:
        self.alerta_fechado = True
        self.alerta.pack_forget()

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
        self.abas[chave].atualizar_lista()
        for outra, botao in self.botoes_aba.items():
            ativa = outra == chave
            botao.configure(
                fg_color=Colors.BG_INPUT if ativa else "transparent",
                text_color=Colors.TEXT_MAIN if ativa else Colors.TEXT_MUTED,
                font=Fonts.BODY_BOLD if ativa else Fonts.BODY,
            )
