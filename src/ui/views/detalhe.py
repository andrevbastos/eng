"""
Blocos do painel de detalhes (RS012, RF010, RF014): todos os dados de um
registro na mesma tela, com rolagem vertical.
"""
from pathlib import Path
from typing import Callable

import customtkinter as ctk

from src.ui.formatos import data_hora_br, descrever_alteracao
from src.ui.theme import Colors, Fonts
from src.ui.widgets import badge, botao, chip_tag, titulo_secao

LARGURA_TEXTO = 620
VAZIO = "—"


class DetalheBase(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

    def cabecalho(
        self,
        titulo: str,
        meta: str,
        etiquetas: list[str],
        ao_editar: Callable,
        ao_excluir: Callable,
    ) -> None:
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=10, pady=(10, 4))
        acoes = ctk.CTkFrame(topo, fg_color="transparent")
        acoes.pack(side="right", anchor="n")
        botao(acoes, "Editar", ao_editar, width=80).pack(side="left", padx=(0, 6))
        botao(acoes, "Excluir", ao_excluir, tipo="perigo", width=80).pack(side="left")

        textos = ctk.CTkFrame(topo, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            textos, text=titulo, font=Fonts.TITLE, text_color=Colors.TEXT_MAIN,
            anchor="w", justify="left", wraplength=LARGURA_TEXTO - 200,
        ).pack(fill="x")
        ctk.CTkLabel(textos, text=meta, font=Fonts.SMALL, text_color=Colors.TEXT_MUTED, anchor="w").pack(fill="x")
        if etiquetas:
            linha = ctk.CTkFrame(textos, fg_color="transparent")
            linha.pack(fill="x", pady=(6, 0))
            for texto in etiquetas:
                badge(linha, texto).pack(side="left", padx=(0, 6))

    def secao(self, titulo: str, acao: tuple[str, Callable] | None = None) -> ctk.CTkFrame:
        """Sub-painel com título e conteúdo, no estilo dos mockups."""
        caixa = ctk.CTkFrame(self, fg_color=Colors.BG_HEADER, corner_radius=8,
                             border_width=1, border_color=Colors.BORDER_SUBTLE)
        caixa.pack(fill="x", padx=10, pady=6)
        titulo_secao(caixa, titulo, acao).pack(fill="x", padx=12, pady=(10, 6))
        conteudo = ctk.CTkFrame(caixa, fg_color="transparent")
        conteudo.pack(fill="x", padx=12, pady=(0, 10))
        return conteudo

    @staticmethod
    def pares(conteudo, itens: list[tuple[str, str | None]], colunas: int = 2) -> None:
        """Rótulo e valor em grade (numa moldura própria, para não misturar grid e pack)."""
        grade = ctk.CTkFrame(conteudo, fg_color="transparent")
        grade.pack(fill="x")
        for coluna in range(colunas):
            grade.grid_columnconfigure(coluna, weight=1, uniform="pares")
        for indice, (rotulo, valor) in enumerate(itens):
            celula = ctk.CTkFrame(grade, fg_color="transparent")
            celula.grid(row=indice // colunas, column=indice % colunas, sticky="nw", pady=(0, 6), padx=(0, 10))
            ctk.CTkLabel(celula, text=rotulo, font=Fonts.SMALL, text_color=Colors.TEXT_MUTED, anchor="w").pack(fill="x")
            ctk.CTkLabel(
                celula, text=valor or VAZIO, font=Fonts.BODY, text_color=Colors.TEXT_MAIN,
                anchor="w", justify="left", wraplength=LARGURA_TEXTO // colunas - 20,
            ).pack(fill="x")

    @staticmethod
    def texto(conteudo, valor: str | None) -> None:
        ctk.CTkLabel(
            conteudo, text=valor or VAZIO, font=Fonts.BODY, text_color=Colors.TEXT_MAIN,
            anchor="w", justify="left", wraplength=LARGURA_TEXTO,
        ).pack(fill="x")

    @staticmethod
    def tags(conteudo, tags) -> None:
        if not tags:
            DetalheBase.texto(conteudo, "Nenhuma tag.")
            return
        linha = ctk.CTkFrame(conteudo, fg_color="transparent")
        linha.pack(fill="x")
        for tag in sorted(tags, key=lambda t: t.nome.lower()):
            chip_tag(linha, tag.nome, tag.cor).pack(side="left", padx=(0, 6))

    @staticmethod
    def documentos(conteudo, documentos) -> None:
        if not documentos:
            DetalheBase.texto(conteudo, "Nenhum documento anexado.")
            return
        for documento in documentos:
            caixa = ctk.CTkFrame(conteudo, fg_color=Colors.BG_INPUT, corner_radius=6)
            caixa.pack(fill="x", pady=(0, 4))
            ctk.CTkLabel(caixa, text=documento.tipo_arquivo.upper(), font=Fonts.BADGE,
                         text_color=Colors.TEXT_MUTED, width=44).pack(side="left", padx=(8, 4), pady=6)
            caminho = Path(documento.caminho_arquivo)
            ctk.CTkLabel(caixa, text=caminho.name, font=Fonts.BODY, text_color=Colors.TEXT_MAIN,
                         anchor="w").pack(side="left")
            ctk.CTkLabel(caixa, text=str(caminho.parent), font=Fonts.SMALL, text_color=Colors.TEXT_MUTED,
                         anchor="w").pack(side="left", padx=(10, 8), fill="x", expand=True)

    @staticmethod
    def historico(conteudo, tabela: str, itens) -> None:
        if not itens:
            DetalheBase.texto(conteudo, "Sem alterações registradas.")
            return
        for item in itens:
            linha = ctk.CTkFrame(conteudo, fg_color="transparent")
            linha.pack(fill="x", pady=(0, 2))
            ctk.CTkLabel(linha, text=data_hora_br(item.data_hora), font=Fonts.SMALL,
                         text_color=Colors.TEXT_MUTED, width=110, anchor="w").pack(side="left", anchor="n")
            ctk.CTkLabel(
                linha, text=descrever_alteracao(tabela, item), font=Fonts.SMALL, text_color=Colors.TEXT_MAIN,
                anchor="w", justify="left", wraplength=LARGURA_TEXTO - 130,
            ).pack(side="left", fill="x", expand=True)
