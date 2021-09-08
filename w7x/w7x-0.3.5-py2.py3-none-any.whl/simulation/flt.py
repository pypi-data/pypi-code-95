"""
Bozhenkovs Field Line Tracer Code with abstract backend.
"""
import typing
import numpy as np

import tfields
import w7x
import w7x.plotting.poincare
from w7x.core import Code, Backend
from w7x.simulation.flavors.field_line_tracer import (
    FieldLineTracerMixin,
    FieldLineTracerBackendMixin,
)


class FieldLineTracerBackend(Backend, FieldLineTracerBackendMixin):
    """
    Backend base class to be subclassed for implementations of the Field Line Tracer Code
    """


# pylint:disable=protected-access
class FieldLineTracer(Code, FieldLineTracerMixin):
    """
    High level Field Line Tracer object.
    """

    STRATEGY_TYPE = FieldLineTracerBackend
    STRATEGY_DEFAULT = w7x.config.get_option("flt", "backend")

    @w7x.node
    @w7x.dependencies.extends(
        FieldLineTracerMixin.find_lcfs,
        step=0.1,
    )
    def find_lcfs(self, state, **kwargs):
        """
        Runtime of ~ 1 min for standard settings on web server

        Examples:
            >>> import w7x
            >>> flt = w7x.simulation.FieldLineTracer()
            >>> with w7x.stateful(False):
            ...     traces = flt.find_lcfs()  # would do the same, but for testing:
            >>> assert traces.lcfs_point[0, 0] > 6.2
            >>> assert traces.lcfs_point[0, 0] < 6.21

        """
        lcfs_point = self.backend._find_lcfs(state, **kwargs)
        traces = w7x.model.Traces(lcfs_point=lcfs_point)
        return traces

    @w7x.node
    @w7x.dependencies.extends(FieldLineTracerMixin.trace_diffusion)
    def trace_diffusion(self, state, **kwargs):
        pwi = self.backend._trace_diffusion(state, **kwargs)
        return pwi

    @w7x.node
    @w7x.dependencies.extends(
        FieldLineTracerMixin.trace_connection_length,
        step=5e-3,
    )
    def trace_connection_length(self, state, **kwargs):
        pwi = self.backend._trace_connection_length(state, **kwargs)
        return pwi

    @w7x.node
    @w7x.dependencies.extends(
        FieldLineTracerMixin.trace_surface,
        step=0.5,
    )
    def trace_surface(self, state, **kwargs):
        surface_points = self.backend._trace_surface(state, **kwargs)
        traces = w7x.model.Traces(surface=surface_points)
        return traces

    @w7x.dependencies.extends(
        FieldLineTracerMixin.trace_poincare,
        step=0.01,
    )
    def trace_poincare(self, state, **kwargs) -> w7x.State:
        poincare_surfaces = self.backend._trace_poincare(state, **kwargs)

        @w7x.node
        def merge_surfaces_to_traces(poincare_surfaces):
            traces = w7x.model.Traces(poincare_surfaces=poincare_surfaces)
            return traces

        traces = merge_surfaces_to_traces(poincare_surfaces)
        return traces

    #######################
    # Not (yet?) Stateful #
    #######################

    @w7x.node
    @w7x.dependencies.stateless(
        w7x.config.CoilSets.Ideal, points=w7x.dependencies.REQUIRED
    )
    def magnetic_field(self, state, **kwargs):
        """
        Args:
            points
        """
        return self.backend._magnetic_field(state, **kwargs)

    @w7x.node
    @w7x.dependencies.stateless(
        w7x.config.CoilSets.Ideal,
        points=w7x.dependencies.REQUIRED,
        phi=w7x.dependencies.REQUIRED,
        step=0.01,
        inverse_field=False,
    )
    def line_phi_span(self, state, **kwargs):
        """
        Args:
            points (Points3D): starting points of tracing
            phi (float): phi in radian
            step (flota): step width of the tracer task
            inverse_field: specify the direction of tracing by switching the bool
        """
        return self.backend._line_phi_span(state, **kwargs)

    @w7x.node
    @w7x.dependencies.extends_stateless(
        line_phi_span,
        phi_tolerance=1.0 / 180 * np.pi,
    )
    def line_phi(self, state, **kwargs):
        """
        Get the crossection of the field lines starting at <points> at exactly one
        phi (exact within the tolerance given by <phi_tolerance>).

        Args - see: line_phi_span, additional:
            phi_tolerance


        Returns:
            Points3D: piercing points of the lines,
                starting at <points> at exactly one
                phi (exact within the tolerance given by <phi_tolerance>).
                The return value will be empty an empty seuqence of Points3D,
                if the step size was not small enough.
        """
        phi = kwargs.get("phi")
        phi_tolerance = kwargs.pop("phi_tolerance")
        lines = self.backend._line_phi_span(state, **kwargs)
        container = []
        for line in lines:
            line.transform(tfields.bases.CYLINDER)
            inds = w7x.lib.tfields.where_phi_between(
                line, phi - phi_tolerance, phi + phi_tolerance
            )
            line = line[inds[0][-1:]]
            line[:, 1] = phi
            container.append(line)
        return tfields.Points3D.merged(*container)

    @w7x.node
    @w7x.dependencies.stateless(
        w7x.config.CoilSets.Ideal,
        points=w7x.dependencies.REQUIRED,
        step=0.2,
        return_type=list,
    )
    def magnetic_characteristics(self, state, **kwargs) -> tfields.TensorFields:
        """
        Args:
            points (field_line_server.types.Points3D): points to retrieve
                characteristics from. Give None to take lcfs point
            taskStepSize (float)
            return_type (type): return either list or tfields.TensorFields.

        Examples:
            >>> from w7x.simulation.flt import FieldLineTracer
            >>> from tfields import Points3D
            >>> flt = FieldLineTracer()
            >>> mchars = flt.magnetic_characteristics(
            ...     points=Points3D([[6.2, 0., 0.]]))  # This is long lasting.
            >>> assert len(mchars) == 1
            >>> mchar = mchars[0]
            >>> assert mchar.iota < 1
            >>> assert mchar.iota > 0.95
            >>> assert mchar.reff < 0.6
            >>> assert mchar.reff > 0.5
            >>> assert mchar.phi0 == 0.0

        """
        return self.backend._magnetic_characteristics(state, **kwargs)

    @w7x.node
    @w7x.dependencies.stateless(
        w7x.config.CoilSets.Ideal,
        phi=0,
        step=0.01,
    )
    def find_axis_at_phi(self, state, **kwargs):
        """
        Args:
            phi (float): phi in rad
            step (float): step size

        Returns:
            Points3D: magnetic axis position at phi=<phi>
        """
        return self.backend._find_axis_at_phi(state, **kwargs)


def __getattr__(name: str) -> typing.Any:
    """
    Forward to generic Api methods

    Note:
        Maybe look closer to
        https://stackoverflow.com/questions/2447353/getattr-on-a-module
    """
    backend_method_name = "_" + name
    if backend_method_name in list(
        filter(lambda x: not x.startswith("__"), dir(FieldLineTracerBackend))
    ):
        frontend_func = getattr(FieldLineTracer, name)
        default_attributes = w7x.dependencies.default_attributes(frontend_func)
        default_parameters = w7x.dependencies.default_parameters(frontend_func)
        backend = FieldLineTracer().backend
        try:
            backend_func = getattr(backend, backend_method_name)
        except AttributeError as err:
            raise NotImplementedError(
                "Backend {backend} requires implementation of {backend_method_name}".format(
                    **locals()
                )
            ) from err

        def forwarded(
            *state_components,
            **parameter_kwargs,
        ):
            state, parameter_kwargs = w7x.dependencies.updated_state_parameters(
                default_attributes,
                default_parameters,
                *state_components,
                **parameter_kwargs,
            )
            return backend_func(state, **parameter_kwargs)

        return forwarded

    raise AttributeError("%r has no attribute %r" % ("w7x.simulation.flt", name))
