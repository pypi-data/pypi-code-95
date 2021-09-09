from numpy import ndarray
from typing import Tuple, Union

Matrix = Union[ndarray]
MatrixPair = Tuple[Matrix, Matrix]
MatrixTriplet = Tuple[Matrix, Matrix, Matrix]
MatrixOrTriplet = Union[Matrix, MatrixTriplet]
ObservationMatrix = Tuple[Matrix, Matrix]
ObservationTriplet = Tuple[MatrixTriplet, MatrixTriplet]
Observation = Union[ObservationMatrix, ObservationTriplet]
