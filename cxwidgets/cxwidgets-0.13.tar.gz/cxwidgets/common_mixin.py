from cxwidgets.aQt.QtCore import pyqtSlot, pyqtProperty
import pycx4.qcda as cda
from .menus.general_cm import CXGeneralCM


class CommonMixin:
    def __init__(self, **kwargs):
        self.chan = None
        self.status = 'unknown'
        self.def_stylesheet = None
        self.status_color = ''
        self.context_menu = None
        self.cx_connect()

    # this works for most widgets (which uses IChan)
    def cx_connect(self):
        if self._cname is None or self._cname == '':
            self.chan = None
            return
        self.chan = cda.IChan(self._cname, private=True, get_curval=True)
        self.chan.valueMeasured.connect(self.cs_update)
        self.chan.resolve.connect(self.resolve_proc)

    def cs_update(self, chan):
        if self.def_stylesheet is None:
            self.def_stylesheet = self.styleSheet()
        color, status = cda.rflags_color_status(chan.rflags)
        if self.status != status:
            if color is None:
                self.setStyleSheet(self.def_stylesheet)
            else:
                pass
                self.setStyleSheet("background-color:" + color)
            self.status = status
            self.status_color = color

    def resolve_proc(self, chan):
        if self.def_stylesheet is None:
            self.def_stylesheet = self.styleSheet()
        if chan.rslv_stat == cda.RslvStats.notfound:
            self.setStyleSheet("background-color:#404040;")
            self.status = 'not_found'
        elif chan.rslv_stat == cda.RslvStats.found:
            self.setStyleSheet(self.def_stylesheet)
            self.status = 'found'

    def contextMenuEvent(self, event):
        self.context_menu = CXGeneralCM(self)
        self.context_menu.popup(event.globalPos())

    @pyqtSlot(str)
    def set_cname(self, name):
        if self._cname == name:
            return
        self._cname = name
        self.cx_connect()

    def get_cname(self):
        return self._cname

    cname = pyqtProperty(str, get_cname, set_cname)


