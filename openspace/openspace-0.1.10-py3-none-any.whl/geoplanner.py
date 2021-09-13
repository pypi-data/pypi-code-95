from openspace.math.time_conversions import epoch_string_to_timestamp
import os
import sys
from PyQt5 import QtWidgets, uic, QtGui
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import random
import pkg_resources
sys.path.append(os.getcwd())

from openspace.catalogs import TwoLineElsets
from openspace.propagators import TwoBodyModel
from openspace.math.coordinates import cartesian_to_spherical
from openspace.math.measurements import Distance, Angle
from openspace.math.time_conversions import get_eci_to_ecef_gst_angle

class GeoWindow(QtWidgets.QMainWindow):
    def __init__(self):

        super(GeoWindow, self).__init__()
        ui = pkg_resources.resource_filename(
            __name__, 
            "resources/ui_files/geoplanner.ui"
            )
        uic.loadUi(ui, self)

        self.add_object_button.released.connect(self.plot_state)
        self.remove_object_button.released.connect(self.remove_state)
        self.load_active_geo_action.triggered.connect(self.load_active_geo)
        self.download_active_geo.triggered.connect(
            TwoLineElsets.get_latest_celetrak_active_geo
            )

        self.tles = {}
        self.active_sccs = {}
        self.rel_geo_plot.addLegend()

    def remove_state(self):
        row = self.available_sccs_table.currentRow()
        scc = self.available_sccs_table.item(row, 0).text()

        if self.active_sccs.get(scc) is not None:
            #self.active_sccs[scc].setData([], [])
            self.rel_geo_plot.removeItem(self.active_sccs[scc])
            del self.active_sccs[scc]
            color = QtGui.QColor(255, 255, 255)
            self.available_sccs_table.item(row, 0).setBackground(color)
            self.available_sccs_table.item(row, 1).setBackground(color)

            


    def plot_state(self):

        row = self.available_sccs_table.currentRow()
        scc = self.available_sccs_table.item(row, 0).text()

        if self.tles.get(scc) is not None:
            epoch, r0, v0, name  = self.tles[scc]
            get_plot_data = True
        else:
            get_plot_data = False
        
        if get_plot_data and self.active_sccs.get(scc) is None:
            tbm = TwoBodyModel(r0, v0, epoch)
            period = tbm.get_period()
            t = 0
            x = []
            y = []
            while t < period:
                r, _ = tbm.get_future_state(epoch.add_seconds(t))
                
                gst = get_eci_to_ecef_gst_angle(epoch.add_seconds(t))
                r = r.rotate_about_z(gst)
                r_lat_long = cartesian_to_spherical(r)
                long = Angle(r_lat_long.get_element(2), "radians").to_unit("degrees")
                x.append(long)
                alt = Distance(r.magnitude(), "meters").to_unit("kilometers")
                y.append(alt - 42164)
                t+=300

            color = QtGui.QColor(0, 255, 0)
            self.available_sccs_table.item(row, 0).setBackground(color)
            self.available_sccs_table.item(row, 1).setBackground(color)

            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            self.active_sccs[scc] = self.rel_geo_plot.plot(
                x, 
                y, 
                pen = pg.mkPen(color=(r,g,b)), 
                name = name
                )

    def load_active_geo(self):
        self.tles  = TwoLineElsets.load_from_latest_active_geos()

        while self.available_sccs_table.rowCount() > 0:
            self. available_sccs_table.removeRow(0)

        for scc in sorted(self.tles.keys()):
            _, _, _, name  = self.tles[scc]
            row = self.available_sccs_table.rowCount()
            self.available_sccs_table.insertRow(row)
            scc_text = QtWidgets.QTableWidgetItem(scc)
            name_text = QtWidgets.QTableWidgetItem(name)
            self.available_sccs_table.setItem(row , 0, scc_text)
            self.available_sccs_table.setItem(row , 1, name_text)

        print(len(self.tles.keys()), "TLEs loaded.")

def run():
    app = QtWidgets.QApplication(sys.argv)
    main = GeoWindow()
    main.show()
    sys.exit(app.exec_())
    