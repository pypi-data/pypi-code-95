#!/usr/bin/env python3
import sys
from cxwidgets.aQt import QtWidgets, QtCore, QtGui
from cxwidgets.aQt.QtCore import Qt
import pyqtgraph as pg
from cxwidgets.auxwidgets import BaseFrameGridW
import math


class BPMScopeItem(pg.GraphicsObject):
    def __init__(self, **kwargs):
        super().__init__()
        self.x_size = kwargs.get('xsize', 200)
        self.z_size = kwargs.get('zsize', 200)
        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setPen(pg.mkPen('g'))
        p.drawEllipse(0, 0, self.x_size, self.z_size)
        p.drawEllipse(self.x_size/4, self.z_size/4, self.x_size/2, self.z_size/2)
        p.drawLine(self.x_size/2, 0, self.x_size/2, self.z_size)
        p.drawLine(0, self.z_size/2, self.x_size, self.z_size/2)
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class BPMGridItem(pg.GraphicsObject):
    def __init__(self, **kwargs):
        super().__init__()
        self.x_size = kwargs.get('xsize', 200)
        self.z_size = kwargs.get('zsize', 200)
        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)

        p.setPen(pg.mkPen(200, 200, 200))
        for ind in range(1, 10):
            p.drawLine(ind * self.x_size/10, 0, ind * self.x_size/10, self.z_size)
            p.drawLine(0, ind * self.z_size/10, self.x_size, ind * self.z_size/10)

        p.setPen(pg.mkPen(0, 0, 0))
        p.drawLine(self.x_size/2, 0, self.x_size/2, self.z_size)
        p.drawLine(0, self.z_size/2, self.x_size, self.z_size/2)
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class BeamItem(pg.GraphicsObject):
    def __init__(self, **kwargs):
        super().__init__()
        self.size = kwargs.get('size', 20)
        self.color = kwargs.get('color', "#ff0000")
        self.x0 = kwargs.get('x0', 0)
        self.z0 = kwargs.get('z0', 0)
        self.x = 0
        self.z = 0

        self.updateBeamPos()
        self._color = QtGui.QColor(self.color)
        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)

        r = self.size/2
        gradient = QtGui.QRadialGradient(r, r, r, r, r)
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, self._color)
        brush = QtGui.QBrush(gradient)
        p.setPen(self._color)
        p.setBrush(brush)
        p.drawEllipse(0, 0, self.size, self.size)
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

    def updateBeamPos(self):
        self.setPos(self.x0 - self.size/2 + self.x, self.z0 - self.size/2 - self.z)

    def setBeamPos(self, x, z):
        self.x, self.z = x, z
        self.updateBeamPos()


class BPMView(pg.GraphicsView):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.x_size = kwargs.get('xsize', 200)
        self.z_size = kwargs.get('zsize', 200)
        self.x_max = kwargs.get('xmax', 20)
        self.z_max = kwargs.get('zmax', 20)
        self.use_scope = kwargs.get('use_scope', False)
        self.use_grid = kwargs.get('use_grid', True)
        self.beam_color = kwargs.get('beam_color', "#00ff00")

        self.setFixedSize(self.x_size, self.z_size)
        self.setAspectLocked(True)
        self.setBackground('w')

        if self.use_scope:
            self.bpm_scope = BPMScopeItem(xsize=self.x_size, zsize=self.z_size)
            self.addItem(self.bpm_scope)

        if self.use_grid:
            self.bpm_grid = BPMGridItem(xsize=self.x_size, zsize=self.z_size)
            self.addItem(self.bpm_grid)

        self.beam = BeamItem(x0=self.x_size/2, z0=self.z_size/2, color=self.beam_color)
        self.addItem(self.beam)

        self.beam_x, self.beam_z = 0, 0
        self.scale_x = self.x_size / (2.0 * self.x_max)
        self.scale_z = self.z_size / (2.0 * self.z_max)

    def setBeamXZ(self, x, z):
        self.beam.setBeamPos(x * self.scale_x, z * self.scale_z)

    def sizeHint(self):
        return QtCore.QSize(self.x_size + 5, self.z_size + 5)

    def minimumSizeHint(self):
        #return QtCore.QSize(self.x_size + 10, self.z_size + 10)
        return QtCore.QSize(self.x_size, self.z_size)


class BPMWidget(BaseFrameGridW):
    def __init__(self, parent=None, **kwargs):
        super(BPMWidget, self).__init__(parent)
        self.name = kwargs.get('label', 'BPM name')
        self.beam_color = kwargs.get('beam_color', "#00ff00")
        self.name_label = QtWidgets.QLabel(self.name)
        self.grid.addWidget(self.name_label, 0, 0, 1, 2)

        self.bpm_w = BPMView(xsize=180, zsize=180, xmax=20, zmax=20,
                             use_scope=False, use_grid=True, beam_color=self.beam_color)
        self.grid.addWidget(self.bpm_w, 1, 0)

        self.int_bar = QtWidgets.QProgressBar(orientation=Qt.Vertical)
        self.int_bar.setFixedWidth(25)
        self.int_bar.setStyleSheet("QProgressBar { text-align: center; color: #000000; font: 10px;}")
        self.grid.addWidget(self.int_bar, 1, 1)

        self.grid_l = QtWidgets.QGridLayout()
        self.grid.addLayout(self.grid_l, 2, 0, 1, 2)

        self.grid_l.addWidget(QtWidgets.QLabel("X:"), 0, 0, Qt.AlignRight)
        self.grid_l.addWidget(QtWidgets.QLabel("Z:"), 1, 0, Qt.AlignRight)
        self.x_label = QtWidgets.QLabel("0.00")
        self.z_label = QtWidgets.QLabel("0.00")
        self.grid_l.addWidget(self.x_label, 0, 1, Qt.AlignLeft)
        self.grid_l.addWidget(self.z_label, 1, 1, Qt.AlignLeft)

        self.grid_l.addWidget(QtWidgets.QLabel("cur:"), 0, 3, Qt.AlignRight)
        self.grid_l.addWidget(QtWidgets.QLabel("n:"), 1, 3, Qt.AlignRight)

        self.c_label = QtWidgets.QLabel("0.00")
        self.n_label = QtWidgets.QLabel("0.00")
        self.grid_l.addWidget(self.c_label, 0, 4, Qt.AlignLeft)
        self.grid_l.addWidget(self.n_label, 1, 4, Qt.AlignLeft)

        #self.setStyleSheet("background-color:#e0e0e0;")
        self.setStyleSheet("QLabel { font: bold 18px;}")

        self.beam_x, self.beam_z, self.prev_beam_x, self.prev_beam_z = 0, 0, 0, 0

    def setBeamXZ(self, x, z):
        self.bpm_w.setBeamXZ(x, z)
        self.x_label.setText("{:.2f}".format(x))
        self.z_label.setText("{:.2f}".format(z))

        self.prev_beam_x, self.prev_beam_z = self.beam_x, self.beam_z
        self.beam_x, self.beam_z = x, z
        delta = math.sqrt((self.prev_beam_x - x)**2 + (self.prev_beam_z - z)**2)
        if delta > 1:
            print('show last beam')

    def setImax(self, Imax):
        self.int_bar.setMaximum(Imax)

    def setIntensity(self, I_rel):
        self.int_bar.setValue(I_rel)

    def setCurrent(self, c):
        self.c_label.setText("{:.2f}".format(c))


import pycx4.qcda as cda


class K500BPM(QtCore.QObject):
    update_I = QtCore.pyqtSignal(float)
    update_x = QtCore.pyqtSignal(float)
    update_z = QtCore.pyqtSignal(float)
    update_c = QtCore.pyqtSignal(float)

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.cnames = ['x', 'z', 'I', 'c']
        self.chans = {cn: cda.DChan(name + '.' + cn) for cn in self.cnames}
        for k in self.chans:
            self.chans[k].valueMeasured.connect(self.proc)

    def proc(self, chan):
        n = chan.short_name()
        getattr(self, "update_" + n).emit(chan.val)


class K500BPMWidget(BPMWidget):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.bpm = K500BPM(name)
        self.setImax(2*4*8192)

        self.bpm.update_I.connect(self.setIntensity)
        self.bpm.update_x.connect(self.new_beam_x)
        self.bpm.update_z.connect(self.new_beam_z)
        self.bpm.update_c.connect(self.setCurrent)

        self.beam_x, self.beam_z = 0, 0
        self.new_x, self.new_z = False, False

    def new_beam_x(self, x):
        self.beam_x = x
        if self.new_z:
            self.new_z = False
            self.setBeamXZ(self.beam_x, self.beam_z)
            return
        self.new_x = True

    def new_beam_z(self, z):
        self.beam_z = z
        if self.new_x:
            self.new_x = False
            self.setBeamXZ(self.beam_x, self.beam_z)
            return
        self.new_z = True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    w = K500BPMWidget("cxout:3.k500.bpm.e2v2.6PIC1")
    w.show()

    sys.exit(app.exec_())
