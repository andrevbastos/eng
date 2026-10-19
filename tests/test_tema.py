"""Tema escuro: RS013 (contraste mínimo 4,5:1), RU007."""
import pytest

from src.ui.theme import CONTRASTE_MINIMO, PARES_DE_CONTRASTE, contraste, texto_sobre


def test_formula_de_contraste_wcag():
    assert contraste("#FFFFFF", "#000000") == pytest.approx(21.0)
    assert contraste("#777777", "#777777") == pytest.approx(1.0)


@pytest.mark.parametrize("texto, fundo", PARES_DE_CONTRASTE)
def test_rs013_pares_de_texto_e_fundo(texto, fundo):
    assert contraste(texto, fundo) >= CONTRASTE_MINIMO


@pytest.mark.parametrize("cor_tag", [f"#{r:02X}{g:02X}{b:02X}"
                                     for r in range(0, 256, 51)
                                     for g in range(0, 256, 51)
                                     for b in range(0, 256, 51)])
def test_rs013_texto_legivel_sobre_qualquer_cor_de_tag(cor_tag):
    assert contraste(texto_sobre(cor_tag), cor_tag) >= CONTRASTE_MINIMO


def test_encurtar_caminho_longo_do_banco():
    from src.ui.views.principal import encurtar_meio

    caminho = r"\\servidor-ifc\assessoria-juridica\bancos\2026\demandas e pareceres\assessoria.db"
    curto = encurtar_meio(caminho, 40)
    assert len(curto) == 40
    assert curto.startswith(r"\\servidor") and curto.endswith("assessoria.db")
    assert encurtar_meio("C:/a.db", 40) == "C:/a.db"
