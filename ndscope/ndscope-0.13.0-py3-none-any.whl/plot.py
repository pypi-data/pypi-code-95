import copy
import collections

import numpy as np

import pyqtgraph as pg
from pyqtgraph import PlotItem, PlotDataItem, FillBetweenItem
try:
    from qtpy import QtCore
    from qtpy.QtGui import QFont, QColor, QPen
except ImportError:
    from PyQt5 import QtCore
    from PyQt5.QtGui import QFont, QColor, QPen

from gpstime import gpstime, gpsnow

from . import util
from . import const
from .plotMenu import NDScopePlotMenu
from . import layout
from . import legend


##################################################

CHANNEL_COLORS = {}


def hold_over_nan(y):
    """hold data over subsequent nans

    This function finds all nans in the input array, and produces an
    creates an output array that is nan everywhere except where the
    input array was nan.  Where the input array was nan, the output
    array will be the value of the input array right before the nan.
    If the first element of the input array is nan then zero will be
    used.  Example:

    y   = [nan, nan,   2,   3,   4,   5, nan, nan, nan,   9,  10]
    out = [  0,   0,   0, nan, nan,   5,   5,   5,   5,   5, nan]

    We use this for indicating "bad" data regions in plots.

    """
    nani = np.where(np.isnan(y))[0]
    if nani.size == y.size:
        return np.zeros_like(y, dtype=np.float)
    out = np.empty_like(y, dtype=np.float)
    out[:] = np.nan
    if nani.size == 0:
        return out
    ti = np.where(np.diff(nani) > 1)[0]
    nstart = np.append(nani[0], nani[ti+1])
    nend = np.append(nani[ti], nani[-1]) + 1
    for s, e in zip(nstart, nend):
        if s == 0:
            v = 0
        else:
            v = y[s-1]
        out[s-1:e+1] = v
    return out


##################################################


class TimeStringAxis(pg.AxisItem):
    def __init__(self, orientation='bottom', **kwargs):
        super().__init__(orientation, **kwargs)
        self.t0 = 0
        self.tick_func = self.t_to_relative

    def t_to_relative(self, t):
        return str(util.TDStr(t))

    def t_to_gps(self, t):
        return t + self.t0

    def t_to_utc(self, t):
        gps = gpstime.fromgps(t + self.t0)
        return gps.strftime(const.TICK_DATE_FMT)

    def t_to_local(self, t):
        gps = gpstime.fromgps(t + self.t0)
        local = gps.astimezone()
        return local.strftime(const.TICK_DATE_FMT)

    def setTickStringsMode(self, mode):
        func_map = {
            'relative': self.t_to_relative,
            'gps': self.t_to_gps,
            'utc': self.t_to_utc,
            'local': self.t_to_local,
        }
        self.tick_func = func_map[mode]
        # this is needed to clear/update the ticks on change:
        self.picture = None
        self.update()

    ######

    def tickSpacing(self, minVal, maxVal, size):
        span = abs(maxVal - minVal)
        for major, minordiv in const.TICK_SPACINGS:
            if span >= 3*major:
                break
        return [
            (major, 0),
            (major/minordiv, 0),
        ]

    def tickStrings(self, values, scale, spacing):
        return [self.tick_func(t) for t in values]

##################################################


class NDScopePlot(PlotItem):
    channel_added = QtCore.Signal(str)
    channel_removed = QtCore.Signal(str)
    new_plot_request = QtCore.Signal('PyQt_PyObject')
    remove_plot_request = QtCore.Signal('PyQt_PyObject')

    def __init__(self, *args):
        """Initialize NDSCope Plot object

        """
        super(NDScopePlot, self).__init__(
            *args,
            axisItems={'bottom': TimeStringAxis()},
        )

        # dict of channel:curve
        self.channels = collections.OrderedDict()
        # dict of channel:label
        self.labels = {}

        # plot options
        # use automatic downsampling and clipping to reduce the
        # drawing load
        self.setDownsampling(mode='peak')
        # clip data to only what's visible
        # FIXME: is this what we want?
        self.setClipToView(True)
        # don't auto-range x axis, since we have special handling
        self.disableAutoRange(axis='x')
        # hide auto-scale buttons
        self.hideButtons()
        # add legend
        self.legend = legend.Legend()
        self.legend.setParentItem(self.vb)
        self.legend.setVisible(False)
        # show grid lines
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setLabel('left', 'counts')
        # limit the zooming range
        self.setLimits(
            minXRange=0.0001,
        )

        self.ctrlMenu = None
        vb = self.getViewBox()
        vb.menu = NDScopePlotMenu(self)

        # If this option is not removed then a default font size will
        # be set in the generated html that will not overridable by
        # setting the font.
        self.titleLabel.opts.pop('size')

        self.font = QFont()
        self.text_color = QColor('gray')

    def add_channel(self, channel, **kwargs):
        """Add channel to plot

        keyword arguments are passed directly to NDScopePlotChannel.

        """
        if channel in self.channels:
            return
        if const.CHANNEL_RE.match(channel) is None:
            # FIXME: should handle this error better in ancestors
            raise ValueError("invalid channel name: {}".format(channel))
        cc = NDScopePlotChannel(channel, **kwargs)
        self.channels[channel] = cc
        self.addItem(cc.curves['y'])
        self.addItem(cc.curves['bad'])
        self.labels[channel] = cc.label
        self._update_title_legend()
        cc.label_changed.connect(self._update_legend_item)
        self.channel_added.emit(channel)

    def remove_channel(self, channel):
        """remove channel from plot

        """
        if channel not in self.channels:
            return
        cc = self.channels[channel]
        self.legend.removeItem(cc.label)
        for curve in cc.curves.values():
            self.removeItem(curve)
        del self.channels[channel]
        self._update_title_legend()
        self.channel_removed.emit(channel)

    def set_font(self, font):
        """Set label and axis font"""
        self.titleLabel.item.setFont(font)
        self.legend.setFont(font)
        self.axes['left']['item'].label.setFont(font)
        self.axes['bottom']['item'].setTickFont(font)
        self.axes['left']['item'].setTickFont(font)
        self.font = font

    def set_text_color(self, color):
        """Set color of label text and axis lines"""
        self.titleLabel.setAttr('color', color.name())
        self.titleLabel.setText(self.titleLabel.text)
        self.legend.setTextColor(color)
        self.axes['left']['item'].labelStyle['color'] = color.name()
        self.axes['bottom']['item'].setPen(QPen(color))
        self.axes['left']['item'].setPen(QPen(color))
        self.text_color = color

    # SLOT
    def _update_legend_item(self, channel):
        cc = self.channels[channel]
        label = cc.label
        self.legend.removeItem(self.labels[channel])
        self.legend.addItem(cc.curves['y'], label)
        self.labels[channel] = label

    def _update_title_legend(self):
        """update plot title and legend"""
        if len(self.channels) < 1:
            self.legend.setVisible(False)
            self.setTitle(None)
        elif len(self.channels) == 1:
            self.legend.setVisible(False)
            self.setTitle(list(self.channels.values())[0].label)
        else:
            self.legend.setVisible(True)
            self.setTitle(None)

    def clear_data(self):
        """clear data for all channels

        """
        for curve in self.channels.values():
            curve.clear_data()

    def _set_t_limits(self, t0):
        """Set the t axis limits for a given t0"""
        self.setLimits(
            xMin=const.GPS_MIN-t0,
            #xMax=gpsnow()-t0+1,
        )

    def update(self, data, t0):
        """update all channel

        `data` should be a DataBufferDict object, and `t0` is the GPS
        time for t=0.

        """
        self.axes['bottom']['item'].t0 = t0
        self._set_t_limits(t0)

        ctype_changed = False

        units = set()

        for channel, cc in self.channels.items():
            if channel not in data or not data[channel]:
                continue

            cd = data[channel]

            if cd.is_trend and not cc.is_trend:
                self.addItem(cc.curves['min'])
                self.addItem(cc.curves['max'])
                if cc.curves['fill']:
                    self.addItem(cc.curves['fill'])
            elif not cd.is_trend and cc.is_trend:
                self.removeItem(cc.curves['min'])
                self.removeItem(cc.curves['max'])
                if cc.curves['fill']:
                    self.removeItem(cc.curves['fill'])

            ctype_changed |= cc.set_ctype(cd.ctype)

            cc.set_data(cd, t0)

            units.add(cc.get_unit(cd.unit))

        self.setLabel('left', '/'.join(list(units)))

        if ctype_changed:
            self._update_title_legend()


##################################################


class NDScopePlotChannel(QtCore.QObject):
    label_changed = QtCore.Signal(str)

    def __init__(self, channel, **kwargs):
        """Initialize channel curve object

        Holds curves for y value, and for trend min/max/fill.

        Keyword arguments are trace style parameters, e.g. `color`,
        `width`, `unit`, `scale` and `offset`.  `color` can be a
        single letter color spec ('b', 'r', etc.), an integer, or an
        [r,g,b] list.  See the following for more info:

          http://www.pyqtgraph.org/documentation/functions.html#pyqtgraph.mkColor

        """
        super(NDScopePlotChannel, self).__init__()

        global CHANNEL_COLORS

        self.channel = channel
        self.ctype = None
        self.is_trend = None
        self.params = dict(layout.CURVE)
        self.params.update(kwargs)
        self._update_transform()

        if self.params.get('color'):
            color = pg.mkColor(self.params['color'])
        elif channel in CHANNEL_COLORS:
            color = CHANNEL_COLORS[channel]
        else:
            while True:
                color = pg.mkColor(layout.get_pen_color())
                if color not in CHANNEL_COLORS.values():
                    break
        CHANNEL_COLORS[channel] = color
        self.params['color'] = color

        pen = pg.mkPen(color, width=self.params.get('width'))
        mmc = copy.copy(color)
        mmc.setAlpha(100)
        mmpen = pg.mkPen(mmc, style=QtCore.Qt.DashLine)

        self.curves = {}
        self.curves['y'] = PlotDataItem([0, 0], pen=pen, name=self.label)
        self.curves['min'] = PlotDataItem([0, 0], pen=mmpen)
        self.curves['max'] = PlotDataItem([0, 0], pen=mmpen)
        # FIXME: fill is expensive, so we disable it until figure it out
        if False:
            self.curves['fill'] = FillBetweenItem(
                self.curves['min'],
                self.curves['max'],
                brush=mmc
            )
        else:
            self.curves['fill'] = None
        # special curve for bad data (nans, infs)
        self.curves['bad'] = PlotDataItem(
            [0, 0],
            pen=pg.mkPen('r', width=1, style=QtCore.Qt.DotLine)
        )

    def set_ctype(self, ctype):
        """Update the channel ctype

        Returns True if type changed, False otherwise

        """
        if ctype == self.ctype:
            return False
        self.ctype = ctype
        if ctype in ['s-trend', 'm-trend']:
            self.is_trend = True
        else:
            self.is_trend = False
        self.label_changed.emit(self.channel)
        return True

    def get_unit(self, default):
        """return channel unit"""
        unit = self.params.get('unit')
        if not unit:
            unit = default or 'counts'
        return unit

    @property
    def label(self):
        """label for this channel"""
        label = self.channel
        if self.params['offset'] != 0:
            label += ' {:+g}'.format(self.params['offset'])
        if self.params['scale'] != 1:
            label += ' *{:g}'.format(self.params['scale'])
        if self.is_trend:
            label += ' [{}]'.format(self.ctype)
        return label

    def _update_transform(self):
        """update the transform function"""
        if self.params['scale'] != 1 or self.params['offset'] != 0:
            def transform(data):
                return (data + self.params['offset']) * self.params['scale']
        else:
            def transform(data):
                return data
        self.transform = transform

    def clear_data(self):
        """clear data for curves

        """
        for curve in self.curves.values():
            try:
                curve.setData(np.array([0, 0]))
            except:
                pass

    def _set_curve_data(self, mod, y, t):
        # FIXME: HACK: replace all +-infs with nans.  the infs
        # were causing the following exception in PlotCurveItem
        # when it tried to find the min/max of the array:
        # ValueError: zero-size array to reduction operation minimum which has no identity
        # using nan is not great, since that's also an indicator
        # of a gap, but not sure what else to use.
        try:
            np.place(y, np.isinf(y), np.nan)
        except ValueError:
            # this check throws a value error if y is int.  but in
            # that case there's nothing we need to convert, so
            # just pass
            pass
        self.curves[mod].setData(
            x=t,
            y=self.transform(y),
            connect="finite",
        )

    def set_data(self, data, t0):
        """set data for curves

        Data should be DataBuffer object.

        """
        t = data.tarray - t0

        if 'raw' in data:
            y = data['raw']
        else:
            y = data['mean']
            for mod in ['min', 'max']:
                self._set_curve_data(mod, data[mod], t)

        self._set_curve_data('y', y, t)

        self.curves['bad'].setData(
            x=t,
            y=hold_over_nan(y),
            connect="finite",
        )
