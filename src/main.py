"""
Main entry point for Assessoria Jurídica IFC application.
Launches the CustomTkinter UI.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.app import App

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
