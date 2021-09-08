from cxwidgets.aQt.QtCore import QTimer, Qt, QSize, pyqtSlot, pyqtProperty
from cxwidgets.aQt.QtGui import QColor, QPainter, QRadialGradient, QBrush
from cxwidgets.aQt.QtWidgets import QWidget


class LedWidget(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._diamX, self._diamY, self._diameter = 0, 0, 20
        self._on_color = QColor("red")
        self._off_color = self._on_color.darker(250)
        self._alignment = Qt.AlignCenter
        self._state = False
        self._timer = QTimer()
        self._timer.timeout.connect(self.toggleState)
        self.setDiameter(self._diameter)

    def paintEvent(self, event):
        d = self._diameter
        r = d / 2
        painter = QPainter()
        x = 0
        y = 0
        if self._alignment & Qt.AlignLeft:
            x = 0
        elif self._alignment & Qt.AlignRight:
            x = self.width() - d
        elif self._alignment & Qt.AlignHCenter:
            x = (self.width() - d) / 2
        elif self._alignment & Qt.AlignJustify:
            x = 0

        if self._alignment & Qt.AlignTop:
            y = 0
        elif self._alignment & Qt.AlignBottom:
            y = self.height() - d
        elif self._alignment & Qt.AlignVCenter:
            y = (self.height() - d) / 2

        color = self._on_color if self._state else self._off_color

        gradient = QRadialGradient(x + r, y + r, d * 0.4, d * 0.4, d * 0.4)
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, color)

        painter.begin(self)
        brush = QBrush(gradient)
        painter.setPen(color)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(brush)
        painter.drawEllipse(x, y, d - 1, d - 1)
        painter.end()

    def minimumSizeHint(self):
        return QSize(self._diameter, self._diameter)

    def sizeHint(self):
        return QSize(self._diameter + 1, self._diameter + 1)

    def getDiameter(self):
        return self._diameter

    @pyqtSlot(int)
    def setDiameter(self, value):
        self._diameter = value
        self.update()

    def getOnColor(self):
        return self._on_color

    @pyqtSlot(QColor)
    def setOnColor(self, value):
        self._on_color = value
        self.update()

    def getOffColor(self):
        return self._off_color

    @pyqtSlot(QColor)
    def setOffColor(self, value):
        self._off_color = value
        self.update()

    def getAlignment(self):
        return self._alignment

    @pyqtSlot(Qt.Alignment)
    def setAlignment(self, value):
        self._alignment = value
        self.update()

    def getState(self):
        return self._state

    @pyqtSlot(bool)
    def setState(self, value):
        self._state = value
        self.update()

    def getValue(self):
        return self._state

    @pyqtSlot(bool)
    def setValue(self, value):
        self._state = value
        self.update()

    @pyqtSlot()
    def toggleState(self):
        self._state = not self._state
        self.update()

    def flashOnce(self):
        self.toggleState()
        self._timer.singleShot(200, self.toggleState)

    diameter = pyqtProperty(int, getDiameter, setDiameter)
    on_color = pyqtProperty(QColor, getOnColor, setOnColor)
    off_color = pyqtProperty(QColor, getOffColor, setOffColor)
    alignment = pyqtProperty(Qt.Alignment, getAlignment, setAlignment)
    state = pyqtProperty(bool, getState, setState)
    value = pyqtProperty(bool, getValue, setValue)

