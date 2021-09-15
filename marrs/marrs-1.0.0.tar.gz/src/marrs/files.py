from .log import debug
from .utils import *


class FilesOperations:

	def __init__(self, device):
		self._device = device

	def pull(self, remote_path, local_path):
		debug("Pulling file from device '{0}': '{1}' -> '{2}'".format(
			self._device.id, remote_path, local_path))
		check_output("{0} pull {1} {2}".format(self._device.__adb_prefix__(),
		                                       remote_path, local_path))

	def push(self, local_path, remote_path):
		debug("Puhsing file to device '{0}': '{1}' -> '{2}'".format(
			self._device.id, local_path, remote_path))
		check_output("{0} push {1} {2}".format(self._device.__adb_prefix__(),
		                                       local_path, remote_path))

	def exists(self, remote_path):
		debug("Checking if file exists on device '{0}': '{1}'".format(
			self._device.id, remote_path))
		return self._device.shell(
			'ls {0} > /dev/null 2>&1; echo $?'.format(remote_path)) == '0'

	def remove(self, remote_path):
		if not self.exists(remote_path):
			debug("Remote path does not exist ('{0}')".format(remote_path))
			return False

		debug("Removing '{0}' from device '{1}'".format(
			remote_path, self._device.id))
		return self._device.shell(
			'rm -rf {0} > /dev/null 2>&1; echo $?'.format(remote_path)) == '0'
