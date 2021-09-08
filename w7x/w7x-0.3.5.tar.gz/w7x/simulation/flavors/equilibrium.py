"""
Generic Equilibrium interface
"""

import abc
import w7x


class EquilibriumMixin(abc.ABC):
    """
    Equilibrium interface.
    """

    @abc.abstractmethod
    @w7x.dependencies(
        w7x.config.CoilSets.Ideal,
        w7x.config.Plasma.Vacuum,
        w7x.config.Equilibria.InitialGuess,
        free_boundary=True,
        dry_run=False,
    )
    def free_boundary(self, state, **kwargs) -> w7x.State:
        """
        Compute the free boundary ideal-MHD equilibrium.
        """

    @abc.abstractmethod
    @w7x.dependencies(
        w7x.config.Plasma.Vacuum,
        w7x.config.Equilibria.InitialGuess,
        free_boundary=False,
        dry_run=False,
    )
    def fixed_boundary(self, state, **kwargs) -> w7x.State:
        """
        Compute the fixed boundary ideal-MHD equilibrium.
        """
