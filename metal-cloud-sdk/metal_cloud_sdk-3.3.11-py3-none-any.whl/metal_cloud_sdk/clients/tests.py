from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class Tests(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(Tests, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the Tests class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object Tests.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if Tests.__instance is None :
			Tests.__instance = Tests(dictParams, arrFilterPlugins)

		return Tests.__instance


	""" 15 functions available on endpoint. """

	def infrastructure_api_public_infrastructure_create(self):

		arrParams = [
		]

		return self.rpc("infrastructure_api_public_infrastructure_create", arrParams)


	def infrastructure_api_public_infrastructure_deploy(self, nInfrastructureID = None, arrNextFunctionCalls = []):

		arrParams = [
			nInfrastructureID,
			arrNextFunctionCalls,
		]

		return self.rpc("infrastructure_api_public_infrastructure_deploy", arrParams)


	def users_api_public_user_create(self):

		arrParams = [
		]

		return self.rpc("users_api_public_user_create", arrParams)


	def test_functions_descriptors(self):

		arrParams = [
		]

		return self.rpc("test_functions_descriptors", arrParams)


	def test_functions_names(self):

		arrParams = [
		]

		return self.rpc("test_functions_names", arrParams)


	def monitoring_api_public_test_networks_traffic_small(self):

		arrParams = [
		]

		return self.rpc("monitoring_api_public_test_networks_traffic_small", arrParams)


	def monitoring_api_public_test_networks_traffic_medium(self):

		arrParams = [
		]

		return self.rpc("monitoring_api_public_test_networks_traffic_medium", arrParams)


	def monitoring_api_public_test_networks_traffic_large(self):

		arrParams = [
		]

		return self.rpc("monitoring_api_public_test_networks_traffic_large", arrParams)


	def test_wrong_event_type(self):

		arrParams = [
		]

		return self.rpc("test_wrong_event_type", arrParams)


	def test_wrong_timestamp(self):

		arrParams = [
		]

		return self.rpc("test_wrong_timestamp", arrParams)


	def test_without_dblink(self):

		arrParams = [
		]

		return self.rpc("test_without_dblink", arrParams)


	def test_persistent_singleton_with_errors(self):

		arrParams = [
		]

		return self.rpc("test_persistent_singleton_with_errors", arrParams)


	def test_persistent_singleton_without_errors(self):

		arrParams = [
		]

		return self.rpc("test_persistent_singleton_without_errors", arrParams)


	def test_with_dblink_with_transaction(self):

		arrParams = [
		]

		return self.rpc("test_with_dblink_with_transaction", arrParams)


	def test_with_dblink_without_transaction(self):

		arrParams = [
		]

		return self.rpc("test_with_dblink_without_transaction", arrParams)


