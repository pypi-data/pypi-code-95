from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np


class AbstractIntegrator(ABC):
    def __init__(self, rhs: Callable, y0: Union[np.ndarray, List[float]]) -> None:
        self.kwargs: Dict[str, Any] = {}

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def _simulate(
        self,
        *,
        t_end: Optional[float] = None,
        steps: Optional[int] = None,
        time_points: Optional[List[float]] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        pass

    @abstractmethod
    def _simulate_to_steady_state(
        self,
        *,
        tolerance: float,
        integrator_kwargs: Dict[str, Any],
        simulation_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        pass

    @abstractmethod
    def get_integrator_kwargs(self) -> Dict[str, Any]:
        pass
