from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty, Qt
import pycx4.qcda as cda
from .pdoublespinbox import PDoubleSpinBox
from .menus.doublespinbox_cm import CXDoubleSpinboxCM
from .common_mixin import CommonMixin

class CXDoubleSpinBox(PDoubleSpinBox, CommonMixin):
    """Inherit: QDoubleSpinbox -> PDoubleSpinbox -> CXDoubleSpinBox.
       It is a double spinbox connected to CX channel.
       Gives some CX info and widget settings control over context menu.
       CX Channel created with data type corresponding to double.
       CX Channel is privately created in order to avoid any interference.

       When value set - it's send to CX (set considered by done signal of PDoubleSpinbox).
       When CX updates value - it's set to spinbox value.

       attributes:
           cname - cx channel name. When changed

    """
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        super().__init__(parent, **kwargs)
        self.done.connect(self.cs_send)
        self.context_menu = None
        self._hardmin = 0
        self._hardmax = 0


    def contextMenuEvent(self, event):
        self.context_menu = CXDoubleSpinboxCM(self)
        self.context_menu.popup(event.globalPos())

    def cx_connect(self):
        if self._cname is None or self._cname == '':
            return
        self.chan = cda.DChan(self._cname, private=True, get_curval=True)
        self.chan.valueChanged.connect(self.cs_update)
        self.chan.resolve.connect(self.resolve_proc)

    @pyqtSlot(float)
    def cs_send(self, value):
        if self.chan is None:
            return
        if value != self.chan.val:
            self.chan.setValue(value)

    def cs_update(self, chan):
        super().cs_update(chan)
        if self.value() != chan.val:
            self.setValue(chan.val)

    @pyqtSlot(float)
    def set_hardmin(self, value):
        self._hardmin = value

    def get_hardmin(self):
        return self._hardmin

    hardmin = pyqtProperty(float, get_hardmin, set_hardmin)

    @pyqtSlot(float)
    def set_hardmax(self, value):
        self._hardmax = value

    def get_hardmax(self):
        return self._hardmax

    hardmax = pyqtProperty(float, get_hardmax, set_hardmax)

