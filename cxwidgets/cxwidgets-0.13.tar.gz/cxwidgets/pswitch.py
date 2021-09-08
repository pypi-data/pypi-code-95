from PyQt5.QtWidgets import QPushButton, QSizePolicy
from PyQt5.QtGui import QBrush, QPen, QColor, QPainter
from PyQt5.QtCore import Qt, QRect, pyqtSignal, pyqtSlot, pyqtProperty


class PSwitch(QPushButton):
    done = pyqtSignal(bool)
    value = pyqtProperty(bool, QPushButton.isChecked)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCheckable(True)
        self.setMinimumWidth(36)
        self.setMinimumHeight(18)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)
        self.a_ratio = 2.2
        self.toggled.connect(self.done)

    @pyqtSlot(bool)
    def setValue(self, value):
        self.setChecked(value)

    def heightForWidth(self, width):
        return width / self.a_ratio

    def paintEvent(self, event):
        bg_color = Qt.green if self.isChecked() else Qt.red
        pen_width = 2
        s = self.size()
        w0 = s.width()
        h0 = s.height()

        w = w0 - 2*pen_width - 2
        h = w/2 if w/2 < h0 - 2*pen_width else h0 - 2*pen_width
        r = h/3

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.rect().center())
        painter.setBrush(QColor(130, 140, 160))

        pen = QPen(QColor(40, 40, 70))
        pen.setWidth(pen_width)
        painter.setPen(pen)
        painter.drawRoundedRect(QRect(-w/2, -h/2, w, h), r, r)

        painter.setBrush(QBrush(bg_color))
        sw_rect = QRect(-w/2, -h/2, h, h)
        if self.isChecked():
            sw_rect.moveLeft(w/2 - h)
        painter.drawRoundedRect(sw_rect, r, r)

