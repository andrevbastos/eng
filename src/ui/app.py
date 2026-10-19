"""
Janela principal da Assessoria Jurídica IFC.

Uso único (NR006): abre direto, sem login. Sem banco configurado (RS001),
mostra a escolha do arquivo .db na própria janela (NR002).
"""
import sys
from pathlib import Path

import customtkinter as ctk

from src import config
from src.aplicacao import Servicos, abrir_banco
from src.config import Configuracao, ConfiguracaoError
from src.ui.theme import ALTURA_MINIMA, LARGURA_MINIMA, Colors, aplicar_tema

# A janela cabe numa tela de 1366×768 descontando barra de tarefas e título.
LARGURA_MINIMA_JANELA = 1024
ALTURA_MINIMA_JANELA = 640


class App(ctk.CTk):
    def __init__(self, arquivo_config: Path | None = None):
        aplicar_tema()
        super().__init__()
        self.arquivo_config = arquivo_config
        self.servicos: Servicos | None = None
        self.current_view = None

        self.title("Assessoria Jurídica IFC - Gestão de Demandas & Pareceres")
        self.geometry(f"{LARGURA_MINIMA}x{ALTURA_MINIMA}")
        self.minsize(LARGURA_MINIMA_JANELA, ALTURA_MINIMA_JANELA)
        self.configure(fg_color=Colors.BG_APP)
        if sys.platform == "win32":
            self.after(0, lambda: self.state("zoomed"))
        self.protocol("WM_DELETE_WINDOW", self.fechar)

        self._iniciar()

    def _iniciar(self) -> None:
        caminho = config.carregar(self.arquivo_config).caminho_db
        if caminho is None:
            self.mostrar_configuracao()
            return
        try:
            self._abrir(config.validar_banco_existente(caminho))
        except ConfiguracaoError as erro:
            self.mostrar_configuracao(f"Não foi possível abrir o banco configurado. {erro}")

    # --- Escolha do banco (RS001) --------------------------------------------

    def usar_novo_banco(self, caminho: str | Path) -> None:
        self._trocar_banco(lambda: config.validar_novo_banco(Path(caminho)))

    def usar_banco_existente(self, caminho: str | Path) -> None:
        self._trocar_banco(lambda: config.validar_banco_existente(Path(caminho)))

    def _trocar_banco(self, validar) -> None:
        try:
            caminho = validar()
            anterior = self.servicos
            self._abrir(caminho)
        except ConfiguracaoError as erro:
            self.current_view.mostrar_erro(str(erro))
            return
        if anterior is not None:
            anterior.fechar()

    def _abrir(self, caminho: Path) -> None:
        servicos = abrir_banco(caminho)
        try:
            config.salvar(Configuracao(caminho), self.arquivo_config)
        except ConfiguracaoError:
            servicos.fechar()
            raise
        self.servicos = servicos
        self.mostrar_principal()

    # --- Telas -----------------------------------------------------------------

    def _trocar_tela(self, view) -> None:
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = view
        view.pack(fill="both", expand=True)

    def mostrar_principal(self) -> None:
        from src.ui.views.principal import PrincipalView

        self._trocar_tela(PrincipalView(self, app=self))

    def mostrar_configuracao(self, mensagem: str | None = None) -> None:
        from src.ui.views.configuracao_banco import ConfiguracaoBancoView

        view = ConfiguracaoBancoView(self, app=self, mensagem=mensagem, pode_voltar=self.servicos is not None)
        self._trocar_tela(view)

    def fechar(self) -> None:
        if self.servicos is not None:
            self.servicos.fechar()
        self.destroy()


def main() -> None:
    App().mainloop()
