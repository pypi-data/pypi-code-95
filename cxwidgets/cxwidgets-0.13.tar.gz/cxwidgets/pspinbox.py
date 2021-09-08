from cxwidgets.aQt.QtWidgets import QSpinBox
from cxwidgets.aQt.QtCore import pyqtSignal, Qt, pyqtProperty

class PSpinBox(QSpinBox):
    done = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        self._cname = None
        super().__init__(*args, **kwargs)
        self.valueChanged.connect(self.done)
        self.setRange(kwargs.get('min', -100000), kwargs.get('max', 100000))
        self._doneByEnter = False

    def wheelEvent(self, event):
        if self.hasFocus():
            super(PSpinBox, self).wheelEvent(event)
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
