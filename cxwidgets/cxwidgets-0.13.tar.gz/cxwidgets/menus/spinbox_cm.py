from cxwidgets.aQt.QtCore import Qt
from cxwidgets import BaseGridW, PSpinBox
from cxwidgets.aQt.QtWidgets import QLabel, QLineEdit, QWidgetAction
from .general_cm import CXGeneralCM


class CXSpinboxSettingsW(BaseGridW):
    def __init__(self, source_w, parent=None):
        super().__init__(parent)
        self.source_w = source_w
        self.l_h1 = QLabel("knob settings")
        self.l_h1.setStyleSheet("font-weight: bold; font-size: 12pt")
        self.grid.addWidget(self.l_h1, 0, 0, 1, 4, Qt.AlignHCenter)

        self.grid.addWidget(QLabel("step:"), 1, 0)
        self.step_sb = PSpinBox()
        self.grid.addWidget(self.step_sb, 1, 1)
        self.step_sb.setValue(source_w.singleStep())
        self.step_sb.done.connect(source_w.setSingleStep)

        self.grid.addWidget(QLabel("range:"), 2, 0)
        self.min_sb = PSpinBox()
        self.grid.addWidget(self.min_sb, 2, 1)
        self.min_sb.setValue(source_w.minimum())
        self.min_sb.done.connect(source_w.setMinimum)

        self.grid.addWidget(QLabel("-"), 2, 2)
        self.max_sb = PSpinBox()
        self.max_sb.setValue(source_w.maximum())
        self.max_sb.done.connect(source_w.setMaximum)
        self.grid.addWidget(self.max_sb, 2, 3)

        if not (source_w.hardmin == 0 and source_w.hardmax == 0):
            self.min_sb.setMinimum(source_w.hardmin)
            self.min_sb.setMaximum(source_w.hardmax)
            self.max_sb.setMinimum(source_w.hardmin)
            self.max_sb.setMaximum(source_w.hardmax)

        self.grid.addWidget(QLabel("max range:"), 3, 0)
        self.grid.addWidget(QLabel(str(source_w.hardmin)), 3, 1, Qt.AlignHCenter)
        self.grid.addWidget(QLabel("-"), 3, 2)
        self.grid.addWidget(QLabel(str(source_w.hardmax)), 3, 3, Qt.AlignHCenter)

        self.grid.setColumnMinimumWidth(1, 100)
        self.grid.setColumnMinimumWidth(3, 100)

        # ranges now working incorrectly - reported to Bolkhov
        print(source_w.chan)
        if source_w.chan is not None:
            print('some info')
            source_w.chan.get_range()
            source_w.chan.get_strings()
            print(source_w.chan.quant)
            print(source_w.chan.rng)

    def validate_minmax(self):
        pass


class CXSpinboxCM(CXGeneralCM):
    def __init__(self, source_w):
        super().__init__(source_w)

        self.addSeparator()

        self.w1 = CXSpinboxSettingsW(source_w)
        self.act_set = QWidgetAction(self)
        self.act_set.setDefaultWidget(self.w1)
        self.addAction(self.act_set)

