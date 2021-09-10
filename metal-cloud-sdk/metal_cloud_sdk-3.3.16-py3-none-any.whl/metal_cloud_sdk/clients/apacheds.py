from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class ApacheDS(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(ApacheDS, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the ApacheDS class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object ApacheDS.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if ApacheDS.__instance is None :
			ApacheDS.__instance = ApacheDS(dictParams, arrFilterPlugins)

		return ApacheDS.__instance


	""" 2 functions available on endpoint. """

	def ldap_users(self, strLDAPFilter = None):

		arrParams = [
			strLDAPFilter,
		]

		return self.rpc("ldap_users", arrParams)


	def ldap_user(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("ldap_user", arrParams)


