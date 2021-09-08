# plot with processing capabilities

from PyQt5.QtWidgets import QCheckBox, QSpinBox, QDoubleSpinBox, QLabel, QPushButton,\
    QSpacerItem, QSizePolicy, QGroupBox, QGridLayout
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtProperty

from .auxwidgets import BaseGridW, VLine
import json
import pyqtgraph as pg
import pycx4.qcda as cda
import time
import numpy as np
import datetime


class CXPlotDataItem(pg.PlotDataItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cname = kwargs.get('cname', None)
        self.max_nelems = kwargs.get('max_nelems', 4096)
        self.chan = cda.VChan(self._cname, max_nelems=self.max_nelems, private=True)
        self.chan.valueMeasured.connect(self.cs_update)
        self._sampling_time = 4.0
        self._start_time = 0.0
        end_time = self.max_nelems * self._sampling_time + self._start_time
        self.xd = np.arange(start=self._start_time, stop=end_time, step=self._sampling_time)
        self.last_data_len = None

    def cs_update(self, chan):
        self.last_data_len = chan.nelems
        self.setData(x=self.xd[:chan.nelems], y=chan.val)

    @pyqtSlot(float)
    def setSamplingTime(self, new_time):
        self.timer.setInterval(new_time)

    def getSamplingTime(self):
        return self.timer.interval()

    sampling_time = pyqtProperty(float, getSamplingTime, setSamplingTime)



class CXPlotToolboxS(BaseGridW):
    def __init__(self):
        super().__init__()
        self.gb_general = QGroupBox('General processing')
        self.grid.addWidget(self.gb_general, 0, 0)
        self.gen_grid = QGridLayout()
        self.gb_general.setLayout(self.gen_grid)

        self.gen_grid.addWidget(QLabel('Averaging'), 0, 0)
        self.avg_spinbox = QSpinBox()
        self.avg_spinbox.setValue(1)
        self.avg_spinbox.setRange(1, 100)
        self.gen_grid.addWidget(self.avg_spinbox, 0, 1)

        self.getBgButton = QPushButton('get BG')
        self.gen_grid.addWidget(self.getBgButton, 1, 0)
        self.bg_checkbox = QCheckBox("apply bg")
        self.gen_grid.addWidget(self.bg_checkbox, 1, 1)

        self.clb_checkbox = QCheckBox("apply clb")
        self.gen_grid.addWidget(self.clb_checkbox, 2, 0)

        self.saveDataButton = QPushButton('Save data')
        self.gen_grid.addWidget(self.saveDataButton, 2, 1)

        # selected region tools
        self.gb_region = QGroupBox('Region processing')
        self.grid.addWidget(self.gb_region, 1, 0)
        self.reg_grid = QGridLayout()
        self.gb_region.setLayout(self.reg_grid)

        self.reg_checkbox = QCheckBox("proc region")
        self.reg_grid.addWidget(self.reg_checkbox, 0, 0)
        self.edges_label = QLabel("[0, 0]")
        self.reg_grid.addWidget(self.edges_label, 0, 1)

        self.reg_grid.addWidget(QLabel("reg avg"), 1, 0)
        self.reg_avg_label = QLabel("0.0")
        self.reg_grid.addWidget(self.reg_avg_label, 1, 1)

        self.grid.addItem(QSpacerItem(50, 500, vPolicy=QSizePolicy.Maximum), 2, 0)



class CXProcPlot(BaseGridW):
    def __init__(self, chan_or_name, sig_name='', t_step=1, calibr=None):
        super().__init__()
        self.sig_name = sig_name
        if isinstance(chan_or_name, cda.VPChan):
            self.chan = chan_or_name
        elif isinstance(chan_or_name, str):
            self.chan = cda.VPChan(chan_or_name, dtype=cda.DTYPE_SINGLE, max_nelems=783155, private=True)
        else:
            # need to raise exception here
            pass
        self.calibr = calibr
        self.t_step = t_step

        self.chan.valueMeasured.connect(self.update_plot)
        self.chan.bgReady.connect(self.bg_ready)

        self.draw_bg_val = False

        self.resize(1200, 800)

        self.toolbox = CXPlotToolboxS()
        self.grid.addWidget(self.toolbox, 0, 0)
        self.toolbox.avg_spinbox.valueChanged.connect(self.set_avg)
        self.toolbox.getBgButton.clicked.connect(self.get_bg)
        self.toolbox.bg_checkbox.stateChanged.connect(self.bg_apply)
        self.toolbox.saveDataButton.clicked.connect(self.save_data)

        self.toolbox.reg_checkbox.stateChanged.connect(self.region_proc)

        self.pen = (0, 255, 0)
        self.graph = pg.GraphicsLayoutWidget(parent=self)
        self.grid.addWidget(self.graph, 0, 1)
        self.plt = self.graph.addPlot(title=sig_name, autoDownsample=True)
        self.plt.disableAutoRange()
        self.plt.showGrid(x=True, y=True)
        self.curv = self.plt.plot(pen=self.pen)
        self.pen_avg = (100, 100, 100)
        self.curv_avg = self.plt.plot(pen=self.pen_avg)


    def update_plot(self, chan):
        v = chan.bg_val if self.draw_bg_val else chan.val
        if self.toolbox.clb_checkbox.isChecked() and self.sig_name in self.calibr:
            clb = self.calibr
            self.data = clb[0] * v * v + clb[1] * v
        else:
            self.data = v
        self.curv.setData(self.data)
        if self.toolbox.reg_checkbox.isChecked():
            self.toolbox.reg_avg_label.setText('{:2.5f}'.format(self.chan.reg_avg))

    def plot_avg(self, chan):
        self.curv_avg.setData(chan.avg_aval)

    def set_avg(self, n_avg):
        self.chan.setAveraging(n_avg)
        if n_avg == 1:
            self.curv_avg.clear()
        else:
            self.chan.avgReady.connect(self.plot_avg)

    def get_bg(self):
        self.chan.getBg(100)

    def bg_ready(self, chan):
        print('bg ready')

    def bg_apply(self, state):
        self.draw_bg_val = bool(state)
        self.chan.setBgApply(state)

    def save_data(self):
        print('saving data')
        out_data = {self.sig_name: self.data.tolist()}
        f = open(self.sig_name + "_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".json", 'w')
        json.dump(out_data, f)
        f.close()

    def region_proc(self, state):
        if state:
            self.lr = pg.LinearRegionItem([300, 1300])
            self.lr.setZValue(-10)
            self.lr.sigRegionChangeFinished.connect(self.region_changed)
            self.plt.addItem(self.lr)
            self.region_changed(self.lr)
        else:
            self.plt.removeItem(self.lr)

    def region_changed(self, l_reg):
        region = l_reg.getRegion()
        self.toolbox.edges_label.setText('[' + str(int(region[0])) + ', ' + str(int(region[1])) + ']')
        self.chan.setRegProc(int(region[0]), int(region[1]))