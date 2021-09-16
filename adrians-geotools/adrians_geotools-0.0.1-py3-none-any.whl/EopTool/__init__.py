""" EopTool

This package was created for easily handling residual comparisons between different eop series. This includes functionality for resampling series,
filtering series on time and uncertainites, and performing regression on the residuals.

Contained in the package are four modules:

    *EopTool.calc - Methods for data calculations
    *EopTool.io - Methods for data loading and exportation
    *EopTool.visualise - Methods for visualisation
    *EopTool.units - Unit data for convenience

and a subpackage EopTool.interface for the GUI driven application.
"""

from EopTool.interface.MainWindow import MainWindow

def run():
    main = MainWindow()
    main.mainloop()


if __name__ == '__main__':
    run()