from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class IPCOrdering2(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(IPCOrdering2, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the IPCOrdering2 class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object IPCOrdering2.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if IPCOrdering2.__instance is None :
			IPCOrdering2.__instance = IPCOrdering2(dictParams, arrFilterPlugins)

		return IPCOrdering2.__instance


	""" 18 functions available on endpoint. """

	def resource_utilization_summary(self, strUserIDOwner, strStartTimestamp, strEndTimestamp, arrInfrastructureIDs = None):

		arrParams = [
			strUserIDOwner,
			strStartTimestamp,
			strEndTimestamp,
			arrInfrastructureIDs,
		]

		return self.rpc("resource_utilization_summary", arrParams)


	def resource_utilization_summary_start_timestamp_default(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("resource_utilization_summary_start_timestamp_default", arrParams)


	def user_jwt_check(self, strEncodedCookie, nUserIdBSI):

		arrParams = [
			strEncodedCookie,
			nUserIdBSI,
		]

		return self.rpc("user_jwt_check", arrParams)


	def user_jwt_create_cookie(self, strJWTCookieType, nUserID = None, bIsLoggedIn = False, bJWTRememberLogin = False):

		arrParams = [
			strJWTCookieType,
			nUserID,
			bIsLoggedIn,
			bJWTRememberLogin,
		]

		return self.rpc("user_jwt_create_cookie", arrParams)


	def user_cookie_session(self, bFetchUserLoginSessionData = False):

		arrParams = [
			bFetchUserLoginSessionData,
		]

		return Deserializer.deserialize(self.rpc("user_cookie_session", arrParams))

	def jwt_session_cookies_types_to_cookies_names(self):

		arrParams = [
		]

		return self.rpc("jwt_session_cookies_types_to_cookies_names", arrParams)


	def user_infrastructure_ids_cached(self, nUserID, bRecreateCache = False):

		arrParams = [
			nUserID,
			bRecreateCache,
		]

		return self.rpc("user_infrastructure_ids_cached", arrParams)


	def prices(self):

		arrParams = [
		]

		return self.rpc("prices", arrParams)


	def datacenters(self, strUserID = None, bOnlyActive = False, bIncludeConfigProperties = False):

		arrParams = [
			strUserID,
			bOnlyActive,
			bIncludeConfigProperties,
		]

		objDatacenter = self.rpc("datacenters", arrParams)
		for strKeyDatacenter in objDatacenter:
			objDatacenter[strKeyDatacenter] = Deserializer.deserialize(objDatacenter[strKeyDatacenter])
		return objDatacenter

	def server_type_get(self, strServerTypeID):

		arrParams = [
			strServerTypeID,
		]

		return Deserializer.deserialize(self.rpc("server_type_get", arrParams))

	def server_types(self, strDatacenterName = None, bOnlyAvailable = False):

		arrParams = [
			strDatacenterName,
			bOnlyAvailable,
		]

		objServerType = self.rpc("server_types", arrParams)
		for strKeyServerType in objServerType:
			objServerType[strKeyServerType] = Deserializer.deserialize(objServerType[strKeyServerType])
		return objServerType

	def server_type_matches(self, strInfrastructureID, objHardwareConfiguration, strInstanceArrayID = None, bAllowServerSwap = False):

		objHardwareConfiguration = Serializer.serialize(objHardwareConfiguration)

		arrParams = [
			strInfrastructureID,
			objHardwareConfiguration,
			strInstanceArrayID,
			bAllowServerSwap,
		]

		return self.rpc("server_type_matches", arrParams)


	def server_types_datacenter(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("server_types_datacenter", arrParams)


	def server_types_match_hardware_configuration(self, strDatacenterName, objHardwareConfiguration):

		objHardwareConfiguration = Serializer.serialize(objHardwareConfiguration)

		arrParams = [
			strDatacenterName,
			objHardwareConfiguration,
		]

		objServerType = self.rpc("server_types_match_hardware_configuration", arrParams)
		for strKeyServerType in objServerType:
			objServerType[strKeyServerType] = Deserializer.deserialize(objServerType[strKeyServerType])
		return objServerType

	def volume_template_get(self, strVolumeTemplateID):

		arrParams = [
			strVolumeTemplateID,
		]

		return Deserializer.deserialize(self.rpc("volume_template_get", arrParams))

	def volume_templates_public(self, arrVolumeTemplateIDs = None):

		arrParams = [
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates_public", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def volume_templates_private(self, strUserID, arrVolumeTemplateIDs = None):

		arrParams = [
			strUserID,
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates_private", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def volume_templates(self, strUserID, arrVolumeTemplateIDs = None):

		arrParams = [
			strUserID,
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

