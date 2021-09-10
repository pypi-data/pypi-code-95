from PyQt5.QtWidgets import (QVBoxLayout,  QHBoxLayout, QFrame)

# TODO  create also oo hash that saves all needed data, so [o,oo] contains all need to save an open anything
class AWidget(QFrame):
    def __init__(self, parent, opts = {}):
        super().__init__(parent)
        self.opts = opts
        if 'vertical' in opts:
            lay = QVBoxLayout()
        else:
            lay = QHBoxLayout()
        self.setLayout(lay)
        if 'o' in opts:
            self.o = opts['o']
        else:
            if not hasattr(self.parent(),'o'):
                self.parent().o = {}
            self.o = self.parent().o

    def force_name(self, name):
        general_name = self.opts['general_name'] if 'general_name' in self.opts else 'input'

        if not name:
            i = 1
            while '{0}: {1}'.format(general_name, i) in self.o:
                i += 1
            name = '{0}: {1}'.format(general_name, i)
        return name

    def present(self):
        self.show()
        if 'gui_parent' not in self.opts:
            p = self.parent()
        else:
            p = self.opts['gui_parent']
        if hasattr(p, 'lay'):
            l = p.lay
        elif hasattr(p, 'layout'):
            l = p.layout()
        else:
            l = p

        if 'index' in self.opts:
            l.insertWidget(self.opts['index'], self)
        if 'grid_index' in self.opts:
            l.addWidget(self, *self.opts['grid_index'])
        else:
            l.addWidget(self)