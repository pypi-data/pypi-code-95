from cxwidgets import BaseGridW, PSpinBox, PCheckBox, LedWidget, HLine
from cxwidgets.aQt.QtWidgets import QLabel, QLineEdit, QTextEdit, QMenu, QWidgetAction, QWidget, QHBoxLayout, QLayout
from cxwidgets.aQt.QtCore import Qt
from pycx4.qcda import rflags_order, rflags_meaning
import datetime
import math

class LabeledLed(QWidget):
    """LedWidget + label

    attributes:
        led - LedWidget
        label - Qlabel
    """
    def __init__(self, parent=None, text='label'):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.led = LedWidget(self)
        self.led.setDiameter(10)
        self.layout.addWidget(self.led)
        self.label = QLabel(text)
        self.layout.addWidget(self.label)


class CXGeneralCMW(BaseGridW):
    """Widget for general CX channel information
    """

    def __init__(self, source_widget, parent=None):
        super().__init__(parent)
        source_chan = source_widget.chan
        self.source_chan = source_chan
        self.l_h1 = QLabel("channel info")
        self.l_h1.setStyleSheet("font-weight: bold; font-size: 12pt")
        self.grid.addWidget(self.l_h1, 0, 0, 1, 2, Qt.AlignHCenter)
        self.grid.addWidget(HLine(), 1, 0, 1, 2, Qt.AlignHCenter)

        self.grid.addWidget(QLabel("name:  "), 2, 0)
        name_txt = 'n/a' if source_chan is None else source_chan.name
        self.grid.addWidget(QLabel(name_txt), 2, 1)

        self.grid.addWidget(QLabel("value:  "), 3, 0)
        self.label_val = QLabel('n/a')
        self.grid.addWidget(self.label_val, 3, 1)

        self.grid.addWidget(QLabel("time:  "), 4, 0)
        self.label_time = QLabel('n/a')
        self.grid.addWidget(self.label_time, 4, 1)

        self.grid.addWidget(QLabel("status:  "), 5, 0)
        self.label_status = QLabel(source_widget.status)
        self.grid.addWidget(self.label_status, 5, 1)

        if source_chan is not None:
            source_chan.valueMeasured.connect(self.data_update)
            self.data_update(source_chan)

    def data_update(self, chan):
        self.label_val.setText(str(chan.val))
        self.label_time.setText(datetime.datetime.fromtimestamp(chan.time / 1e6).strftime("%Y-%m-%d %H:%M:%S.%f"))



class CXFlagsMenu(QMenu):
    """QMenu to show CX rflags
    """
    def __init__(self, source_widget):
        super().__init__()
        source_chan = source_widget.chan
        self.source_chan = source_chan
        self.setTitle('rflags')
        self.items = {}
        self.widgets = {}

        for k in rflags_order:
            self.widgets[k] = LabeledLed(text=rflags_meaning[k])
            self.items[k] = QWidgetAction(self)
            self.items[k].setDefaultWidget(self.widgets[k])
            self.addAction(self.items[k])

        if source_chan is not None:
            self.setFlags(source_chan.rflags)

    def setFlags(self, rflags: int):
        for k in self.widgets:
            if (k & rflags) > 0:
                self.widgets[k].led.setValue(1)
            else:
                self.widgets[k].led.setValue(0)


class CXGeneralCM(QMenu):
    """General context menu for most CX-connected widgets

    """
    def __init__(self, source_w):
        super().__init__()
        self.source_w = source_w

        w = CXGeneralCMW(source_w)
        self.act_gen = QWidgetAction(self)
        self.act_gen.setDefaultWidget(w)
        self.addAction(self.act_gen)

        self.fl_menu = CXFlagsMenu(source_w)
        self.addMenu(self.fl_menu)

        # self.setAttribute(Qt.WA_DeleteOnClose) # this also works, but runs later
        self.aboutToHide.connect(self.deleteLater)
