"""Тестовый запуск ReferencesView."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication  # noqa: E402

from src.views.references.references_view import ReferencesView  # noqa: E402


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReferencesView()
    window.setWindowTitle("Test References")
    window.setGeometry(100, 100, 1200, 800)
    window.show()
    sys.exit(app.exec_())
