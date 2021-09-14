# -*- coding: utf-8 -*-
import os
import traceback
import subprocess

import numpy as np

import pyqtgraph as pg
try:
    from qtpy import QtGui, QtWidgets
    from qtpy.QtCore import Qt, QRegularExpression, QTimer
    from qtpy.QtWidgets import QStyle, QFileDialog, QFontDialog
    from qtpy.QtGui import QFont, QColor
    from qtpy import uic
except ImportError:
    from PyQt5 import QtGui, QtWidgets
    from PyQt5.QtCore import Qt, QRegularExpression, QTimer
    from PyQt5.QtWidgets import QStyle, QFileDialog, QFontDialog
    from PyQt5.QtGui import QFont, QColor
    from PyQt5 import uic

# NOTE: must be imported after pyqt or else config is reset
import logging

from . import __version__
from . import const
from . import util
from .data import DataStore
from .plot import NDScopePlot
from .trigger import Trigger
from .crosshair import Crosshair
from .cursors import TCursors, YCursors
from . import export


logger = logging.getLogger('SCOPE')

##################################################
# CONFIG


if os.getenv('ANTIALIAS'):
    pg.setConfigOption('antialias', True)
    logger.info("Anti-aliasing ENABLED")
# pg.setConfigOption('leftButtonPan', False)
# see also ViewBox.setMouseMode(ViewBox.RectMode)
# file:///usr/share/doc/python-pyqtgraph-doc/html/graphicsItems/viewbox.html#pyqtgraph.ViewBox.setMouseMode


STATUS_STYLES = {
    "data": "background: rgba(0,100,0,100);",
    "msg": "background: rgba(0,0,100,100);",
    "error": "background: rgba(255,0,0,255); color: black; font-weight: bold;",
}


TREND_OPTIONS = [
    'auto',
    'raw',
    'sec',
    'min',
]

##################################################


Ui_MainWindow, QMainWindow = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'scope.ui'))


class NDScope(QMainWindow, Ui_MainWindow):
    def __init__(self, layout):
        """initilize NDScope object

        `layout` should be a list of subplot definitions, each being a
        dictionary matching the keyword arguments to add_plot()
        (e.g. row, col, colspan, channels, etc.).

        """
        super(NDScope, self).__init__(None)
        self.setupUi(self)

        ndsserver = os.getenv('NDSSERVER')
        logger.info(f"version {__version__}")
        logger.info(f"server {ndsserver}")
        self.statusBar.addWidget(QtWidgets.QLabel(f"ndscope {__version__}    NDS server: {ndsserver}"))
        self.statusClearButton = QtWidgets.QPushButton('clear')
        self.statusBar.addPermanentWidget(self.statusClearButton)
        self.statusBar.messageChanged.connect(self.status_clear)
        self.statusClearButton.clicked.connect(self.status_clear)
        self.status_clear()

        # FIXME: HACK: this is an attempt to bypass the following bug:
        #
        # Traceback (most recent call last):
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/GraphicsObject.py", line 23, in itemChange
        #     self.parentChanged()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/GraphicsItem.py", line 440, in parentChanged
        #     self._updateView()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/GraphicsItem.py", line 492, in _updateView
        #     self.viewRangeChanged()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/PlotDataItem.py", line 671, in viewRangeChanged
        #     self.updateItems()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/PlotDataItem.py", line 483, in updateItems
        #     x,y = self.getData()
        #   File "/usr/lib/python3/dist-packages/pyqtgraph/graphicsItems/PlotDataItem.py", line 561, in getData
        #     if view is None or not view.autoRangeEnabled()[0]:
        # AttributeError: 'GraphicsLayoutWidget' object has no attribute 'autoRangeEnabled'
        def autoRangeEnabled():
            return False, False
        self.graphView.autoRangeEnabled = autoRangeEnabled

        ##########
        # data and data retrieval

        self.data = DataStore()
        self.last_fetch_cmd = None
        self.last_data = (None, 0, 0)

        self.data.signal_data_online_start.connect(self._data_online_start)
        self.data.signal_data_retrieve_start.connect(self._data_retrieve_start)
        self.data.signal_data.connect(self._update_plots)
        self.data.signal_data_online_done.connect(self._data_online_done)
        self.data.signal_data_retrieve_done.connect(self._data_retrieve_done)

        ##########
        # window/range entry

        def NonEmptyValidator():
            return QtGui.QRegularExpressionValidator(QRegularExpression('.+'))

        self.entryT0GPS.textEdited.connect(self.update_entryT0Greg)
        self.entryT0GPS.setValidator(QtGui.QDoubleValidator())
        self.entryT0GPS.returnPressed.connect(self.update_t0)

        self.entryT0Greg.textEdited.connect(self.update_entryT0GPS)
        self.entryT0Greg.setValidator(NonEmptyValidator())
        self.entryT0Greg.returnPressed.connect(self.update_t0)

        self.buttonT0Now.clicked.connect(self.set_entryT0)

        self.entryWindowStart.setValidator(QtGui.QDoubleValidator())
        self.entryWindowStart.returnPressed.connect(self.update_window)

        self.entryWindowEnd.setValidator(QtGui.QDoubleValidator())
        self.entryWindowEnd.returnPressed.connect(self.update_window)

        self.entryStartGPS.textEdited.connect(self.update_entryStartGreg)
        self.entryStartGPS.setValidator(QtGui.QDoubleValidator())
        self.entryStartGPS.returnPressed.connect(self.update_range)

        self.entryStartGreg.textEdited.connect(self.update_entryStartGPS)
        self.entryStartGreg.setValidator(NonEmptyValidator())
        self.entryStartGreg.returnPressed.connect(self.update_range)

        self.entryEndGPS.setValidator(QtGui.QDoubleValidator())
        self.entryEndGPS.textEdited.connect(self.update_entryEndGreg)
        self.entryEndGPS.returnPressed.connect(self.update_range)

        self.entryEndGreg.textEdited.connect(self.update_entryEndGPS)
        self.entryEndGreg.setValidator(NonEmptyValidator())
        self.entryEndGreg.returnPressed.connect(self.update_range)

        self.buttonEndNow.clicked.connect(self.set_entryEnd)

        self.fetchButton1.clicked.connect(self.update_t0)
        self.fetchButton2.clicked.connect(self.update_range)

        ##########
        # trend

        self.trendSelectGroup = QtWidgets.QButtonGroup()
        # NOTE: the numbers correspond to indices in TREND_OPTIONS
        self.trendSelectGroup.addButton(self.trendAutoSelect, 0)
        self.trendSelectGroup.addButton(self.trendRawSelect, 1)
        self.trendSelectGroup.addButton(self.trendSecSelect, 2)
        self.trendSelectGroup.addButton(self.trendMinSelect, 3)
        self.trendSelectGroup.buttonClicked.connect(self._trend_select)

        self.trendRawSecThresh.setValidator(QtGui.QIntValidator())
        self.trendRawSecThresh.setText(str(const.TREND_TRANS_THRESHOLD['raw/sec']))
        self.trendRawSecThresh.returnPressed.connect(self._set_trend_rawsec)

        self.trendSecMinThresh.setValidator(QtGui.QIntValidator())
        self.trendSecMinThresh.setText(str(const.TREND_TRANS_THRESHOLD['sec/min']))
        self.trendSecMinThresh.returnPressed.connect(self._set_trend_secmin)

        ##########
        # axis

        self.timeAxisRelativeSelect.toggled.connect(lambda: self.time_axis_select('relative'))
        self.timeAxisGPSSelect.toggled.connect(lambda: self.time_axis_select('gps'))
        self.timeAxisUTCSelect.toggled.connect(lambda: self.time_axis_select('utc'))
        self.timeAxisLocalSelect.toggled.connect(lambda: self.time_axis_select('local'))

        ##########
        # trigger

        self.trigger = Trigger()
        self.trigger.sigLevelChanged.connect(self._update_triggerLevel)
        self.triggerLevel.setValidator(QtGui.QDoubleValidator())
        self.triggerLevel.returnPressed.connect(self._set_trigger_level)
        self.triggerResetLevel.clicked.connect(self.reset_trigger_level)
        self.triggerSingle.clicked.connect(self.trigger.set_single)
        self.triggerInvert.clicked.connect(self.trigger.set_invert)
        self.triggerGroup.toggled.connect(self._toggle_trigger)

        ##########
        # crosshair

        self.Crosshair = Crosshair()
        self.Crosshair.signal_position.connect(self._update_crosshair_entry)
        self._crosshair_proxy = None
        self.crosshairGroup.toggled.connect(self._toggle_crosshair)

        ##########
        # cursors

        self.TCursors = TCursors()
        self.cursorTGroup.toggled.connect(self._toggle_t_cursors)
        self.cursorTReset.clicked.connect(self.TCursors.reset)

        self.YCursors = YCursors()
        self.cursorYGroup.toggled.connect(self._toggle_y_cursors)
        self.cursorYPlot.currentIndexChanged.connect(self._set_y_cursors_plot)
        self.cursorYReset.clicked.connect(self.YCursors.reset)

        ##########
        # style

        self.fontSize.valueChanged.connect(self.set_font_size)
        self.backgroundCheckBox.stateChanged.connect(self._background_select)

        ##########
        # export

        self.exportPathButton.clicked.connect(self._export_dialog)
        self.exportPath.returnPressed.connect(self._export2Handler)
        self.exportButton.clicked.connect(self._export2Handler)
        self.exportShowButton.clicked.connect(self._exportShowHandler)
        self.exportButton2.clicked.connect(self.export)

        ##########
        # controls

        self.controlBar.hide()
        self.controlExpandButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarShadeButton))
        self.controlExpandButton.setText('')
        self.controlExpandButton.clicked.connect(self._controlExpand)
        self.controlCollapseButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarUnshadeButton))
        self.controlCollapseButton.setText('')
        self.controlCollapseButton.clicked.connect(self._controlCollapse)

        self.startButton.clicked.connect(self.start)
        self.startButton2.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.stopButton2.clicked.connect(self.stop)
        self.resetRangeButton.clicked.connect(self.reset_range)
        self.resetRangeButton2.clicked.connect(self.reset_range)
        self.resetT0Button.clicked.connect(self.reset_t0)
        self.resetT0Button2.clicked.connect(self.reset_t0)

        ##########
        # button icons
        # FIXME: should set this in .ui somehow

        self.startButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.startButton2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton2.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        # self.fetchButton1.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        # self.fetchButton2.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        # self.resetRangeButton.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        # self.resetRangeButton2.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.exportPathButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.exportButton.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.exportShowButton.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        self.exportButton2.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))

        ##########
        # initial config

        self.font = QFont()
        self.text_color = QColor('gray')

        self._base_ui()

        self.plotLayout = self.graphView.addLayout()

        self.plots = []

        for subplot in layout:
            self.add_plot(**subplot)

        self.data.init = False

        self.graphView.nextRow()
        self.referenceTimeLabel = self.graphView.addLabel(
            "GPS Time",
            #bold=True,
        )

        self.set_t0(util.gpstime_parse('now').gps())
        self.set_window(-2, 0)

        ##########
        # main mouse gesture signal

        #self.plot0.sigXRangeChanged.connect(self.update_mouse)
        self.update_mouse_proxy = pg.SignalProxy(
            self.plot0.sigXRangeChanged,
            rateLimit=1,
            slot=self.update_mouse,
        )

    ##########

    def set_font(self, font):
        self.fontSize.setValue(font.pointSize())
        referenceTimeLabelFont = QFont(font)
        referenceTimeLabelFont.setPointSize(font.pointSize() + 2)
        self.referenceTimeLabel.item.setFont(referenceTimeLabelFont)
        self.Crosshair.set_font(font)
        self.TCursors.set_font(font)
        self.YCursors.set_font(font)
        self.trigger.set_font(font)
        for plot in self.plots:
            plot.set_font(font)
        self.font = font

    def set_font_size(self, size):
        """Set font size for plots"""
        font = QFont(self.font)
        font.setPointSize(size)
        self.set_font(font)

    def set_text_color(self, color):
        """Sets the color of the text in the plots

        labels, axis lines and tick labels, and cursors, crosshair,
        and trigger levels and text.

        """
        self.Crosshair.set_text_color(color)
        self.TCursors.set_text_color(color)
        self.YCursors.set_text_color(color)
        self.trigger.set_text_color(color)
        for plot in self.plots:
            plot.set_text_color(color)
        self.text_color = color

    def set_background(self, color='k'):
        """Sets the color of the background.

        Options are 'w': white, 'k': black

        """
        if color == 'w':
            self.graphView.setBackground(QColor('white'))
            self.referenceTimeLabel.setAttr('color', QColor('black'))
            self.referenceTimeLabel.setText(self.referenceTimeLabel.text)
            self.backgroundCheckBox.setCheckState(Qt.Checked)
        elif color == 'k':
            self.graphView.setBackground(QColor('black'))
            self.referenceTimeLabel.setAttr('color', QColor('white'))
            self.referenceTimeLabel.setText(self.referenceTimeLabel.text)
            self.backgroundCheckBox.setCheckState(Qt.Unchecked)
        else:
            raise ValueError("background color value must be 'w' or 'k'.")

    def _base_ui(self):
        self.startButton.setEnabled(False)
        self.startButton2.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.stopButton2.setEnabled(False)
        self.windowTab.setEnabled(False)
        self.rangeTab.setEnabled(False)
        self.triggerTab.setEnabled(False)
        self.exportTab.setEnabled(False)
        self.exportButton2.setEnabled(False)

    def _initialized_ui(self):
        self.startButton.setEnabled(True)
        self.startButton2.setEnabled(True)
        self.windowTab.setEnabled(True)
        self.rangeTab.setEnabled(True)
        self.triggerTab.setEnabled(True)
        self.exportTab.setEnabled(True)
        self.exportButton2.setEnabled(True)

    ##########
    # status bar

    def status_clear(self, text=None):
        # this method is connected to the statusBar.messageChanged
        # slot, so that the status bar is reset when a temporary
        # message is cleared. but we only want to reset when it's
        # cleared (test is empty), not when a new message is added.
        if text:
            return
        self.statusBar.setStyleSheet("")
        self.statusClearButton.setVisible(False)
        self.statusBar.clearMessage()

    def status_message(self, msg, timeout=0, style="msg", clear_button=False, log=True):
        if log:
            logger.warning(msg)
        style = STATUS_STYLES.get(style)
        if style:
            self.statusBar.setStyleSheet(f"QStatusBar{{{style}}}")
        self.statusBar.showMessage(msg, int(timeout*1000))
        if clear_button:
            self.statusClearButton.setVisible(True)
        else:
            self.statusClearButton.setVisible(False)

    def status_error(self, msg):
        logger.error(msg)
        self.statusBar.setStyleSheet(STATUS_STYLES["error"])
        self.statusBar.showMessage(msg)
        self.statusClearButton.setVisible(True)

    ##########
    # controls box

    def _controlExpand(self):
        self.controlBarSmall.hide()
        self.controlBar.show()

    def _controlCollapse(self):
        self.controlBar.hide()
        self.controlBarSmall.show()

    ##########
    # CHANNELS AND PLOTS

    def add_plot(self, channels=None, yrange=None, **kwargs):
        """Add plot to the scope

        If provided `channels` should be a list of channel:property
        dicts to add to the plot on initialization.

        """
        logger.info(f"creating plot {kwargs}...")

        plot = NDScopePlot()
        plot.set_font(self.font)
        plot.set_text_color(self.text_color)
        plot.channel_added.connect(self._channel_added)
        plot.channel_removed.connect(self._channel_removed)
        plot.new_plot_request.connect(self.add_plot_handler)
        plot.remove_plot_request.connect(self.remove_plot)

        # tie all plot x-axes together
        if self.plots:
            plot.setXLink(self.plot0)

        # set y ranges
        if yrange in [None, 'auto']:
            plot.enableAutoRange(axis='y')
        else:
            plot.setYRange(*yrange)

        self.plots.append(plot)

        self.TCursors.add_plot(plot)
        self.cursorYPlot.clear()
        self.cursorYPlot.addItems([str(i) for i, p in enumerate(self.plots)])

        if channels:
            # each channel should be a {name: curve_params} dict
            for chan in channels:
                name, ckwargs = list(chan.items())[0]
                ckwargs = ckwargs or {}
                plot.add_channel(name, **ckwargs)

        # FIXME: where to add if row/col not specified?  need some
        # sort of layout policy
        self.plotLayout.addItem(
            plot, **kwargs,
        )

        # HACK: this is how to remove the "export" command from the
        # context menu
        plot.scene().contextMenu = None

        return plot

    def add_plot_handler(self, recv):
        """handler to add new plot based on signal from plotMenu"""
        ref_plot, new_loc, plot_kwargs = recv
        occupied_cells = set()
        for plot, cells in self.plotLayout.items.items():
            occupied_cells.update(cells)
            if plot == ref_plot:
                tabspec = util.cells_to_tabspec(cells)
        rowcol = (tabspec['row'], tabspec['col'])
        while rowcol in occupied_cells:
            row, col = rowcol
            if new_loc == 'row':
                col += 1
            elif new_loc == 'col':
                row += 1
            rowcol = (row, col)
        plot_kwargs['row'] = row
        plot_kwargs['col'] = col
        self.add_plot(**plot_kwargs)

    def remove_plot(self, plot):
        """remove plot from layout"""
        if len(self.plots) == 1:
            self.status_error("Can not remove last plot.")
            return
        for p, cells in self.plotLayout.items.items():
            if p == plot:
                tabspec = util.cells_to_tabspec(cells)
                if tabspec['row'] == 0 and tabspec['col'] == 0:
                    self.status_error("Can not remove (0,0) plot.")
                    return
        # first remove all channels
        # make copy of list cause we'll be changing it
        for chan in list(plot.channels.keys()):
            plot.remove_channel(chan)
        self.plotLayout.removeItem(plot)

    @property
    def plot0(self):
        return self.plots[0]

    def plots4chan(self, channel):
        """Return list of plots displaying channel"""
        plots = []
        for plot in self.plots:
            if channel in plot.channels:
                plots.append(plot)
        return plots

    def _channel_added(self, channel):
        if len(self.data.channels) == 0:
            self._initialized_ui()
        self.data.add_channel(str(channel))
        self._update_triggerSelect()

    def _channel_removed(self, channel):
        self.data.remove_channel(str(channel))
        self._update_triggerSelect()
        if len(self.data.channels) == 0:
            self._base_ui()

    ##########
    # RANGE AND SPAN

    def get_window(self):
        (xmin, xmax), (ymin, ymax) = self.plot0.viewRange()
        return xmin, xmax

    def get_range(self):
        """tuple of (start, end) times"""
        xmin, xmax = self.get_window()
        start = self.t0 + xmin
        end = self.t0 + xmax
        return start, end

    def get_span(self):
        """time span in seconds"""
        start, end = self.get_range()
        return abs(end - start)

    def preferred_trend(self):
        """preferred trend for the current time span"""
        trend = TREND_OPTIONS[self.trendSelectGroup.checkedId()]
        if trend == 'auto':
            span = self.get_span()
            if span > const.TREND_TRANS_THRESHOLD['sec/min']:
                return 'min'
            elif span > const.TREND_TRANS_THRESHOLD['raw/sec']:
                return 'sec'
            else:
                return 'raw'
        else:
            return trend

    ##########
    # UI

    def start(self, window=None):
        """Start online mode

        """
        if window:
            span = abs(min(window))
        else:
            span = self.get_span()
            window = (-span, 0)
        self.set_window(*window)
        trend = self.preferred_trend()
        if trend == 'min':
            self.status_error("Online minute trends not supported.  Try a smaller window.")
            return
        logger.info('START')
        self.data.online_start(trend, span)

    def stop(self):
        """Stop online mode

        """
        logger.info('STOP')
        self.data.online_stop()

    def _data_request(self, force=False):
        ltrend, lstart, lend = self.last_data
        trend = self.preferred_trend()
        start, end = self.get_range()
        if not force \
           and trend == ltrend \
           and start >= lstart \
           and end <= lend:
            return
        self.data.request(trend, (start, end))

    def _fetch(self, **kwargs):
        if QtWidgets.QApplication.keyboardModifiers() == Qt.ShiftModifier:
            self.data.reset()
        if 't0' in kwargs:
            t0 = kwargs['t0']
            window = kwargs['window']
            start = t0 + window[0]
            end = t0 + window[1]
        else:
            start = kwargs['start']
            end = kwargs['end']
            t0 = max(start, end)
            window = (-abs(start-end), 0)
        logger.info('FETCH: {}'.format((start, end)))
        self.triggerGroup.setChecked(False)
        self.set_t0(t0)
        self.set_window(window[0], window[1])
        self._data_request(force=True)

    def fetch(self, **kwargs):
        """Fetch data offline

        May specify `t0` and `window`, or `start` and `end`.

        """
        self.last_fetch_cmd = kwargs
        self._fetch(**kwargs)

    def reset_range(self):
        """Reset to last fetch range

        """
        logger.info('RESET')
        for plot in self.plots:
            plot.enableAutoRange(axis='y')
        if self.data.online:
            span = self.get_span()
            self.set_window(-span, 0)
        elif self.last_fetch_cmd:
            self._fetch(**self.last_fetch_cmd)

    def update_mouse(self):
        """update time range on mouse pan/zoom"""
        self.updateGPS()
        self.update_entryWindow()
        self.update_tlabel()
        self._data_request()

    def get_entryWindow(self):
        try:
            window = (
                float(self.entryWindowStart.text()),
                float(self.entryWindowEnd.text()),
            )
        except ValueError:
            return
        self.last_window = window
        return window

    def update_t0(self):
        self.update_entryT0GPS()
        try:
            t0 = float(self.entryT0GPS.text())
            window = self.get_entryWindow()
        except ValueError:
            return
        if window is None:
            return
        self._fetch(t0=t0, window=window)

    def update_window(self):
        window = self.get_entryWindow()
        if window is None:
            return
        self._set_window(*window)

    def update_range(self):
        self.update_entryStartGPS()
        self.update_entryEndGPS()
        try:
            start = float(self.entryStartGPS.text())
            end = float(self.entryEndGPS.text())
        except ValueError:
            return
        self._fetch(start=start, end=end)

    # SLOT
    def _data_online_start(self, msg):
        self._data_retrieve_start(msg)
        self.crosshairGroup.setEnabled(False)
        self.disable_crosshair()
        self.startButton.setEnabled(False)
        self.startButton2.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.stopButton2.setEnabled(True)
        self.timeAxisRelativeSelect.setChecked(True)
        self.axisTab.setEnabled(False)

    # SLOT
    def _data_retrieve_start(self, msg):
        self.status_message(msg, style="data", log=False)
        self.rangeTab.setEnabled(False)
        self.entryT0GPS.setEnabled(False)
        self.entryT0Greg.setEnabled(False)
        self.buttonT0Now.setEnabled(False)
        self.fetchButton1.setEnabled(False)
        self.fetchButton2.setEnabled(False)
        self.resetT0Button.setEnabled(False)
        self.resetT0Button2.setEnabled(False)
        self.exportTab.setEnabled(False)
        self.exportButton2.setEnabled(False)

    def _data_done_status(self, signal):
        error, active = signal
        if error:
            self.status_error(error)
        if active:
            return True
        if not error:
            self.status_clear()
        return False

    def _data_done_reset(self):
        # for plot in self.plots:
        #     plot.disableAutoRange(axis='y')
        self.rangeTab.setEnabled(True)
        self.entryT0GPS.setEnabled(True)
        self.entryT0Greg.setEnabled(True)
        self.buttonT0Now.setEnabled(True)
        self.fetchButton1.setEnabled(True)
        self.fetchButton2.setEnabled(True)
        self.resetT0Button.setEnabled(True)
        self.resetT0Button2.setEnabled(True)
        self.exportTab.setEnabled(True)
        self.exportButton2.setEnabled(True)

    # SLOT
    def _data_online_done(self, signal):
        self.crosshairGroup.setEnabled(True)
        if self.crosshairGroup.isChecked():
            self.enable_crosshair()
        self.startButton.setEnabled(True)
        self.startButton2.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.stopButton2.setEnabled(False)
        self.axisTab.setEnabled(True)
        if self._data_done_status(signal):
            return
        self._data_done_reset()

    # SLOT
    def _data_retrieve_done(self, signal):
        if self._data_done_status(signal):
            return
        self._data_done_reset()

    ##########
    # PLOTTING

    # SLOT
    def _update_plots(self, recv):
        logger.log(5, f"PLOT: {recv}")

        data, trend, online = recv

        if not data:
            logger.log(5, "CLEAR")
            for plot in self.plots:
                plot.clear_data()
            return

        # if this isn't the trend we need then drop the packet
        preferred_trend = self.preferred_trend()
        if trend != preferred_trend:
            logger.debug(f"DROP {trend} trend packet ({preferred_trend} preferred)")
            return

        self.last_data = (trend,) + data.range

        trigger = None
        if online:
            # if we're online, check for triggers
            if self.trigger.active:
                trigger = self.trigger.check(data)
                if trigger:
                    self._update_triggerTime(trigger)
                    self.set_t0(trigger)

            else:
                self.set_t0(data.range[1])

        for plot in self.plots:
            plot.update(data, self.t0)

        if trigger and self.trigger.single:
            self.stop()

    def update_tlabel(self):
        # span = self.get_span()
        # mod = ''
        # try:
        #     prec = int(np.round(np.log10(span))) - 2
        # except OverflowError:
        #     span = 2.385e-07
        #     prec = -9
        #     mod = '<'
        # sstr = '{mod}{span}'.format(
        #     mod=mod,
        #     span=util.seconds_time_str(span, prec),
        # )
        self.referenceTimeLabel.setText(
            #'t0 = {greg} [{gps:0.4f}], {span} span'.format(
            't0 = {greg} [{gps:0.4f}]'.format(
                greg=util.gpstime_str_greg(
                    util.gpstime_parse(self.t0),
                    fmt=const.DATETIME_FMT,
                ),
                gps=self.t0,
                #span=sstr,
            )
        )

    def set_t0(self, t0):
        self.t0 = t0
        logger.log(5, f"t0 = {t0}")
        self.update_tlabel()
        self.updateGPS()

    def reset_t0(self):
        start, end = self.get_range()
        t0 = (start+end)/2
        xd = (end-start)/2
        self._fetch(t0=t0, window=(-xd, xd))

    def _set_window(self, xmin, xmax):
        logger.debug('RANGE: {} {}'.format(xmin, xmax))
        self.plot0.setXRange(xmin, xmax, padding=0, update=False)

    def set_window(self, xmin, xmax):
        self._set_window(xmin, xmax)
        self.update_entryWindow()

    ##########
    # TIMES

    def updateGPS(self):
        start, end = self.get_range()
        self.set_entryT0(self.t0)
        self.set_entryStart(start)
        self.set_entryEnd(end)

    def set_entryT0(self, time=None):
        if time:
            gt = util.gpstime_parse(time)
        else:
            gt = util.gpstime_parse('now')
        self.entryT0GPS.setText(util.gpstime_str_gps(gt))
        self.entryT0Greg.setText(util.gpstime_str_greg(gt))

    def update_entryT0GPS(self):
        gt = util.gpstime_parse(self.entryT0Greg.text())
        if not gt:
            return
        self.entryT0GPS.setText(util.gpstime_str_gps(gt))

    def update_entryT0Greg(self):
        gt = util.gpstime_parse(self.entryT0GPS.text())
        if not gt:
            return
        self.entryT0Greg.setText(util.gpstime_str_greg(gt))

    def update_entryWindow(self):
        xmin, xmax = self.get_window()
        self.entryWindowStart.setText(f'{xmin:.6f}')
        self.entryWindowEnd.setText(f'{xmax:.6f}')

    def set_entryStart(self, time):
        gt = util.gpstime_parse(time)
        self.entryStartGPS.setText(util.gpstime_str_gps(gt))
        self.entryStartGreg.setText(util.gpstime_str_greg(gt))

    def set_entryEnd(self, time=None):
        if time:
            gt = util.gpstime_parse(time)
        else:
            gt = util.gpstime_parse('now')
        self.entryEndGPS.setText(util.gpstime_str_gps(gt))
        self.entryEndGreg.setText(util.gpstime_str_greg(gt))

    def update_entryStartGPS(self):
        t = self.entryStartGreg.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryStartGPS.setText(util.gpstime_str_gps(gt))

    def update_entryStartGreg(self):
        t = self.entryStartGPS.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryStartGreg.setText(util.gpstime_str_greg(gt))

    def update_entryEndGPS(self):
        t = self.entryEndGreg.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryEndGPS.setText(util.gpstime_str_gps(gt))

    def update_entryEndGreg(self):
        t = self.entryEndGPS.text()
        gt = util.gpstime_parse(t)
        if not gt:
            return
        self.entryEndGreg.setText(util.gpstime_str_greg(gt))

    ##########
    # TREND

    def _trend_select(self, button):
        trend = TREND_OPTIONS[self.trendSelectGroup.checkedId()]
        logger.debug(f"trend select: {trend}")
        if button == self.trendAutoSelect:
            self.trendThreshGroup.setEnabled(True)
        else:
            self.trendThreshGroup.setEnabled(False)
        self._data_request()
        # if self.data.online:
        #     self.data.online_restart()
        # else:
        #     self._data_request()

    def _set_trend_rawsec(self, *args):
        const.TREND_TRANS_THRESHOLD['raw/sec'] = int(self.trendRawSecThresh.text())

    def _set_trend_secmin(self, *args):
        const.TREND_TRANS_THRESHOLD['sec/min'] = int(self.trendSecMinThresh.text())

    ##########
    # AXIS

    def time_axis_select(self, mode):
        logger.debug(f"time axis select: {mode}")
        for plot in self.plots:
            plot.axes['bottom']['item'].setTickStringsMode(mode)
        if mode == 'relative':
            self.referenceTimeLabel.show()
        else:
            self.referenceTimeLabel.hide()

    ##########
    # TRIGGER

    def set_trigger_channel(self, channel):
        """set the trigger channel"""
        assert channel in self.data.channels + [None]
        if channel == self.trigger.channel:
            return
        if self.trigger.channel is not None:
            tplot = self.plots4chan(self.trigger.channel)[0]
        else:
            tplot = None
        if channel is not None:
            nplot = self.plots4chan(channel)[0]
        else:
            nplot = None
        self.trigger.channel = channel
        if nplot != tplot:
            if tplot:
                tplot.removeItem(self.trigger.line)
            if nplot:
                nplot.addItem(self.trigger.line, ignoreBounds=True)
                nplot.disableAutoRange(axis='y')
            return True
        else:
            return False

    def _update_trigger_channel(self):
        """update trigger channel from menu select"""
        chan = str(self.triggerSelect.currentText())
        if self.set_trigger_channel(chan):
            self.reset_trigger_level()
        logger.info("trigger set: {}".format(chan))

    def _update_triggerSelect(self):
        """update the trigger channel select menu"""
        try:
            self.triggerSelect.currentIndexChanged.disconnect(self._update_trigger_channel)
        except TypeError:
            pass
        self.triggerSelect.clear()
        self.triggerSelect.addItems(self.data.channels)
        self.triggerSelect.currentIndexChanged.connect(self._update_trigger_channel)

    def set_trigger_level(self, level):
        """set trigger level"""
        self.trigger.set_level(level)

    def _update_triggerLevel(self):
        """update trigger level text entry on mouse level change"""
        self.triggerLevel.setText('{:g}'.format(self.trigger.level))

    def _set_trigger_level(self):
        """set the trigger level from text entry return press"""
        value = float(self.triggerLevel.text())
        self.set_trigger_level(value)

    def reset_trigger_level(self):
        """reset the trigger level to the midpoint of the range"""
        chan = self.trigger.channel
        if self.data['raw'] and chan in self.data['raw']:
            y = self.data['raw'][chan].data['raw']
            yn = y[np.where(np.invert(np.isnan(y)))[0]]
            value = np.mean(yn)
        else:
            value = 0
        self.set_trigger_level(value)

    def enable_trigger(self):
        """enable trigger"""
        chan = str(self.triggerSelect.currentText())
        self.set_trigger_channel(chan)
        self.reset_trigger_level()
        span = self.get_span()
        self.set_window(-span/2, span/2)
        logger.info("trigger enabled")

    def disable_trigger(self):
        """disable trigger"""
        self.set_trigger_channel(None)
        span = self.get_span()
        self.set_window(-span, 0)
        logger.info("trigger disabled")

    def _toggle_trigger(self):
        """toggle trigger on/off"""
        if not self.trigger:
            return
        if self.triggerGroup.isChecked():
            self.enable_trigger()
        else:
            self.disable_trigger()

    def _update_triggerTime(self, time):
        """update trigger time label (from trigger)"""
        self.triggerTime.setText('{:14.6f}'.format(time))

    ##########
    # CROSSHAIR

    def _connect_crosshair(self):
        """connect the crosshair update signal handler"""
        self._crosshair_proxy = pg.SignalProxy(
            self.graphView.scene().sigMouseMoved,
            rateLimit=20,
            slot=self._update_crosshair)

    def _enable_crosshair(self):
        """enable crosshair, base method"""
        for plot in self.plots:
            plot.disableAutoRange(axis='y')
        self._connect_crosshair()
        self.graphView.scene().sigMouseClicked.connect(self._clicked_crosshair)
        self.graphView.setCursor(Qt.CrossCursor)
        logger.info("crosshair enabled")

    def enable_crosshair(self):
        """enable crosshair"""
        if self.crosshairGroup.isChecked():
            return
        self._enable_crosshair()
        self.crosshairGroup.setChecked(True)

    def _disable_crosshair(self):
        """disable crosshair, base method"""
        self.Crosshair.set_active_plot(None)
        self._crosshair_proxy = None
        try:
            self.graphView.scene().sigMouseClicked.disconnect(self._clicked_crosshair)
        except TypeError:
            pass
        self.graphView.setCursor(Qt.ArrowCursor)
        self.crosshairGPS.setText('')
        self.crosshairGreg.setText('')
        self.crosshairYValue.setText('')
        logger.info("crosshair disabled")

    def disable_crosshair(self):
        """disable crosshair"""
        if not self.crosshairGroup.isChecked():
            return
        self.crosshairGroup.setChecked(False)
        self._disable_crosshair()

    def _toggle_crosshair(self):
        """toggle crosshair on/off"""
        if self.crosshairGroup.isChecked():
            self._enable_crosshair()
        else:
            self._disable_crosshair()

    def _update_crosshair(self, event):
        """update crosshair on mouse move"""
        # using signal proxy unfortunately turns the original
        # arguments into a tuple pos = event
        pos = event[0]
        for plot in self.plots:
            if plot.sceneBoundingRect().contains(pos):
                break
        self.Crosshair.update(pos, plot, self.t0)

    def _update_crosshair_entry(self, recv):
        t, greg, y = recv
        self.crosshairGPS.setText(str(t))
        self.crosshairGreg.setText(greg)
        self.crosshairYValue.setText(str(y))

    def _clicked_crosshair(self, event):
        """drop crosshair on click, pickup on click"""
        if event.button() != 1:
            return
        if self._crosshair_proxy is None:
            self._connect_crosshair()
        else:
            self._crosshair_proxy = None

    ##########
    # CURSORS

    def enable_t_cursors(self):
        """enable the time cursor"""
        self.TCursors.enable()
        logger.info("T-cursor enabled")

    def disable_t_cursors(self):
        """disable the time cursor"""
        self.TCursors.disable()
        logger.info("T-cursor disabled")

    def _toggle_t_cursors(self):
        """toggle T cursor on/off"""
        if self.cursorTGroup.isChecked():
            self.enable_t_cursors()
        else:
            self.disable_t_cursors()

    def _set_y_cursors_plot(self):
        """set plot for Y cursors"""
        if not self.cursorYGroup.isChecked():
            return
        ind = self.cursorYPlot.currentText()
        if ind:
            plot = self.plots[int(ind)]
            self.YCursors.set_plot(plot)

    def enable_y_cursors(self):
        """enable Y cursors"""
        self._set_y_cursors_plot()
        logger.info("Y-cursor enabled")

    def disable_y_cursors(self):
        """disable Y cursors"""
        self.YCursors.set_plot(None)
        logger.info("Y-cursor disabled")

    def _toggle_y_cursors(self):
        if self.cursorYGroup.isChecked():
            self.enable_y_cursors()
        else:
            self.disable_y_cursors()

    ##########
    # STYLE

    def font_select_dialog(self):
        font, ok = QFontDialog.getFont(self.font)
        if ok:
            self.set_font(font)

    def _background_select(self, state):
        if state == Qt.Checked:
            self.set_background('w')
        else:
            self.set_background('k')

    ##########
    # EXPORT

    def _export_dialog(self):
        """export save file dialog"""
        path = export.export_dialog(
            QFileDialog.getSaveFileName,
            self,
            self.exportPath.text(),
        )
        if not path:
            return
        self.exportPath.setText(path)
        return path

    def export(self, path=None):
        """Export plot scene, data, or layout to file.

        Supports PNG, SVG, PDF image formats, HDF5 for data, and YAML for
        layout.  A file select dialog will be presented if a path is not
        supplied.

        """
        if not path:
            path = self._export_dialog()
            if not path:
                return
        if not path or os.path.isdir(path):
            self.status_error(f"Must specify file path.")
            return
        ext = os.path.splitext(path)[1]
        if ext in [None, '']:
            self.status_error(f"Must specify export file extension.")
            return
        self.status_message(f"Writing file {path}...", timeout=10)
        self.exportPath.setText(path)
        QTimer.singleShot(1, self._export)
        # we do this timer thing so that the event loop will display
        # the above status message, in case it takes some time to
        # render/construct the output

    def _export(self):
        path = self.exportPath.text()
        ext = os.path.splitext(path)[1]

        if ext in export.IMAGE_EXPORT_FUNCTIONS:
            obj = 'scene'
            export_func = export.IMAGE_EXPORT_FUNCTIONS[ext]
            args = (
                self.graphView.scene(),
                path,
            )
            kwargs = dict()

        elif ext in export.DATA_EXPORT_FUNCTIONS:
            obj = 'data'
            export_func = export.DATA_EXPORT_FUNCTIONS[ext]
            trend = self.data.last_trend
            args = (
                self.data.db[trend],
                path,
                *self.get_range()
            )
            kwargs = dict(
                t0=self.t0,
                window=self.get_window(),
            )

        elif ext in export.TEMPLATE_EXPORT_FUNCTIONS:
            obj = 'layout'
            export_func = export.TEMPLATE_EXPORT_FUNCTIONS[ext]
            args = (
                self.plotLayout.items,
                path,
            )
            kwargs = dict(
                bw=(self.backgroundCheckBox.checkState() == Qt.Checked),
                window_title=self.windowTitle().replace('ndscope: ', ''),
                time_window=self.get_window(),
                font_size=self.font.pointSize(),
            )

        else:
            self.status_error(f"Unsupported export file extension: {ext}")
            return

        try:
            export_func(*args, **kwargs)
        except Exception as e:
            logger.info(traceback.format_exc())
            self.status_error(str(e))
            return

        ftype = ext[1:].upper()
        self.status_message(f"Exported {obj} to {ftype}: {path}", timeout=10)

    def _export2Handler(self, path=None):
        path = self.exportPath.text()
        self.export(path)

    def _exportShowHandler(self):
        path = self.exportPath.text()
        if not path or not os.path.exists(path):
            self.status_error("No path, or no file at path.  Export first.")
            return
        ext = os.path.splitext(path)[1]
        if ext in ['.hdf5', '.h5']:
            export.matplot_h5(path)
        else:
            try:
                subprocess.Popen(['xdg-open', path])
            except FileNotFoundError:
                self.status_error("xdg-open binary not found.  Please install 'xdg-utils' package.")
            # FIXME: catch open errors even though process backgrounded?
