from cxwidgets.aQt.QtWidgets import QProgressBar
from .common_mixin import CommonMixin

class CXProgressBar(QProgressBar, CommonMixin):
    def __init__(self, *args, **kwargs):
        self._cname = None
        super().__init__(*args, **kwargs)

    def cs_update(self, chan):
        super().cs_update(chan)
        if self.value() != chan.val:
            self.setValue(chan.val)

