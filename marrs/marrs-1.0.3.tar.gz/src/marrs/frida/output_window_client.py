import json
import platform
import random
import sys
from os import system

import requests

from .consts import FRIDA_SERVER_KILL_COMMAND
from .output_window_server import get_output_server_file_path
from ..log import debug


class OutputWindowClient:

	def __init__(self, device_id, app_name):
		self.port = random.randint(30000, 60000)
		self.device_id = device_id
		self.app_name = app_name
		self.started = False

	def start(self):
		file_path = get_output_server_file_path()

		plat = platform.system()
		if plat == 'Windows':
			cmd = 'start cmd /c "\"{0}\" \"{1}\" {2} {3} {4}"'.format(
				sys.executable, file_path, self.device_id, self.app_name, self.port)
		else:
			raise Exception("'{0}' platform is not supported yet".format(plat))

		debug(cmd)
		res = system(cmd)

		self.started = True

	def kill(self):
		if self.started:
			self.print(FRIDA_SERVER_KILL_COMMAND)

	def print(self, s):
		if not self.started:
			return

		requests.post(
			'http://localhost:{0}'.format(self.port), data=json.dumps({'msg': s}))
