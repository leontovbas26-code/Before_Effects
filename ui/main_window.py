from PyQt6.QtWidgets import QMainWindow, QDockWidget, QTextEdit, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.curve_editor import CurveEditor

class BeforeEffectsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Before Effects - Open Source Motion Design")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setDockOptions(QMainWindow.DockOption.AllowNestedDocks | QMainWindow.DockOption.AllowTabbedDocks)
        
        # Окно просмотра (Вьювер)
        self.viewer = QWidget()
        viewer_layout = QVBoxLayout()
        viewer_label = QLabel("🎬 Composition Viewer")
        viewer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        viewer_layout.addWidget(viewer_label)
        self.viewer.setLayout(viewer_layout)
        self.setCentralWidget(self.viewer)
        
        # Панели интерфейса
        self.project_dock = QDockWidget("📁 Project Files", self)
        self.project_dock.setWidget(QTextEdit("Список файлов:\n- logo.png\n- intro.mp4"))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)
        
        self.curve_dock = QDockWidget("📈 Curve Editor (Интерполяция)", self)
        self.curve_editor_widget = CurveEditor()
        self.curve_dock.setWidget(self.curve_editor_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.curve_dock)
        
        self.inspector_dock = QDockWidget("⚙️ Inspector", self)
        self.inspector_dock.setWidget(QTextEdit("Свойства слоя:\n- Position\n- Scale"))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)
        
        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0d0d12; }
            QDockWidget { color: #a5a5b5; font-weight: bold; }
            QDockWidget::title { background-color: #161622; padding: 6px; border-bottom: 2px solid #252538; }
            QTextEdit, QWidget { background-color: #09090d; color: #e2e2e8; border: 1px solid #1f1f2e; }
            QLabel { color: #9d4edd; font-size: 18px; font-weight: bold; border: none; }
        """)
