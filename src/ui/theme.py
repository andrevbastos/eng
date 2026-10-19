"""
Tema escuro e constantes visuais (RS013, RU007, RNF002).

RS013: contraste mínimo de 4,5:1 entre texto e fundo; cores além dos tons de
cinza só em tags, alertas de prazo e botões de ação. Os pares texto/fundo
usados na interface ficam em PARES_DE_CONTRASTE e são verificados nos testes.
"""
import customtkinter as ctk

CONTRASTE_MINIMO = 4.5
LARGURA_MINIMA = 1366
ALTURA_MINIMA = 768


def aplicar_tema() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


class Colors:
    # Tons de cinza (fundos e texto).
    BG_APP = "#1A1D21"
    BG_HEADER = "#13161A"
    BG_CARD = "#181B20"
    BG_CARD_HOVER = "#20242B"
    BG_INPUT = "#252930"
    BG_BTN_SEC = "#2E333B"
    BG_BTN_SEC_HOVER = "#363B44"

    TEXT_MAIN = "#D9E1E8"
    TEXT_MUTED = "#A3ACB7"
    TEXT_ON_ACCENT = "#FFFFFF"

    BORDER = "#2A2E35"
    BORDER_SUBTLE = "#23262C"

    # Botões de ação.
    ACCENT_BLUE = "#2563EB"
    ACCENT_BLUE_HOVER = "#1D4ED8"
    DANGER = "#B91C1C"
    DANGER_HOVER = "#991B1B"

    # Alertas de prazo (RS019): até 5 dias em amarelo; vencida em vermelho.
    PRAZO_PROXIMO_BG = "#3A3112"
    PRAZO_PROXIMO_FG = "#FACC15"
    PRAZO_VENCIDO_BG = "#3F1D1D"
    PRAZO_VENCIDO_FG = "#F87171"

    # Campo obrigatório vazio ou inválido (RS017).
    ERRO_FG = "#FCA5A5"


class Fonts:
    MAIN_FAMILY = "Segoe UI"

    TITLE = (MAIN_FAMILY, 18, "bold")
    SUBTITLE = (MAIN_FAMILY, 14, "bold")
    SECTION_HEADER = (MAIN_FAMILY, 11, "bold")
    BODY = (MAIN_FAMILY, 12, "normal")
    BODY_BOLD = (MAIN_FAMILY, 12, "bold")
    SMALL = (MAIN_FAMILY, 11, "normal")
    BADGE = (MAIN_FAMILY, 10, "bold")


_FUNDOS_NEUTROS = (
    Colors.BG_APP, Colors.BG_HEADER, Colors.BG_CARD, Colors.BG_CARD_HOVER,
    Colors.BG_INPUT, Colors.BG_BTN_SEC, Colors.BG_BTN_SEC_HOVER,
)

# (texto, fundo) de cada combinação usada na interface.
PARES_DE_CONTRASTE = (
    *[(Colors.TEXT_MAIN, fundo) for fundo in _FUNDOS_NEUTROS],
    *[(Colors.TEXT_MUTED, fundo) for fundo in _FUNDOS_NEUTROS],
    *[(Colors.ERRO_FG, fundo) for fundo in _FUNDOS_NEUTROS],
    (Colors.TEXT_ON_ACCENT, Colors.ACCENT_BLUE),
    (Colors.TEXT_ON_ACCENT, Colors.ACCENT_BLUE_HOVER),
    (Colors.TEXT_ON_ACCENT, Colors.DANGER),
    (Colors.TEXT_ON_ACCENT, Colors.DANGER_HOVER),
    (Colors.PRAZO_PROXIMO_FG, Colors.PRAZO_PROXIMO_BG),
    (Colors.PRAZO_VENCIDO_FG, Colors.PRAZO_VENCIDO_BG),
)


def luminancia(cor: str) -> float:
    """Luminância relativa (WCAG 2.x) de uma cor #RRGGBB."""
    canais = [int(cor.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lineares = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lineares[0] + 0.7152 * lineares[1] + 0.0722 * lineares[2]


def contraste(cor_a: str, cor_b: str) -> float:
    clara, escura = sorted((luminancia(cor_a), luminancia(cor_b)), reverse=True)
    return (clara + 0.05) / (escura + 0.05)


def texto_sobre(cor_fundo: str) -> str:
    """Cor de texto (branco ou preto) mais legível sobre a cor de uma tag.

    Com branco e preto puros, o melhor dos dois sempre atinge ao menos 4,58:1.
    """
    escuro = "#000000"
    if contraste(Colors.TEXT_ON_ACCENT, cor_fundo) >= contraste(escuro, cor_fundo):
        return Colors.TEXT_ON_ACCENT
    return escuro
