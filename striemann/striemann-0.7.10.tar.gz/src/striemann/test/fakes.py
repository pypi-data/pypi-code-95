"""In-memory fake replacements for objects in striemann.metrics.

For use in tests.
"""

__all__ = ["metric_id", "FakeTimer", "FakeMetrics"]

from striemann.metrics import MetricId
from striemann._deprecation import deprecated


def metric_id(service_name, tags=None, fields=None):
    """Helper function for creating instances of :class:`~striemann.metrics.MetricId`"""
    return MetricId(
        service_name, frozenset(tags or []), frozenset(fields.items() or {})
    )


class FakeTimer:
    """Fake implementation of the context manager :meth:`~striemann.metrics.Metrics.time`"""

    def __init__(self, service_name, tags, attributes, metrics):
        self.metric_id = metric_id(service_name, tags, attributes)
        self.metrics = metrics

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.metrics.append((self.metric_id, 1))


class FakeMetrics(list):
    """Fake implementation of :class:`~striemann.metrics.Metrics`

    Examples:

        >>> import expects
        >>> from striemann.test.expectsmatcher import contain_metric
        >>> metrics = FakeMetrics()
        >>> metrics.incrementCounter('Burgers sold')
        >>>
        >>> assert (metric_id('Burgers sold'), 1) in metrics

        >>> metrics.recordGauge('Hunger level', 10)
        >>> expect(metrics).to(contain_metric('Hunger level'))
    """

    @deprecated("Use FakeMetrics rather than FakeMetrics.metrics")
    @property
    def metrics(self):
        return self

    def recordGauge(self, service_name, value, tags=[], **kwargs):
        self.append((metric_id(service_name, tags, kwargs), value))

    def recordRange(self, service_name, value, tags=[], **kwargs):
        self.append((metric_id(service_name, tags, kwargs), value))

    def incrementCounter(self, servicename, value=1, tags=[], **kwargs):
        self.append((metric_id(servicename, tags, kwargs), value))

    def time(self, service_name, tags=[], **kwargs):
        return FakeTimer(service_name, tags, kwargs, self)

    def flush(self, is_closing=False):
        self.clear()
