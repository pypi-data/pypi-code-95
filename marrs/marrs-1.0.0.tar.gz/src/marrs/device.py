"""
Represents a connected Android Device
"""

import re
from time import sleep

from .android_manifest import AndroidManifest
from .app import App
from .consts import *
from .files import FilesOperations
from .log import *
from .storage import Storage
from .utils import *


class Device:

	def __get_all_apps__(self):
		res = self.shell("pm list packages -f")
		res = res.strip().split('\n')
		res = list(map(lambda x: x[len('package:'):], res))
		apps = []
		for p in res:
			eq_idx = p.rfind('=')
			remote_apk_path = p[:eq_idx]
			package_name = p[eq_idx + 1:]

			app = App(self, package_name, remote_apk_path)

			apps.append(app)

		return apps

	def __log__(self, s, level=Log.INFO, extra_info=None):
		to_print = Fore.GREEN + '[' + self.id + '] ' + Style.RESET_ALL + s

		if extra_info:
			to_print += " [" + Style.BRIGHT + Fore.MAGENTA + str(
				extra_info) + Style.RESET_ALL + "]"

		log(to_print, level=level, do_style=False)

	def __warn__(self, s, extra_info=None):
		self.__log__(Fore.YELLOW + s, Log.WARN, extra_info)

	def __dlog__(self, s, extra_info=None):
		self.__log__(Fore.BLUE + Style.BRIGHT + s, Log.DEBUG, extra_info)

	def __error__(self, s):
		self.__log__(Fore.RED + Style.BRIGHT + s, Log.ERROR)

	def __success__(self, s):
		self.__log__(Fore.GREEN + Style.BRIGHT + s, Log.INFO)

	def __adb_prefix__(self):
		return '"{0}" -s {1}'.format(self.adb_path, self.id)

	def __init__(self, serial, adb_path='adb'):
		self.id = serial
		self.adb_path = adb_path
		self.files = FilesOperations(self)

	def __repr__(self):
		return self.id

	def summary(self):
		"""
		Prints some details about the device.
		"""

		def aux_print(name, value):
			pad = 15
			self.__log__(Fore.CYAN + name.ljust(pad) + Style.RESET_ALL + str(value))

		self.__log__("Device summary:")
		aux_print("	Arch", self.get_arch())
		aux_print("	Android ver.", self.get_android_version())
		aux_print("	API level", self.get_api_level())
		aux_print("	Is rooted", self.is_rooted())

	def shell(self, cmd, wait=True, as_root=False):
		"""
		Run shell command on the device.

		:param cmd: The cmd to run.
		:type cmd: str
		:param wait: Should wait for the execution to finish
		:type wait: bool
		:param as_root: Run the command as root (supported only on rooted device with `su` binary)
		:type as_root: bool
		:return: The output if wait=True, the Popen object otherwise.
		:rtype: str
		"""
		cmd = '{0} shell {1} "{2}"'.format(self.__adb_prefix__(), "su root" if as_root else "", cmd)

		if wait:
			return check_output(cmd)

		return run_cmd(cmd)

	def get_apps(self, name_substr=None):
		"""
		Get a list of apps installed on the device.
		:param name_substr: Specify to return apps which their name contains this string
		:type name_substr: str
		:return: A list of apps
		:rtype: List of :py:class:`~marrs.app.App`s
		"""
		apps = self.__get_all_apps__()

		if name_substr:
			apps = list(filter(lambda app: name_substr in app.name, apps))

		return apps

	def get_app_version(self, app_name):
		"""
		Get application installed version.

		:param app_name: The full name of the app
		:type app_name: str
		:return: The version of the given app
		:rtype: str
		"""
		if not self.get_app(app_name):
			return None

		res = self.shell('dumpsys package {0} | grep versionName'.format(app_name))
		p = re.compile(r'versionName=([\.\d]+)')
		return p.findall(res)[0]

	def install_app(self, apk_path, force_install=False):
		"""
		Install an APK file on the device.

		:param apk_path: The path to the APK file
		:type apk_path: str
		:param force_install: If True, will install the APK if the app with the same version is already installed on the device
		:type force_install: bool
		:return: The :py:class:`~marrs.app.App` object of the installed app
		:rtype: :py:class:`~marrs.app.App`
		"""
		self.__log__("Installing app from apk ({0})".format(apk_path))

		manifest = AndroidManifest.from_apk(apk_path)
		app_name = manifest.get_package_name()

		self.__log__("	Installing app", extra_info=app_name)

		app = self.get_app(app_name)

		if app:
			current_version = app.get_version()
			version_to_install = manifest.get_package_version()

			if not force_install and current_version == version_to_install:
				self.__warn__(
					"	The package '{0}' with the same version ({1}) is already installed on the device".format(
						app_name, current_version))
				return app

			self.__warn__("	Package already installed on device, uninstalling version {0}".format(current_version))

			app.uninstall()

		check_output('{0} install "{1}"'.format(self.__adb_prefix__(), apk_path))

		return self.get_app(app_name)

	def is_app_installed(self, app_name):
		"""
		Check if app is installed on the device.

		:param app_name: The name of the application
		:type app_name: str
		:return: True if the app is installed on the device, False otherwise.
		:rtype: bool
		"""
		return self.get_app(app_name) is not None

	def uninstall_app(self, app_name):
		"""
		Uninstall application from the device.

		:param app_name: The application's name to uninstall.
		:type app_name: str
		"""
		self.__log__("Uninstalling app", extra_info=app_name)

		if not self.is_app_installed(app_name):
			self.__warn__("  App is not installed")
			return

		check_output("{0} uninstall {1}".format(self.__adb_prefix__(), app_name))

	def get_app(self, app_name):
		"""
		Get app by name.

		:param app_name: The name of the app
		:type app_name: str
		:return: :py:class:`~marrs.app.App` object if app with the given name is installed on the device, None otherwise.
		:rtype: :py:class:`~marrs.app.App`
		"""
		apps = self.__get_all_apps__()

		for app in apps:
			if app.name == app_name:
				return app

		return None

	def is_app_running(self, app_name):
		"""
		Check if app is running.

		:param app_name: The name of the app
		:type app_name: str
		:return: True if app is running, False otherwise.
		:rtype: bool
		"""
		try:
			self.shell("pidof {0}".format(app_name))
			return True
		except:
			return False

	def is_rooted(self):
		"""
		Check if device is rooted (by trying to run 'su root').

		:return: True if device is rooted, False otherwise.
		:rtype: bool
		"""
		return self.shell('su root \\"echo\\" > /dev/null 2>&1; echo $?') == '0'

	def get_android_version(self):
		"""
		Returns the android version of the device.

		:return: Android version of the device
		:rtype: str
		"""
		return self.shell("getprop ro.build.version.release")

	def get_api_level(self):
		"""
		Returns the API level of the device.

		:return: API level of the device
		:rtype: str
		"""
		return self.shell("getprop ro.build.version.sdk")

	def get_arch(self):
		"""
		Returns the architechture of the device (arm64 / arm / x86_64 / x86)

		:return: The architecture of the device
		:rtype: str
		"""
		res = self.shell("getprop ro.product.cpu.abi").lower()
		archs = ['arm64', 'arm', 'x86_64', 'x86']
		for arch in archs:
			if arch in res:
				return arch

		raise Exception('Failed identify arch : `{0}`'.format(res))

	def is_frida_server_running(self, frida_process_name='frida-server'):
		"""
		Check if frida server is running on the device.

		:param frida_process_name: The name of the frida server process
		:type frida_process_name: str
		:return: True if frida server is running, False otherwise.
		:rtype: bool
		"""
		return frida_process_name in self.shell("ps")

	def kill_frida_server(self):
		"""
		Kills frida server's procces.

		:raises: Exception: If failed to kill the process
		"""

		self.__log__("Killing frida server process")

		if not self.is_frida_server_running():
			self.__warn__("Frida server is not running on device")
			return

		self.shell("pkill frida-server", as_root=True)

		sleep(1)
		self.shell("echo")

		if self.is_frida_server_running():
			raise Exception("Failed to kill frida server")

	def delete_frida_server(self):
		"""
		Deletes all the files which their path mathches the following pattern: '/data/local/tmp/frida-server-\*'
		"""
		self.shell("rm /data/local/tmp/frida-server-* 1> /dev/null 2>&1")

	def __upload_frida_server__(self, version=FRIDA_SERVER_VERSION, arch=None):
		if not arch:
			arch = self.get_arch()

		extra_info = "arch={arch}, version={version}".format(
			arch=arch, version=version)

		self.__log__("Uploading frida server to device", extra_info=extra_info)

		frida_server_filename = FRIDA_SERVER_FILENAME.format(
			version=version, arch=arch)
		self.__dlog__("frida_server_filename = " + frida_server_filename)

		if Storage.contains(frida_server_filename):
			self.__log__(
				"Frida server exists in local storage", extra_info=extra_info)

			frida_server_local_filepath = Storage.get(frida_server_filename)

		else:
			self.__dlog__(
				"Frida server doesn't exist in local storage", extra_info=extra_info)
			self.__log__(
				"Trying to download it from the internet", extra_info=extra_info)

			frida_server_url = FRIDA_SERVER_DOWNLOAD_URL.format(
				version=version, filename=frida_server_filename)
			self.__dlog__("frida_server_url = " + frida_server_url)

			filename = get_filename_from_url(frida_server_url)
			dest_file_path = path.join(Storage.create_temp_dir(), filename)
			frida_server_file_path = download_from_url(frida_server_url, dest_file_path)

			if not frida_server_file_path:
				raise Exception("Failed download frida server from the internet")

			self.__dlog__("frida_server_file_path = " + frida_server_file_path)

			Storage.save(frida_server_file_path)

			frida_server_local_filepath = extract_xz_file(frida_server_file_path)

		self.__dlog__("frida_server_local_filepath = " + frida_server_local_filepath)

		frida_server_remote_path = FRIDA_SERVER_REMOTE_PATH.format(
			version=version, arch=arch)
		self.__dlog__("frida_server_remote_path = " + frida_server_remote_path)
		self.files.push(frida_server_local_filepath, frida_server_remote_path)

	def run_frida_server(self, frida_server_version=FRIDA_SERVER_VERSION):
		"""
		Run frida server of the given version on the device.
		First it will check if the binary is already exists on the device. If so, will run it.
		If it doesn't exist, it will check if the binary exists in the package's store. If so, it will take it from there.
		Otherwise, it will try to download the binary from the internet, upload it and run it on the device.

		:param frida_server_version: the frida server's version to run on the device
		:type frida_server_version: str
		:raise Exception: If the device is not rooted or if failed to run frida server on the device.
		"""
		self.__log__("Running frida server on device")

		if self.is_frida_server_running():
			self.__warn__("	Frida server is already running on device")
			return

		if not self.is_rooted():
			raise Exception("Device must be rooted in order to run frida server")
			return

		arch = self.get_arch()
		extra_info = "arch={arch}, version={version}".format(
			arch=arch, version=frida_server_version)

		frida_server_remote_path = FRIDA_SERVER_REMOTE_PATH.format(
			version=frida_server_version, arch=arch)

		if self.files.exists(frida_server_remote_path):
			self.__log__(
				"	Frida server file is already exists on device",
				extra_info=extra_info)
		else:
			self.__warn__("	Frida server file doesn't exist on device")
			self.__upload_frida_server__(frida_server_version, arch)

		self.shell("chmod +x {0}".format(frida_server_remote_path), as_root=True)
		self.shell(
			"nohup .{0} &".format(frida_server_remote_path),
			wait=False,
			as_root=True)

		sleep(1)

		if not self.is_frida_server_running():
			raise Exception("Failed run frida server on the device")

		self.__success__("	Frida server is now running on device")

	def start_app(self, app_name, main_activity=None):
		"""
		Start application on the device.
		Will do nothing if app is already running.

		:param app_name: The name of the app to start.
		:type app_name: str
		:param main_activity: the main activity of the application to start. If None, it will extract it from the app's apk that exists on the device.
		:type main_activity: str
		:raise Exception: If the device is not rooted or if failed to run frida server on the device.
		"""
		self.__log__("Starting app", extra_info=app_name)

		if self.is_app_running(app_name):
			self.__warn__("	App is already running on device")
			return

		if not main_activity:
			app = self.get_app(app_name)
			main_activity = app.get_main_activity()

		self.__log__("	Main activity is '{0}'".format(main_activity))

		self.shell("am start -n {0}/{1}".format(app_name, main_activity))

		sleep(1)

	def force_stop_app(self, app_name):
		"""
		Force stop application.

		:param app_name: The name of the app to force stop.
		:type app_name: str
		"""
		self.__log__("Force stop app", extra_info=app_name)
		self.shell("am force-stop {0}".format(app_name))

	def clear_app_data(self, app_name):
		"""
		Clear application data.

		:param app_name: The name of the app to clear data for.
		:type app_name: str
		"""
		self.__log__("Clearing app data", extra_info=app_name)

		self.shell("pm clear {0}".format(app_name))
