"""
Componentes reutilizáveis da interface: campos de formulário (RS017),
cabeçalhos de seção, chips de tag e o estilo escuro da lista (RS013).
"""
from tkinter import filedialog, ttk
from typing import Any, Callable

import customtkinter as ctk

from src.ui.formatos import data_br, ler_data_br
from src.ui.theme import Colors, Fonts, texto_sobre

OBRIGATORIO = "Campo obrigatório."
DATA_INVALIDA = "Data inválida. Use DD/MM/AAAA."


class Campo(ctk.CTkFrame):
    """Rótulo + entrada + mensagem de erro.

    valor() devolve o valor já convertido; levanta ValueError se o texto for
    inválido. Campos obrigatórios vazios ficam com a borda destacada (RS017).
    """

    def __init__(self, parent, rotulo: str, obrigatorio: bool = False, ao_mudar: Callable | None = None):
        super().__init__(parent, fg_color="transparent")
        self.obrigatorio = obrigatorio
        self.ao_mudar = ao_mudar
        self._erro_externo: str | None = None

        ctk.CTkLabel(
            self,
            text=f"{rotulo} *" if obrigatorio else rotulo,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x")
        self.widget = self._criar_widget()
        self.widget.pack(fill="x", pady=(2, 0))
        self.lbl_erro = ctk.CTkLabel(self, text="", font=Fonts.SMALL, text_color=Colors.ERRO_FG, anchor="w", height=16)
        self.lbl_erro.pack(fill="x")

    # --- A implementar pelos tipos de campo ----------------------------------

    def _criar_widget(self):
        raise NotImplementedError

    def texto(self) -> str:
        raise NotImplementedError

    def definir(self, valor: Any) -> None:
        raise NotImplementedError

    def valor(self) -> Any:
        return self.texto().strip() or None

    def _pintar_borda(self, cor: str) -> None:
        self.widget.configure(border_color=cor)

    # --- Estado de validação ------------------------------------------------

    def erro_local(self) -> str | None:
        """Erro detectável sem consultar os serviços: obrigatório vazio ou formato."""
        try:
            valor = self.valor()
        except ValueError:
            return DATA_INVALIDA
        if self.obrigatorio and valor is None:
            return OBRIGATORIO
        return None

    def mostrar_erro_externo(self, mensagem: str | None) -> None:
        """Erro devolvido pelos serviços (ValidacaoError)."""
        self._erro_externo = mensagem
        self.atualizar_destaque()

    def atualizar_destaque(self) -> None:
        local = self.erro_local()
        # A mensagem "obrigatório" fica só no destaque da borda, para não poluir o formulário vazio.
        mensagem = self._erro_externo or (local if local and local != OBRIGATORIO else "")
        self.lbl_erro.configure(text=mensagem)
        self._pintar_borda(Colors.ERRO_FG if (local or self._erro_externo) else Colors.BORDER)

    def _mudou(self, *_):
        self._erro_externo = None
        self.atualizar_destaque()
        if self.ao_mudar:
            self.ao_mudar()


class Entrada(ctk.CTkEntry):
    """Entrada de uma linha que avisa quando o texto muda.

    Não usa textvariable: com ela, o CustomTkinter não mostra o placeholder.
    """

    def __init__(self, parent, ao_mudar: Callable | None = None, **kwargs):
        opcoes = dict(
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_MAIN,
            placeholder_text_color=Colors.TEXT_MUTED,
            height=32,
        )
        opcoes.update(kwargs)
        super().__init__(parent, **opcoes)
        self.ao_mudar = ao_mudar
        self._ultimo = ""
        self.bind("<KeyRelease>", lambda _e: self._verificar())
        for evento in ("<<Paste>>", "<<Cut>>"):
            self.bind(evento, lambda _e: self.after_idle(self._verificar))

    def texto(self) -> str:
        return self.get()

    def definir(self, texto: str) -> None:
        self.delete(0, "end")
        if texto:
            self.insert(0, texto)
        elif self.focus_get() is not self._entry:
            # O CustomTkinter só devolve o placeholder ao perder o foco; aqui o foco já está fora.
            self._activate_placeholder()
        self._verificar()

    def _verificar(self) -> None:
        atual = self.get()
        if atual != self._ultimo:
            self._ultimo = atual
            if self.ao_mudar:
                self.ao_mudar()


class CampoTexto(Campo):
    placeholder = ""

    def _criar_widget(self):
        self.entrada = Entrada(self, ao_mudar=self._mudou, placeholder_text=self.placeholder or None)
        return self.entrada

    def texto(self) -> str:
        return self.entrada.texto()

    def definir(self, valor: Any) -> None:
        self.entrada.definir("" if valor is None else str(valor))


class CampoData(CampoTexto):
    placeholder = "DD/MM/AAAA"

    def valor(self):
        return ler_data_br(self.texto())

    def definir(self, valor: Any) -> None:
        self.entrada.definir(data_br(valor))


class CampoTextoLongo(Campo):
    def __init__(self, parent, rotulo: str, altura: int = 72, **kwargs):
        self.altura = altura
        super().__init__(parent, rotulo, **kwargs)

    def _criar_widget(self):
        caixa = ctk.CTkTextbox(
            self,
            height=self.altura,
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            border_width=2,
            text_color=Colors.TEXT_MAIN,
            wrap="word",
        )
        caixa.bind("<KeyRelease>", self._mudou)
        caixa.bind("<<Paste>>", lambda _e: self.after_idle(self._mudou))
        return caixa

    def texto(self) -> str:
        return self.widget.get("1.0", "end-1c")

    def definir(self, valor: Any) -> None:
        self.widget.delete("1.0", "end")
        if valor:
            self.widget.insert("1.0", str(valor))
        self._mudou()


class CampoOpcoes(Campo):
    def __init__(self, parent, rotulo: str, opcoes: tuple[str, ...], **kwargs):
        self.opcoes = opcoes
        super().__init__(parent, rotulo, **kwargs)

    def _criar_widget(self):
        combo = ctk.CTkComboBox(
            self,
            values=list(self.opcoes),
            state="readonly",
            font=Fonts.BODY,
            dropdown_font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            button_color=Colors.BG_BTN_SEC,
            button_hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            dropdown_fg_color=Colors.BG_INPUT,
            dropdown_text_color=Colors.TEXT_MAIN,
            dropdown_hover_color=Colors.BG_BTN_SEC_HOVER,
            height=32,
            command=self._mudou,
        )
        combo.set("")
        return combo

    def texto(self) -> str:
        return self.widget.get()

    def definir(self, valor: Any) -> None:
        self.widget.set(valor or "")
        self._mudou()


class CampoBooleano(Campo):
    def __init__(self, parent, rotulo: str, texto_opcao: str, **kwargs):
        self.texto_opcao = texto_opcao
        super().__init__(parent, rotulo, **kwargs)

    def _criar_widget(self):
        self.var = ctk.BooleanVar(value=False)
        return ctk.CTkCheckBox(
            self,
            text=self.texto_opcao,
            variable=self.var,
            font=Fonts.BODY,
            text_color=Colors.TEXT_MAIN,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            command=self._mudou,
        )

    def texto(self) -> str:
        return ""

    def valor(self) -> bool:
        return self.var.get()

    def definir(self, valor: Any) -> None:
        self.var.set(bool(valor))

    def _pintar_borda(self, cor: str) -> None:
        pass


class CampoPasta(CampoTexto):
    """Texto com botão para escolher uma pasta local (caminho_pasta)."""

    def _criar_widget(self):
        linha = ctk.CTkFrame(self, fg_color="transparent")
        self.entrada = Entrada(linha, ao_mudar=self._mudou)
        self.entrada.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            linha,
            text="Procurar pasta...",
            font=Fonts.BODY,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            width=130,
            height=32,
            command=self._procurar,
        ).pack(side="right")
        return linha

    def _pintar_borda(self, cor: str) -> None:
        self.entrada.configure(border_color=cor)

    def _procurar(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta local dos documentos")
        if pasta:
            self.entrada.definir(pasta)


# --- Filtros da pesquisa (RF007) ------------------------------------------------

class FiltroOpcoes(ctk.CTkComboBox):
    """Lista de opções com uma primeira opção "todos", que remove o filtro."""

    def __init__(self, parent, todos: str, opcoes: dict[str, Any], ao_mudar: Callable, width: int = 140):
        self.todos = todos
        self.mapa: dict[str, Any] = {}
        super().__init__(
            parent,
            values=[todos],
            state="readonly",
            width=width,
            height=30,
            font=Fonts.SMALL,
            dropdown_font=Fonts.SMALL,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            button_color=Colors.BG_BTN_SEC,
            button_hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            dropdown_fg_color=Colors.BG_INPUT,
            dropdown_text_color=Colors.TEXT_MAIN,
            dropdown_hover_color=Colors.BG_BTN_SEC_HOVER,
            command=lambda _valor: ao_mudar(),
        )
        self.definir_opcoes(opcoes)
        self.set(todos)

    def definir_opcoes(self, opcoes: dict[str, Any]) -> None:
        """Troca as opções sem avisar; se a escolhida sumiu (ex.: tag excluída), volta a "todos"."""
        self.mapa = dict(opcoes)
        self.configure(values=[self.todos, *self.mapa])
        if self.get() not in self.mapa:
            self.set(self.todos)

    def valor(self) -> Any:
        return self.mapa.get(self.get())

    def escolher(self, rotulo: str) -> None:
        self.set(rotulo)
        self._command(rotulo)

    def ativo(self) -> bool:
        return self.get() != self.todos

    def limpar(self) -> None:
        self.set(self.todos)


class FiltroData(Entrada):
    """Data DD/MM/AAAA opcional; inválida fica com a borda destacada e não filtra."""

    def __init__(self, parent, ao_mudar: Callable, width: int = 100):
        super().__init__(parent, ao_mudar=lambda: self._mudou(ao_mudar), placeholder_text="DD/MM/AAAA",
                         width=width, height=30, font=Fonts.SMALL)

    def _mudou(self, ao_mudar: Callable) -> None:
        self.configure(border_color=Colors.ERRO_FG if self.invalida() else Colors.BORDER)
        ao_mudar()

    def valor(self):
        """Levanta ValueError se o texto não for uma data válida."""
        return ler_data_br(self.texto())

    def invalida(self) -> bool:
        try:
            self.valor()
        except ValueError:
            return True
        return False

    def ativo(self) -> bool:
        return bool(self.texto().strip())

    def limpar(self) -> None:
        self.definir("")


# --- Elementos de exibição ----------------------------------------------------

def botao(parent, texto: str, comando: Callable, tipo: str = "secundario", **kwargs) -> ctk.CTkButton:
    """Botões de ação: primário (azul), perigo (vermelho) ou secundário (cinza)."""
    cores = {
        "primario": (Colors.ACCENT_BLUE, Colors.ACCENT_BLUE_HOVER, Colors.TEXT_ON_ACCENT),
        "perigo": (Colors.DANGER, Colors.DANGER_HOVER, Colors.TEXT_ON_ACCENT),
        "secundario": (Colors.BG_BTN_SEC, Colors.BG_BTN_SEC_HOVER, Colors.TEXT_MAIN),
    }[tipo]
    opcoes = dict(
        text=texto,
        command=comando,
        font=Fonts.BODY_BOLD if tipo == "primario" else Fonts.BODY,
        fg_color=cores[0],
        hover_color=cores[1],
        text_color=cores[2],
        text_color_disabled=Colors.TEXT_MUTED,
        height=30,
        corner_radius=6,
    )
    opcoes.update(kwargs)
    return ctk.CTkButton(parent, **opcoes)


def titulo_secao(parent, texto: str, acao: tuple[str, Callable] | None = None) -> ctk.CTkFrame:
    linha = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(linha, text=texto.upper(), font=Fonts.SECTION_HEADER, text_color=Colors.TEXT_MUTED).pack(side="left")
    if acao:
        botao(linha, acao[0], acao[1], height=24, width=90, font=Fonts.SMALL).pack(side="right")
    return linha


def chip_tag(parent, nome: str, cor: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=f" {nome} ",
        font=Fonts.BADGE,
        fg_color=cor,
        text_color=texto_sobre(cor),
        corner_radius=8,
        height=20,
    )


def badge(parent, texto: str) -> ctk.CTkLabel:
    """Status em cinza: cores ficam reservadas a tags, prazos e botões (RS013)."""
    return ctk.CTkLabel(
        parent,
        text=f"  {texto}  ",
        font=Fonts.BADGE,
        fg_color=Colors.BG_BTN_SEC,
        text_color=Colors.TEXT_MAIN,
        corner_radius=8,
        height=22,
    )


ESTILO_LISTA = "Lista.Treeview"


def _fonte_tk(fonte: tuple) -> tuple:
    """O CustomTkinter mede fontes em pixels; o Tk puro, em pontos. Tamanho negativo = pixels."""
    familia, tamanho, *resto = fonte
    return (familia, -abs(tamanho), *resto)


def configurar_estilo_lista(raiz) -> None:
    """Treeview no tema escuro (a lista de resultados, RS012)."""
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure(
        ESTILO_LISTA,
        background=Colors.BG_CARD,
        fieldbackground=Colors.BG_CARD,
        foreground=Colors.TEXT_MAIN,
        bordercolor=Colors.BORDER_SUBTLE,
        borderwidth=0,
        rowheight=28,
        font=_fonte_tk(Fonts.BODY),
    )
    estilo.map(
        ESTILO_LISTA,
        background=[("selected", Colors.BG_BTN_SEC_HOVER)],
        foreground=[("selected", Colors.TEXT_MAIN)],
    )
    estilo.configure(
        f"{ESTILO_LISTA}.Heading",
        background=Colors.BG_HEADER,
        foreground=Colors.TEXT_MUTED,
        bordercolor=Colors.BORDER_SUBTLE,
        relief="flat",
        font=_fonte_tk(Fonts.SECTION_HEADER),
        padding=(6, 6),
    )
    estilo.map(f"{ESTILO_LISTA}.Heading", background=[("active", Colors.BG_BTN_SEC)])
    estilo.layout(ESTILO_LISTA, [("Treeview.treearea", {"sticky": "nswe"})])
