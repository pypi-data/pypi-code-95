from cxwidgets.aQt.QtWidgets import QPushButton
from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty
import pycx4.qcda as cda
from .common_mixin import CommonMixin


class CXPushButton(QPushButton, CommonMixin):
    def __init__(self, *args, **kwargs):
        self._cname = None
        super().__init__(*args, **kwargs)
        self.clicked.connect(self.cs_send)

    @pyqtSlot()
    def cs_send(self):
        if self.chan is None:
            return
        self.chan.setValue(1)


