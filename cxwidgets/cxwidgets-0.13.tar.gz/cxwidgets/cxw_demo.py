#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication, QLabel
from cxwidgets.aQt.QtCore import Qt
from cxwidgets import BaseGridW, CXSwitch, CXDevSwitch


class DemoW(BaseGridW):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.grid.addWidget(QLabel("CX widgets demo"), 0, 0, 1, 2, Qt.AlignHCenter)

        self.grid.addWidget(QLabel("CXSwitch"), 1, 0)
        s1 = CXSwitch(cname='cxhw:0.ddm.v2k_auto')
        self.grid.addWidget(s1, 1, 1)

        self.grid.addWidget(QLabel("CXDevSwitch"), 2, 0)
        s2 = CXDevSwitch(devname='cxhw:18.v0308_blm1.c0')
        self.grid.addWidget(s2, 2, 1)



app = QApplication(sys.argv)

grid = ()

#w = CXLCDNumber(None, 'canhw:13.BUN1.Imes')
#w.show()

#w2 = CXCheckBox(cname='Ql1.Iset')
#w2.show()

w = DemoW()

w.show()


sys.exit(app.exec_())
