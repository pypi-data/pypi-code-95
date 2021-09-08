from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty
from cxwidgets import PCheckBox
from .common_mixin import CommonMixin


class CXCheckBox(PCheckBox, CommonMixin):
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        super().__init__(parent, **kwargs)
        self.done.connect(self.cs_send)

    @pyqtSlot(bool)
    def cs_send(self, value):
        if int(value) == self.chan.val:
            return
        self.chan.setValue(value)

    def cs_update(self, chan):
        super().cs_update(chan)
        self.setValue(bool(chan.val))



