from ...enums import MovementDirection
from ...Internal import Instrument


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StepMovement:
	"""Step movement of the azimuth"""
	def __init__(self, io: Instrument):
		self._io = io

	def set_size(self, step: float) -> None:
		"""CONT:AZIM:POS:STEP \n
		Sets the single-step size. Range: 0.1 .. 360."""
		self._io.write_float('CONT:AZIM:POS:STEP', step)

	def set_direction(self, direction: MovementDirection) -> None:
		"""CONT:AZIM:STEP:DIR POS|NEG \n
		Configures the single-step movement for the Azimuth."""
		assert isinstance(direction, MovementDirection), f'input variable "direction", value {direction} is not of enums.MovementDirection type'
		cmd = 'CONT:AZIM:STEP:DIR '
		if direction == MovementDirection.POSitive:
			cmd += 'POS'
		elif direction == MovementDirection.NEGative:
			cmd += 'NEG'
		self._io.write(cmd)

	def start(self) -> None:
		"""CONT:AZIM:STEP:STAR \n
		Moves the azimuth by a single step."""
		self._io.write('CONT:AZIM:STEP:STAR')
