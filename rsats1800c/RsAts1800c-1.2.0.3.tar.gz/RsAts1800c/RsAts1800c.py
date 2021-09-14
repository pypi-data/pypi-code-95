from .Internal import Instrument


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RsAts1800c:

	def __init__(self, resource_name: str, preset: bool = False):
		"""Initializes new RsAts1800c session. \n
		:param resource_name: VISA resource name, e.g. 'TCPIP::192.168.2.1::200::SOCKET'
		:param preset: Presets the instrument - sends SYST:PRES command"""
		self._io = Instrument.Instrument(resource_name)
		self._io.visa_timeout = 5000
		self.driver_version = '1.2.0.3'
		if preset is True:
			self._io.write("SYST:PRES")

	def __str__(self):
		if self._io:
			return f"RsAts1800C session '{self._io.resource_name}'"
		else:
			return f"RsAts1800C with session closed"

	def close(self):
		"""Closes the active RsAts1800C session."""
		self._io.close()

	@property
	def azimuth(self):
		"""Group of azimuth-related commands"""
		if not hasattr(self, '_azimuth'):
			from .Implementations.Azimuth import Azimuth
			self._azimuth = Azimuth(self._io)
		return self._azimuth

	@property
	def elevation(self):
		"""Group of elevation-related commands"""
		if not hasattr(self, '_elevation'):
			from .Implementations.Elevation import Elevation
			self._elevation = Elevation(self._io)
		return self._elevation

	@property
	def feed_switcher(self):
		"""Group of feed switcher-related commands"""
		if not hasattr(self, '_feed_switcher'):
			from .Implementations.FeedSwitcher import FeedSwitcher
			self._feed_switcher = FeedSwitcher(self._io)
		return self._feed_switcher

	@property
	def system(self):
		"""Group of general system-related commands"""
		if not hasattr(self, '_system'):
			from .Implementations.System import System
			self._system = System(self._io)
		return self._system

	@property
	def utilities(self):
		"""Utilities - direct write and read methods"""
		if not hasattr(self, '_utilities'):
			from .Implementations.Utilities import Utilities
			self._utilities = Utilities(self._io, self.driver_version)
		return self._utilities
