"""
Formulário genérico exibido no painel da direita, sem nova janela (RS012, NR002).

RS017: campos obrigatórios vazios ficam destacados e "Salvar" só é
habilitado quando todos estão preenchidos e as datas são válidas. Os erros
devolvidos pelos serviços (ValidacaoError) aparecem no campo correspondente;
se o banco estiver ocupado, o formulário continua preenchido.
"""
from dataclasses import dataclass, field
from typing import Any, Callable

import customtkinter as ctk

from src.services import ServicoError, ValidacaoError
from src.ui.formatos import ROTULOS_CAMPOS
from src.ui.theme import Colors, Fonts
from src.ui.widgets import (
    Campo, CampoBooleano, CampoCor, CampoData, CampoOpcoes, CampoPasta, CampoTexto, CampoTextoLongo, botao,
)

TIPOS = {
    "texto": CampoTexto,
    "data": CampoData,
    "longo": CampoTextoLongo,
    "opcoes": CampoOpcoes,
    "booleano": CampoBooleano,
    "pasta": CampoPasta,
    "cor": CampoCor,
}


@dataclass
class Especificacao:
    nome: str
    tipo: str = "texto"
    obrigatorio: bool = False
    rotulo: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)


class FormularioView(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        titulo: str,
        linhas: list[list[Especificacao]],
        ao_salvar: Callable[[dict[str, Any]], None],
        ao_cancelar: Callable[[], None],
        valores: dict[str, Any] | None = None,
        texto_salvar: str = "Salvar",
    ):
        super().__init__(parent, fg_color="transparent")
        self.ao_salvar = ao_salvar
        self.campos: dict[str, Campo] = {}

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(topo, text=titulo, font=Fonts.SUBTITLE, text_color=Colors.TEXT_MAIN).pack(side="left")
        self.btn_salvar = botao(topo, texto_salvar, self.salvar, tipo="primario", width=120)
        self.btn_salvar.pack(side="right")
        botao(topo, "Cancelar", ao_cancelar, width=90).pack(side="right", padx=(0, 8))

        # A mensagem (erro geral ou banco ocupado) só ocupa espaço quando existe.
        area_mensagem = ctk.CTkFrame(self, fg_color="transparent", height=1)
        area_mensagem.pack(fill="x", padx=16)
        self.lbl_mensagem = ctk.CTkLabel(
            area_mensagem, text="", font=Fonts.BODY, text_color=Colors.ERRO_FG,
            anchor="w", justify="left", wraplength=640,
        )

        corpo = ctk.CTkScrollableFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for linha in linhas:
            moldura = ctk.CTkFrame(corpo, fg_color="transparent")
            moldura.pack(fill="x", padx=8, pady=(0, 2))
            for coluna, espec in enumerate(linha):
                moldura.grid_columnconfigure(coluna, weight=1, uniform="campos")
                campo = TIPOS[espec.tipo](
                    moldura,
                    espec.rotulo or ROTULOS_CAMPOS.get(espec.nome, espec.nome),
                    obrigatorio=espec.obrigatorio,
                    ao_mudar=self.atualizar_estado,
                    **espec.extras,
                )
                campo.grid(row=0, column=coluna, sticky="ew", padx=(0 if coluna == 0 else 6, 0))
                self.campos[espec.nome] = campo

        for nome, valor in (valores or {}).items():
            if nome in self.campos:
                self.campos[nome].definir(valor)
        self.atualizar_estado()

    def atualizar_estado(self) -> None:
        pronto = True
        for campo in self.campos.values():
            campo.atualizar_destaque()
            if campo.erro_local():
                pronto = False
        # Desabilitado fica cinza: azul fica reservado ao botão de ação disponível (RS013).
        self.btn_salvar.configure(
            state="normal" if pronto else "disabled",
            fg_color=Colors.ACCENT_BLUE if pronto else Colors.BG_BTN_SEC,
        )

    def dados(self) -> dict[str, Any]:
        return {nome: campo.valor() for nome, campo in self.campos.items()}

    def mostrar_mensagem(self, texto: str) -> None:
        self.lbl_mensagem.configure(text=texto)
        if texto:
            self.lbl_mensagem.pack(fill="x", pady=(0, 4))
        else:
            self.lbl_mensagem.pack_forget()

    def salvar(self) -> None:
        self.atualizar_estado()
        if self.btn_salvar.cget("state") == "disabled":
            return
        self.mostrar_mensagem("")
        try:
            self.ao_salvar(self.dados())
        except ValidacaoError as erro:
            gerais = []
            for nome, mensagem in erro.erros.items():
                if nome in self.campos:
                    self.campos[nome].mostrar_erro_externo(mensagem)
                else:
                    gerais.append(mensagem)
            self.mostrar_mensagem(" ".join(gerais) or "Corrija os campos destacados.")
        except ServicoError as erro:
            # Inclui BancoOcupadoError: nada foi gravado e o formulário continua preenchido.
            self.mostrar_mensagem(str(erro))
