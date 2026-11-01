import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import BeforeEffectsApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BeforeEffectsApp()
    window.show()
    sys.exit(app.exec())
