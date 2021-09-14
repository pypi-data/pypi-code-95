from ...enums import MovementDirection
from ...Internal import Instrument


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StepMovement:
	"""Step movement of the elevation"""
	def __init__(self, io: Instrument):
		self._io = io

	def set_size(self, step: float) -> None:
		"""CONT:ELEV:POS:STEP \n
		Sets the single-step size. Range: 0.1 .. 360."""
		self._io.write_float('CONT:ELEV:POS:STEP', step)

	def set_direction(self, direction: MovementDirection) -> None:
		"""CONT:ELEV:STEP:DIR POS|NEG \n
		Configures the single-step movement for the Elevation."""
		assert isinstance(direction, MovementDirection), f'input variable "direction", value {direction} is not of enums.MovementDirection type'
		cmd = 'CONT:ELEV:STEP:DIR '
		if direction == MovementDirection.POSitive:
			cmd += 'POS'
		elif direction == MovementDirection.NEGative:
			cmd += 'NEG'
		self._io.write(cmd)

	def start(self) -> None:
		"""CONT:ELEV:STEP:STAR \n
		Moves the elevation by a single step."""
		self._io.write('CONT:ELEV:STEP:STAR')
