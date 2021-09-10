from PyQt5.QtWidgets import QMainWindow, QApplication
import Sim

import sys

class Simulator:
    @classmethod
    def run(cls): # open the simulator gui
        app = QApplication(sys.argv)

        m = QMainWindow()
        m.resize(1000, 1000)
        w = Sim.Mod(m)

        m.setCentralWidget(w)
        m.show()

        sys.exit(app.exec_())
    @classmethod

    def statistics(cls, num=10): # statistics analysis
        if num < 100: # don't start when num < 100
            num = 100
            print('The number of bits was overwritten to 100 because it was too small')
        return Sim.statistics(num)

Simulator.run()