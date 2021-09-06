__all__ = [
    "MetricId",
    "Recorder",
    "LogTransport",
    "StdoutTransport",
    "InMemoryTransport",
    "RiemannTransport",
    "CompositeTransport",
    "Gauge",
    "Range",
    "Counter",
    "Timer",
    "Metrics",
]


import collections
import copy
import json
import logging
import timeit
from collections import defaultdict, namedtuple
from datetime import datetime

from riemann_client.client import Client
from riemann_client.riemann_pb2 import Msg
from riemann_client.transport import TCPTransport

from ._deprecation import deprecated

MetricId = namedtuple("MetricId", "name tags attributes")
MetricId.__doc__ = "Used to uniquely identify a metric"
MetricId.name.__doc__ = "(str): The 'service' of the metric."
MetricId.tags.__doc__ = "(List[str]): A list of string tags associated with the metric."
MetricId.attributes.__doc__ = (
    "(Dict[str, Any]): Arbitrary key-value pairs associated with the metric"
)


class Metric:
    """A single measurement.

    Args:
        service (str): The name of the metric.
        value (SupportsFloat): The numeric value recorded.
        ttl (Optional[int]): The time-to-live of the metric in seconds.
        tags (List[str]): A list of string tags to apply to the metric.
        fields (Dict[str, Any]): A set of key-value pairs to apply to the metric.
        description (str): The metric type: counter, gauge or range
    """

    def __init__(self, service, value, ttl, tags, fields, description=None):
        self.tags = tags or []
        self.value = value
        self.name = service
        self.ttl = ttl
        self.description = description
        self.id = self._id(self.name, self.tags, fields)
        self.attributes = {str(k): str(v) for k, v in fields.items()}

    def _id(self, service_name, tags, fields):
        return MetricId(service_name, frozenset(tags), frozenset(fields.items()))


class Recorder:
    """
    Collects metrics and flushes them to a transport
    """

    def send(self, metric, value, transport, suffix=""):

        ttl = metric.ttl
        event = {
            "tags": metric.tags,
            "attributes": metric.attributes,
            "service": metric.name + suffix,
            "metric_f": value,
            "description": metric.description,
        }

        if ttl is not None:
            event["ttl"] = ttl

        transport.send_event(event)


class Transport:
    """Sends metrics for storage or processing"""

    def send_event(self, event):
        """Buffer a single event for sending."""
        pass

    def flush(self, is_closing):
        """Send all buffered metrics

        Args:
            is_closing (bool): True if the transport should tear down any resources,
                eg. Sockets or file handles.
        """


class LogTransport(Transport):

    """
    Simple Transport that sprints metrics to the log. Useful for development
    environments
    """

    def __init__(self):
        self._logger = logging.getLogger("metrics")

    def send_event(self, event):
        self._logger.info(
            "metric %s=%s (%s)",
            event["service"],
            event["metric_f"],
            json.dumps(event.get("attributes")),
        )

    def flush(self, is_closing):
        pass


class StdoutTransport(Transport):

    """
    Simple Transport that writes metrics to standard output.

    The metrics are written in a format suited to parsing by elasticsearch

    The format is similar to the JSON format used by other striemann transports, but:

    - Adds a metric type to the data to make them distinguishable (counter/gauge/range)

    - Add specific information to make metrics more visible in terms of env, service and ownership

    - Wraps the data in a "metric" key to make it easier to distinguish from other messages
      grabbed from stdout
    """

    def __init__(self, service, owner, env):
        self.batch = []
        self.service = service
        self.owner = owner
        self.env = env

    def send_event(self, event):
        # initialize a data dict and merge attributes
        # with tags and description to use in metric
        data = {}
        data["tags"] = event.get("tags", [])
        data["description"] = event["description"]
        data.update(event.get("attributes", {}))
        ttl = event.get("ttl")

        metric_for_stdout = {
            "name": event["service"],
            "value": event["metric_f"],
            "data": data,
            "env": self.env,
            "owner": self.owner,
            "service": self.service,
        }
        if ttl:
            metric_for_stdout["ttl"] = ttl
        self.batch.append({"metric": metric_for_stdout})

    def flush(self, is_closing):
        for event in self.batch:
            now = datetime.now()
            event["metric"]["time"] = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            print(json.dumps(event), flush=True)

        self.batch = []


class InMemoryTransport(Transport):

    """
    Dummy transport that keeps a copy of the last flushed batch of events. This
    is used to store the data for the stats endpoints.
    """

    def __init__(self):
        self.current_batch = []
        self.last_batch = []

    def send_event(self, event):
        self.current_batch.append(event)

    def flush(self, is_closing):
        self.last_batch = list(self.current_batch)
        self.current_batch = []


class RiemannTransport(Transport):

    """
    Transport that sends metrics to a Riemann server.
    """

    def __init__(self, host="localhost", port="5555", timeout=5):
        self.host = host
        self.port = port

        self.transport = TCPTransport(self.host, self.port, timeout)
        self._new_message()
        self._connected = False

    def send_event(self, event):
        riemann_event = Client.create_event(event)
        self._message.events.add().MergeFrom(riemann_event)

    def _connect(self):
        self.transport.connect()
        self._connected = True

    def _disconnect(self):
        self.transport.disconnect()
        self._connected = False

    def _ensure_connected(self):
        # This is just to avoid logging about failure on the first try

        if not self._connected:
            self._connect()

    def flush(self, is_closing):
        self._ensure_connected()
        try:
            self.transport.send(self._message)
        except Exception as e:
            self._disconnect()
            logging.warning("Failed to flush metrics to riemann")
            try:
                self._connect()
                self.transport.send(self._message)
            except Exception as e:
                logging.error("Failed twice to flush metrics to riemann", exc_info=True)

        if is_closing:
            self._disconnect()
        self._new_message()

    def _new_message(self):
        self._message = Msg()

    @deprecated("Should be no need to check, will reconnect automatically")
    def is_connected(self):
        """Check whether the transport is connected."""

        return True


class CompositeTransport(Transport):

    """
    Transport that wraps two or more transports and forwards events to all of
    them.
    """

    def __init__(self, *args):
        self._transports = args

    def send_event(self, event):
        for t in self._transports:
            t.send_event(copy.deepcopy(event))

    def flush(self, is_closing):
        for t in self._transports:
            t.flush(is_closing)


class Range(Recorder):
    """
    Summaries record the range of a value across a set of datapoints,
    eg response time, items cleared from cache, and forward aggregated
    metrics to describe that range.
    """

    def __init__(self, source):
        self._source = source
        self._reset()

    def _reset(self):
        self._metrics_summaries = defaultdict(dict)

    def record(self, service_name, value, ttl=None, tags=[], attributes=dict()):
        if self._source:
            attributes["source"] = self._source

        new_metric = Metric(service_name, value, ttl, tags, attributes, "range")

        current_summary = self._metrics_summaries[new_metric.id]
        first_metric = current_summary.get("first")
        current_max = current_summary.get("max")
        current_min = current_summary.get("min")
        current_count = current_summary.get("count", 0)
        current_total = current_summary.get("total", 0)

        new_value = new_metric.value
        new_min = min(current_min, new_value) if current_min is not None else new_value
        new_max = max(current_max, new_value) if current_max is not None else new_value
        new_count = current_count + 1
        new_total = current_total + new_value

        self._metrics_summaries[new_metric.id] = {
            "first": first_metric if first_metric else new_metric,
            "min": new_min,
            "max": new_max,
            "count": new_count,
            "total": new_total,
        }

    def flush(self, transport):
        for summary in self._metrics_summaries.values():
            first = summary["first"]

            self.send(first, summary["min"], transport, ".min")
            self.send(first, summary["max"], transport, ".max")
            self.send(first, summary["total"] / summary["count"], transport, ".mean")
            self.send(first, summary["count"], transport, ".count")

        self._reset()


class Counter(Recorder):

    """
    Counters record incrementing or decrementing values, eg. Events Processed,
    error count, cache hits.
    """

    def __init__(self, source):
        self._source = source
        self._counters = collections.defaultdict(list)

    def record(self, service_name, value, ttl, tags, attributes):
        if self._source:
            attributes["source"] = self._source

        metric = Metric(service_name, value, ttl, tags, attributes, "counter")
        self._counters[metric.id].append(metric)

    def flush(self, transport):
        for counter in self._counters.values():
            count = sum(m.value for m in counter)
            self.send(counter[0], count, transport)
        self._counters = defaultdict(list)


class Gauge(Recorder):

    """
    Gauges record scalar values at a single point in time, eg. queue size,
    active sessions, and forward only the latest value.
    """

    def __init__(self, source):
        self._source = source
        self._gauges = dict()

    def record(self, service_name, value, ttl, tags, attributes):
        if self._source:
            attributes["source"] = self._source

        metric = Metric(service_name, value, ttl, tags, attributes, "gauge")
        self._gauges[metric.id] = metric

    def flush(self, transport):
        for gauge in self._gauges.values():
            self.send(gauge, gauge.value, transport)
        self._gauges = dict()


class Timer:

    """
    Timers provide a context manager that times an operation and records a
    gauge with the elapsed time.
    """

    def __init__(self, service_name, ttl, tags, attributes, histogram):
        self.service_name = service_name
        self.ttl = ttl
        self.tags = tags
        self.attributes = attributes
        self.recorder = histogram

    def __enter__(self):
        self.start = timeit.default_timer()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        elapsed = timeit.default_timer() - self.start
        self.recorder.record(
            self.service_name, elapsed, self.ttl, self.tags, self.attributes
        )


class Metrics:
    """Buffers metrics and forwards them to a :class:`~striemann.metrics.Transport`

    Args:
      transport(Transport): The transport used to send metrics.

      source(Optional[str]): If provided, this value will be added to all outbound metrics
          as the `source` attribute. The value may still be overridden on a
          per-metric basis.

    Examples:
        >>> from striemann.metrics import InMemoryTransport, Metrics
        >>> import pprint
        >>>
        >>> pp = pprint.PrettyPrinter(indent=4)
        >>>
        >>> transport = InMemoryTransport()
        >>> metrics = Metrics(transport)
        >>>
        >>> metrics.incrementCounter("Burgers sold")
        >>> metrics.flush()
        >>> print(transport.last_batch)
        [{'tags': [], 'attributes': {}, 'service': 'metrics written', 'metric_f': 1}]
    """

    def __init__(self, transport, source=None):
        self._transport = transport
        self._gauges = Gauge(source)
        self._ranges = Range(source)
        self._counters = Counter(source)

    def recordGauge(self, service_name, value, ttl=None, tags=None, **kwargs):
        """Record a single scalar value, eg. Queue Depth, Current Uptime, Disk Free

        Args:
            service_name (str): The name of the recorded metric.
            value (SupportsFloat): The numeric value to record.
            ttl (Optional[int]): An optional time-to-live for the metric, measured in seconds.
            tags (Optional[List[str]]): A list of strings to associate with the metric.
            **kwargs (Any): Additional key-value pairs to associate with the metric.

        Examples:

            In the simplest case, we just want to record a single number.
            Each time we record a Gauge, we replace the previous value.

            >>> metrics.recordGauge("Customers in restaurant", 10)
            >>> metrics.recordGauge("Customers in restaurant", 8)
            >>> metrics.flush()
            >>> print(transport.last_batch)
            [{'tags': [], 'attributes': {}, 'service': 'Customers in restaurant', 'metric_f': 8}]

            We might want to segregate our metrics by some other attribute so
            so that we can aggregate and drill-down.

            >>> metrics.recordGauge("Customers in restaurant", 6, hair="brown")
            >>> metrics.recordGauge("Customers in restaurant", 2, hair="blonde")
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [   {   'attributes': {'hair': 'blonde'},
                    'metric_f': 2,
                    'service': 'Customers in restaurant',
                    'tags': []},
                {   'attributes': {'hair': 'brown'},
                    'metric_f': 6,
                    'service': 'Customers in restaurant',
                    'tags': []}]
        """
        self._gauges.record(service_name, value, ttl, tags, kwargs)

    def incrementCounter(self, service_name, value=1, ttl=None, tags=None, **kwargs):
        """Record an increase in a value, eg. Cache Hits, Files Written

        Args:
            service_name (str): The name of the recorded metric.
            value (SupportsFloat): The numeric value to record.
            ttl (Optional[int]): An optional time-to-live for the metric, measured in seconds.
            tags (Optional[List[str]]): A list of strings to associate with the metric.
            **kwargs (Any): Additional key-value pairs to associate with the metric.

        Examples:

            Counters are useful when we don't know an absolute value, but we want
            to record that something happened.

            >>> metrics.incrementCounter("Burgers sold")
            >>> metrics.incrementCounter("Burgers sold")
            >>> metrics.incrementCounter("Burgers sold", value=2)
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [{'attributes': {}, 'metric_f': 4, 'service': 'Burgers sold', 'tags': []}]

            Counters reset after each flush.

            >>> metrics.incrementCounter("Burgers sold")
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [{'attributes': {}, 'metric_f': 1, 'service': 'Burgers sold', 'tags': []}]

            Counters can have tags and attributes associated with them.
            Each unique set of tags and attributes is flushed as a separate metric.

            >>> metrics.incrementCounter("Burgers sold", tags=["drive-thru"], name="cheeseburger")
            >>> metrics.incrementCounter("Burgers sold", name="cheeseburger")
            >>> metrics.incrementCounter("Burgers sold", value=2, name="whopper")
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [   {   'attributes': {'name': 'cheeseburger'},
                    'metric_f': 1,
                    'service': 'Burgers sold',
                    'tags': ['drive-thru']},
                {   'attributes': {'name': 'cheeseburger'},
                    'metric_f': 1,
                    'service': 'Burgers sold',
                    'tags': []},
                {   'attributes': {'name': 'whopper'},
                    'metric_f': 2,
                    'service': 'Burgers sold',
                    'tags': []}]
        """
        self._counters.record(service_name, value, ttl, tags, kwargs)

    def decrementCounter(self, service_name, value=1, ttl=None, tags=None, **kwargs):
        """Record an decrease in a value, eg. Cache Hits, Files Written

        Args:
            service_name (str): The name of the recorded metric.
            value (SupportsFloat): The numeric value to record.
            ttl (Optional[int]): An optional time-to-live for the metric, measured in seconds.
            tags (Optional[List[str]]): A list of strings to associate with the metric.
            **kwargs (Any): Additional key-value pairs to associate with the metric.

        Examples:

            Occasionally, we want to record a decrease in a value.

            >>> metrics.incrementCounter("Customers waiting")
            >>> metrics.incrementCounter("Customers waiting")
            >>>
            >>> metrics.decrementCounter("Customers waiting")
            >>>
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [{'attributes': {}, 'metric_f': 1, 'service': 'Customers waiting', 'tags': []}]
        """

        self._counters.record(service_name, 0 - value, ttl, tags, kwargs)

    def time(self, service_name, ttl=None, tags=None, **kwargs):
        """Record the time taken for an operation.

        The time method returns a context manager that can be used for timing
        an operation. The timer uses the `default timer<https://docs.python.org/2/library/timeit.html#timeit.default_timer>_` for the operating system.

        Under the hood, the time method uses a :class:`~striemann.metrics.Range`
        to record its values.

        Args:
            service_name (str): The name of the recorded metric.
            value (SupportsFloat): The numeric value to record.
            ttl (Optional[int]): An optional time-to-live for the metric, measured in seconds.
            tags (Optional[List[str]]): A list of strings to associate with the metric.
            **kwargs (Any): Additional key-value pairs to associate with the metric.

        Examples:

            Since timers use a :class:`striemann.metrics.Range` to record their values
            they send a summary of all the values recorded since the last flush.

            >>> import time
            >>> with metrics.time("Burger Cooking Time"):
            >>>    time.sleep(1)
            >>> with metrics.time("Burger Cooking Time"):
            >>>    time.sleep(5)
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [   {   'attributes': {},
                    'metric_f': 1.0011436779996075,
                    'service': 'Burger cooking time.min',
                    'tags': []},
                {   'attributes': {},
                    'metric_f': 5.00513941600002,
                    'service': 'Burger cooking time.max',
                    'tags': []},
                {   'attributes': {},
                    'metric_f': 3.0031415469998137,
                    'service': 'Burger cooking time.mean',
                    'tags': []},
                {   'attributes': {},
                    'metric_f': 2,
                    'service': 'Burger cooking time.count',
                    'tags': []}]

            Timers respect tags and attributes when aggregating.

            >>> with metrics.time("Burger Cooking Time", type="whopper"):
            >>>    time.sleep(1)
            >>> with metrics.time("Burger Cooking Time", type="cheeseburger"):
            >>>    time.sleep(5)
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [   {   'attributes': {'type': 'whopper'},
                    'metric_f': 1.001190301999486,
                    'service': 'Burger cooking time.min',
                    'tags': []},
                {   'attributes': {'type': 'whopper'},
                    'metric_f': 1.001190301999486,
                    'service': 'Burger cooking time.max',
                    'tags': []},
                {   'attributes': {'type': 'whopper'},
                    'metric_f': 1.001190301999486,
                    'service': 'Burger cooking time.mean',
                    'tags': []},
                {   'attributes': {'type': 'whopper'},
                    'metric_f': 1,
                    'service': 'Burger cooking time.count',
                    'tags': []},
                {   'attributes': {'type': 'cheeseburger'},
                    'metric_f': 5.005140869999195,
                    'service': 'Burger cooking time.min',
                    'tags': []},
                {   'attributes': {'type': 'cheeseburger'},
                    'metric_f': 5.005140869999195,
                    'service': 'Burger cooking time.max',
                    'tags': []},
                {   'attributes': {'type': 'cheeseburger'},
                    'metric_f': 5.005140869999195,
                    'service': 'Burger cooking time.mean',
                    'tags': []},
                {   'attributes': {'type': 'cheeseburger'},
                    'metric_f': 1,
                    'service': 'Burger cooking time.count',
                    'tags': []}]
        """

        return Timer(service_name, ttl, tags, kwargs, self._ranges)

    def recordRange(self, service_name, value, ttl=None, tags=[], **kwargs):
        """Record statistics about a range of values

        Ranges are useful when we care about a metric in aggregate rather than
        recording each individual event. When flushed, a Range sends the minimum,
        maximum, and mean of each recorded metric, and the count of values recorded.

        Args:
            service_name (str): The name of the recorded metric.
            value (SupportsFloat): The numeric value to record.
            ttl (Optional[int]): An optional time-to-live for the metric, measured in seconds.
            tags (Optional[List[str]]): A list of strings to associate with the metric.
            **kwargs (Any): Additional key-value pairs to associate with the metric.

        Examples:

            Ranges are useful when we want to know the distribution of a value.
            They're used by the :meth:`~striemann.metrics.Metrics.time` method internally.

            >>> metrics.recordRange("Customer height", 163)
            >>> metrics.recordRange("Customer height", 185)
            >>> metrics.recordRange("Customer height", 134)
            >>> metrics.recordRange("Customer height", 158)
            >>> metrics.recordRange("Customer height", 170)
            >>>
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [   {   'attributes': {},
                    'metric_f': -185,
                    'service': 'Customer height.min',
                    'tags': []},
                {   'attributes': {},
                    'metric_f': -134,
                    'service': 'Customer height.max',
                    'tags': []},
                {   'attributes': {},
                    'metric_f': -162.0,
                    'service': 'Customer height.mean',
                    'tags': []},
                {   'attributes': {},
                    'metric_f': 5,
                    'service': 'Customer height.count',
                    'tags': []}]

            Ranges respect tags an attributes when aggregating their values.

            >>> metrics.recordRange("Customer height", 163, sex='female')
            >>> metrics.recordRange("Customer height", 185, sex='male')
            >>> metrics.recordRange("Customer height", 134, tags='child', sex='male')
            >>> metrics.recordRange("Customer height", 158, sex='female')
            >>> metrics.recordRange("Customer height", 170, sex='male')
            >>>
            >>> metrics.flush()
            >>> pp.pprint(transport.last_batch)
            [   {   'attributes': {'sex': 'female'},
                    'metric_f': 158,
                    'service': 'Customer height.min',
                    'tags': []},
                {   'attributes': {'sex': 'female'},
                    'metric_f': 163,
                    'service': 'Customer height.max',
                    'tags': []},
                {   'attributes': {'sex': 'female'},
                    'metric_f': 160.5,
                    'service': 'Customer height.mean',
                    'tags': []},
                {   'attributes': {'sex': 'female'},
                    'metric_f': 2,
                    'service': 'Customer height.count',
                    'tags': []},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 170,
                    'service': 'Customer height.min',
                    'tags': []},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 185,
                    'service': 'Customer height.max',
                    'tags': []},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 177.5,
                    'service': 'Customer height.mean',
                    'tags': []},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 2,
                    'service': 'Customer height.count',
                    'tags': []},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 134,
                    'service': 'Customer height.min',
                    'tags': 'child'},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 134,
                    'service': 'Customer height.max',
                    'tags': 'child'},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 134.0,
                    'service': 'Customer height.mean',
                    'tags': 'child'},
                {   'attributes': {'sex': 'male'},
                    'metric_f': 1,
                    'service': 'Customer height.count',
                    'tags': 'child'}]
        """
        self._ranges.record(service_name, value, ttl, tags, kwargs)

    def flush(self, is_closing=False):
        """Flush all metrics to the underlying transport.

        Args:
            is_closing (bool): True if the transport should be shut down.
        """
        self._gauges.flush(self._transport)
        self._counters.flush(self._transport)
        self._ranges.flush(self._transport)
        self._transport.flush(is_closing)
