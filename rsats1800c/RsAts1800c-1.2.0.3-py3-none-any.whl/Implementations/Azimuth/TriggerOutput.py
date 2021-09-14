from ...Internal import Instrument


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TriggerOutput:
	"""Trigger output of the azimuth movement"""
	def __init__(self, io: Instrument):
		self._io = io

	def set_state(self, state: bool) -> None:
		"""CONT:AZIM:TRIG:STAT \n
		Enables or disables the generation of a hardware trigger event at every given number of degrees of azimuth-axis movement.
		The number of degrees is specified in set_step()"""
		self._io.write_bool_as_int('CONT:AZIM:TRIG:STAT', state)

	def set_step(self, step: float) -> None:
		"""CONT:AZIM:TRIG:STEP \n
		Configures the azimuth axis to generate a trigger event every given number of degrees, if enabled.
		The range of step sizes depends on several parameters, for example azimuth speed and measurement instrument speed. We recommend a minimum step size of 3° for 20°/s azimuth speed and 5° for 50°/s azimuth speed."""
		self._io.write_float('CONT:AZIM:TRIG:STEP', step)
