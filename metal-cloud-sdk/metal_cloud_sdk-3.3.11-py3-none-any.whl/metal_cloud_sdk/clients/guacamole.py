from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class Guacamole(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(Guacamole, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the Guacamole class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object Guacamole.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if Guacamole.__instance is None :
			Guacamole.__instance = Guacamole(dictParams, arrFilterPlugins)

		return Guacamole.__instance


	""" 9 functions available on endpoint. """

	def remote_console_credentials_get(self, strProductType, nInstanceID, strProtocol, objCookies, strAuthenticatorCode, useBSICredentials):

		objCookies = Serializer.serialize(objCookies)

		arrParams = [
			strProductType,
			nInstanceID,
			strProtocol,
			objCookies,
			strAuthenticatorCode,
			useBSICredentials,
		]

		return Deserializer.deserialize(self.rpc("remote_console_credentials_get", arrParams))

	def remote_console_allowed_domains_get(self):

		arrParams = [
		]

		return self.rpc("remote_console_allowed_domains_get", arrParams)


	def remote_console_user_cookie_authorize(self, objCookies):

		objCookies = Serializer.serialize(objCookies)

		arrParams = [
			objCookies,
		]

		return self.rpc("remote_console_user_cookie_authorize", arrParams)


	def remote_console_jwt_cookie_names_get(self):

		arrParams = [
		]

		return self.rpc("remote_console_jwt_cookie_names_get", arrParams)


	def remote_console_event_log(self, strProductType, nProductID, nUserID):

		arrParams = [
			strProductType,
			nProductID,
			nUserID,
		]

		self.rpc("remote_console_event_log", arrParams)


	def remote_console_instance_connectivity_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		self.rpc("remote_console_instance_connectivity_check", arrParams)


	def remote_console_supported_protocols_get(self):

		arrParams = [
		]

		return self.rpc("remote_console_supported_protocols_get", arrParams)


	def remote_console_container_hostnames(self, nContainerID):

		arrParams = [
			nContainerID,
		]

		return self.rpc("remote_console_container_hostnames", arrParams)


	def remote_console_container_connectivity_check(self, nContainerID):

		arrParams = [
			nContainerID,
		]

		self.rpc("remote_console_container_connectivity_check", arrParams)


