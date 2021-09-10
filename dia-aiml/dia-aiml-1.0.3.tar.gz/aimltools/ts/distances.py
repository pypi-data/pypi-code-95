"""
Sub-module of TSAnalysis

Contains classes and methods to compute distances between signals
"""

import numpy as np
from tslearn.metrics import soft_dtw, dtw
from aimltools.ts.dependencies import PD_distance
from aimltools.ts.dependencies import tam_distance as tam
from abc import ABCMeta, abstractmethod
import logging

logger = logging.getLogger(__name__)


# Defines distance mixins
class BaseMixin(metaclass = ABCMeta):
    """
    Defines pattern for child mixins
    """

    @abstractmethod
    def compute_distance(self):
        """Mandatorily implement this method in all child mixins"""

    @abstractmethod
    def compute_distance_(self):
        """Mandatorily implement this method in all child mixins"""


class EuclideanMixin(BaseMixin): 
    """
    Mixin class for computing Euclidean distance between two signals
    """

    def compute_distance(self, signalA, signalB):
        
        # Checks if the arrays are of equal lengths
        try:
            assert len(signalA) == len(signalB)
        except:
            raise AssertionError("""
            Expected arrays of equal lengths. 
            Received lengths of {} and {} respectively. 
            """.format(len(signalA), len(signalB)))
        
        euclidean_dist = np.linalg.norm(signalA - signalB, ord=2)
        return euclidean_dist

    def compute_distance_(self, signalA, signalB):
        return self.compute_distance(signalA, signalB)


class PDMixin(BaseMixin):  
    """
    Mixin class for computing Permutation Distance between two signals
    """ 
    def __init__(self, metric = 'kullback', m = 3, step = 1):
        self.__metric = metric
        self.__m = m
        self.__step = step

    def compute_distance(self, signalA, signalB, metric = 'kullback', m = 3, step = 1):
        metric = metric.lower()
        logger.info("Divergence metric set to {}".format(metric.title()))
        pd_distance = PD_distance(signalA, signalB, metric, m, step)
        return pd_distance

    def compute_distance_(self, signalA, signalB):
        return self.compute_distance(signalA, signalB, metric = self.__metric, m = self.__m, step = self.__step)


class SoftDTWMixin(BaseMixin):
    """
    Mixin class for computing Soft Dynamic Time Warping distance between two signals
    """
    def __init__(self, gamma=1.0, normalize = True):
        self.__gamma = gamma
        self.__normalize = normalize

    def compute_distance(self, signalA, signalB, gamma=1.0, normalize = True):
        if normalize == True:
            soft_dtw_distance_AB = soft_dtw(signalA, signalB, gamma)
            soft_dtw_distance_AA = soft_dtw(signalA, signalA, gamma)
            soft_dtw_distance_BB = soft_dtw(signalB, signalB, gamma)
            soft_dtw_distance = soft_dtw_distance_AB - (1 / 2) * ((soft_dtw_distance_AA) + (soft_dtw_distance_BB))
        else:
            soft_dtw_distance = soft_dtw(signalA, signalB, gamma)

        return soft_dtw_distance

    def compute_distance_(self, signalA, signalB):
        return self.compute_distance(signalA, signalB, gamma=self.__gamma, normalize=self.__normalize)


class DTWMixin(BaseMixin):
    """
    Mixin class for computing Dynamic Time Warping distance between two signals
    """
    def __init__(self, global_constraint=None, sakoe_chiba_radius=None, itakura_max_slope=None):
        self.__global_constraint = global_constraint
        self.__sakoe_chiba_radius = sakoe_chiba_radius
        self.__itakura_max_slope = itakura_max_slope

    def compute_distance(self, signalA, signalB, global_constraint=None, 
                            sakoe_chiba_radius=None, itakura_max_slope=None):
        dtw_distance = dtw(signalA, signalB, global_constraint, 
                            sakoe_chiba_radius, itakura_max_slope)
        return dtw_distance

    def compute_distance_(self, signalA, signalB):
        return self.compute_distance(signalA, signalB, global_constraint=self.__global_constraint, sakoe_chiba_radius=self.__sakoe_chiba_radius, itakura_max_slope=self.__itakura_max_slope)

class TAMMixin(BaseMixin):
    """
    Mixin class for computing Time Alignment Measure distance between two signals 
    """ 

    def compute_distance(self, signalA, signalB):
        tam_dist = tam(signalA, signalB)
        return tam_dist

    def compute_distance_(self, signalA, signalB):
        return self.compute_distance(signalA, signalB)

# Defines base class
class TSDistanceBaseClass(metaclass = ABCMeta):
    """
    Base class containing common functionality and abstract methods
    """

    def __init__(self, signalA, signalB, distance_type, **kwargs):
        self.signalA = signalA
        self.signalB = signalB
        self.distance_type = distance_type
        self.kwargs = kwargs

    def __repr__(self):
        return """Distance type = {}, \n
                Arguments = {}""".format(self.distance_type, self.kwargs)
    
    @abstractmethod
    def distance_method(self):
        """Mandatorily implement this method in all child classes"""


# Defines user interface
def tsdist(signalA, signalB, distance_type = 'euclidean',
            **kwargs):

    """
    A function to compute the distance between two time signal arrays

    Parameters
    ----------
    signalA : np.ndarray
            An array containing a signal/time series

    signalB : np.ndarray
            Another array containing a signal/time series

    distance_type : str
            The distance measure used for computation. Defaults to 'euclidean'
            Supported distances are:
            'euclidean' = Euclidean distance
            'pdc' = Permutation distribution clustering
            'tam' = Time alignment measure
            'dtw' = Dynamic time warping
            'sdtw' = Short dynamic time warping
            
    kwargs : dict
            Keyword arguments to be passed depending on
            the value of 'type'

    Returns
    -------
    distance : np.float64
            The computed distance metric
    """

    # Dict of a distance_type and its corresponding mixin
    # Add a new {distance_type: mixin} key-value pair to 
    # register a new distance implementation 
    distance_mixin_match_dict = {
                                'euclidean': EuclideanMixin,
                                'pdc': PDMixin,
                                'tam': TAMMixin,
                                'dtw': DTWMixin,
                                'sdtw': SoftDTWMixin
                                }

    supported = list(distance_mixin_match_dict.keys())

    try:
        mixin_to_use = distance_mixin_match_dict[distance_type]
    except:
        raise ValueError("""
        Unsupported value '{}' for distance_type. 
        Currently supported distances are -
        {}""".format(distance_type, supported))

    # Throws exception if mixin_to_use is not a child of BaseMixin
    assert issubclass(mixin_to_use, BaseMixin)
                   
    # Defines child class from base class and required mixin
    class TSDistance(TSDistanceBaseClass, mixin_to_use):

        def __init__(self, signalA, signalB, distance_type, **kwargs):
            super().__init__(signalA, signalB, distance_type, **kwargs)
        
        def distance_method(self):
            logging.info("Distance type = {}".format(self.distance_type))
            distance = self.compute_distance(signalA, signalB, **self.kwargs)
            return distance

    # Instantiates child class
    instance = TSDistance(signalA, signalB, distance_type, **kwargs)
    distance = instance.distance_method()
    return distance
            