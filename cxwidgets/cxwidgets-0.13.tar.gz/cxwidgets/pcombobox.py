from cxwidgets.aQt.QtWidgets import QComboBox
from cxwidgets.aQt.QtCore import pyqtSignal

class PComboBox(QComboBox):

    done = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentIndexChanged.connect(self.done)
        self.cs_name = None
        self.val_list = None

    def setValue(self, val):
        if self.val_list:
            ind = self.val_list.index(val)
            self.setCurrentIndex(ind)
        else:
            self.setCurrentIndex(val)

    def value(self):
        return self.currentIndex()
