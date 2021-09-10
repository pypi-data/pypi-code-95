from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class HadoopDataLake(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(HadoopDataLake, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the HadoopDataLake class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object HadoopDataLake.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if HadoopDataLake.__instance is None :
			HadoopDataLake.__instance = HadoopDataLake(dictParams, arrFilterPlugins)

		return HadoopDataLake.__instance


	""" 4 functions available on endpoint. """

	def subnet_pools(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("subnet_pools", arrParams)


	def subnet_pool_ranges(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("subnet_pool_ranges", arrParams)


	def data_lakes_traffic_update(self, arrDataLakesTrafficData):

		arrParams = [
			arrDataLakesTrafficData,
		]

		self.rpc("data_lakes_traffic_update", arrParams)


	def mass_storages_traffic_update(self, arrDataLakesTrafficData):

		arrParams = [
			arrDataLakesTrafficData,
		]

		self.rpc("mass_storages_traffic_update", arrParams)


