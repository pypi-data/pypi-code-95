from cxwidgets.aQt.QtWidgets import QLCDNumber
from .common_mixin import CommonMixin


class CXLCDNumber(QLCDNumber, CommonMixin):
    def __init__(self, parent=None, **kwargs):
        self._cname = None
        super().__init__(parent, **kwargs)

    def cs_update(self, chan):
        super().cs_update(chan)
        self.display(chan.val)

