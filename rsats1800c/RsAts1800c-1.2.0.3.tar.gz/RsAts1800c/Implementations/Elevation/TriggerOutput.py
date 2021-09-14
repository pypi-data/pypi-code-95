from ...Internal import Instrument


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TriggerOutput:
	"""Trigger output of the elevation movement"""
	def __init__(self, io: Instrument):
		self._io = io

	def set_state(self, state: bool) -> None:
		"""CONT:ELEV:TRIG:STAT \n
		Enables or disables the generation of a hardware trigger event at every given number of degrees of elevation-axis movement.
		The number of degrees is specified in set_step()"""
		self._io.write_bool_as_int('CONT:ELEV:TRIG:STAT', state)

	def set_step(self, step: float) -> None:
		"""CONT:ELEV:TRIG:STEP \n
		Configures the elevation axis to generate a trigger event every given number of degrees, if enabled.
		The range of step sizes depends on several parameters, for example elevation speed and measurement instrument speed. We recommend a minimum step size of 3° for 20°/s elevation speed and 5° for 50°/s elevation speed."""
		self._io.write_float('CONT:ELEV:TRIG:STEP', step)
