from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class Kerberos(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(Kerberos, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the Kerberos class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object Kerberos.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if Kerberos.__instance is None :
			Kerberos.__instance = Kerberos(dictParams, arrFilterPlugins)

		return Kerberos.__instance


	""" 7 functions available on endpoint. """

	def krb5_database_create(self):

		arrParams = [
		]

		self.rpc("krb5_database_create", arrParams)


	def krb5_database_destroy(self):

		arrParams = [
		]

		self.rpc("krb5_database_destroy", arrParams)


	def krb5_principal_get(self, strPrincipalName):

		arrParams = [
			strPrincipalName,
		]

		return self.rpc("krb5_principal_get", arrParams)


	def krb5_principal_create(self, objPrincipal):

		objPrincipal = Serializer.serialize(objPrincipal)

		arrParams = [
			objPrincipal,
		]

		self.rpc("krb5_principal_create", arrParams)


	def krb5_principal_update(self, objPrincipal):

		objPrincipal = Serializer.serialize(objPrincipal)

		arrParams = [
			objPrincipal,
		]

		self.rpc("krb5_principal_update", arrParams)


	def krb5_principal_delete(self, strPrincipalName):

		arrParams = [
			strPrincipalName,
		]

		self.rpc("krb5_principal_delete", arrParams)


	def krb5_policy_get(self, strPolicyName):

		arrParams = [
			strPolicyName,
		]

		return self.rpc("krb5_policy_get", arrParams)


