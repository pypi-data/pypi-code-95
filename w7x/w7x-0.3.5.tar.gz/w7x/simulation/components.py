"""
Bozhenkovs Field Line Tracer Code with abstract backend.
"""
from abc import abstractmethod
import numpy as np
import scipy.stats

import tfields
import w7x
import w7x.plotting.poincare
from w7x.core import Code, Backend


class ComponentsBackend(Backend):
    """
    Backend base class to be subclassed for implementations of the Components db code
    """

    @staticmethod
    @abstractmethod
    def _get_mesh(mm_id) -> tfields.Mesh3D:
        """
        Get the mesh associated with the mm_id

        Args:
            mm_id (int): components db id of meshed model
        """

    @staticmethod
    @abstractmethod
    def _mesh_slice(component, phi) -> tfields.TensorMaps:
        """
        Get poincare points for a set of mm_ids and phis
        with intersectMeshPhiPlane service from the Mesh server web service.

        Args:
            phi (list of floats): list of phi in rad

        Returns:
            phi_container (list[list[Points3D for each vertex] for each mm_id] for each phi)
        """

    @staticmethod
    def _module(state, **kwargs):
        """
        Returns:
            int: which module the geometry is in

        Legacy:
            previously called 'component_module'
        """


# pylint:disable=protected-access
class Components(Code):  # pylint: disable=abstract-method
    """
    High level Field Line Tracer object.
    """

    STRATEGY_TYPE = ComponentsBackend
    STRATEGY_DEFAULT = "web_service"

    @w7x.node
    @w7x.dependencies(w7x.dependencies.REQUIRED(w7x.model.Assembly), ...)
    def set_meshes(self, state, component=None) -> w7x.State:
        """
        Update the state.assembly.comopnents[:].components[:].mesh field

        If state.has(PWI), convert entries there to Tensors
        """
        components = state.assembly.get_components(flat=True)
        if component is not None:
            # check this component is part of the state
            for comp in components:
                if comp.id == component.id:
                    break
            else:
                raise ValueError(
                    f"component with id {component.id} not part of state.assembly"
                )

            components = [component]

        assembly = w7x.model.Assembly()
        for comp in components:
            if comp.mesh is None:
                comp.mesh = self.backend._get_mesh(comp.id)
            assembly.add(comp)

        return assembly

    @w7x.dependencies(
        w7x.dependencies.REQUIRED(w7x.model.Assembly),
        phi=w7x.dependencies.REQUIRED,
    )
    def mesh_slice(self, state, **kwargs) -> w7x.model.Assembly:
        """
        Add slices for each component of the state.assembly to the component

        Args:
            phi: list of phi or phi in radian
        """
        phi_list_rad = kwargs.pop("phi")
        try:
            iter(phi_list_rad)
        except TypeError:
            # not iterable
            phi_list_rad = [phi_list_rad]

        component_phi_res = []
        for component in state.assembly.get_components(flat=True):
            component = w7x.model.Component(
                id=component.id,
                custom_id=component.custom_id,
                slices=component.slices,
            )
            if component.slices is None:
                component.slices = {}
            for phi in phi_list_rad:
                if phi not in component.slices:
                    res = self.backend._mesh_slice(component, phi)
                    component_phi_res.append((component, phi, res))

        @w7x.node
        def merge_slices_to_assembly(slice_tuples):
            """
            This function is necessary to encapsulate the setitem operation for dask.delayed
                -> parallel graph
            """
            assembly = w7x.model.Assembly()
            for component, phi, res in slice_tuples:
                component.slices[phi] = res
                assembly.add(component)
            return assembly

        return merge_slices_to_assembly(component_phi_res)


def n_hits_from_load(heat_load, n_tot, area, p_conv, ceta):
    """
    Args:
        heat_load(float) heat load
        n_tot (int): total number of hits
        area (float)
        p_conv (float): convective power
        ceta (int): mapping factor

    Returns float: number of hits expected on area given Args
    """
    p_conv *= 1.0 / ceta  # correct for mapping all divertors to one
    return int(round((1.0 * heat_load * n_tot * area) / p_conv))


def load_from_n_hits(n_hits, n_tot, area, p_conv, ceta):
    """
    Args:
        n_hits (int): numer of hits on the area
        n_tot(int): total number of hits
        area (float)
        p_conv (float): convective power
        ceta (int): mapping factor

    Returns float: heat per area given Args
    """
    p_conv *= 1.0 / ceta  # correct for mapping all divertors to one
    return (n_hits * p_conv) * 1.0 / (n_tot * area)


def prob_n_hits_lt_n_des(n_hits_list, n_des_list):
    """
    Returns: P(n_hits < n_des | p_conv, n_tot, q_design)
        see [Boeckenhoff2019](doi:10.1088/1741-4326/ab201e)
    """
    tile_probs = []
    for n_hits, n_des in zip(n_hits_list, n_des_list):
        n_hits = int(np.round(n_hits))
        prob = scipy.stats.poisson.cdf(n_des, n_hits)
        tile_probs.append(float(prob))
    return tile_probs
