from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty
from .pspinbox import PSpinBox
from .menus.spinbox_cm import CXSpinboxCM
from .common_mixin import CommonMixin
import pycx4.qcda as cda


class CXSpinBox(PSpinBox, CommonMixin):
    def __init__(self, *args, **kwargs):
        self._cname = None
        super().__init__(*args, **kwargs)
        self.done.connect(self.cs_send)
        self._hardmin = 0
        self._hardmax = 0

    def contextMenuEvent(self, event):
        self.context_menu = CXSpinboxCM(self)
        self.context_menu.popup(event.globalPos())

    @pyqtSlot(int)
    def cs_send(self, value):
        if self.chan is None:
            return
        if value != self.chan.val:
            self.chan.setValue(value)

    def cs_update(self, chan):
        super().cs_update(chan)
        if self.value() != chan.val:
            self.setValue(chan.val)

    @pyqtSlot(int)
    def set_hardmin(self, value):
        self._hardmin = value

    def get_hardmin(self):
        return self._hardmin

    hardmin = pyqtProperty(int, get_hardmin, set_hardmin)

    @pyqtSlot(int)
    def set_hardmax(self, value):
        self._hardmax = value

    def get_hardmax(self):
        return self._hardmax

    hardmax = pyqtProperty(int, get_hardmax, set_hardmax)
