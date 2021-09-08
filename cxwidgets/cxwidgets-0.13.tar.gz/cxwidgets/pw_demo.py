#!/usr/bin/env python3

import sys
from aux.Qt import *
from cx_lcdnumber import CXLCDNumber
from cx_checkbox import CXCheckBox


app = QtWidgets.QApplication(sys.argv)
w = CXLCDNumber(None, 'canhw:13.BUN1.Imes')
w.show()

w2 = CXCheckBox(cname='Ql1.Iset')
w2.show()

sys.exit(app.exec_())
