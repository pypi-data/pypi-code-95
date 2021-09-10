import requests


class TorrentHandler:
	"""
	Allows to control the Transmission download and upload speed to avoid bandwidth saturation
	"""
	def __init__(self, apiHandler):
		self.apiHandler = apiHandler

	def slowTorrent(self):
		"""
		Send the request to the server to apply alternative speed (slower)
		:return: The request outcome
		"""
		r = requests.post(self.apiHandler, data={'torrent': 'slow_torrent'})
		return r

	def fastTorrent(self):
		"""
		Send the request to the server to restore original Transmission speed
		:return: The request outcome
		"""
		r = requests.post(self.apiHandler, data={'torrent': 'fast_torrent'})
		return r
