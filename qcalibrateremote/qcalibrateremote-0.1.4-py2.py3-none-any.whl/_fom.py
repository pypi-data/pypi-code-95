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

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Protocol

from numpy import ndarray


@dataclass
class FigureOfMerit:
    """ The result of infidelity (figure of merit evaluation).  
    """
    figure_of_merit: float
    """Pair of a figure of merit value (infidelity measure)
    """
    data: str
    """An arbitrary metadata to be stored in the database, i.e. raw measurement data
    """


@dataclass
class Pulse:
    """Defines ev
    """
    times: ndarray
    """puls value sampling offsets"""
    values: ndarray
    """puls values"""


class EvaluateFigureOfMerit(metaclass=ABCMeta):
    """Abstract class for figure of merit evaluation"""
    """. """

    @abstractmethod
    def evaluate(self, parameters: Dict[str, float], pulses: Dict[str, Pulse]) -> FigureOfMerit:
        """Abstract method for figure of merit evaluation

        Parameters
        ----------
        parameters : Dict[str,float]
            free optimistation parameters
        pulses : Dict[str, Pulse]
            dCRAB pulses 

        Returns
        -------
        FigureOfMerit
            data class of figure of merit and an arbitrary data serialized as a string
        """
        pass

    def close(self):
        """ Invoked on end of an optimization session, can be used to clean up 
        """
        ...


class EvaluateFigureOfMeritFactory(Protocol):
    """abstract figure of merit factory (abstract constructor)
    """
    def __call__(self, *args: Any, **kwds: Any) -> EvaluateFigureOfMerit: ...
