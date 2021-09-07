# -*- coding: utf-8 -*-
"""
    pip_services3_commons.run.FixedRateTimer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Fixed rate timer implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import inspect
import time
from threading import Thread, Event, Lock
from typing import Callable, Any, Optional

from pip_services3_commons.run import Parameters, INotifiable
from .IClosable import IClosable


class Timer(Thread):
    def __init__(self, interval, delay, callback):
        Thread.__init__(self)
        self._interval = interval
        self._callback = callback
        self._event = Event()
        self._delay = delay

    def run(self):
        time.sleep(self._delay)
        while not self._event.is_set():
            self._callback()
            time.sleep(self._interval)

    def stop(self):
        if self.is_alive():
            # set event_name to signal thread to terminate
            self._event.set()
            # block calling thread until thread really has terminated
            self.join()


class FixedRateTimer(IClosable):
    """
    Timer that is triggered in equal time intervals.

    It has summetric cross-language implementation
    and is often used by Pip.Services toolkit to perform periodic processing and cleanup in microservices.
    """

    __lock = None

    def __init__(self, task_or_object: Any = None, interval: int = None, delay: int = None):
        """
        Creates new instance of the timer and sets its values.

        :param task_or_object: (optional) a Notifiable object or callback function to call when timer is triggered.

        :param interval: (optional) an __interval to trigger timer in milliseconds.

        :param delay: (optional) a __delay before the first triggering in milliseconds.
        """
        self.__lock = Lock()
        self.__task: INotifiable = None
        self.__callback: Callable = None
        self.__delay: int = None
        self.__interval: int = None
        self.__timer: Any = None
        self.__started: bool = False

        if hasattr(task_or_object, 'notify') and inspect.ismethod(
                task_or_object.notify):
            self.set_task(task_or_object)
        else:
            self.set_callback(task_or_object)

        self.set_interval(interval)
        self.set_delay(delay)

    def get_task(self) -> INotifiable:
        """
        Gets the INotifiable object that receives notifications from this timer.

        :return: the INotifiable object or null if it is not set.
        """
        return self.__task

    def set_task(self, value: INotifiable):
        self.__task = value
        self.__callback = self.__timer_callback

    def get_callback(self) -> Callable:
        """
        Gets the callback function that is called when this timer is triggered.

        :return: the callback function or null if it is not set.
        """
        return self.__callback

    def set_callback(self, value: Callable):
        """
        Sets the callback function that is called when this timer is triggered.

        :param value: the callback function to be called.
        """
        self.__callback = value
        self.__task = None

    def get_delay(self) -> int:
        """
        Gets initial delay before the timer is triggered for the first time.

        :return: the delay in milliseconds.
        """
        return self.__delay

    def set_delay(self, value: int):
        """
        Sets initial delay before the timer is triggered for the first time.
        :param value: a delay in milliseconds.
        """
        self.__delay = value

    def get_interval(self) -> int:
        """
        Gets periodic timer triggering interval.

        :return: the interval in milliseconds
        """
        return self.__interval

    def set_interval(self, value: int):
        """
        Sets periodic timer triggering interval.

        :param value: an interval in milliseconds.
        """
        self.__interval = value

    def is_started(self) -> bool:
        """
        Checks if the timer is started.

        :return: true if the timer is started and false if it is stopped.
        """
        return self.__timer is not None

    def start(self):
        """
        Starts the timer.
        Initially the timer is triggered after __delay.
        After that it is triggered after __interval until it is stopped.
        """
        self.__lock.acquire()
        try:
            # Stop previously set timer
            if not (self.__timer is None):
                self.__timer.stop()
                self.__timer = None

            if self.__interval is None or self.__interval <= 0:
                return

            delay = max(0, self.__delay - self.__interval)

            # Set a new timer
            self.__timer = Timer(self.__interval / 1000, delay / 1000, self.__callback)
            self.__timer.start()

            # Set __started flag
            self.__started = True
        finally:
            self.__lock.release()

    def __timer_callback(self):
        try:
            self.__task.notify("pip-commons-timer", Parameters())
        except:
            # Ignore or better log
            pass

    def stop(self):
        """
        Stops the timer.
        """
        self.__lock.acquire()
        try:
            # Stop the timer
            if not (self.__timer is None):
                self.__timer.stop()
                self.__timer = None

            # Unset __started flag
            self.__started = False
        finally:
            self.__lock.release()

    def close(self, correlation_id: Optional[str]):
        """
        Closes the timer.
        This is __required by :class:`IClosable <pip_services3_commons.run.IClosable.IClosable>` interface,
        but besides that it is identical to stop().

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self.stop()
