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

__authors__ = ["H. Payno", "Orange"]
__license__ = "MIT"
__date__ = "04/10/2018"

"""
Unit test from the Orange canvas main instance

"""
import os
import sys
import gc
import re
import logging
import pickle
import pkg_resources
from AnyQt.QtGui import QFont
from AnyQt.QtCore import Qt, QDir
import AnyQt.importhooks

if AnyQt.USED_API == "pyqt5":
    # Use a backport shim to fake leftover PyQt4 imports
    AnyQt.importhooks.install_backport_hook('pyqt4')

from silx.gui import qt as silxqt
from Orange import canvas
from Orange.canvas.config import cache_dir
from Orange.canvas import config
try:
    from Orange.canvas.application.canvasmain import CanvasMainWindow
    from Orange.canvas.application.outputview import TextStream
    from Orange.canvas.registry.base import WidgetRegistry
    from Orange.canvas.registry import qt
    from Orange.canvas.registry import set_global_registry
    from Orange.canvas.scheme import SchemeNode, SchemeLink
    from Orange.canvas.registry import cache
except ImportError:
    pass

from unittest import TestCase

log = logging.getLogger(__name__)


app = silxqt.QApplication.instance() or silxqt.QApplication([])


if AnyQt.USED_API == 'pyside':
    from PySide.QtTest import QTest
elif AnyQt.USED_API == 'pyside2':
    from PySide2.QtTest import QTest
elif AnyQt.USED_API == 'pyqt5':
    from PyQt5.QtTest import QTest
elif AnyQt.USED_API == 'pyqt4':
    from PyQt4.QtTest import QTest
else:
    raise ImportError('Unsupported Qt bindings')


class OrangeWorkflowTest(TestCase):
    """Define a specific TestCase reltive to OrangeWorkflow"""

    def addWidget(self, widgetID):
        """Create an instanciation of the widgetID

        :return SchemeNode: the node created
        """
        assert(type(widgetID) is str)
        assert(self.widget_registry.has_widget(widgetID))
        widget_desc = self.widget_registry.widget(widgetID)
        myItem = SchemeNode(widget_desc)
        self.canvas_window.current_document().scheme().add_node(myItem)
        return myItem

    def link(self, schemeNode1, outNode1, schemeNode2, inputNode2):
        """Create a link between the node on the given input and output

        :param SchemeNode schemeNode1: the node emitting the output signal
        :param outNode1: the output chanel to be linked
        :param SchemeNode schemeNode2: the node receiving the input signal
        :param inputNode2: the input chanel to be linked
        :return: the link created between the two nodes
        """
        assert(type(schemeNode1) is SchemeNode)
        assert(type(schemeNode2) is SchemeNode)
        assert(type(outNode1) is str)
        assert(type(inputNode2) is str)
        link = SchemeLink(schemeNode1, outNode1, schemeNode2, inputNode2)
        self.canvas_window.current_document().scheme().add_link(link)
        return link

    def getWidgetForNode(self, node):
        """

        :param SchemeNode node: the node for which we want the corresponding
            widget
        :return: the widget instanciated for the given node
        """
        assert(type(node) is SchemeNode)
        return self.canvas_window.current_document().scheme().widget_for_node(node)

    @classmethod
    def setUpClass(cls):
        cls.init(cls)
        TestCase.setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.canvas_window.deleteLater()
        # make sure no events are resting
        while (app.hasPendingEvents()):
            app.processEvents()
            cls.processOrangeEvents(cls)
        app.flush()
        del cls.canvas_window

        gc.collect()
        # Collect any cycles before deleting the QApplication instance
        TestCase.tearDownClass()

    def tearDown(self):
        while(app.hasPendingEvents()):
            app.processEvents()
            TestCase.tearDown(self)

    @staticmethod
    def fix_osx_10_9_private_font():
        # Fix fonts on Os X (QTBUG 47206, 40833, 32789)
        if sys.platform == "darwin":
            import platform
            try:
                version = platform.mac_ver()[0]
                version = float(version[:version.rfind(".")])
                if version >= 10.11:  # El Capitan
                    QFont.insertSubstitution(".SF NS Text", "Helvetica Neue")
                elif version >= 10.10:  # Yosemite
                    QFont.insertSubstitution(".Helvetica Neue DeskInterface",
                                             "Helvetica Neue")
                elif version >= 10.9:
                    QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")
            except AttributeError:
                pass

    @staticmethod
    def fix_win_pythonw_std_stream():
        """
        On windows when running without a console (using pythonw.exe) the
        std[err|out] file descriptors are invalid and start throwing exceptions
        when their buffer is flushed (`http://bugs.python.org/issue706263`_)

        """
        if sys.platform == "win32" and \
                os.path.basename(sys.executable) == "pythonw.exe":
            if sys.stdout is None:
                sys.stdout = open(os.devnull, "w")
            if sys.stderr is None:
                sys.stderr = open(os.devnull, "w")

    def processOrangeEvents(self):
        self.canvas_window.current_document().scheme().signal_manager.process_queued()

    def processOrangeEventsStack(self):
        node_update_front = self.canvas_window.current_document().scheme().signal_manager.node_update_front()
        if node_update_front:
            self.processOrangeEvents()
            self.processOrangeEventsStack()

    def qWait(self, time_ms):
        QTest.qWait(time_ms)

    def init(self):
        # Fix streams before configuring logging (otherwise it will store
        # and write to the old file descriptors)
        OrangeWorkflowTest.fix_win_pythonw_std_stream()

        # Try to fix fonts on OSX Mavericks
        OrangeWorkflowTest.fix_osx_10_9_private_font()

        # File handler should always be at least INFO level so we need
        # the application root level to be at least at INFO.

        rootlogger = logging.getLogger(canvas.__name__)

        # Standard output stream handler at the requested level
        stream_hander = logging.StreamHandler()
        rootlogger.addHandler(stream_hander)

        # NOTE: config.init() must be called after the QApplication constructor
        config.init()

        file_handler = logging.FileHandler(
            filename=os.path.join(config.log_dir(), "canvas.log"),
            mode="w"
        )

        rootlogger.addHandler(file_handler)

        # intercept any QFileOpenEvent requests until the main window is
        # fully initialized.
        # NOTE: The QApplication must have the executable ($0) and filename
        # arguments passed in argv otherwise the FileOpen events are
        # triggered for them (this is done by Cocoa, but QApplicaiton filters
        # them out if passed in argv)

        open_requests = []

        def onrequest(url):
            open_requests.append(url)

        # app.fileOpenRequest.connect(onrequest)

        stylesheet = "orange"
        stylesheet_string = None

        if stylesheet != "none":
            if os.path.isfile(stylesheet):
                with open(stylesheet, "r") as f:
                    stylesheet_string = f.read()
            else:
                if not os.path.splitext(stylesheet)[1]:
                    # no extension
                    stylesheet = os.path.extsep.join([stylesheet, "qss"])

                pkg_name = canvas.__name__
                resource = "styles/" + stylesheet

                if pkg_resources.resource_exists(pkg_name, resource):
                    stylesheet_string = \
                        pkg_resources.resource_string(pkg_name, resource).decode()

                    base = pkg_resources.resource_filename(pkg_name, "styles")

                    pattern = re.compile(
                        r"^\s@([a-zA-Z0-9_]+?)\s*:\s*([a-zA-Z0-9_/]+?);\s*$",
                        flags=re.MULTILINE
                    )

                    matches = pattern.findall(stylesheet_string)

                    for prefix, search_path in matches:
                        QDir.addSearchPath(prefix, os.path.join(base, search_path))
                        log.info("Adding search path %r for prefix, %r",
                                 search_path, prefix)

                    stylesheet_string = pattern.sub("", stylesheet_string)

                else:
                    log.info("%r style sheet not found.", stylesheet)

        # Add the default canvas_icons search path
        dirpath = os.path.abspath(os.path.dirname(canvas.__file__))
        QDir.addSearchPath("canvas_icons", os.path.join(dirpath, "icons"))
        self.canvas_window = CanvasMainWindow()
        self.canvas_window.setWindowIcon(config.application_icon())

        if stylesheet_string is not None:
            self.canvas_window.setStyleSheet(stylesheet_string)

        reg_cache = None
        widget_discovery = qt.QtWidgetDiscovery(cached_descriptions=reg_cache)

        self.widget_registry = qt.QtWidgetRegistry()

        widget_discovery.found_category.connect(
            self.widget_registry.register_category
        )
        widget_discovery.found_widget.connect(
            self.widget_registry.register_widget
        )

        cache_filename = os.path.join(cache_dir(), "widget-registry.pck")
        widget_discovery.run(config.widgets_entry_points())
        # Store cached descriptions
        cache.save_registry_cache(widget_discovery.cached_descriptions)
        with open(cache_filename, "wb") as f:
            pickle.dump(WidgetRegistry(self.widget_registry), f)

        set_global_registry(self.widget_registry)
        self.canvas_window.set_widget_registry(self.widget_registry)
        self.canvas_window.show()

        # Process events to make sure the self.canvas_window layout has
        # a chance to activate (the welcome dialog is modal and will
        # block the event queue, plus we need a chance to receive open file
        # signals when running without a splash screen)
        app.processEvents()
        log.info("discovery ended")
        # Tee stdout and stderr into Output dock
        log_view = self.canvas_window.log_view()

        stdout = TextStream()
        stdout.stream.connect(log_view.write)
        if sys.stdout:
            stdout.stream.connect(sys.stdout.write)
            stdout.flushed.connect(sys.stdout.flush)
        stderr = TextStream()
        error_writer = log_view.formated(color=Qt.red)
        stderr.stream.connect(error_writer.write)
        if sys.stderr:
            stderr.stream.connect(sys.stderr.write)
            stderr.flushed.connect(sys.stderr.flush)

        log.info("End initialization")
