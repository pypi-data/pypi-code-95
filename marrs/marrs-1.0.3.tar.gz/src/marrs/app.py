"""
Represents an Android Application.

This object can be retrieved by calling :py:meth:`~marrs.device.Device.get_app`,
:py:meth:`~marrs.device.Device.get_apps` or :py:meth:`~marrs.device.Device.install_app` methods on a :py:class:`~marrs.device.Device` object.
"""

from .android_manifest import AndroidManifest
from .frida import FridaAgent
from .storage import Storage
from .utils import *


class App:

	def __init__(self, device, package_name, remote_apk_path):
		self.device = device
		self.name = package_name
		self.remote_apk_path = remote_apk_path
		self.local_apk_path = None
		self.main_activity = None
		self.frida_agent = None
		self._tmp_dir = None

	def __str__(self):
		return self.name

	def __repr__(self):
		return "App('{0}')".format(self.name)

	def __del__(self):
		if self._tmp_dir:
			delete_folder(self._tmp_dir)

	# if self.frida_agent:
	#	self.frida_agent.kill()

	def is_installed(self):
		"""
		Check wether this app is installed on the device.

		:return: True if app is installed on the device, False otherwise
		:rtype: bool
		"""
		return self.device.is_app_installed(self.name)

	def install(self):
		"""
		Install this app on the device.
		The app's APK file is taken from the device.
		"""
		self.device.install_app(self.get_local_apk_path())

	def uninstall(self):
		"""
		Uninstall the application from the device.
		"""
		self.device.uninstall_app(self.name)

	def is_running(self):
		"""
		Check if this app is currently running on the device.

		:return: True if app is currently running, False otherwise.
		:rtype: bool
		"""
		return self.device.is_app_running(self.name)

	def clear_data(self):
		"""
		Clear application data.
		"""
		self.device.clear_app_data(self.name)

	def force_stop(self):
		"""
		Stop the application from running.
		"""
		self.device.force_stop_app(self.name)

	def start(self):
		"""
		Start the application.
		"""
		self.device.start_app(self.name, self.get_main_activity())

	def get_version(self):
		"""
		Get the version of the application.

		:return: The app's version if installed, None otherwise
		:rtype: str
		"""
		return self.device.get_app_version(self.name)

	def get_local_apk_path(self):
		"""
		Returns the local path to the app's APK file.
		If the APK doesn't exist on local machine, it will be pulled from the device to package's local storage.

		:return: The local path to the app's APK file
		:rtype: str
		"""
		if self.local_apk_path:
			return self.local_apk_path

		self._tmp_dir = Storage.create_temp_dir()
		local_apk_path = path.join(self._tmp_dir, get_filename(self.remote_apk_path, with_extension=True))
		self.device.files.pull(self.remote_apk_path, local_apk_path)
		self.local_apk_path = local_apk_path
		return self.local_apk_path

	def get_main_activity(self):
		"""
		Returns the name of the main activity of the app.

		:return: The name of the main activity.
		:rtype: str
		"""
		if self.main_activity:
			return self.main_activity

		local_apk_path = self.get_local_apk_path()
		manifest = AndroidManifest.from_apk(local_apk_path)
		self.main_activity = manifest.get_main_activity()
		return self.main_activity

	def attach_frida_agent(self, initial_script=None):
		"""
		Attach a :py:class:`~marrs.frida.agent.FridaAgent` to the app.

		:param initial_script: An initial script to run while the app is spawned.
		:type initial_script: str
		:return: An :py:class:`~marrs.frida.agent.FridaAgent` object or None if an error occured
		:rtype: :py:class:`~marrs.frida.agent.FridaAgent`
		"""
		self.device.__log__("Attaching frida agent to app", extra_info=self.name)

		if self.frida_agent is not None:
			self.device.__error__("	Frida agent is already attached to this app")
			return None

		if not self.device.is_rooted():
			self.device.__error__("	Device must be rooted in order to use frida")
			return None

		if not self.device.is_frida_server_running():
			self.device.__warn__("	Frida server is not running on the device")
			self.device.run_frida_server()

		self.frida_agent = FridaAgent(self, initial_script)
		return self.frida_agent
