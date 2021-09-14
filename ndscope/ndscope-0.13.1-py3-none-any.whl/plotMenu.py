import os
import weakref
import logging

try:
    from qtpy import QtCore, QtGui, QtWidgets, uic
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic

from .const import CHANNEL_REGEXP, CHANNEL_RE


AxisCtrlTemplate, __ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'axisCtrlTemplate.ui'))


class AxisCtrlMenu(QtWidgets.QMenu, AxisCtrlTemplate):
    def __init__(self, title, mainmenu):
        super(AxisCtrlMenu, self).__init__(title, mainmenu)
        self.setupUi(self)
        self.mouseCheck.toggled.connect(mainmenu.yMouseToggled)
        self.manualRadio.clicked.connect(mainmenu.yManualClicked)
        self.minText.setValidator(QtGui.QDoubleValidator())
        self.minText.editingFinished.connect(mainmenu.yRangeTextChanged)
        self.maxText.setValidator(QtGui.QDoubleValidator())
        self.maxText.editingFinished.connect(mainmenu.yRangeTextChanged)
        self.autoRadio.clicked.connect(mainmenu.yAutoClicked)
        self.autoPercentSpin.valueChanged.connect(mainmenu.yAutoSpinChanged)
        self.autoPanCheck.toggled.connect(mainmenu.yAutoPanToggled)
        self.visibleOnlyCheck.toggled.connect(mainmenu.yVisibleOnlyToggled)


# this is lifted from the pqtgraph.ViewBoxMenu module
class NDScopePlotMenu(QtWidgets.QMenu):
    def __init__(self, plot):
        QtWidgets.QMenu.__init__(self)
        # keep weakref to view to avoid circular reference (don't know
        # why, but this prevents the ViewBox from being collected)
        self.plot = weakref.ref(plot)
        self.view = weakref.ref(plot.getViewBox())
        self.viewMap = weakref.WeakValueDictionary()

        self.setTitle("plot options")

        # view all data
        self.viewAll = QtWidgets.QAction("view all data", self)
        self.viewAll.triggered.connect(self.autoRange)
        self.addAction(self.viewAll)

        self.yAxisUI = AxisCtrlMenu("Y axis", self)
        self.addMenu(self.yAxisUI)

        self.mouseMenu = QtWidgets.QMenu("mouse mode")
        group = QtWidgets.QActionGroup(self)
        # This does not work! QAction _must_ be initialized with a permanent
        # object as the parent or else it may be collected prematurely.
        #pan = self.leftMenu.addAction("3 button", self.set3ButtonMode)
        #zoom = self.leftMenu.addAction("1 button", self.set1ButtonMode)
        pan = QtWidgets.QAction("pan/zoom", self.mouseMenu)
        rect = QtWidgets.QAction("zoom box", self.mouseMenu)
        self.mouseMenu.addAction(pan)
        self.mouseMenu.addAction(rect)
        pan.triggered.connect(self.setMouseModePan)
        rect.triggered.connect(self.setMouseModeRect)
        pan.setCheckable(True)
        rect.setCheckable(True)
        pan.setActionGroup(group)
        rect.setActionGroup(group)
        self.mouseModes = [pan, rect]
        self.addMenu(self.mouseMenu)

        self.addLabel()
        try:
            self.addSection("add/remove channels")
        except:
            self.addSeparator()
            self.addLabel("add/remove channel")
        self.addLabel()

        # self.ptree = ParameterTree()
        # pa = QtWidgets.QWidgetAction(self)
        # pa.setDefaultWidget(self.ptree)
        # self.addAction(pa)

        # add channel
        self.addChannelEntry = QtWidgets.QLineEdit()
        self.addChannelEntry.setMinimumSize(300, 24)
        self.addChannelEntry.setPlaceholderText("enter channel to add")
        self.addChannelEntry.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(CHANNEL_REGEXP)))
        self.addChannelEntry.textChanged.connect(self.validate_add)
        # self.addChannelEntry.returnPressed.connect(self.add_channel)
        self.addChannelEntry.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        acea = QtWidgets.QWidgetAction(self)
        acea.setDefaultWidget(self.addChannelEntry)
        self.addAction(acea)

        self.addChannelButton = self.addButton("add channel to plot")
        self.addChannelButton.setEnabled(False)
        self.addChannelButton.clicked.connect(self.add_channel)

        self.addLabel()

        # remove channel
        self.removeChannelList = QtWidgets.QComboBox()
        self.removeChannelList.setMinimumSize(200, 26)
        self.removeChannelList.currentIndexChanged.connect(self.remove_channel)
        # self.removeChannelList.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        rcl = QtWidgets.QWidgetAction(self)
        rcl.setDefaultWidget(self.removeChannelList)
        self.addAction(rcl)

        self.addLabel()
        self.addSection("add/remove plot")
        self.addLabel()

        self.newPlotRowButton = self.addButton("add plot to row")
        self.newPlotRowButton.clicked.connect(self.new_plot_row)

        self.newPlotColButton = self.addButton("add plot to column")
        self.newPlotColButton.clicked.connect(self.new_plot_col)

        self.addLabel()

        self.removePlotButton = self.addButton("remove plot")
        self.removePlotButton.clicked.connect(self.remove_plot)

        self.addLabel()

        self.addSeparator()

        self.setContentsMargins(10, 10, 10, 10)

        self.view().sigStateChanged.connect(self.viewStateChanged)
        self.updateState()

    ##########

    def addLabel(self, label=''):
        ql = QtWidgets.QLabel()
        ql.setText(label)
        ql.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        qla = QtWidgets.QWidgetAction(self)
        qla.setDefaultWidget(ql)
        self.addAction(qla)

    def addButton(self, label):
        button = QtWidgets.QPushButton(label)
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(button)
        self.addAction(action)
        return button

    ##########

    def viewStateChanged(self):
        self.valid = False
        if self.yAxisUI.minText.isVisible():
            self.updateState()

    def updateState(self):
        # Something about the viewbox has changed; update the menu GUI

        state = self.view().getState(copy=False)
        if state['mouseMode'] == self.view().PanMode:
            self.mouseModes[0].setChecked(True)
        else:
            self.mouseModes[1].setChecked(True)

        i = 1
        tr = state['targetRange'][i]
        self.yAxisUI.minText.setText("%0.5g" % tr[0])
        self.yAxisUI.maxText.setText("%0.5g" % tr[1])
        if state['autoRange'][i] is not False:
            self.yAxisUI.autoRadio.setChecked(True)
            if state['autoRange'][i] is not True:
                self.yAxisUI.autoPercentSpin.setValue(state['autoRange'][i]*100)
        else:
            self.yAxisUI.manualRadio.setChecked(True)
        self.yAxisUI.mouseCheck.setChecked(state['mouseEnabled'][i])

        self.yAxisUI.autoPanCheck.setChecked(state['autoPan'][i])
        self.yAxisUI.visibleOnlyCheck.setChecked(state['autoVisibleOnly'][i])
        self.yAxisUI.invertCheck.setChecked(state.get('yInverted', False))

        self.valid = True

    def popup(self, *args):
        if not self.valid:
            self.updateState()

        # update remove channels list
        self.update_channel_list()

        # see if there's a channel in the clipboard
        channel = QtWidgets.QApplication.clipboard().text(
            mode=QtGui.QClipboard.Selection)

        # if we have a channel add it to the label
        if CHANNEL_RE.match(channel):
            self.addChannelEntry.setText(channel)
        else:
            self.addChannelEntry.setText('')

        # FIXME: only remove plot if it's not the last
        # if numplots > 1:
        #     self.removePlotButton.setEnabled(True)

        # cparams = {chan:c.params for chan, c in self.plot().channels.items()}
        # self.ptree.setParameters(
        #     parameters.create_channels_params(cparams),
        #     showTop=False,
        # )

        QtWidgets.QMenu.popup(self, *args)

    ##########

    def autoRange(self):
        # don't let signal call this directly--it'll add an unwanted argument
        self.view().autoRange()

    ##########

    def update_channel_list(self):
        channels = list(self.plot().channels.keys())
        self.removeChannelList.clear()
        ls = ['remove channel'] + channels
        self.removeChannelList.addItems(ls)
        self.removeChannelList.insertSeparator(1)

    def validate_add(self):
        channel = str(self.addChannelEntry.text())
        if CHANNEL_RE.match(channel):
            if channel in self.plot().channels:
                self.addChannelEntry.setStyleSheet("background: #87b5ff;")
                self.addChannelButton.setEnabled(False)
            else:
                self.addChannelEntry.setStyleSheet("font-weight: bold; background: #90ff8c;")
                self.addChannelButton.setEnabled(True)
        else:
            self.addChannelEntry.setStyleSheet('')
            self.addChannelButton.setEnabled(False)

    def add_channel(self):
        channel = str(self.addChannelEntry.text())
        if CHANNEL_RE.match(channel):
            self.plot().add_channel(channel)
        self.close()

    def remove_channel(self, *args):
        self.removeChannelList.currentIndexChanged.disconnect(self.remove_channel)
        channel = str(self.removeChannelList.currentText())
        self.plot().remove_channel(channel)
        self.removeChannelList.currentIndexChanged.connect(self.remove_channel)
        self.close()

    def new_plot_row(self):
        self.new_plot('row')

    def new_plot_col(self):
        self.new_plot('col')

    def new_plot(self, rowcol):
        channel = str(self.addChannelEntry.text())
        kwargs = {}
        if CHANNEL_RE.match(channel):
            kwargs['channels'] = [{channel: None}]
        self.plot().new_plot_request.emit(
            (self.plot(), rowcol, kwargs),
        )
        self.close()

    def remove_plot(self):
        self.plot().remove_plot_request.emit(self.plot())
        self.close()

    ##########

    def setMouseModePan(self):
        self.view().setLeftButtonAction('pan')

    def setMouseModeRect(self):
        self.view().setLeftButtonAction('rect')

    def yMouseToggled(self, b):
        self.view().setMouseEnabled(y=b)

    def yManualClicked(self):
        self.view().enableAutoRange(self.view().YAxis, False)

    def yRangeTextChanged(self):
        self.yAxisUI.manualRadio.setChecked(True)
        try:
            self.view().setYRange(float(self.yAxisUI.minText.text()), float(self.yAxisUI.maxText.text()), padding=0)
        except ValueError as e:
            logging.error(f"Y range: {e}")

    def yAutoClicked(self):
        val = self.yAxisUI.autoPercentSpin.value() * 0.01
        self.view().enableAutoRange(self.view().YAxis, val)

    def yAutoSpinChanged(self, val):
        self.yAxisUI.autoRadio.setChecked(True)
        self.view().enableAutoRange(self.view().YAxis, val*0.01)

    def yAutoPanToggled(self, b):
        self.view().setAutoPan(y=b)

    def yVisibleOnlyToggled(self, b):
        self.view().setAutoVisible(y=b)

    def yInvertToggled(self, b):
        self.view().invertY(b)
