




from .IWalkIOAdapter import IWalkIOAdapter





try:
	import fabric

	class IFabricIOAdapter(IWalkIOAdapter):

		def __init__(self, host:str = None, port:int = None, user:str = None, pwd:str = None, c:fabric.Connection = None):
			if c:
				self.__c = c
			else:
				self.__c = fabric.Connection(host=host, user=user, port=port, connect_kwargs={"password": pwd})
			self.__sftp = self.__c.sftp()
		#

		def listdirCallback(self):
			return self.__sftp.listdir
		#

		def lstatCallback(self):
			return self.__sftp.lstat
		#

	#

except Exception as ee:

	class IFabricIOAdapter(IWalkIOAdapter):

		def __init__(self, **kwargs):
			raise Exception("'fabric' is not installed!")
		#

	#



