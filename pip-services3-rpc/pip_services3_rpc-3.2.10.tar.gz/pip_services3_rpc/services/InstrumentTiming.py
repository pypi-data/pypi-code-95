# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_components.count import ICounters, CounterTiming
from pip_services3_components.log import ILogger
from pip_services3_components.trace.TraceTiming import TraceTiming


class InstrumentTiming:

    def __init__(self, correlation_id: Optional[str], name: str, verb: str, logger: ILogger, counters: ICounters,
                 counter_timing: Optional[CounterTiming], trace_timing: Optional[TraceTiming]):
        self.__correlation_id = correlation_id
        self.__name = name
        self.__verb = verb or 'call'
        self.__logger = logger
        self.__counters = counters
        self.__counter_timing = counter_timing
        self.__trace_timing = trace_timing

    def __clear(self):
        """
        Clear references to avoid double processing
        """
        self.__counters = None
        self.__logger = None
        self.__counter_timing = None
        self.__trace_timing = None

    def end_timing(self, err: Exception = None):
        if err is None:
            self.end_success()
        else:
            self.end_failure(err)

    def end_success(self):
        if self.__counter_timing is not None:
            self.__counter_timing.end_timing()

        if self.__trace_timing is not None:
            self.__trace_timing.end_trace()

        self.__clear()

    def end_failure(self, err: Exception):
        if self.__counter_timing is not None:
            self.__counter_timing.end_timing()

        if err is not None:
            if self.__logger is not None:
                self.__logger.error(self.__correlation_id, err, "Failed to call %s method", self.__name)

            if self.__counters is not None:
                self.__counters.increment_one(self.__name + '.' + self.__verb + '_errors')

            if self.__trace_timing is not None:
                self.__trace_timing.end_failure(err)

        else:
            if self.__trace_timing is not None:
                self.__trace_timing.end_trace()

        self.__clear()
