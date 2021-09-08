from cxwidgets.aQt.QtCore import pyqtProperty, pyqtSlot
from .pledwidget import LedWidget
from .common_mixin import CommonMixin


class CXEventLed(LedWidget, CommonMixin):
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        super().__init__(parent, **kwargs)
        self.setState(False)

    def cs_update(self, chan):
        super().cs_update(chan)
        self.flashOnce()


class CXStateLed(LedWidget, CommonMixin):
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        super().__init__(parent, **kwargs)

    def cs_update(self, chan):
        super().cs_update(chan)
        self.setState(bool(chan.val))
