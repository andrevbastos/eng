"""Exceções que a camada de serviços entrega à interface."""


class ServicoError(Exception):
    """Base das exceções de serviço; a mensagem é exibível ao usuário."""


class ValidacaoError(ServicoError):
    """Dados recusados (RS017). `erros` mapeia campo -> mensagem, para destacar na tela."""

    def __init__(self, erros: dict[str, str]):
        self.erros = erros
        super().__init__("; ".join(f"{campo}: {msg}" for campo, msg in erros.items()))


class NaoEncontradoError(ServicoError):
    def __init__(self, tabela: str, registro_id: int):
        self.tabela = tabela
        self.registro_id = registro_id
        super().__init__(f"Registro {registro_id} não encontrado em {tabela}.")


class BancoOcupadoError(ServicoError):
    """O arquivo .db continuou bloqueado após a espera; nada foi gravado."""

    def __init__(self):
        super().__init__(
            "O banco de dados está ocupado por outro programa. "
            "Nada foi salvo; tente novamente em instantes."
        )
