import pyqtgraph as pg
try:
    from qtpy import QtCore
    from qtpy.QtCore import Qt
    from qtpy.QtCore import Signal
except ImportError:
    from PyQt5 import QtCore
    from PyQt5.QtCore import Qt
    from PyQt5.QtCore import pyqtSignal as Signal

from . import util
from .const import LABEL_FILL


class Crosshair(QtCore.QObject):
    signal_position = Signal('PyQt_PyObject')

    pen = pg.mkPen(style=Qt.DotLine)

    def __init__(self):
        """crosshair needs scope to get t0 value"""
        super().__init__()

        self.hline = pg.InfiniteLine(
            angle=0,
            pen=self.pen,
            movable=False,
        )
        self.vline = pg.InfiniteLine(
            angle=90,
            pen=self.pen,
            movable=False,
        )
        self.label = pg.TextItem(
            anchor=(1, 1),
            fill=LABEL_FILL,
        )
        self.active_plot = None

    def set_font(self, font):
        """Set text label font"""
        self.label.textItem.setFont(font)

    def set_text_color(self, color):
        """Set color of label text and crosshair lines"""
        self.label.textItem.setDefaultTextColor(color)
        self.hline.pen.setColor(color)
        self.vline.pen.setColor(color)

    def set_active_plot(self, plot):
        if plot == self.active_plot:
            return
        if self.active_plot:
            self.active_plot.removeItem(self.hline)
            self.active_plot.removeItem(self.vline)
            self.active_plot.removeItem(self.label)
            self.active_plot = None
        if plot:
            plot.addItem(self.hline)
            plot.addItem(self.vline)
            plot.addItem(self.label)
            self.active_plot = plot

    def update(self, pos, plot, t0):
        self.set_active_plot(plot)
        ppos = plot.vb.mapSceneToView(pos)
        x = ppos.x()
        y = ppos.y()
        (xmin, xmax), (ymin, ymax) = plot.viewRange()
        if x > (xmin+xmax)/2:
            ax = 1
        else:
            ax = 0
        if y < (ymin+ymax)/2:
            ay = 1
        else:
            ay = 0
        t = t0 + x
        self.hline.setPos(y)
        self.vline.setPos(x)
        self.label.setPos(x, y)
        self.label.setAnchor((ax, ay))
        greg = util.gpstime_str_greg(util.gpstime_parse(t), '%Y/%m/%d %H:%M:%S %Z')
        label = '''<table>
<tr><td rowspan="2" valign="middle">T=</td><td>{:0.7f}</td></tr>
<tr><td>{}</td></tr>
<tr><td>Y=</td><td>{:g}</td></tr>
</table></nobr>'''.format(t, greg, y)
        self.label.setHtml(label)
        self.signal_position.emit((t, greg, y))
