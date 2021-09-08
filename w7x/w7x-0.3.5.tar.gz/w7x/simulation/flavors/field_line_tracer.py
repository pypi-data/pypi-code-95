"""
Generic Field Line Tracer interface. The FieldLineTracerMixin describes a polymorphism to be used
by all field line tracer implementations. Derive the FieldLineTracerMixin, together with w7x.Code.
"""
import abc
import typing

import tfields
import w7x


# pylint:disable=too-few-public-methods
class FieldLineTracerBackendMixin(abc.ABC):
    """
    FieldLineTracerBackend interface
    """

    @staticmethod
    @abc.abstractmethod
    def _find_lcfs(state, **kwargs) -> tfields.Points3D:
        """
        Returns:
            A point on the surface off the last closed flux surface (lcfs)
        """

    @staticmethod
    @abc.abstractmethod
    def _trace_diffusion(
        state, **kwargs
    ) -> typing.Tuple[tfields.Points3D, tfields.Mesh3D]:
        pass

    @staticmethod
    @abc.abstractmethod
    def _trace_connection_length(
        state, **kwargs
    ) -> typing.Tuple[tfields.Points3D, tfields.Mesh3D]:
        pass

    @staticmethod
    @abc.abstractmethod
    def _trace_surface(state, **kwargs) -> tfields.Points3D:
        pass

    @staticmethod
    @abc.abstractmethod
    def _trace_poincare(state, **kwargs) -> typing.List[tfields.Points3D]:
        pass


class FieldLineTracerMixin(abc.ABC):
    """
    FieldLineTracer interface
    """

    @abc.abstractmethod
    @w7x.dependencies(
        w7x.config.CoilSets.Ideal,
        w7x.config.Assemblies.Pfcs,
    )
    def find_lcfs(self, state, **kwargs) -> w7x.State:
        """
        Calculate the position of the last closed flux surface.
        """
        # TODO-1(@dboe): if state.equilibrium.lcfs() -> use this one and return on point on
        # this surface maybe even sample from this surface directly in the tracer?

    @abc.abstractmethod
    @w7x.dependencies(
        w7x.config.CoilSets.Ideal,
        w7x.config.Assemblies.Pfcs,
        w7x.config.Plasma.Vacuum,
        start_points=w7x.dependencies.REQUIRED,
        step=5e-2,  # mendler: 0.02
        connection_limit=3e4,  # mendler: 3e4 ~ 98% hits, vorher 3e6
        inverse_field=False,
    )
    def trace_diffusion(self, state, **kwargs) -> w7x.State:
        """
        Run the tracing calculation with diffusion perpendicular to the field
        TODO-1(@dboe,@mendler): Convert temperature to velocity
            Diffusion isotrope orth to field -> do not vary step size
        """

    @abc.abstractmethod
    @w7x.dependencies(
        w7x.config.CoilSets.Ideal,
        w7x.config.Assemblies.Pfcs,
        w7x.config.Plasma.Vacuum,
        start_points=w7x.dependencies.REQUIRED,
        step=5e-2,
        connection_limit=3e4,  # Max connection lenghts ~ O(1e3) m, assym. case assume 1e4
        inverse_field=False,
    )
    def trace_connection_length(self, state, **kwargs) -> w7x.State:
        """
        Run the tracing calculation with diffusion perpendicular to the field
        """

    @abc.abstractmethod
    @w7x.dependencies(
        w7x.config.CoilSets.Ideal,
        start_point=w7x.dependencies.REQUIRED,
        n_points=w7x.dependencies.REQUIRED,
    )
    def trace_surface(self, state, **kwargs):
        """
        Trace a surface given a single point on that surface.

        Args:
            start_point: point to trace
            n_points: number of points required on that surface
            **kwargs: used for specific implementation of the backend
        """

    @abc.abstractmethod
    @w7x.dependencies(
        w7x.config.CoilSets.Ideal,
        phi=w7x.dependencies.REQUIRED,
        seeds=w7x.dependencies.REQUIRED,
        n_points=300,
    )
    def trace_poincare(self, state, **kwargs):
        """
        Calculate poincare points flux surface wise with field line tracer
        service from the web service.

        Args:
            phi (float or list of floats): list of phi in rad
            seeds (PoincareSeeds): seeds object for initial points for field
                lines. Each seed in seeds will give a surface
            n_points (int, optional): number of toroidal revolutions per
                seed = number of points per fluxSurface.

        Returns:
            list of Points3D instances of shape (len(seeds) * len(phi_list_rad, n_points)
                poincare_flux_surfaces.
                Iter order: for seed in seeds: for phi in phi_list_rad: ...
                Each flux surface represents a closed flux surface with length n_points.

        Returns:
            list of Points3D instances: poincare_flux_surfaces.
            Each fluxSurface
                        ->length: number of seeds
                        ->meaning: it represents a closed flux surface
                        ->phi0 is attached to the object as a stamp

        Examples:
            >>> import tfields
            >>> from w7x.simulation.flt import FieldLineTracer
            >>> node = FieldLineTracer()
            >>> state = node.trace_poincare(
            ...     phi=[0., 2.],
            ...     seeds=tfields.Points3D([[6.0, 0.0, 0.0]]),
            ...     n_points=3,
            ... )
            >>> res = state.traces.poincare_surfaces
            >>> assert len(res) == 1
            >>> assert res[0].shape == (6, 3)
            >>> state2 = node.trace_poincare(
            ...     phi=[0., 2.],
            ...     seeds=tfields.Points3D([[6.0, 0.0, 0.0]]),
            ...     n_points=1,
            ... )
            >>> res2 = state2.traces.poincare_surfaces
            >>> assert len(res2) == 1
            >>> assert res2[0].shape == (2, 3)
            >>> state3 = node.trace_poincare(
            ...     phi=[2.],
            ...     seeds=tfields.Points3D([[6.0, 0.0, 0.0], [5.8, 0.0, 0.0]]),
            ...     n_points=1,
            ... )
            >>> res3 = state3.traces.poincare_surfaces
            >>> assert len(res3) == 2
            >>> assert res3[0].shape == (1, 3)
            >>> assert res3[1].shape == (1, 3)
        """

    #############################################################
    # Methods that perform more than just forwarding to backend #
    #############################################################

    @w7x.dependencies.extends(
        trace_connection_length,
        inverse_field=w7x.dependencies.REJECTED,
    )
    def connection_length(
        self,
        state: w7x.State,
        mode: str = "t2t",
        **kwargs,
    ) -> w7x.State:
        """
        Calculate the connection length

        Args:
            *args: state
            start_points:
                int: number of points to trace
                Points3D: full start point set that should be traced.
                    This requires less computation
            mode: variant choice on how to handle the calculation
                't2t': -> 'target to target' connection length. Trace both directions
                    (inverse_field).
            **kwargs: forwarded to trace_diffusion

        Returns:
            state : State
                A state object with the updated diffusion etries

        """
        if mode == "t2t":
            # target to target connection legnth
            with w7x.stateful(False):
                pwi = w7x.model.Pwi.merged(
                    self.trace_connection_length(state, inverse_field=False, **kwargs),
                    self.trace_connection_length(state, inverse_field=True, **kwargs),
                )
            state = w7x.State.merged(state, pwi)
        else:
            raise NotImplementedError(f"Mode '{mode}' not implemented.")
        return state

    @w7x.dependencies.extends(
        trace_diffusion,
        inverse_field=w7x.dependencies.REJECTED,
        mode="bidirectional",
    )
    def diffusion(
        self,
        state: w7x.State,
        **kwargs,
    ) -> w7x.State:
        """
        Args:
            *args: state
            start_points:
                int: number of points to trace
                Points3D: full start point set that should be traced.
                    This requires less computation
            mode: Mode of calculation. options:
                "bidirectional": Trace forward and backward with diffusion
                "counterflow": = "bidirectional". Followed by (diffusive) tracing backwards
                    respectively from hit points with different parameters (maybe without diff?).
            **kwargs: forwarded to trace_diffusion

        Returns:
            state : State
                A state object with the updated diffusion etries

        Examples:
            >>> import tfields
            >>> import w7x
            >>> from w7x.simulation import FieldLineTracer

            Triangle approximating the bean plane
            >>> mesh = tfields.Mesh3D([[5.4,0,-1], [5.4,0,1], [6.5,0,0]],
            ...                       faces=[[0,1,2]], coord_sys='cylinder')

            Machine constitued from bean plane triangle and divertor
            >>> assembly = w7x.model.Assembly(
            ...     components=[w7x.model.Assembly(
            ...         components=[w7x.model.Component(id=165),
            ...                     w7x.model.Component(mesh=mesh)
            ...     ])
            ... ])
            >>> node = FieldLineTracer(assembly)
            >>> node.backend = 'mock'

            Initial point starting very close to the triangle
            >>> initial_points = tfields.Points3D([[6.0,0.0001,0]], coord_sys='cylinder')
            >>> state = node.diffusion(start_points=initial_points).compute()

            As expected, the triangle was hit only
            >>> assert len([pci.hit_points_faces for pci in state.pwi.components]) == 2
            >>> for pci in state.pwi.components:
            ...     assert len(pci.hit_points_faces) == 1
        """
        n_start = None
        start_points = kwargs.pop(
            "start_points", 12500
        )  # This will be remembered by history
        if isinstance(start_points, int):
            n_start = start_points
            state = self.find_lcfs(state)
            # TODO(@dboe):
            # default: 1 (mendler) or 0.5 (gao) cm inside
            #     check: projektion von 30 cm in die dreiecksebene, schwerpunkt, winkelverteilung?
            # better surface  - if close to rational, you'll have a bundle no matter what step size
            #                 - check iota? Pick position at iota inside the lcfs without resonance
            #                       - get lcfs, check iota, if iota resonant, move inward 1cm
            #                       - while iota in bound of resondance:
            #                           move inward 1cm
            #                       - if new iota different resonance:
            #                           Intervallschachtelung
            #                       - check iota, if iota resonant, move inward 1cm
            #                 - if iota close to rational, move inwards 1 cm at least
            #                 - check crossection at phi=x (project) check distribution
            #                 - if runtime too large, just do vmec run and smple surface?
            #    - why not axis, if step size is large?
            start_point = state.traces.lcfs_point
            # start_point[:, 0] = start_point[:, 0] - 0.005  # TODO: remove after sweep scan
            state = self.trace_surface(
                state,
                start_point=start_point,
                n_points=n_start,
            )
            if w7x.distribute.enabled():
                state = state.compute()
            start_points = state.traces.surface

        state = w7x.State.merged(
            self.trace_diffusion(state, start_points=start_points, **kwargs),
            self.trace_diffusion(
                state, inverse_field=True, start_points=start_points, **kwargs
            ),
        )

        return state
