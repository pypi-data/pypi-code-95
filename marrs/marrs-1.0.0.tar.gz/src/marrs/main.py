from .device import Device
from .log import error
from .utils import check_output


def get_devices(rooted_only=False, adb_path='adb'):
	devices = check_output('"{0}" devices'.format(adb_path))

	devices = devices.strip().split('\n')[1:]  # skip first line

	def filter_func(line):
		parts = line.split()

		if len(parts) != 2:
			return False

		if parts[1] != 'device':
			return False

		return True

	def map_func(line):
		return Device(line.split()[0], adb_path)

	devices = list(map(map_func, filter(filter_func, devices)))

	if rooted_only:
		devices = list(filter(lambda d: d.is_rooted(), devices))

	return devices


def get_device(adb_path='adb'):
	"""
	Get the first device object.

	:param name: adb_path - The path to Android Debug Bridge binary
	:param type: str
	:return: Device
	"""
	devices = get_devices(adb_path=adb_path)

	if not devices:
		error("There are no connected devices")
		return None

	return devices[0]
