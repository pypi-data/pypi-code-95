from cxwidgets.aQt.QtCore import Qt, pyqtSignal, pyqtProperty
from cxwidgets.aQt.QtWidgets import QDoubleSpinBox


class PDoubleSpinBox(QDoubleSpinBox):
    done = pyqtSignal(float)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        # = kwargs.get("doneByEnter")

        self.valueChanged.connect(self.done)
        self.setRange(kwargs.get('min', -100000.0), kwargs.get('max', 100000.0))

        self.setFocusPolicy(Qt.StrongFocus)

        self._doneByEnter = False

    def wheelEvent(self, event):
        #print("focus", self.hasFocus())
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()

    def focusInEvent(self, event):
        self.setFocusPolicy(Qt.WheelFocus)
        self.update()

    def focusOutEvent(self, event):
        self.setFocusPolicy(Qt.StrongFocus)
        self.update()

    @pyqtProperty(bool)
    def doneByEnter(self):
        return self._doneByEnter

    @doneByEnter.setter
    def doneByEnter(self, value):
        if self._doneByEnter == value:
            return
        if value:
            self.valueChanged.disconnect(self.done)
        else:
            self.valueChanged.disconnect(self.done)
        self._doneByEnter = value

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and self._doneByEnter:
            self.done.emit(self.value())
        super().keyPressEvent(event)




