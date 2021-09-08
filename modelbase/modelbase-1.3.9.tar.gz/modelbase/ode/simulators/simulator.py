"""Write me."""
from __future__ import annotations

import concurrent.futures as futures
import copy
import itertools as it
import sys as sys
import warnings
from functools import partial
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ...core.utils import warning_on_one_line
from ...utils.plotting import _get_plot_kwargs, _style_subplot, plot, plot_grid
from ..integrators import AbstractIntegrator
from ..models import Model
from . import _BaseRateSimulator, _BaseSimulator

from mpl_toolkits.mplot3d import Axes3D as _Axes3D  # flake8: NOQA


warnings.formatwarning = warning_on_one_line  # type: ignore


class _Simulate(_BaseRateSimulator[Model]):
    """Simulator for ODE models."""

    def __init__(
        self,
        model: Model,
        integrator: Type[AbstractIntegrator],
        y0: Optional[List[float]] = None,
        time: Optional[List[np.ndarray]] = None,
        results: Optional[List[np.ndarray]] = None,
        parameters: List[Dict[str, float]] = None,
    ) -> None:
        """
        Parameters
        ----------
        kwargs
            {parameters}
        """
        super().__init__(
            model=model,
            integrator=integrator,
            y0=y0,
            time=time,
            results=results,
            parameters=parameters,
        )

    def plot(
        self,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
        grid: bool = True,
        tight_layout: bool = True,
        ax: plt.Axes = None,
        figure_kwargs: Dict[str, Any] = None,
        subplot_kwargs: Dict[str, Any] = None,
        plot_kwargs: Dict[str, Any] = None,
        grid_kwargs: Dict[str, Any] = None,
        legend_kwargs: Dict[str, Any] = None,
        tick_kwargs: Dict[str, Any] = None,
        label_kwargs: Dict[str, Any] = None,
        title_kwargs: Dict[str, Any] = None,
    ) -> Tuple[Optional[plt.Figure], Optional[plt.Axes]]:
        """Plot simulation results for a selection of compounds."""
        compounds = self.model.get_compounds()
        x = cast(np.ndarray, self.get_time(concatenated=True))
        y = cast(pd.DataFrame, self.get_full_results_df(normalise=normalise, concatenated=True))
        if x is None or y is None:
            return None, None
        return plot(
            plot_args=(x, y.loc[:, compounds]),
            legend=compounds,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            grid=grid,
            tight_layout=tight_layout,
            ax=ax,
            figure_kwargs=figure_kwargs,
            subplot_kwargs=subplot_kwargs,
            plot_kwargs=plot_kwargs,
            grid_kwargs=grid_kwargs,
            legend_kwargs=legend_kwargs,
            tick_kwargs=tick_kwargs,
            label_kwargs=label_kwargs,
            title_kwargs=title_kwargs,
        )
