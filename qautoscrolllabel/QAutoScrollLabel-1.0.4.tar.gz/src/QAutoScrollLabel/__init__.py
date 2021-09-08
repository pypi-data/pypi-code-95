# importing libraries
import typing
from time import sleep
from multipledispatch import dispatch

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QScrollArea, QWidget, QLabel, QScrollBar, QHBoxLayout


class ScrollLabel(QScrollArea):
    __text = "Please use the funtion setText to change this text"

    def __init__(self, a0: str = __text, parent: QWidget = None):
        """This is the widget where the text will be placed, if you want the Label scrolls automatically use
        QAutoScrollLabel instead.

        If you still want to use this class instead of QAutoScrollLabel, please note that this class will NOT
        scroll automatically

        :arg a0: String to show in Label
        """
        QScrollArea.__init__(self, parent)  # Initialize QScrollArea

        self.setWidgetResizable(True)  # making widget resizable

        # making qwidget object to content the QLabel
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        self.__lay = QHBoxLayout(content)

        # creating label
        self.__label = QLabel(content)

        # adding label to the layout
        self.__lay.addWidget(self.__label)

        # create QScrollBar object to scroll into the label with text
        self.scrollbar = QScrollBar()
        self.setHorizontalScrollBar(self.scrollbar)

        self.setText(a0)

    def setText(self, a0: str):
        """
        Set a new text in the label
        """

        self.__label.setText(a0)

        self.__label.adjustSize()
        self.__lay.setContentsMargins(0, 0, 0, 0)
        self.resize(200, self.__label.height() + 4)

    # noinspection PyMethodMayBeStatic
    def text(self) -> str:
        """
        Get the current text in the Label
        """
        return self.__label.text()


# noinspection PyUnresolvedReferences
class QAutoScrollLabel(ScrollLabel):

    # noinspection PyShadowingNames
    def __init__(self, parent: QWidget = None, debug: bool = False):
        """
        This Class creates a Widget that scrolls automatically if the text in the Label that the ScrollLabel class has
        inside it is wider than the Widget itself.

        :param debug: True if you want to enable debug Funtions [False by default]
        :param parent: Parent widget
        """

        # Widget text by default
        __text = "The text in this widget moves automatically if the text is larger than the Widget itself."

        super(QAutoScrollLabel, self).__init__(__text, parent)

        # Hide ScrollBars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Save parameter debug in a class variable
        self.__debug = debug
        self.__debug_fun = self.__debugger

    class __Scroller(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self, scroll: QScrollBar):
            """
            Worker type QObject to execute the AutoScroll in the Widget

            :param scroll: Scroll bar to auto-scroll
            """

            QObject.__init__(self)
            self.__scrollbar = scroll
            self.__orient = 1
            self.__vel = 10
            self.__csleep = 0.7

        def run(self):
            """This is the function that will perform the automatic scrolling of the text in the Widget.
            This connects to the "started" function of a QThread Object."""

            while True:  # This funtion will be alive until the program close

                if self.__scrollbar.maximum() > 0:
                    if self.__orient == 1:  # Move to the right
                        if self.__scrollbar.maximum() - self.__scrollbar.value() < self.__vel:
                            self.__scrollbar.setValue(self.__scrollbar.maximum())
                        self.__scrollbar.setValue(self.__scrollbar.value() + self.__vel)

                    elif self.__orient == -1:  # Move to the left
                        if self.__scrollbar.value() < self.__vel:
                            self.__scrollbar.setValue(self.__scrollbar.minimum())
                        self.__scrollbar.setValue(self.__scrollbar.value() - self.__vel)

                    # Change scrolling orientation an keep 1 second in that point
                    if self.__scrollbar.value() == self.__scrollbar.maximum():  # Change orientaton from Right to Left
                        self.__orient = -1
                        sleep(1)

                    elif self.__scrollbar.value() == self.__scrollbar.minimum():  # Change orientaton from Left to Right
                        self.__orient = 1
                        sleep(1)

                    self.progress.emit(self.__orient)

                else:

                    pass

                sleep(self.__csleep)

        def setVelocity(self, a0: int):
            """Set the velocity (Pixels Per Tick)"""
            self.__vel = a0

        def setTimeBetweenTicks(self, a0: float):
            """Set the time in seconds (int o float) between Ticks"""
            self.__csleep = a0

        @property
        def velocity(self):
            return self.__vel

        @property
        def timeBetweenTicks(self):
            return self.__csleep

        @property
        def orientation(self):
            return self.__orient

    def show(self) -> None:
        """Shows the widget and start the Auto-Scroll Thread"""
        QWidget.show(self)

        # Configure QTread with the worker Scroller
        self.__thread = QThread()
        self.__worker = self.__Scroller(self.scrollbar)
        self.__worker.moveToThread(self.__thread)

        # Connect Signals
        self.__thread.started.connect(self.__worker.run)
        self.__worker.finished.connect(self.__thread.quit)
        self.__worker.finished.connect(self.__worker.deleteLater)
        self.__thread.finished.connect(self.__thread.deleteLater)

        # Connect Debugger Signal
        self.__worker.progress.connect(self.__debug_fun)

        # Start QTread
        self.__thread.start()

    def setVelocity(self, a0: int):
        """Set the velocity (Pixels Per Tick)"""
        self.__worker.setVelocity(a0)

    @dispatch(float)
    def setTimeBetweenTicks(self, a0: float):
        """Set the time in seconds (int o float) between Ticks"""
        self.__worker.setTimeBetweenTicks(a0)

    @dispatch(int)
    def setTimeBetweenTicks(self, a0: int):
        """Set the time in seconds (int o float) between Ticks"""
        self.__worker.setTimeBetweenTicks(float(a0))

    @property
    def velocity(self):
        return self.__worker.velocity

    @property
    def timeBetweenTicks(self):
        return self.__worker.timeBetweenTicks

    @property
    def orientation(self):
        return "RIGHT" if self.__worker.orientation == 1 else "LEFT"

    def __debugger(self):
        """Prints the debug Info"""
        if self.__debug:
            print("Orientation:", self.orientation,
                  f"Pos: {self.scrollbar.value()}Px",
                  f"Max: {self.scrollbar.maximum()}Px",
                  f"Vel: {self.__worker.velocity}Px/t",
                  f"Time between ticks: {self.__worker.timeBetweenTicks}S",
                  f"Ticks Per Second: {1 / self.__worker.timeBetweenTicks} T/s")

    def debug(self, debug: bool = None) -> None:
        """
        Enable debbug info
        :param debug: True or false to enable or disable the debugger, if None the current state will be inverted.
        """

        if debug is None:
            if not self.__debug:
                self.__debug = True

            else:
                self.__debug = False

        if self.__debug:

            self.setStyleSheet("")

        else:

            self.setStyleSheet("border: 0px solid black")

    def setDebug(self, debug_fun: typing.Callable):
        self.__debug_fun = debug_fun

    @property
    def debugStatus(self):
        return self.__debug
