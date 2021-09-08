from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty
from cxwidgets.aQt.QtWidgets import QLabel
import pycx4.qcda as cda
from .common_mixin import CommonMixin

class CXIntLabel(QLabel, CommonMixin):
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        super().__init__(parent, **kwargs)
        if self.chan is None:
            self.setText('No cname')

    def cs_update(self, chan):
        super().cs_update(chan)
        self.setText(str(chan.val))


class CXDoubleLabel(QLabel, CommonMixin):
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        super().__init__(parent, **kwargs)
        if self.chan is None:
            self.setText('No cname')
        self._decimals = 0 # init stored
        self.decimals = 3 # default value

    def cs_update(self, chan):
        super().cs_update(chan)
        self.setText(format(chan.val, self.format_spec))

    def cx_connect(self):
        if self._cname is None or self._cname == '':
            return
        self.chan = cda.DChan(self._cname, private=True)
        self.chan.valueChanged.connect(self.cs_update)
        self.chan.resolve.connect(self.resolve_proc)

    @pyqtSlot(int)
    def setDecimals(self, n: int):
        self._decimals = n
        self.format_spec = '.' + str(self._decimals) + 'f'

    def getDecimals(self) -> int:
        return self._decimals

    decimals = pyqtProperty(int, getDecimals, setDecimals)


class CXStrLabel(QLabel, CommonMixin):
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        self._max_len = kwargs.get('max_len', 100)
        super().__init__(parent)

    def cx_connect(self):
        if self._cname is None or self._cname == '':
            return
        self.chan = cda.StrChan(self._cname, private=True, max_nelems=self._max_len, on_update=True)
        self.chan.valueChanged.connect(self.cs_update)
        self.chan.resolve.connect(self.resolve_proc)

    def cs_update(self, chan):
        super().cs_update(chan)
        self.setText(str(chan.val))

    @pyqtSlot(float)
    def set_max_len(self, max_len):
        self._max_len = max_len
        self.cx_connect()

    def get_max_len(self):
        return self._max_len

    max_len = pyqtProperty(int, get_max_len, set_max_len)

