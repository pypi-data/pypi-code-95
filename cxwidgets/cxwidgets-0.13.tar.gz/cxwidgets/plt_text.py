#!/usr/bin/env python3
import sys
from cxwidgets.aQt import QtWidgets, QtCore, QtGui
import pyqtgraph as pg


class BPMScopeItem(pg.GraphicsObject):
    def __init__(self, **kwargs):
        super().__init__()
        self.x_size = kwargs.get('xsize', 200)
        self.y_size = kwargs.get('ysize', 200)

        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.setPen(pg.mkPen('g'))
        p.drawEllipse(0, 0, self.x_size, self.y_size)
        p.drawEllipse(self.x_size/4, self.y_size/4, self.x_size/2, self.y_size/2)

        p.drawLine(self.x_size/2, 0, self.x_size/2, self.y_size)
        p.drawLine(0, self.y_size/2, self.x_size, self.y_size/2)

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

class BeamItem(pg.GraphicsObject):
    def __init__(self, **kwargs):
        super().__init__()
        self.size = kwargs.get('size', 20)
        self.x0 = kwargs.get('x0', 0)
        self.y0 = kwargs.get('y0', 0)
        self.x = 0
        self.y = 0

        self.setBeamPos(0, 0)
        self._color = QtGui.QColor(255, 0, 0)
        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)

        #x = self.x0 + self.x
        #y = self.y0 + self.y
        r = self.size/2

        gradient = QtGui.QRadialGradient(r, r, r, r, r)
        gradient.setColorAt(0, QtCore.Qt.black)
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

    def setBeamPos(self, x, y):
        self.setPos(self.x0 - self.size/2 + x, self.y0 - self.size/2 - y)
        self.x, self.y = x, y



class BPMView(pg.GraphicsView):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.x_size = kwargs.get('xsize', 200)
        self.y_size = kwargs.get('ysize', 200)

        self.resize(self.x_size, self.y_size)
        self.setAspectLocked(True)

        self.bpm_scope = BPMScopeItem(xsize=self.x_size, ysize=self.y_size)
        self.addItem(self.bpm_scope)

        self.beam = BeamItem(x0=self.x_size/2, y0=self.y_size/2)
        self.addItem(self.beam)

    def timer_move(self):
        self.setBeamXY(50, 50)

    def setBeamXY(self, x, y):
        self.beam.setBeamPos(x, y)


app = QtWidgets.QApplication(sys.argv)

## Create window with GraphicsView widget
w = BPMView(xsize=200, ysize=200)
w.show()

## Create image item
#img = pg.ImageItem(np.zeros((200, 200)))
#w.addItem(img)

## Set initial view bounds
#w.setRange(QtCore.QRectF(0, 0, 200, 200))

## start drawing with 3x3 brush
# kern = np.array([
#     [0.0, 0.5, 0.0],
#     [0.5, 1.0, 0.5],
#     [0.0, 0.5, 0.0]
# ])
# img.setDrawKernel(kern, mask=kern, center=(1,1), mode='add')
# img.setLevels([0, 10])

sys.exit(app.exec_())
