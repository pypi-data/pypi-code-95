from cxwidgets.aQt.QtWidgets import QComboBox
from cxwidgets.aQt.QtGui import QIcon, QColor
from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty, Qt
import pycx4.qcda as cda
from .common_mixin import CommonMixin

class CXTextComboBox(QComboBox, CommonMixin):
    def __init__(self, *args, **kwargs):
        self._cname = None
        self._values = ['none'] + kwargs.get('values', [])
        self._colors = [None] + kwargs.get('colors', [])
        self._icons = kwargs.get('icons', None)
        self._max_len = kwargs.get('max_len', max([len(x) for x in self._values]))
        super().__init__(*args, **kwargs)

        for x in range(len(self._values)):
            self.insertItem(x, self._values[x])
            if self._icons is not None and x > 0:
                self.setItemIcon(x, QIcon(self._icons[x-1]))
            if x < len(self._colors):
                if self._colors[x] is not None:
                    self.setItemData(x, QColor(self._colors[x]), Qt.BackgroundRole)

        self.model().item(0).setEnabled(False)
        # keep next after all
        self.currentIndexChanged.connect(self.cs_send)
        self.currentIndexChanged.connect(self.update_bgcolor)

    def update_bgcolor(self, ind):
        if ind < len(self._colors):
            if self._colors[ind] is not None:
               self.setStyleSheet('QComboBox {background: ' + self._colors[ind] + ";}")

    def cx_connect(self):
        if self._cname is None or self._cname == '':
            return
        self.chan = cda.StrChan(self._cname, max_nelems=self._max_len, private=True)
        self.chan.valueChanged.connect(self.cs_update)
        self.chan.resolve.connect(self.resolve_proc)

    @pyqtSlot(str)
    def setValue(self, value):
        try:
            self.setCurrentIndex(self._values.index(value))
        except ValueError:
            self.setCurrentIndex(0)

    def value(self):
        return self._values[self.currentIndex()]

    @pyqtSlot(int)
    def cs_send(self, ind):
        if self.chan.val != self._values[ind]:
            self.chan.setValue(self._values[ind])

    def cs_update(self, chan):
        super().cs_update(chan)
        if self.value() != chan.val:
            self.setValue(chan.val)


class CXIntComboBox(QComboBox, CommonMixin):
    def __init__(self, *args, **kwargs):
        self._cname = None
        super().__init__(*args, **kwargs)
        self._values = kwargs.get('values', {})

        for k in self._values:
            self.insertItem(k, self._values[k])

        self.currentIndexChanged.connect(self.cs_send)

    @pyqtSlot(str)
    def setValue(self, value):
        self.setCurrentIndex(value)

    def value(self):
        return self.currentIndex()

    @pyqtSlot(int)
    def cs_send(self, ind):
        if self.chan.val != ind:
            self.chan.setValue(ind)

    def cs_update(self, chan):
        if self.value() != chan.val:
            self.setValue(chan.val)

