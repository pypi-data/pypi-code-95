from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty
from cxwidgets import PSwitch
import pycx4.qcda as cda
from .menus.general_cm import CXGeneralCM
from .common_mixin import CommonMixin

class CXSwitch(PSwitch, CommonMixin):
    def __init__(self, *args, **kwargs):
        self._cname = None
        super().__init__(*args, **kwargs)
        self._invert = kwargs.get('invert', False)
        self.done.connect(self.cs_send)

    def setInvert(self, inv):
        self._invert = inv

    def isInvert(self):
        return self._invert

    invert = pyqtProperty(bool, isInvert, setInvert)

    @pyqtSlot(bool)
    def cs_send(self, value):
        v = not bool(value) if self.invert else bool(value)
        if int(v) == self.chan.val:
            return
        self.chan.setValue(v)

    def cs_update(self, chan):
        super().cs_update(chan)
        v = not bool(chan.val) if self.invert else bool(chan.val)
        self.setValue(v)


class CXDevSwitch(PSwitch):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.state_chan, self.off_chan, self.on_chan = None, None, None
        self._devname = kwargs.get('devname', None)
        self.cx_connect()
        self.done.connect(self.cs_send)

    def cx_connect(self):
        if self._devname is None:
            return
        self.state_chan = cda.IChan(self._devname + '.is_on', private=True, on_update=True)
        self.on_chan = cda.IChan(self._devname + '.switch_on', private=True, on_update=True)
        self.off_chan = cda.IChan(self._devname + '.switch_off', private=True, on_update=True)
        self.state_chan.valueChanged.connect(self.cs_update)

    @pyqtSlot(bool)
    def cs_send(self, value):
        if int(value) == self.state_chan.val:
            return
        if value:
            self.on_chan.setValue(1)
        else:
            self.off_chan.setValue(1)

    def cs_update(self, chan):
        self.setValue(bool(chan.val))

    @pyqtSlot(str)
    def set_devname(self, devname):
        if self._devname == devname:
            return
        self._devname = devname
        self.cx_connect()

    def get_devname(self):
        return self._devname

    devname = pyqtProperty(str, get_devname, set_devname)
