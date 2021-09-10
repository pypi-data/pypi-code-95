from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class Docs(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(Docs, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the Docs class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object Docs.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if Docs.__instance is None :
			Docs.__instance = Docs(dictParams, arrFilterPlugins)

		return Docs.__instance


	""" 0 functions available on endpoint. """

