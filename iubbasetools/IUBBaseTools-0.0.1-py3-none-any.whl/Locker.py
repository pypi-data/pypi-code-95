import os
import psutil


class Locker:
	"""
	Allows only 1 instance of this software per time
	"""
	def __init__(self, name):
		self.myFile = name
		self.processes = self._get_other_processes()
		self.myPid = os.getpid()

	def _get_other_processes(self):
		processes = []
		for proc in psutil.process_iter(['pid', 'name', 'username']):
			if "python" in proc.info['name'] and self.myPid != proc.info['pid']:
				if self.myFile in proc.cmdline()[1]:
					processes.append(proc)
		return processes

	def already_running(self):
		return len(self.processes) > 0

	def get_processes_same_name(self):
		"""
		Return the list of PID of processes with same name
		:return: The list of PID
		"""
		return [proc.info['pid'] for proc in self.processes]
