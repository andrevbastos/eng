"""
Aba Pareceres (RF002, RF010, RF014, RS012, RS017, RD004).
"""
from src.ui.formatos import data_br
from src.ui.views.aba import AbaBase, Coluna
from src.ui.views.detalhe import DetalheBase
from src.ui.views.formulario import Especificacao as E
from src.ui.views.formulario import FormularioView

LINHAS_PARECER = [
    [E("numero", obrigatorio=True, rotulo="Número do parecer"), E("data", "data", obrigatorio=True, rotulo="Data de emissão")],
    [E("assunto", obrigatorio=True)],
    [E("conclusao", "longo", obrigatorio=True, rotulo="Conclusão / fundamentação", extras={"altura": 140})],
    [E("observacoes", "longo", extras={"altura": 80})],
]


class AbaPareceres(AbaBase):
    colunas = [
        Coluna("id", "ID", 50, alinhar="center"),
        Coluna("numero", "Número", 130),
        Coluna("assunto", "Assunto", 260, esticar=True),
        Coluna("data", "Data", 100, alinhar="center"),
    ]
    titulo_lista = "PARECERES"
    texto_novo = "+ Novo parecer"

    def registros(self) -> list:
        return self.servicos.pareceres.listar()

    def valores_linha(self, parecer) -> tuple:
        return (parecer.id, parecer.numero, parecer.assunto, data_br(parecer.data))

    def criar_formulario(self, parecer_id: int | None):
        if parecer_id is None:
            valores, titulo = {}, "Novo parecer"
        else:
            parecer = self.servicos.pareceres.buscar(parecer_id)
            valores = {e.nome: getattr(parecer, e.nome) for linha in LINHAS_PARECER for e in linha}
            titulo = f"Editar parecer {parecer.numero}"

        def salvar(dados):
            if parecer_id is None:
                salvo = self.servicos.pareceres.criar(**dados)
            else:
                salvo = self.servicos.pareceres.editar(parecer_id, **dados)
            self.atualizar_lista(selecionar=salvo.id)
            self.mostrar_detalhe(salvo.id)

        return FormularioView(self.painel, titulo, LINHAS_PARECER, salvar, self.voltar, valores,
                              texto_salvar="Salvar parecer")

    def criar_detalhe(self, parecer_id: int):
        parecer = self.servicos.pareceres.buscar(parecer_id)
        historico = self.servicos.pareceres.listar_historico(parecer_id)
        return DetalheParecer(self.painel, self, parecer, historico)

    def excluir_parecer(self, parecer) -> None:
        n_documentos = len(parecer.documentos)
        aviso = f"Também serão removidos do sistema: {n_documentos} documento(s)." if n_documentos else ""
        self.excluir(self.servicos.pareceres, parecer.id, f"o parecer {parecer.numero}", aviso, n_documentos)


class DetalheParecer(DetalheBase):
    def __init__(self, parent, aba: AbaPareceres, parecer, historico):
        super().__init__(parent)
        self.cabecalho(
            f"Parecer {parecer.numero}",
            f"#{parecer.id} · Emissão {data_br(parecer.data)}",
            [],
            ao_editar=lambda: aba.mostrar_formulario(parecer.id),
            ao_excluir=lambda: aba.excluir_parecer(parecer),
        )
        self.texto(self.secao("Assunto"), parecer.assunto)
        self.texto(self.secao("Conclusão"), parecer.conclusao)
        self.texto(self.secao("Observações"), parecer.observacoes)
        self.tags(self.secao("Tags"), parecer.tags)
        self.documentos(self.secao("Documentos"), parecer.documentos)
        self.historico(self.secao("Histórico de alterações"), "pareceres", historico)
