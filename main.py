"""
Entry point de teste para abrir a interface CustomTkinter.

Uso, a partir do diretório eng/:
    uv run main.py
"""
from src.ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
