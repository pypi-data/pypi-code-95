




from .IWalkIOAdapter import IWalkIOAdapter





try:
	import paramiko.sftp_client

	class IParamicoIOAdapter(IWalkIOAdapter):

		def __init__(self, sftp:paramiko.sftp_client.SFTPClient):
			assert sftp
			self.__sftp = sftp
		#

		def listdirCallback(self):
			return self.__sftp.listdir
		#

		def lstatCallback(self):
			return self.__sftp.lstat
		#

	#

except Exception as ee:

	class IParamicoIOAdapter(IWalkIOAdapter):

		def __init__(self, **kwargs):
			raise Exception("'paramiko' is not installed!")
		#

	#



