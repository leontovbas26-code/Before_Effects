from PyQt6.QtWidgets import (QMainWindow, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton,
                             QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QToolBar, QInputDialog,
                             QFileDialog)
from PyQt6.QtCore import Qt, QTimer, QPointF
import json


class BeforeEffectsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Before Effects 2024 - Untitled Project.bep")
        self.setGeometry(50, 50, 1400, 850)
        self.setDockOptions(QMainWindow.DockOption.AllowNestedDocks | QMainWindow.DockOption.AllowTabbedDocks)

        mb = self.menuBar()
        file_menu = mb.addMenu("File")
        new_menu = file_menu.addMenu("New")
        new_menu.addAction("New Project").triggered.connect(self.file_new_project)

        open_proj_act = file_menu.addAction("Open Project...")
        open_proj_act.setShortcut("Ctrl+O")
        open_proj_act.triggered.connect(self.file_load_project)

        file_menu.addAction("Open Team Project...")
        open_recent_menu = file_menu.addMenu("Open Recent")
        open_recent_menu.addAction("None")
        file_menu.addAction("Browse in Bridge...").setShortcut("Ctrl+Alt+Shift+O")
        file_menu.addSeparator()

        file_menu.addAction("Close").setShortcut("Ctrl+W")
        file_menu.addAction("Close Project")

        save_act = file_menu.addAction("Save")
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.file_save_project)

        file_menu.addMenu("Save As").addAction("Save As...")
        file_menu.addAction("Increment and Save").setShortcut("Ctrl+Alt+Shift+S")
        file_menu.addAction("Revert")
        file_menu.addSeparator()

        file_menu.addMenu("Import").addAction("File...")
        file_menu.addMenu("Import Recent Footage")
        file_menu.addMenu("Export").addAction("Add to Adobe Render Queue")
        file_menu.addSeparator()

        file_menu.addMenu("Adobe Dynamic Link")
        file_menu.addAction("Find").setShortcut("Ctrl+F")
        file_menu.addAction("Add Footage to Comp").setShortcut("Ctrl+/")
        file_menu.addAction("New Comp from Selection...").setShortcut("Alt+\\")
        file_menu.addSeparator()

        file_menu.addMenu("Dependencies")
        file_menu.addAction("Watch Folder...")
        file_menu.addMenu("Scripts").addAction("Run Script File...")
        file_menu.addSeparator()

        file_menu.addAction("Project Settings...").setShortcut("Ctrl+Alt+Shift+K")
        # Замени старую строчку Exit на этот блок:
        exit_act = file_menu.addAction("Exit")
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)

        for name in ["Edit", "Composition", "Layer", "Effect", "Animation", "View", "Window", "Help"]:
            mb.addMenu(name)

        self.create_ae_toolbar()

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

        self.right_dock = QDockWidget("Effects & Preview", self)
        rw = QListWidget()
        rw.addItems(["🔎 Search Help", "▶ Preview Controls", "📐 Align", "🔊 Audio", "✨ Effects & Presets"])
        self.right_dock.setWidget(rw)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

        self.timeline_dock = QDockWidget("Timeline: Comp 1", self)
        tmw = QWidget()
        tl = QHBoxLayout()
        tl.setContentsMargins(0, 0, 0, 0)

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

        from ui.curve_editor import CurveEditor
        self.curve_editor_widget = CurveEditor()
        self.curve_editor_widget.parent_window = self
        rtl.addWidget(self.curve_editor_widget, stretch=1)
        rtc.setLayout(rtl)

        tl.addWidget(self.layer_table)
        tl.addWidget(rtc, stretch=1)
        tmw.setLayout(tl)
        self.timeline_dock.setWidget(tmw)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_dock)

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
        for icon in ["🏠", "⬈", "✋", "🔍"]: tb.addAction(icon)
        tb.addSeparator()
        for icon in ["⟳", "🎥"]: tb.addAction(icon)
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
        if not hasattr(self, 'curve_editor_widget') or not self.curve_editor_widget.points: return
        cy = self.curve_editor_widget.get_value_at_percent(fv)
        tx = max(10, min(300, 20 + int(fv * 2.8)))
        ty = max(10, min(580, int(cy + 100)))
        self.animated_box.move(tx, ty)

    def file_new_project(self):
        self.current_frame = 0
        self.time_slider.setValue(0)
        self.layer_table.setRowCount(0)
        self.animated_box.setText("Be")
        self.animated_box.setStyleSheet("background-color:#9d4edd; color:white; font-weight:bold; border-radius:6px;")
        self.animated_box.setFixedSize(50, 50)
        self.animated_box.move(155, 300)
        if hasattr(self, 'curve_editor_widget'):
            self.curve_editor_widget.points = [QPointF(50, 200), QPointF(550, 50)]
            self.curve_editor_widget.update()

    def file_save_project(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "Before Effects Project (*.bep)")
        if not file_path: return
        layers_data = []
        for row in range(self.layer_table.rowCount()):
            layers_data.append({
                "row_num": self.layer_table.item(row, 1).text() if self.layer_table.item(row, 1) else str(row + 1),
                "name": self.layer_table.item(row, 2).text() if self.layer_table.item(row, 2) else "Layer"
            })
        points_data = []
        if hasattr(self, 'curve_editor_widget') and self.curve_editor_widget.points:
            points_data = [{"x": pt.x(), "y": pt.y()} for pt in self.curve_editor_widget.points]
        project_struct = {
            "current_frame": self.current_frame,
            "layers": layers_data,
            "curve_points": points_data,
            "box_text": self.animated_box.text()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project_struct, f, indent=4, ensure_ascii=False)

    def file_load_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "Before Effects Project (*.bep)")
        if not file_path: return
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.file_new_project()
        self.layer_table.setRowCount(0)
        for row, l_info in enumerate(data.get("layers", [])):
            self.layer_table.insertRow(row)
            self.layer_table.setItem(row, 0, QTableWidgetItem("  ⚫"))
            self.layer_table.setItem(row, 1, QTableWidgetItem(l_info["row_num"]))
            self.layer_table.setItem(row, 2, QTableWidgetItem(l_info["name"]))
        self.current_frame = data.get("current_frame", 0)
        self.time_slider.setValue(self.current_frame)
        self.animated_box.setText(data.get("box_text", "Be"))
        self.animated_box.adjustSize()
        if hasattr(self, 'curve_editor_widget') and "curve_points" in data:
            parsed_pts = [QPointF(pt["x"], pt["y"]) for pt in data["curve_points"]]
            if parsed_pts:
                self.curve_editor_widget.points = parsed_pts
                self.curve_editor_widget.update()
        self.render_frame(self.current_frame)

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