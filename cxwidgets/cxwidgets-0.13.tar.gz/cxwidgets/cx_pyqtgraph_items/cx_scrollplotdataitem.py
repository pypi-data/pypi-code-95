from PyQt5.QtCore import QTimer, pyqtSlot, pyqtProperty
import datetime
import time
import pyqtgraph as pg
import pycx4.qcda as cda
import numpy as np


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = kwargs.get('format', "%H:%M:%S.%f")

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime(self.format) for value in values]


class AgeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = kwargs.get('format', "%H:%M:%S.%f")

    def tickStrings(self, values, scale, spacing):
        ct = time.time() + time.timezone
        return [datetime.datetime.fromtimestamp(ct-value).strftime(self.format) for value in values]


# simple but not very optimized
class CXScrollPlotDataItem(pg.PlotDataItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cname = kwargs.get('cname', None)
        self.length = kwargs.get('length', 1000)
        self.time_depth = kwargs.get('time_depth', 1000)

        self.window = 0
        self.yd = np.zeros(self.length)
        self.xd = np.zeros(self.length)
        self.cur_yd = self.yd
        self.cur_xd = self.xd
        self.chan = cda.DChan(self._cname, private=True, on_update=True)
        self.chan.valueMeasured.connect(self.cs_update)
        self.n_update = 0

        self.setDownsampling(auto=True, method='peak')

        self.timer = QTimer()
        self.timer.start(self.update_time)
        self.update_time = kwargs.get('utime', 1000)
        self.timer.timeout.connect(self.plot_update)

    def cs_update(self, chan):
        self.cur_yd[0] = chan.val
        self.cur_yd = np.roll(self.cur_yd, -1)
        self.cur_xd[0] = chan.time/1e6
        self.cur_xd = np.roll(self.cur_xd, -1)
        if self.n_update < self.length:
            self.n_update += 1

    def plot_update(self):
        if self.n_update < self.length:
            self.setData(self.cur_xd[-1 * self.n_update:], self.cur_yd[-1 * self.n_update:])
        else:
            self.setData(self.cur_xd, self.cur_yd)

    @pyqtSlot(int)
    def set_update_time(self, new_time):
        self.timer.setInterval(new_time)

    def get_update_time(self):
        return self.timer.interval()

    update_time = pyqtProperty(int, get_update_time, set_update_time)


class CXScrollAgePlotDataItem(pg.PlotDataItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cname = kwargs.get('cname', None)
        self.length = kwargs.get('length', 1000)
        self.time_depth = kwargs.get('time_depth', 1000)

        self.window = 0
        self.data = np.zeros((2,self.length))
        self.cur_data = self.data
        self.chan = cda.DChan(self._cname, private=True, on_update=True)
        self.chan.valueMeasured.connect(self.cs_update)
        self.n_update = 0

        self.setDownsampling(auto=True, method='peak')

        self.timer = QTimer()
        self.timer.start(self.update_time)
        self.update_time = kwargs.get('utime', 1000)
        self.timer.timeout.connect(self.plot_update)
        self.ltime = 0

    def cs_update(self, chan):
        self.cur_data[0][0] = chan.val
        self.cur_data[1][0] = chan.time/1e6
        self.cur_data = np.roll(self.cur_data, -1)
        self.ltime = chan.time/1e6
        if self.n_update < self.length:
            self.n_update += 1

    def plot_update(self):
        if self.n_update < self.length:
            self.setData(self.ltime-self.cur_data[0][-1 * self.n_update:], self.cur_data[1][-1 * self.n_update:])
        else:
            self.setData(self.ltime-self.cur_data[0], self.cur_data[1])

    @pyqtSlot(int)
    def set_update_time(self, new_time):
        self.timer.setInterval(new_time)

    def get_update_time(self):
        return self.timer.interval()

    update_time = pyqtProperty(int, get_update_time, set_update_time)


# need to create composite item?
class CXComositeScrollAgePlotDataItem():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_item = kwargs.get('plot', None)
        self._cname = kwargs.get('cname', None)
        self.chan = cda.DChan(self._cname, private=True, on_update=True)
        self.chan.valueMeasured.connect(self.cs_update)

        self.max_chunks = 10
        self.chunk_size = 100
        self.chunk_ind = 0
        self.curves = []
        self.cdata = np.zeros((2, self.chunk_size))
        self.ind = 0

    def cs_update(self, chan):
        self.cdata[0][self.ind] = chan.val
        self.cur_data[1][self.ind] = chan.time/1e6
        self.ltime = chan.time/1e6
        self.ind += 1
        if self.ind == self.chunk_size:
            self.ind = 0
            self.chunk_ind += 1
            if self.chunk_ind == len(self.curves) and self.chunk_ind < self.max_chunks:
                self.curves.append()


    def plot_update(self):
        #start_time =
        self.curves[self.chunk_ind].setData()
        for x in self.curves:
            x.setPos()


    def setPlot(self, plot):
        self.plot_item = plot

    def addChunk(self):
        self.curves.append(pg.PlotDataItem())
        self.plot_item.self.curves[-1]

# def update3():
#     global p5, data5, ptr5, curves
#     now = pg.ptime.time()
#     for c in curves:
#         c.setPos(-(now - startTime), 0)
#
#     i = ptr5 % chunkSize
#     if i == 0:
#         curve = p5.plot()
#         curves.append(curve)
#         last = data5[-1]
#         data5 = np.empty((chunkSize + 1, 2))
#         data5[0] = last
#         while len(curves) > maxChunks:
#             c = curves.pop(0)
#             p5.removeItem(c)
#     else:
#         curve = curves[-1]
#     data5[i + 1, 0] = now - startTime
#     data5[i + 1, 1] = np.random.normal()
#     curve.setData(x=data5[:i + 2, 0], y=data5[:i + 2, 1])
#     ptr5 += 1
#
#
