# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.client.DirectClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Direct client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, Optional

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConnectionException
from pip_services3_commons.refer import IReferenceable, DependencyResolver, IReferences
from pip_services3_commons.run import IOpenable
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import CompositeLogger
from pip_services3_components.trace.CompositeTracer import CompositeTracer

from pip_services3_rpc.services.InstrumentTiming import InstrumentTiming


class DirectClient(IConfigurable, IReferenceable, IOpenable):
    """
    Abstract client that calls controller directly in the same memory space. It is used when multiple microservices are deployed in a single container (monolyth) and communication between them can be done by direct calls rather then through the network.

    ### Configuration parameters ###
        - dependencies:
            - controller:            override controller descriptor

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:controller:*:*:1.0`       controller to call business methods

    Example:

    .. code-block:: python

        class MyDirectClient(DirectClient, IMyClient):
            def __init__(self):
                super(MyDirectClient, self).__init__()
                self._dependencyResolver.put('controller', Descriptor("mygroup", "controller", "*", "*", "*"))

            # ...

            def get_data(self, correlation_id, id):
                timing = self.instrument(correlationId, 'myclient.get_data')
                result = self._controller.get_data(correlationId, id)
                timing.end_timing()
                return result

            client = MyDirectClient()
            client.set_references(References.from_tuples(Descriptor("mygroup","controller","default","default","1.0"), controller))
            data = client.get_data("123", "1")
            # ...
    """

    def __init__(self):
        """
        Creates a new instance of the client.
        """
        # The controller reference.
        self._controller: Any = None
        # The open flag.
        self._opened: bool = True
        # The logger.
        self._logger: CompositeLogger = CompositeLogger()
        #  The tracer.
        self._tracer: CompositeTracer = CompositeTracer()
        # The performance counters
        self._counters: CompositeCounters = CompositeCounters()
        # The dependency resolver to get controller reference.
        self._dependency_resolver: DependencyResolver = DependencyResolver()
        self._dependency_resolver.put('controller', 'none')

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._dependency_resolver.configure(config)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._tracer.set_references(references)
        self._dependency_resolver.set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def _instrument(self, correlation_id: Optional[str], name: str) -> InstrumentTiming:
        """
        Adds instrumentation to log calls and measure call time.
        It returns a Timing object that is used to end the time measurement.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param name: a method name.
        :return: InstrumentTiming object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Calling %s method", name)
        self._counters.increment_one(name + ".call_count")

        counter_timing = self._counters.begin_timing(name + '.call_time')
        trace_timing = self._tracer.begin_trace(correlation_id, name, None)
        return InstrumentTiming(correlation_id, name, "call",
                                self._logger, self._counters, counter_timing, trace_timing)

    # def _instrument_error(self, correlation_id, name, err, result, callback):
    #     """
    #     Adds instrumentation to error handling.
    #
    #     :param correlation_id: (optional) transaction id to trace execution through call chain.
    #     :param name: a method name.
    #     :param err: an occured error
    #     :param result: (optional) an execution result
    #     :param callback: (optional) an execution callback
    #     """
    #     if err is not None:
    #         self.__logger.error(correlation_id, err, f'Failed to call {name} method')
    #         self.__counters.increment_one(f"{name}.call_errors")
    #     if callback:
    #         callback(err, result)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._opened

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self._opened:
            return

        if self._controller is None:
            raise ConnectionException(correlation_id, 'NO_CONTROLLER', 'Controller references is missing')

        self._opened = True
        self._logger.info(correlation_id, 'Opened direct client')

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self._opened:
            self._logger.info(correlation_id, 'Closed direct client')

        self._opened = False
