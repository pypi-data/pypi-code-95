from cxwidgets.aQt.QtWidgets import QLineEdit
from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty
import pycx4.qcda as cda
from .common_mixin import CommonMixin

class CXLineEdit(QLineEdit, CommonMixin):
    def __init__(self, *args, **kwargs):
        self._cname = None
        self._max_len = kwargs.get('max_len', 100)
        super().__init__(*args, **kwargs)
        self.setReadOnly(bool(kwargs.get('readonly', False)))

    def cx_connect(self):
        if self._cname is None or self._cname == '':
            return
        self.chan = cda.StrChan(self._cname, max_nelems=self._max_len, private=True, on_update=True)
        self.chan.valueChanged.connect(self.cs_update)

    def cs_update(self, chan):
        super().cs_update(chan)
        if self.text() != chan.val:
            self.setText(chan.val)

    @pyqtSlot(str)
    def cs_send(self, value):
        self.chan.setValue(value)

    def set_max_len(self, ml):
        if self._max_len == ml:
            return
        self._max_len = ml
        self.cx_connect()

    def get_max_len(self):
        return self._max_len

    max_len = pyqtProperty(int, get_max_len, set_max_len)

