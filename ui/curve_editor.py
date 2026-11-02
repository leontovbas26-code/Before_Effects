import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QPointF


class CurveEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 250)
        self.mode = 0
        self.points = [QPointF(50, 200), QPointF(550, 50)]
        self.handle1 = QPointF(150, 100)
        self.dragged_item = None

    def set_mode(self, mode_id):
        self.mode = mode_id
        self.points = [QPointF(50, 200), QPointF(550, 50)]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#09090d"))

        # Сетка панели кривых
        pen_grid = QPen(QColor("#1f1f2e"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen_grid)
        for i in range(1, 6):
            y = self.height() // 6 * i
            painter.drawLine(0, y, self.width(), y)
            x = self.width() // 6 * i
            painter.drawLine(x, 0, x, self.height())

        if self.mode == 0:
            self.draw_points_mode(painter)
        else:
            self.draw_handles_mode(painter)

    def draw_points_mode(self, painter):
        pen_line = QPen(QColor("#9d4edd"), 3)
        painter.setPen(pen_line)
        path = QPainterPath()
        path.moveTo(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        painter.drawPath(path)

        painter.setPen(QPen(QColor("#00f5d4"), 2))
        painter.setBrush(QBrush(QColor("#09090d")))
        for p in self.points:
            painter.drawEllipse(p, 6, 6)

    def draw_handles_mode(self, painter):
        p1, p2 = self.points[0], self.points[1]
        painter.setPen(QPen(QColor("#ff007f"), 1))
        painter.drawLine(p1, self.handle1)

        painter.setPen(QPen(QColor("#ff007f"), 2))
        painter.setBrush(QBrush(QColor("#ff007f")))
        painter.drawEllipse(self.handle1, 4, 4)

        path = QPainterPath()
        path.moveTo(p1)
        path.cubicTo(self.handle1, p2, p2)

        painter.setPen(QPen(QColor("#9d4edd"), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        painter.setPen(QPen(QColor("#00f5d4"), 2))
        painter.setBrush(QBrush(QColor("#09090d")))
        painter.drawEllipse(p1, 6, 6)
        painter.drawEllipse(p2, 6, 6)

    def mousePressEvent(self, event):
        pos = event.position()
        if self.mode == 0:
            for i, p in enumerate(self.points):
                if (p - pos).manhattanLength() < 10:
                    self.dragged_item = ("point", i)
                    return
            new_point = QPointF(pos.x(), pos.y())
            self.points.append(new_point)
            self.points.sort(key=lambda p: p.x())
            self.update()
        elif self.mode == 1:
            if (self.handle1 - pos).manhattanLength() < 10:
                self.dragged_item = ("handle", 1)

    def mouseMoveEvent(self, event):
        if not self.dragged_item:
            return
        pos = event.position()
        type_, index = self.dragged_item

        if type_ == "point":
            self.points[index] = QPointF(pos.x(), pos.y())
            # Безопасный вызов обновления кадра напрямую через рендерер
            if hasattr(self, 'parent_window') and self.parent_window:
                self.parent_window.render_frame(self.parent_window.current_frame)
        elif type_ == "handle":
            self.handle1 = QPointF(pos.x(), pos.y())
            if hasattr(self, 'parent_window') and self.parent_window:
                self.parent_window.render_frame(self.parent_window.current_frame)

        self.update()

    def mouseReleaseEvent(self, event):
        self.dragged_item = None

    # --- ВОТ ЭТА ФУНКЦИЯ, КОТОРОЙ НЕ ХВАТАЛО ---
    def get_value_at_percent(self, percent):
        """Супер-безопасный расчет высоты кривой для анимации"""
        if not self.points or len(self.points) < 2:
            return 150.0

        sorted_pts = sorted(self.points, key=lambda p: p.x())
        start_x = sorted_pts[0].x()
        end_x = sorted_pts[-1].x()
        width = end_x - start_x

        if width <= 0:
            return sorted_pts[0].y()

        target_x = start_x + width * (percent / 100.0)

        if target_x <= start_x:
            return sorted_pts[0].y()
        if target_x >= end_x:
            return sorted_pts[-1].y()

        for i in range(len(sorted_pts) - 1):
            p1 = sorted_pts[i]
            p2 = sorted_pts[i + 1]
            if p1.x() <= target_x <= p2.x():
                segment_w = p2.x() - p1.x()
                if segment_w <= 0:
                    return p1.y()
                t = (target_x - p1.x()) / segment_w
                return p1.y() + t * (p2.y() - p1.y())

        return 150.0
