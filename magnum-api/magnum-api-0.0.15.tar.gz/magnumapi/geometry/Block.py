from abc import ABC, abstractmethod, abstractproperty
from typing import List, Type

import pandas as pd
import matplotlib.pyplot as plt

from magnumapi.geometry.Area import Area
from magnumapi.geometry.roxie.BlockDefinition import BlockDefinition
from magnumapi.geometry.roxie.CableDefinition import CableDefinition
from magnumapi.geometry.roxie.ConductorDefinition import ConductorDefinition
from magnumapi.geometry.roxie.InsulationDefinition import InsulationDefinition
from magnumapi.geometry.roxie.StrandDefinition import StrandDefinition


class Block(ABC):
    """ An Block class implementing a container with block definitions from cadata input.
    In addition, the class stores initialized coordinates of all conductors per block.
    This is a base class extended by implementations of different types (cos-theta, rectangular, etc.).
    """

    def __init__(self,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition) -> None:
        """ Method constructing an instance of a Block class

        :param cable_def: a cable definition from cadata
        :param insul_def: an insulation definition from cadata
        :param strand_def: a strand definition from cadata
        :param conductor_def: a conductor definition from cadata
        """
        self.cable_def = cable_def
        self.insul_def = insul_def
        self.strand_def = strand_def
        self.conductor_def = conductor_def
        self.areas: List[Area] = []

    @abstractmethod
    def plot_block(self, ax: plt.Axes) -> None:
        """ Abstract method for plotting an insulated block

        :param ax: a matplotlib axis on which a block will be plotted
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def plot_bare_block(self, ax: plt.Axes) -> None:
        """ Abstract method for plotting a bare block

        :param ax: a matplotlib axis on which a bare block will be plotted
        """
        raise NotImplementedError('This method is not implemented for this class')

    def get_bare_areas(self) -> List[Area]:
        """ Method returning bare areas, i.e., areas without insulation

        :return: a list of areas without insulation of a given block
        """
        return [self.get_bare_area(area) for area in self.areas]

    def get_bare_area(self, area_ins: Area) -> Area:
        """ Abstract method for returning a bare area

        :param area_ins: an insulated area
        :return: a bare area
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def build_block(self) -> None:
        """ Abstract method for building a block

        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def to_roxie_df(self) -> pd.DataFrame:
        """ Abstract method for converting a block definition into a ROXIE-compatible dataframe

        """
        raise NotImplementedError('This method is not implemented for this class')

    def to_df(self) -> pd.DataFrame:
        """ Method concatenating rows representing coordinates of each area into a dataframe

        :return: a dataframe with coordinate information of each area of a block instance
        """
        return pd.concat([area.to_df() for area in self.areas], axis=0)

    def is_outside_of_first_quadrant(self, eps=1e-30) -> True:
        """ Method checking whether at least one area of a given block are outside of the first quadrant

        :param eps: a machine precision for comparison of 0 value
        :return: True if at least one area of a given block is outside of the first quadrant,
        False otherwise, i.e., if all areas are within the first quadrant.
        """
        if not self.areas:
            return False

        is_inside_first_quadrant = False
        for area in self.areas:
            is_inside_first_quadrant |= Area.is_outside_of_first_quadrant(area, eps=eps)

        return is_inside_first_quadrant
