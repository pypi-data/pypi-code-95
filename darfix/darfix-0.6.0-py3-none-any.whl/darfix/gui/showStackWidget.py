# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "03/12/2020"

import glob
import os

from silx.io import fabioh5
from silx.io.url import DataUrl
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.StackView import StackViewMainWindow

import darfix
from darfix.core.dataset import Data
from darfix.gui.datasetSelectionWidget import DirSelectionWidget


class ShowStackWidget(qt.QMainWindow):
    """
    Widget to show a stack of data
    """
    sigComputed = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        layout = qt.QVBoxLayout()
        self._filenameData = DirSelectionWidget(parent=self)
        self._filenameData.dirChanged.connect(self.updateStack)
        layout.addWidget(self._filenameData)
        self._sv = StackViewMainWindow()
        self._sv.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME,
                                      normalization='linear'))
        self._sv.hide()
        layout.addWidget(self._sv)
        widget = qt.QWidget(parent=self)
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def updateStack(self):
        """
        Update stack with new first filename
        """
        _dir = self._filenameData.getDir()
        data_urls = []
        metadata = []
        for filename in sorted(glob.glob(_dir + "/*")):
            if os.path.isfile(filename):
                data_urls.append(DataUrl(file_path=filename, scheme='fabio'))
                metadata.append(fabioh5.EdfFabioReader(file_name=filename))

        data = Data(urls=data_urls, metadata=metadata, in_memory=False)

        self._sv.setStack(data)
        self._sv.show()
