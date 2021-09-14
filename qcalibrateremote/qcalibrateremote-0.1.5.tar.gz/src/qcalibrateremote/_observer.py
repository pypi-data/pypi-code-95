#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from dataclasses import dataclass
from typing import Dict, List

from ._fom import Pulse


@dataclass
class IterationResult:
    iteration: int
    parameters: Dict[str, float]
    pulses: Dict[str, Pulse]
    figure_of_merit: float
    data: str


@dataclass
class PulseMeta:
    """Pulse meta parameter"""
    index: int
    """ordinal of a pulse in pulse meta list"""
    name: str
    """name of the pulse"""
    configuration: str
    """JSON serilized pulse optimization meta-parameters like basis, sampling, initial quess and boundaries"""


@dataclass
class ParameterMeta:
    """Parameter optimization meta"""
    index: int
    """ordinal of a parameter in a parametzer list"""
    name: int
    """name of a parameter"""
    configuration: str
    """parameter optimization configuration, like boundaries and initial guess"""


@dataclass
class RunMetaParameters:
    """run attributes"""
    run_id: str
    """database ID"""
    configuration: str
    """JSON serialized optimization parameters"""
    parameter_metas: List[ParameterMeta]
    """List of optimizable parameters"""
    pulse_metas: List[PulseMeta]
    """List of optimizable pulses"""


class OptimizationObserver:
    """Base optimization observer
        don't do anything
    """

    def on_start(
            self,
            run_id: str,
            configuration: str,
            parameter_metas: List[ParameterMeta],
            pulse_metas: List[PulseMeta],
            **kwargs):
        """Invoked after the run entity is created

        Parameters
        ----------
        run_id : str
            The run entity id, can be used to navigate user to the run details page
        configuration : str
            JSON serilaized configuration
        parameter_metas : List[ParameterMeta]
            list of metadata (like range and ansatz) of optimized parameters
        pulse_metas : List[PulseMeta]
            list of metadata (like base, range and ansatz) of optimized pulses
        """
        ...

    def on_iteration(
            self,
            iteration: int,
            parameters: Dict[str, float],
            pulses: Dict[str, Pulse],
            figure_of_merit: float,
            data: str,
            **kwargs):
        """invoked after the figure of merit is evaluated by the client

        Parameters
        ----------
        iteration : int
            the number of iteration (starting with 0)
        parameters : Dict[str, float]
            optimization parametes to evaluate, the key matches parameter name as defined in experiment configuration
        pulses : Dict[str, Pulse]
            pulse parametes to evaluate, the key matches parameter name as defined in experiment configuration
        figure_of_merit : float
            the evaluated figure of merit value
        data : str
            arbitrary data, returened by the figure of merit evaluator
        """
        ...

    def on_end(self):
        """Called as a last before the optimization is finished, can be used to free resources like network connection or mutexes
        """
        ...

    def on_error(self, exception: Exception):
        """Invoked if optimization is interrupted due to an exception

        Parameters
        ----------
        exception : Exception
            The exceptio caused the optimization run abortion
        """
        ...


class OptimizationResultCollector(OptimizationObserver):
    """Stores intermediate iteration results
    """

    def __init__(self) -> None:
        super().__init__()
        self._parameters: RunMetaParameters = None
        self._iterations: List[IterationResult] = []
        self._exception: Exception = None
        self._top: List[IterationResult] = []

    def on_start(self, run_id, configuration: str, parameter_metas, pulse_metas, **kwargs):
        self._parameters = RunMetaParameters(
            run_id=run_id,
            configuration=configuration,
            parameter_metas=parameter_metas,
            pulse_metas=pulse_metas)

    def on_iteration(self,
                     iteration: int,
                     parameters: Dict[str, float],
                     pulses: Dict[str, Pulse],
                     figure_of_merit: float,
                     data: str,
                     **kwargs):
        iteration_result = IterationResult(
            iteration=iteration,
            parameters=parameters,
            pulses=pulses,
            figure_of_merit=figure_of_merit,
            data=data)

        self._iterations.append(iteration_result)

        if len(self._top) == 0:
            self._top.append(iteration_result)
        else:
            # TODO: implement parametrisable multiple top
            if self._top[0].figure_of_merit > iteration_result.figure_of_merit:
                self._top[0] = iteration_result

    def on_error(self, exception: Exception):
        self._exception = exception

    @property
    def parameters(self) -> RunMetaParameters:
        """ gets optimization run parameters

        Returns
        -------
        RunMetaParameters
            optimization run parameters
        """
        return self._parameters

    @property
    def iterations(self) -> List[IterationResult]:
        """ gets iteration results

        Returns
        -------
        List[IterationResult]
            iteration results, last iteration last
        """
        return self._iterations

    @property
    def exception(self) -> Exception:
        """ gets         

        Returns
        -------
        Exception
            exeption in case of error
        """
        return self.exception

    @property
    def top(self) -> List[IterationResult]:
        """ gets best iterations (currently just the single one)

        Returns
        -------
        List[IterationResult]
            iteration(s) with  the lowest figure of merit value, the best (lowest figure of merit) first
        """
        return self._top
