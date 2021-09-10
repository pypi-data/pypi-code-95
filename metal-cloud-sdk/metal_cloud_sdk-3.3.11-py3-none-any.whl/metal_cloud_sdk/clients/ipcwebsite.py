from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class IPCWebsite(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(IPCWebsite, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the IPCWebsite class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object IPCWebsite.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if IPCWebsite.__instance is None :
			IPCWebsite.__instance = IPCWebsite(dictParams, arrFilterPlugins)

		return IPCWebsite.__instance


	""" 2 functions available on endpoint. """

	def prices(self):

		arrParams = [
		]

		return self.rpc("prices", arrParams)


	def server_types(self, strDatacenterName = None, bOnlyAvailable = False):

		arrParams = [
			strDatacenterName,
			bOnlyAvailable,
		]

		objServerType = self.rpc("server_types", arrParams)
		for strKeyServerType in objServerType:
			objServerType[strKeyServerType] = Deserializer.deserialize(objServerType[strKeyServerType])
		return objServerType

