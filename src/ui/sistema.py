"""Abertura de arquivos e links pelo sistema operacional (RS020, RF011)."""
import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def abrir_arquivo(caminho: str) -> None:
    """Abre no aplicativo padrão. Levanta FileNotFoundError se o arquivo sumiu."""
    if not Path(caminho).is_file():
        raise FileNotFoundError(caminho)
    if sys.platform == "win32":
        os.startfile(caminho)  # noqa: S606 (só existe no Windows)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", caminho])
    else:
        subprocess.Popen(["xdg-open", caminho])


def abrir_url(url: str) -> None:
    """Abre o link no navegador padrão."""
    webbrowser.open(url)
