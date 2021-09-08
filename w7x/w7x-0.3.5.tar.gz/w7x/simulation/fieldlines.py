"""
Stellop-XFieldlines Field Line Tracer Code with abstract backend.
"""
import w7x
import w7x.plotting.poincare
from w7x.core import Code, Backend
from w7x.simulation.flavors.field_line_tracer import (
    FieldLineTracerMixin,
    FieldLineTracerBackendMixin,
)


class FieldLinesBackend(Backend, FieldLineTracerBackendMixin):
    """
    Backend base class to be subclassed for implementations of the Field Line Tracer Code
    """


# pylint:disable=protected-access
class FieldLines(Code, FieldLineTracerMixin):  # pylint: disable=abstract-method
    """
    High level Field Line Tracer object.
    """

    STRATEGY_TYPE = FieldLinesBackend
    STRATEGY_DEFAULT = w7x.config.get_option("fieldlines", "backend")

    @w7x.node
    @w7x.dependencies.extends(
        FieldLineTracerMixin.trace_poincare,
        step=0.01,
    )
    def trace_poincare(self, state, **kwargs) -> w7x.State:
        poincare_surfaces = self.backend._trace_poincare(state, **kwargs)
        traces = w7x.model.Traces(poincare_surfaces=poincare_surfaces)
        return traces
