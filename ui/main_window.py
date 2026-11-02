from PyQt6.QtWidgets import (QMainWindow, QDockWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSlider, QPushButton,
                             QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QToolBar, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
from ui.curve_editor import CurveEditor


class BeforeEffectsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Before Effects 2024 - Untitled Project.bfe")
        self.setGeometry(50, 50, 1400, 850)
        self.setDockOptions(QMainWindow.DockOption.AllowNestedDocks | QMainWindow.DockOption.AllowTabbedDocks)

        # --- ВЕРХНЕЕ ТЕКСТОВОЕ МЕНЮ ---
        mb = self.menuBar()
        for name in ["File", "Edit", "Composition", "Layer", "Effect", "Animation", "View", "Window", "Help"]:
            mb.addMenu(name)

        # --- ВЕРХНЯЯ ПАНЕЛЬ ИНСТРУМЕНТОВ ---
        self.create_ae_toolbar()

        # --- ЦЕНТРАЛЬНЫЙ ЭКРАН (ВЬЮВЕР) ---
        self.central_widget = QWidget()
        cl = QVBoxLayout()
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.canvas = QWidget()
        self.canvas.setFixedSize(360, 640)
        self.canvas.setStyleSheet("background-color:#000000; border:1px solid #3a3a3a;")

        self.animated_box = QLabel("Be", self.canvas)
        self.animated_box.setFixedSize(50, 50)
        self.animated_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.animated_box.setStyleSheet("background-color:#9d4edd; color:white; font-weight:bold; border-radius:6px;")
        self.animated_box.move(155, 300)

        cl.addWidget(self.canvas)
        self.central_widget.setLayout(cl)
        self.setCentralWidget(self.central_widget)
        # --- ПАНЕЛЬ ПРОЕКТА (СЛЕВА) ---
        self.project_dock = QDockWidget("Project", self)
        pw = QWidget()
        pl = QVBoxLayout()
        il = QLabel("Comp 1\n1080 x 1920 (1.00)\nA 0:00:10:00, 59.94 fps")
        il.setStyleSheet("color:#8a8a9d; font-size:11px;")
        self.media_list = QListWidget()
        self.media_list.addItem("🎬 Comp 1 (Composition)")
        pl.addWidget(il)
        pl.addWidget(self.media_list)
        pw.setLayout(pl)
        self.project_dock.setWidget(pw)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)

        # --- ПАНЕЛЬ ЭФФЕКТОВ (СПРАВА) ---
        self.right_dock = QDockWidget("Effects & Preview", self)
        rw = QListWidget()
        rw.addItems(["🔎 Search Help", "▶ Preview Controls", "📐 Align", "🔊 Audio", "✨ Effects & Presets"])
        self.right_dock.setWidget(rw)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

        # --- ТАЙМЛАЙН (СНИЗУ) ---
        self.timeline_dock = QDockWidget("Timeline: Comp 1", self)
        tmw = QWidget()
        tl = QHBoxLayout()
        tl.setContentsMargins(0, 0, 0, 0)

        # Список слоев слева в таймлайне
        self.layer_table = QTableWidget(2, 3)
        self.layer_table.setHorizontalHeaderLabels(["👁", "#", "Source Name"])
        self.layer_table.verticalHeader().setVisible(False)
        self.layer_table.setFixedWidth(350)
        self.layer_table.setStyleSheet("background-color:#141416; color:#cfcfd6; border:none;")
        self.layer_table.setItem(0, 0, QTableWidgetItem("  ⚫"))
        self.layer_table.setItem(0, 1, QTableWidgetItem("1"))
        self.layer_table.setItem(0, 2, QTableWidgetItem("🔤 Text Layer"))
        self.layer_table.setItem(1, 0, QTableWidgetItem("  ⚫"))
        self.layer_table.setItem(1, 1, QTableWidgetItem("2"))
        self.layer_table.setItem(1, 2, QTableWidgetItem("🟩 Shape Layer"))
        self.layer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Шкала и график справа в таймлайне
        rtc = QWidget()
        rtl = QVBoxLayout()
        rtl.setContentsMargins(0, 0, 0, 0)
        tcl = QHBoxLayout()
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedWidth(40)
        self.play_btn.clicked.connect(self.toggle_play)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.sliderMoved.connect(self.time_changed)

        tcl.addWidget(self.play_btn)
        tcl.addWidget(self.time_slider)
        rtl.addLayout(tcl)

        self.curve_editor_widget = CurveEditor()
        self.curve_editor_widget.parent_window = self
        rtl.addWidget(self.curve_editor_widget, stretch=1)
        rtc.setLayout(rtl)

        tl.addWidget(self.layer_table)
        tl.addWidget(rtc, stretch=1)
        tmw.setLayout(tl)
        self.timeline_dock.setWidget(tmw)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_dock)

        # Переменные плеера
        self.current_frame = 0
        self.is_playing = False
        self.playback_timer = QTimer()
        self.playback_timer.setInterval(16)
        self.playback_timer.timeout.connect(self.next_frame)

        self.apply_style()
        self.showMaximized()

    def create_ae_toolbar(self):
        tb = QToolBar("AE Toolbar", self)
        tb.setMovable(False)
        tb.setStyleSheet("background-color:#222226; border-bottom:1px solid #141416; spacing:10px; padding:4px;")
        self.addToolBar(tb)

        for icon in ["🏠", "⬈", "✋", "🔍"]:
            tb.addAction(icon)
        tb.addSeparator()
        for icon in ["⟳", "🎥"]:
            tb.addAction(icon)
        tb.addSeparator()

        bs = tb.addAction("🟩")
        tb.addAction("✒️")
        bt = tb.addAction("📝")

        bt.triggered.connect(self.toolbar_add_text)
        bs.triggered.connect(self.toolbar_add_shape)

    def toolbar_add_text(self):
        t, ok = QInputDialog.getText(self, "Type Tool", "Текст слоя:")
        if ok and t:
            r = self.layer_table.rowCount()
            self.layer_table.insertRow(r)
            self.layer_table.setItem(r, 0, QTableWidgetItem("  ⚫"))
            self.layer_table.setItem(r, 1, QTableWidgetItem(str(r + 1)))
            self.layer_table.setItem(r, 2, QTableWidgetItem(f"🔤 {t}"))
            self.animated_box.setText(t)
            self.animated_box.adjustSize()

    def toolbar_add_shape(self):
        r = self.layer_table.rowCount()
        self.layer_table.insertRow(r)
        self.layer_table.setItem(r, 0, QTableWidgetItem("  ⚫"))
        self.layer_table.setItem(r, 1, QTableWidgetItem(str(r + 1)))
        self.layer_table.setItem(r, 2, QTableWidgetItem("🟩 New Shape"))
        self.animated_box.setText("")
        self.animated_box.setStyleSheet("background-color:#9d4edd; border-radius:6px;")
        self.animated_box.setFixedSize(60, 60)

    def toggle_play(self):
        if self.is_playing:
            self.playback_timer.stop()
            self.play_btn.setText("▶")
        else:
            if self.current_frame >= 100: self.current_frame = 0
            self.playback_timer.start()
            self.play_btn.setText("⏸")
        self.is_playing = not self.is_playing

    def next_frame(self):
        if self.current_frame < 100:
            self.current_frame += 1
            self.time_slider.blockSignals(True)
            self.time_slider.setValue(self.current_frame)
            self.time_slider.blockSignals(False)
            self.render_frame(self.current_frame)
        else:
            self.toggle_play()

    def time_changed(self, v):
        self.current_frame = v
        self.render_frame(v)

    def render_frame(self, fv):
        if not hasattr(self, 'curve_editor_widget') or not self.curve_editor_widget.points:
            return
        cy = self.curve_editor_widget.get_value_at_percent(fv)
        tx = max(10, min(300, 20 + int(fv * 2.8)))
        ty = max(10, min(580, int(cy + 100)))
        self.animated_box.move(tx, ty)

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1c1c1f; }
            QMenuBar { background-color: #1c1c1f; color: #cfcfd6; font-size: 12px; border-bottom: 1px solid #141416; }
            QMenuBar::item { background-color: transparent; padding: 4px 8px; }
            QMenuBar::item:selected { background-color: #28282c; color: #ffffff; }
            QMenu { background-color: #1c1c1f; color: #cfcfd6; border: 1px solid #141416; }
            QDockWidget { color: #cfcfd6; font-weight: bold; font-size: 12px; }
            QDockWidget::title { background-color: #28282c; padding: 6px; border-bottom: 1px solid #141416; }
            QListWidget, QTableWidget, QWidget { background-color: #141416; color: #cfcfd6; border: 1px solid #28282c; }
            QHeaderView::section { background-color: #28282c; color: #cfcfd6; border: 1px solid #141416; font-size: 11px; }
            QSlider::handle:horizontal { background: #9d4edd; border-radius: 4px; }
            QPushButton { background-color: #3e3e45; color: #cfcfd6; border-radius: 3px; padding: 4px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #52525b; }
            QLabel { color: #cfcfd6; border: none; }
        """)
