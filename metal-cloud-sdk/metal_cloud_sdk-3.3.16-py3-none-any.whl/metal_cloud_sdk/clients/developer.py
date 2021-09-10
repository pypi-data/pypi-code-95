from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class Developer(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(Developer, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the Developer class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object Developer.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if Developer.__instance is None :
			Developer.__instance = Developer(dictParams, arrFilterPlugins)

		return Developer.__instance


	""" 1008 functions available on endpoint. """

	def cluster_gui_settings_save(self, strClusterID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strClusterID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("cluster_gui_settings_save", arrParams)


	def event_counters(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("event_counters", arrParams)


	def infrastructure_get(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_get", arrParams))

	def infrastructure_hang_until_touched(self, nInfrastructureID, strKnownValue):

		arrParams = [
			nInfrastructureID,
			strKnownValue,
		]

		return self.rpc("infrastructure_hang_until_touched", arrParams)


	def instance_interface_ips(self, nInstanceInterfaceID):

		arrParams = [
			nInstanceInterfaceID,
		]

		return self.rpc("instance_interface_ips", arrParams)


	def instance_get(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return Deserializer.deserialize(self.rpc("instance_get", arrParams))

	def instance_array_get(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_get", arrParams))

	def instance_array_gui_settings_save(self, strInstanceArrayID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strInstanceArrayID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("instance_array_gui_settings_save", arrParams)


	def subnet_get(self, strSubnetID):

		arrParams = [
			strSubnetID,
		]

		return Deserializer.deserialize(self.rpc("subnet_get", arrParams))

	def data_lake_gui_settings_save(self, strDataLakeID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strDataLakeID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("data_lake_gui_settings_save", arrParams)


	def monitoring_instance_measurement_value_get(self, nInstanceMeasurementID):

		arrParams = [
			nInstanceMeasurementID,
		]

		return self.rpc("monitoring_instance_measurement_value_get", arrParams)


	def monitoring_instance_measurements_get_for_instance(self, strInstanceID, bIgnoreVirtualEthernetInterfaces = False):

		arrParams = [
			strInstanceID,
			bIgnoreVirtualEthernetInterfaces,
		]

		return self.rpc("monitoring_instance_measurements_get_for_instance", arrParams)


	def monitoring_instance_measurements_rendering_get(self, strInstanceID, arrMeasurements, objRenderingOptions = [], bEncodeBase64 = True):

		objRenderingOptions = Serializer.serialize(objRenderingOptions)

		arrParams = [
			strInstanceID,
			arrMeasurements,
			objRenderingOptions,
			bEncodeBase64,
		]

		return self.rpc("monitoring_instance_measurements_rendering_get", arrParams)


	def monitoring_instance_interface_measurements_rendering_get(self, nInstanceInterfaceID, arrMeasurements, objRenderingOptions = [], bEncodeBase64 = True):

		objRenderingOptions = Serializer.serialize(objRenderingOptions)

		arrParams = [
			nInstanceInterfaceID,
			arrMeasurements,
			objRenderingOptions,
			bEncodeBase64,
		]

		return self.rpc("monitoring_instance_interface_measurements_rendering_get", arrParams)


	def monitoring_network_measurements_rendering_get(self, strNetworkID, strNetworkTrafficType, arrMeasurements, objRenderingOptions = [], bEncodeBase64 = True):

		objRenderingOptions = Serializer.serialize(objRenderingOptions)

		arrParams = [
			strNetworkID,
			strNetworkTrafficType,
			arrMeasurements,
			objRenderingOptions,
			bEncodeBase64,
		]

		return self.rpc("monitoring_network_measurements_rendering_get", arrParams)


	def network_get(self, strNetworkID):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_get", arrParams))

	def network_gui_settings_save(self, strNetworkID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strNetworkID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("network_gui_settings_save", arrParams)


	def server_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return Deserializer.deserialize(self.rpc("server_get", arrParams))

	def server_type_get(self, strServerTypeID):

		arrParams = [
			strServerTypeID,
		]

		return Deserializer.deserialize(self.rpc("server_type_get", arrParams))

	def server_type_available_server_count(self, strUserIDOwner, strDatacenterName, strServerTypeID, nMaximumResults):

		arrParams = [
			strUserIDOwner,
			strDatacenterName,
			strServerTypeID,
			nMaximumResults,
		]

		return self.rpc("server_type_available_server_count", arrParams)


	def shared_drive_get(self, strSharedDriveID):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_get", arrParams))

	def shared_drive_gui_settings_save(self, strSharedDriveID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strSharedDriveID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("shared_drive_gui_settings_save", arrParams)


	def drive_get(self, strDriveID):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_get", arrParams))

	def drive_array_get(self, strDriveArrayID):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_get", arrParams))

	def drive_array_gui_settings_save(self, strDriveArrayID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strDriveArrayID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("drive_array_gui_settings_save", arrParams)


	def volume_template_get(self, strVolumeTemplateID):

		arrParams = [
			strVolumeTemplateID,
		]

		return Deserializer.deserialize(self.rpc("volume_template_get", arrParams))

	def user_change_password_encrypted(self, strUserID, strAESCipherPassword, strRSACipherAESKey, strOldPassword = None):

		arrParams = [
			strUserID,
			strAESCipherPassword,
			strRSACipherAESKey,
			strOldPassword,
		]

		self.rpc("user_change_password_encrypted", arrParams)


	def user_authenticate_password_encrypted(self, strLoginEmail, strAESCipherPassword, strRSACipherAESKey, strOneTimePassword = None, bRememberLogin = True, bTestCredentials = False, bRenewKerberosTicket = False):

		arrParams = [
			strLoginEmail,
			strAESCipherPassword,
			strRSACipherAESKey,
			strOneTimePassword,
			bRememberLogin,
			bTestCredentials,
			bRenewKerberosTicket,
		]

		return self.rpc("user_authenticate_password_encrypted", arrParams)


	def transport_request_public_key(self, bGenerateNewIfNotFound = True):

		arrParams = [
			bGenerateNewIfNotFound,
		]

		return self.rpc("transport_request_public_key", arrParams)


	def user_email_to_user_id(self, strLoginEmail):

		arrParams = [
			strLoginEmail,
		]

		return self.rpc("user_email_to_user_id", arrParams)


	def cluster_create(self, strInfrastructureID, objCluster):

		objCluster = Serializer.serialize(objCluster)

		arrParams = [
			strInfrastructureID,
			objCluster,
		]

		return Deserializer.deserialize(self.rpc("cluster_create", arrParams))

	def cluster_get(self, strClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 10):

		arrParams = [
			strClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("cluster_get", arrParams))

	def cluster_edit(self, strClusterID, objClusterOperation):

		objClusterOperation = Serializer.serialize(objClusterOperation)

		arrParams = [
			strClusterID,
			objClusterOperation,
		]

		return Deserializer.deserialize(self.rpc("cluster_edit", arrParams))

	def cluster_stop(self, strClusterID):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_stop", arrParams))

	def cluster_start(self, strClusterID):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_start", arrParams))

	def cluster_delete(self, strClusterID):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_delete", arrParams))

	def clusters(self, strInfrastructureID, arrClusterIDs = None, bAccessSaaSAPI = False, nAccessSaaSAPITimeoutSeconds = 10):

		arrParams = [
			strInfrastructureID,
			arrClusterIDs,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		objCluster = self.rpc("clusters", arrParams)
		for strKeyCluster in objCluster:
			objCluster[strKeyCluster] = Deserializer.deserialize(objCluster[strKeyCluster])
		return objCluster

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

	def events_delete(self, strInfrastructureID, arrEventIDs):

		arrParams = [
			strInfrastructureID,
			arrEventIDs,
		]

		self.rpc("events_delete", arrParams)


	def infrastructure_create(self, strUserID, objInfrastructure, strInfrastructureIDAsTemplate = None):

		objInfrastructure = Serializer.serialize(objInfrastructure)

		arrParams = [
			strUserID,
			objInfrastructure,
			strInfrastructureIDAsTemplate,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_create", arrParams))

	def infrastructure_deploy(self, strInfrastructureID, objShutdownOptions = None, objDeployOptions = None, bAllowDataLoss = False, bSkipAnsible = False):

		objShutdownOptions = Serializer.serialize(objShutdownOptions)
		objDeployOptions = Serializer.serialize(objDeployOptions)

		arrParams = [
			strInfrastructureID,
			objShutdownOptions,
			objDeployOptions,
			bAllowDataLoss,
			bSkipAnsible,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy", arrParams))

	def infrastructure_operation_cancel(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		self.rpc("infrastructure_operation_cancel", arrParams)


	def infrastructure_user_add(self, strInfrastructureID, strUserEmail, objInfrastructurePermissions = None, bCreateUserIfNotExists = False):

		objInfrastructurePermissions = Serializer.serialize(objInfrastructurePermissions)

		arrParams = [
			strInfrastructureID,
			strUserEmail,
			objInfrastructurePermissions,
			bCreateUserIfNotExists,
		]

		self.rpc("infrastructure_user_add", arrParams)


	def infrastructure_user_remove(self, strInfrastructureID, strUserID):

		arrParams = [
			strInfrastructureID,
			strUserID,
		]

		return self.rpc("infrastructure_user_remove", arrParams)


	def infrastructure_user_update(self, strInfrastructureID, strUserEmail, objInfrastructurePermissions):

		objInfrastructurePermissions = Serializer.serialize(objInfrastructurePermissions)

		arrParams = [
			strInfrastructureID,
			strUserEmail,
			objInfrastructurePermissions,
		]

		self.rpc("infrastructure_user_update", arrParams)


	def infrastructure_user_ssh_keys(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("infrastructure_user_ssh_keys", arrParams)


	def infrastructure_users(self, strInfrastructureID, arrUserIDs = None):

		arrParams = [
			strInfrastructureID,
			arrUserIDs,
		]

		objUser = self.rpc("infrastructure_users", arrParams)
		for strKeyUser in objUser:
			objUser[strKeyUser] = Deserializer.deserialize(objUser[strKeyUser])
		return objUser

	def infrastructure_edit(self, strInfrastructureID, objInfrastructureOperation):

		objInfrastructureOperation = Serializer.serialize(objInfrastructureOperation)

		arrParams = [
			strInfrastructureID,
			objInfrastructureOperation,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_edit", arrParams))

	def infrastructure_deploy_options(self, strInfrastructureID, bReplaceServerTypes = False):

		arrParams = [
			strInfrastructureID,
			bReplaceServerTypes,
		]

		return self.rpc("infrastructure_deploy_options", arrParams)


	def infrastructure_deploy_overview(self, strInfrastructureID, objDeployOptions = None):

		objDeployOptions = Serializer.serialize(objDeployOptions)

		arrParams = [
			strInfrastructureID,
			objDeployOptions,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy_overview", arrParams))

	def infrastructure_delete(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_delete", arrParams))

	def infrastructure_user_limits(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_user_limits", arrParams))

	def infrastructure_gui_settings_save(self, strInfrastructureID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strInfrastructureID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("infrastructure_gui_settings_save", arrParams)


	def instance_edit(self, strInstanceID, objInstanceOperation):

		objInstanceOperation = Serializer.serialize(objInstanceOperation)

		arrParams = [
			strInstanceID,
			objInstanceOperation,
		]

		return Deserializer.deserialize(self.rpc("instance_edit", arrParams))

	def instance_delete(self, strInstanceID, bKeepDetachingDrives):

		arrParams = [
			strInstanceID,
			bKeepDetachingDrives,
		]

		return Deserializer.deserialize(self.rpc("instance_delete", arrParams))

	def instance_array_instances(self, strInstanceArrayID, arrInstanceIDs = None):

		arrParams = [
			strInstanceArrayID,
			arrInstanceIDs,
		]

		objInstance = self.rpc("instance_array_instances", arrParams)
		for strKeyInstance in objInstance:
			objInstance[strKeyInstance] = Deserializer.deserialize(objInstance[strKeyInstance])
		return objInstance

	def instance_server_power_get(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_server_power_get", arrParams)


	def instance_server_power_set(self, strInstanceID, strPowerCommand):

		arrParams = [
			strInstanceID,
			strPowerCommand,
		]

		self.rpc("instance_server_power_set", arrParams)


	def instance_array_create(self, strInfrastructureID, objInstanceArray):

		objInstanceArray = Serializer.serialize(objInstanceArray)

		arrParams = [
			strInfrastructureID,
			objInstanceArray,
		]

		return Deserializer.deserialize(self.rpc("instance_array_create", arrParams))

	def instance_array_edit(self, strInstanceArrayID, objInstanceArrayOperation, bSwapExistingInstancesHardware = False, bKeepDetachingDrives = None, objServerTypeMatches = None, arrInstanceIDsPreferredForDelete = None):

		objInstanceArrayOperation = Serializer.serialize(objInstanceArrayOperation)
		objServerTypeMatches = Serializer.serialize(objServerTypeMatches)

		arrParams = [
			strInstanceArrayID,
			objInstanceArrayOperation,
			bSwapExistingInstancesHardware,
			bKeepDetachingDrives,
			objServerTypeMatches,
			arrInstanceIDsPreferredForDelete,
		]

		return Deserializer.deserialize(self.rpc("instance_array_edit", arrParams))

	def instance_array_delete(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_delete", arrParams))

	def instance_array_stop(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_stop", arrParams))

	def instance_array_start(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_start", arrParams))

	def instance_arrays(self, strInfrastructureID, arrInstanceArrayIDs = None):

		arrParams = [
			strInfrastructureID,
			arrInstanceArrayIDs,
		]

		objInstanceArray = self.rpc("instance_arrays", arrParams)
		for strKeyInstanceArray in objInstanceArray:
			objInstanceArray[strKeyInstanceArray] = Deserializer.deserialize(objInstanceArray[strKeyInstanceArray])
		return objInstanceArray

	def instance_array_interface_attach_network(self, strInstanceArrayID, nInstanceArrayInterfaceIndex, strNetworkID):

		arrParams = [
			strInstanceArrayID,
			nInstanceArrayInterfaceIndex,
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_interface_attach_network", arrParams))

	def instance_array_interface_detach(self, strInstanceArrayID, nInstanceArrayInterfaceIndex):

		arrParams = [
			strInstanceArrayID,
			nInstanceArrayInterfaceIndex,
		]

		return Deserializer.deserialize(self.rpc("instance_array_interface_detach", arrParams))

	def subnet_create(self, strNetworkID, objSubnet):

		objSubnet = Serializer.serialize(objSubnet)

		arrParams = [
			strNetworkID,
			objSubnet,
		]

		return Deserializer.deserialize(self.rpc("subnet_create", arrParams))

	def subnet_delete(self, strSubnetID):

		arrParams = [
			strSubnetID,
		]

		return Deserializer.deserialize(self.rpc("subnet_delete", arrParams))

	def subnets(self, strNetworkID, arrSubnetIDs = None):

		arrParams = [
			strNetworkID,
			arrSubnetIDs,
		]

		objSubnet = self.rpc("subnets", arrParams)
		for strKeySubnet in objSubnet:
			objSubnet[strKeySubnet] = Deserializer.deserialize(objSubnet[strKeySubnet])
		return objSubnet

	def data_lake_create(self, strInfrastructureID, objDataLake):

		objDataLake = Serializer.serialize(objDataLake)

		arrParams = [
			strInfrastructureID,
			objDataLake,
		]

		return Deserializer.deserialize(self.rpc("data_lake_create", arrParams))

	def data_lake_get(self, strDataLakeID):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_get", arrParams))

	def data_lake_edit(self, strDataLakeID, objDataLakeOperation):

		objDataLakeOperation = Serializer.serialize(objDataLakeOperation)

		arrParams = [
			strDataLakeID,
			objDataLakeOperation,
		]

		return self.rpc("data_lake_edit", arrParams)


	def data_lake_stop(self, strDataLakeID):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_stop", arrParams))

	def data_lake_start(self, strDataLakeID):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_start", arrParams))

	def data_lake_delete(self, strDataLakeID):

		arrParams = [
			strDataLakeID,
		]

		return Deserializer.deserialize(self.rpc("data_lake_delete", arrParams))

	def data_lakes(self, strInfrastructureID, arrDataLakeIDs = None):

		arrParams = [
			strInfrastructureID,
			arrDataLakeIDs,
		]

		objDataLake = self.rpc("data_lakes", arrParams)
		for strKeyDataLake in objDataLake:
			objDataLake[strKeyDataLake] = Deserializer.deserialize(objDataLake[strKeyDataLake])
		return objDataLake

	def data_lake_krb_conf_download_url(self):

		arrParams = [
		]

		return self.rpc("data_lake_krb_conf_download_url", arrParams)


	def network_create(self, strInfrastructureID, objNetwork):

		objNetwork = Serializer.serialize(objNetwork)

		arrParams = [
			strInfrastructureID,
			objNetwork,
		]

		return Deserializer.deserialize(self.rpc("network_create", arrParams))

	def network_edit(self, strNetworkID, objNetworkOperation):

		objNetworkOperation = Serializer.serialize(objNetworkOperation)

		arrParams = [
			strNetworkID,
			objNetworkOperation,
		]

		return Deserializer.deserialize(self.rpc("network_edit", arrParams))

	def network_delete(self, strNetworkID):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_delete", arrParams))

	def network_stop(self, strNetworkID):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_stop", arrParams))

	def network_start(self, strNetworkID):

		arrParams = [
			strNetworkID,
		]

		return Deserializer.deserialize(self.rpc("network_start", arrParams))

	def networks(self, strInfrastructureID, arrNetworkIDs = None):

		arrParams = [
			strInfrastructureID,
			arrNetworkIDs,
		]

		objNetwork = self.rpc("networks", arrParams)
		for strKeyNetwork in objNetwork:
			objNetwork[strKeyNetwork] = Deserializer.deserialize(objNetwork[strKeyNetwork])
		return objNetwork

	def network_join(self, strNetworkID, strNetworkToBeDeletedID):

		arrParams = [
			strNetworkID,
			strNetworkToBeDeletedID,
		]

		return Deserializer.deserialize(self.rpc("network_join", arrParams))

	def resource_utilization_summary(self, strUserIDOwner, strStartTimestamp, strEndTimestamp, arrInfrastructureIDs = None):

		arrParams = [
			strUserIDOwner,
			strStartTimestamp,
			strEndTimestamp,
			arrInfrastructureIDs,
		]

		return self.rpc("resource_utilization_summary", arrParams)


	def resource_utilization_detailed(self, strUserIDOwner, strStartTimestamp, strEndTimestamp, arrInfrastructureIDs = None):

		arrParams = [
			strUserIDOwner,
			strStartTimestamp,
			strEndTimestamp,
			arrInfrastructureIDs,
		]

		return self.rpc("resource_utilization_detailed", arrParams)


	def servers(self, strInfrastructureID, arrServerIDs = None):

		arrParams = [
			strInfrastructureID,
			arrServerIDs,
		]

		arrServers = self.rpc("servers", arrParams)
		for index in range(len(arrServers)):
			arrServers[index] = Deserializer.deserialize(arrServers[index])
		return arrServers

	def server_type_reservation_create(self, strUserID, objReservation, nQuantity = 1):

		objReservation = Serializer.serialize(objReservation)

		arrParams = [
			strUserID,
			objReservation,
			nQuantity,
		]

		arrServerTypeReservations = self.rpc("server_type_reservation_create", arrParams)
		for index in range(len(arrServerTypeReservations)):
			arrServerTypeReservations[index] = Deserializer.deserialize(arrServerTypeReservations[index])
		return arrServerTypeReservations

	def server_type_reservation_get(self, nServerTypeReservationID):

		arrParams = [
			nServerTypeReservationID,
		]

		return Deserializer.deserialize(self.rpc("server_type_reservation_get", arrParams))

	def server_type_reservation_edit(self, nServerTypeReservationID, objServerTypeReservation):

		objServerTypeReservation = Serializer.serialize(objServerTypeReservation)

		arrParams = [
			nServerTypeReservationID,
			objServerTypeReservation,
		]

		return Deserializer.deserialize(self.rpc("server_type_reservation_edit", arrParams))

	def user_server_type_reservations(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_server_type_reservations", arrParams)


	def instance_server_power_set_batch(self, strInfrastructureID, arrInstanceIDs, strPowerCommand):

		arrParams = [
			strInfrastructureID,
			arrInstanceIDs,
			strPowerCommand,
		]

		self.rpc("instance_server_power_set_batch", arrParams)


	def instance_server_power_get_batch(self, strInfrastructureID, arrInstanceIDs):

		arrParams = [
			strInfrastructureID,
			arrInstanceIDs,
		]

		return self.rpc("instance_server_power_get_batch", arrParams)


	def infrastructure_deploy_shutdown_required(self, strInfrastructureID, strPowerCommand = "none", bOnlyPoweredOn = True):

		arrParams = [
			strInfrastructureID,
			strPowerCommand,
			bOnlyPoweredOn,
		]

		return self.rpc("infrastructure_deploy_shutdown_required", arrParams)


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


	def shared_drive_create(self, strInfrastructureID, objSharedDrive):

		objSharedDrive = Serializer.serialize(objSharedDrive)

		arrParams = [
			strInfrastructureID,
			objSharedDrive,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_create", arrParams))

	def shared_drive_edit(self, strSharedDriveID, objSharedDriveOperation):

		objSharedDriveOperation = Serializer.serialize(objSharedDriveOperation)

		arrParams = [
			strSharedDriveID,
			objSharedDriveOperation,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_edit", arrParams))

	def shared_drive_delete(self, strSharedDriveID):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_delete", arrParams))

	def shared_drive_stop(self, strSharedDriveID):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_stop", arrParams))

	def shared_drive_start(self, strSharedDriveID):

		arrParams = [
			strSharedDriveID,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_start", arrParams))

	def shared_drive_instance_arrays(self, strSharedDriveID):

		arrParams = [
			strSharedDriveID,
		]

		return self.rpc("shared_drive_instance_arrays", arrParams)


	def instance_array_shared_drives(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return self.rpc("instance_array_shared_drives", arrParams)


	def shared_drives(self, strInfrastructureID, arrSharedDriveIDs = None):

		arrParams = [
			strInfrastructureID,
			arrSharedDriveIDs,
		]

		objSharedDrive = self.rpc("shared_drives", arrParams)
		for strKeySharedDrive in objSharedDrive:
			objSharedDrive[strKeySharedDrive] = Deserializer.deserialize(objSharedDrive[strKeySharedDrive])
		return objSharedDrive

	def search(self, strUserID, strKeywords, arrTables = None, objTablesColumns = None, strCollapseType = "array_subrows", arrOrderBy = [], arrLimit = None):

		objTablesColumns = Serializer.serialize(objTablesColumns)

		arrParams = [
			strUserID,
			strKeywords,
			arrTables,
			objTablesColumns,
			strCollapseType,
			arrOrderBy,
			arrLimit,
		]

		return self.rpc("search", arrParams)


	def query(self, strUserID, strSQLQuery, strCollapseType = "array_subrows"):

		arrParams = [
			strUserID,
			strSQLQuery,
			strCollapseType,
		]

		return self.rpc("query", arrParams)


	def drive_edit(self, strDriveID, objDriveOperation):

		objDriveOperation = Serializer.serialize(objDriveOperation)

		arrParams = [
			strDriveID,
			objDriveOperation,
		]

		return Deserializer.deserialize(self.rpc("drive_edit", arrParams))

	def drive_delete(self, strDriveID):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_delete", arrParams))

	def drive_attach_instance(self, strDriveID, strInstanceID):

		arrParams = [
			strDriveID,
			strInstanceID,
		]

		return Deserializer.deserialize(self.rpc("drive_attach_instance", arrParams))

	def drive_detach_instance(self, strDriveID):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_detach_instance", arrParams))

	def instance_drives(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		objDrive = self.rpc("instance_drives", arrParams)
		for strKeyDrive in objDrive:
			objDrive[strKeyDrive] = Deserializer.deserialize(objDrive[strKeyDrive])
		return objDrive

	def drive_snapshot_create(self, strDriveID):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_snapshot_create", arrParams))

	def drive_snapshot_rollback(self, strSnapshotID):

		arrParams = [
			strSnapshotID,
		]

		self.rpc("drive_snapshot_rollback", arrParams)


	def drive_snapshot_delete(self, strSnapshotID):

		arrParams = [
			strSnapshotID,
		]

		self.rpc("drive_snapshot_delete", arrParams)


	def drive_snapshots(self, strDriveID, arrSnapshotIDs = None):

		arrParams = [
			strDriveID,
			arrSnapshotIDs,
		]

		objSnapshot = self.rpc("drive_snapshots", arrParams)
		for strKeySnapshot in objSnapshot:
			objSnapshot[strKeySnapshot] = Deserializer.deserialize(objSnapshot[strKeySnapshot])
		return objSnapshot

	def volume_templates(self, strUserID, arrVolumeTemplateIDs = None):

		arrParams = [
			strUserID,
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def volume_templates_public(self, arrVolumeTemplateIDs = None):

		arrParams = [
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates_public", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def drive_array_create(self, strInfrastructureID, objDriveArray):

		objDriveArray = Serializer.serialize(objDriveArray)

		arrParams = [
			strInfrastructureID,
			objDriveArray,
		]

		return Deserializer.deserialize(self.rpc("drive_array_create", arrParams))

	def drive_array_edit(self, strDriveArrayID, objDriveArrayOperation, objDriveArrayEditOptions = {"update_active_drives_size":False}):

		objDriveArrayOperation = Serializer.serialize(objDriveArrayOperation)
		objDriveArrayEditOptions = Serializer.serialize(objDriveArrayEditOptions)

		arrParams = [
			strDriveArrayID,
			objDriveArrayOperation,
			objDriveArrayEditOptions,
		]

		return Deserializer.deserialize(self.rpc("drive_array_edit", arrParams))

	def drive_array_delete(self, strDriveArrayID):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_delete", arrParams))

	def drive_array_stop(self, strDriveArrayID):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_stop", arrParams))

	def drive_array_start(self, strDriveArrayID):

		arrParams = [
			strDriveArrayID,
		]

		return Deserializer.deserialize(self.rpc("drive_array_start", arrParams))

	def drive_array_drives(self, strDriveArrayID, arrDriveIDs = None):

		arrParams = [
			strDriveArrayID,
			arrDriveIDs,
		]

		objDrive = self.rpc("drive_array_drives", arrParams)
		for strKeyDrive in objDrive:
			objDrive[strKeyDrive] = Deserializer.deserialize(objDrive[strKeyDrive])
		return objDrive

	def drive_arrays(self, strInfrastructureID, arrDriveArrayIDs = None):

		arrParams = [
			strInfrastructureID,
			arrDriveArrayIDs,
		]

		objDriveArray = self.rpc("drive_arrays", arrParams)
		for strKeyDriveArray in objDriveArray:
			objDriveArray[strKeyDriveArray] = Deserializer.deserialize(objDriveArray[strKeyDriveArray])
		return objDriveArray

	def user_create(self, strDisplayName, strLoginEmail, strRedirectURL = None, strAESKey = None):

		arrParams = [
			strDisplayName,
			strLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		return Deserializer.deserialize(self.rpc("user_create", arrParams))

	def user_get(self, strUserID):

		arrParams = [
			strUserID,
		]

		return Deserializer.deserialize(self.rpc("user_get", arrParams))

	def infrastructures(self, strUserID, arrInfrastructureIDs = None):

		arrParams = [
			strUserID,
			arrInfrastructureIDs,
		]

		objInfrastructure = self.rpc("infrastructures", arrParams)
		for strKeyInfrastructure in objInfrastructure:
			objInfrastructure[strKeyInfrastructure] = Deserializer.deserialize(objInfrastructure[strKeyInfrastructure])
		return objInfrastructure

	def user_authenticate_password(self, strLoginEmail, strPassword, strOneTimePassword = None, bRememberLogin = True, bTestCredentials = False, bRenewKerberosTicket = False):

		arrParams = [
			strLoginEmail,
			strPassword,
			strOneTimePassword,
			bRememberLogin,
			bTestCredentials,
			bRenewKerberosTicket,
		]

		return self.rpc("user_authenticate_password", arrParams)


	def user_authenticate_api_key(self, strUserID, strAPIKey, strOneTimePassword = None, bRememberLogin = True):

		arrParams = [
			strUserID,
			strAPIKey,
			strOneTimePassword,
			bRememberLogin,
		]

		return Deserializer.deserialize(self.rpc("user_authenticate_api_key", arrParams))

	def user_change_password(self, strUserID, strNewPassword, strOldPassword = None):

		arrParams = [
			strUserID,
			strNewPassword,
			strOldPassword,
		]

		self.rpc("user_change_password", arrParams)


	def user_infrastructure_default_set(self, strUserID, strInfrastructureID):

		arrParams = [
			strUserID,
			strInfrastructureID,
		]

		return self.rpc("user_infrastructure_default_set", arrParams)


	def user_infrastructure_default_unset(self, strUserID):

		arrParams = [
			strUserID,
		]

		self.rpc("user_infrastructure_default_unset", arrParams)


	def user_ssh_key_create(self, strUserID, strSSHKey):

		arrParams = [
			strUserID,
			strSSHKey,
		]

		return Deserializer.deserialize(self.rpc("user_ssh_key_create", arrParams))

	def user_ssh_keys(self, strUserID):

		arrParams = [
			strUserID,
		]

		arrSSHKeys = self.rpc("user_ssh_keys", arrParams)
		for index in range(len(arrSSHKeys)):
			arrSSHKeys[index] = Deserializer.deserialize(arrSSHKeys[index])
		return arrSSHKeys

	def user_ssh_key_delete(self, nSSHKeyID):

		arrParams = [
			nSSHKeyID,
		]

		self.rpc("user_ssh_key_delete", arrParams)


	def user_api_key_regenerate(self, strUserID):

		arrParams = [
			strUserID,
		]

		self.rpc("user_api_key_regenerate", arrParams)


	def user_password_recovery(self, strLoginEmail, strRedirectURL = None, strAESKey = None):

		arrParams = [
			strLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		self.rpc("user_password_recovery", arrParams)


	def user_create_retry_mail(self, strLoginEmail, strRedirectURL = None, strAESKey = None):

		arrParams = [
			strLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		self.rpc("user_create_retry_mail", arrParams)


	def user_update_email(self, strUserID, strNewLoginEmail, strRedirectURL = None, strAESKey = None):

		arrParams = [
			strUserID,
			strNewLoginEmail,
			strRedirectURL,
			strAESKey,
		]

		return self.rpc("user_update_email", arrParams)


	def user_update_language(self, strUserID, strLanguage):

		arrParams = [
			strUserID,
			strLanguage,
		]

		return Deserializer.deserialize(self.rpc("user_update_language", arrParams))

	def user_delegate_add(self, strUserID, strDelegateUserEmail, bCreateUserIfNotExists = False):

		arrParams = [
			strUserID,
			strDelegateUserEmail,
			bCreateUserIfNotExists,
		]

		self.rpc("user_delegate_add", arrParams)


	def user_delegate_remove(self, strUserID, strDelegateUserEmail):

		arrParams = [
			strUserID,
			strDelegateUserEmail,
		]

		self.rpc("user_delegate_remove", arrParams)


	def user_delegate_children(self, strUserID):

		arrParams = [
			strUserID,
		]

		objUser = self.rpc("user_delegate_children", arrParams)
		for strKeyUser in objUser:
			objUser[strKeyUser] = Deserializer.deserialize(objUser[strKeyUser])
		return objUser

	def user_delegate_parents(self, strUserID):

		arrParams = [
			strUserID,
		]

		objUser = self.rpc("user_delegate_parents", arrParams)
		for strKeyUser in objUser:
			objUser[strKeyUser] = Deserializer.deserialize(objUser[strKeyUser])
		return objUser

	def user_cookie_session(self, bFetchUserLoginSessionData = False):

		arrParams = [
			bFetchUserLoginSessionData,
		]

		return Deserializer.deserialize(self.rpc("user_cookie_session", arrParams))

	def user_logout(self):

		arrParams = [
		]

		return self.rpc("user_logout", arrParams)


	def user_gui_settings_save(self, strUserID, objGUIUserSettings, arrPropertyNames):

		objGUIUserSettings = Serializer.serialize(objGUIUserSettings)

		arrParams = [
			strUserID,
			objGUIUserSettings,
			arrPropertyNames,
		]

		self.rpc("user_gui_settings_save", arrParams)


	def throw_error(self, nErrorCode):

		arrParams = [
			nErrorCode,
		]

		self.rpc("throw_error", arrParams)


	def afc_get(self, nAFCID):

		arrParams = [
			nAFCID,
		]

		return self.rpc("afc_get", arrParams)


	def afc_make_call(self, nAFCID, bIgnoreMaxRetry = False):

		arrParams = [
			nAFCID,
			bIgnoreMaxRetry,
		]

		return self.rpc("afc_make_call", arrParams)


	def afc_retry_call(self, nAFCID, bIgnoreMaxRetry = False, pdo = None):

		pdo = Serializer.serialize(pdo)

		arrParams = [
			nAFCID,
			bIgnoreMaxRetry,
			pdo,
		]

		return self.rpc("afc_retry_call", arrParams)


	def afc_delete(self, nAFCID):

		arrParams = [
			nAFCID,
		]

		self.rpc("afc_delete", arrParams)


	def afc_counters(self, objAFCCountersFilter = None):

		objAFCCountersFilter = Serializer.serialize(objAFCCountersFilter)

		arrParams = [
			objAFCCountersFilter,
		]

		return self.rpc("afc_counters", arrParams)


	def afc_silence(self, nAFCID):

		arrParams = [
			nAFCID,
		]

		self.rpc("afc_silence", arrParams)


	def afc_max_retries_increase(self, arrAFCIDs):

		arrParams = [
			arrAFCIDs,
		]

		return self.rpc("afc_max_retries_increase", arrParams)


	def afc_delete_non_asynchronous_calls(self, arrAFCIDs):

		arrParams = [
			arrAFCIDs,
		]

		self.rpc("afc_delete_non_asynchronous_calls", arrParams)


	def afc_silence_non_asynchronous_calls(self, arrAFCIDs):

		arrParams = [
			arrAFCIDs,
		]

		self.rpc("afc_silence_non_asynchronous_calls", arrParams)


	def hdfs_cluster_get(self, strDatacenter = None):

		arrParams = [
			strDatacenter,
		]

		return self.rpc("hdfs_cluster_get", arrParams)


	def database_sanitize_query(self):

		arrParams = [
		]

		return self.rpc("database_sanitize_query", arrParams)


	def datacenter_base_urls(self):

		arrParams = [
		]

		return self.rpc("datacenter_base_urls", arrParams)


	def dhcp_lease_get(self, strMACAddress, nServerID = None):

		arrParams = [
			strMACAddress,
			nServerID,
		]

		return self.rpc("dhcp_lease_get", arrParams)


	def dhcp_lease_create(self, strMACAddress, strSwitchHostname = None, nExpiryMinutes = 60, strDatacenterName = None, nServerID = None):

		arrParams = [
			strMACAddress,
			strSwitchHostname,
			nExpiryMinutes,
			strDatacenterName,
			nServerID,
		]

		return self.rpc("dhcp_lease_create", arrParams)


	def dns_deploy(self, nInfrastructureID = None):

		arrParams = [
			nInfrastructureID,
		]

		self.rpc("dns_deploy", arrParams)


	def dns_subdomains_regenerate(self):

		arrParams = [
		]

		self.rpc("dns_subdomains_regenerate", arrParams)


	def dns_subdomains_regenerate_records(self, nInfrastructureID = None, bRebuilding = True):

		arrParams = [
			nInfrastructureID,
			bRebuilding,
		]

		self.rpc("dns_subdomains_regenerate_records", arrParams)


	def dns_iana_ipv4_ranges_generate_reverse(self):

		arrParams = [
		]

		self.rpc("dns_iana_ipv4_ranges_generate_reverse", arrParams)


	def dns_ptr_records_clear(self):

		arrParams = [
		]

		self.rpc("dns_ptr_records_clear", arrParams)


	def dns_infrastructure_provision_callback(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		self.rpc("dns_infrastructure_provision_callback", arrParams)


	def dns_infrastructure_provision_callback_all_infrastructures(self, bOnlyActiveOrOngoing):

		arrParams = [
			bOnlyActiveOrOngoing,
		]

		self.rpc("dns_infrastructure_provision_callback_all_infrastructures", arrParams)


	def event_counters_developer(self):

		arrParams = [
		]

		return self.rpc("event_counters_developer", arrParams)


	def event_delete(self, nEventID):

		arrParams = [
			nEventID,
		]

		self.rpc("event_delete", arrParams)


	def afc_error_codes_not_documented(self):

		arrParams = [
		]

		return self.rpc("afc_error_codes_not_documented", arrParams)


	def afc_error_codes_never_fired(self):

		arrParams = [
		]

		return self.rpc("afc_error_codes_never_fired", arrParams)


	def afc_error_codes_code_comments(self):

		arrParams = [
		]

		return self.rpc("afc_error_codes_code_comments", arrParams)


	def exceptions_sort_by_type(self, bShowAuthors = False):

		arrParams = [
			bShowAuthors,
		]

		return self.rpc("exceptions_sort_by_type", arrParams)


	def events_get_code(self, bShowAuthors = False):

		arrParams = [
			bShowAuthors,
		]

		return self.rpc("events_get_code", arrParams)


	def infrastructure_servers(self, nInfrastructureID, bChanges, bMainTable):

		arrParams = [
			nInfrastructureID,
			bChanges,
			bMainTable,
		]

		return self.rpc("infrastructure_servers", arrParams)


	def infrastructure_instances_info(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_instances_info", arrParams)


	def infrastructure_owner_change(self, nInfrastructureID, nNewOwnerID, bSkipSubnetPoolsChange = False):

		arrParams = [
			nInfrastructureID,
			nNewOwnerID,
			bSkipSubnetPoolsChange,
		]

		self.rpc("infrastructure_owner_change", arrParams)


	def instance_info(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_info", arrParams)


	def instance_server_replace(self, nInstanceID, nNewServerID, strFaultyServerStatus = "defective"):

		arrParams = [
			nInstanceID,
			nNewServerID,
			strFaultyServerStatus,
		]

		return self.rpc("instance_server_replace", arrParams)


	def instance_interface_get(self, nInstanceInterfaceID):

		arrParams = [
			nInstanceInterfaceID,
		]

		return Deserializer.deserialize(self.rpc("instance_interface_get", arrParams))

	def instance_array_interface_get(self, nInstanceArrayInterfaceID):

		arrParams = [
			nInstanceArrayInterfaceID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_interface_get", arrParams))

	def ip_allocate_oob(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("ip_allocate_oob", arrParams)


	def subnet_oob_get(self, nSubnetID):

		arrParams = [
			nSubnetID,
		]

		return Deserializer.deserialize(self.rpc("subnet_oob_get", arrParams))

	def subnet_oob_create(self, objSubnet):

		objSubnet = Serializer.serialize(objSubnet)

		arrParams = [
			objSubnet,
		]

		return Deserializer.deserialize(self.rpc("subnet_oob_create", arrParams))

	def subnet_pool_get(self, nSubnetPoolID):

		arrParams = [
			nSubnetPoolID,
		]

		return self.rpc("subnet_pool_get", arrParams)


	def subnet_pool_create(self, objSubnetPool):

		objSubnetPool = Serializer.serialize(objSubnetPool)

		arrParams = [
			objSubnetPool,
		]

		return self.rpc("subnet_pool_create", arrParams)


	def cache_destroy(self):

		arrParams = [
		]

		self.rpc("cache_destroy", arrParams)


	def network_traffic_sflow_parse(self):

		arrParams = [
		]

		self.rpc("network_traffic_sflow_parse", arrParams)


	def test_development_network_traffic_sflow_generate(self):

		arrParams = [
		]

		self.rpc("test_development_network_traffic_sflow_generate", arrParams)


	def network_traffic_summary_get(self, nInfrastructureID, strStartTimestamp, strEndTimestamp):

		arrParams = [
			nInfrastructureID,
			strStartTimestamp,
			strEndTimestamp,
		]

		return self.rpc("network_traffic_summary_get", arrParams)


	def provisioner_volume_import(self, nUploadID):

		arrParams = [
			nUploadID,
		]

		self.rpc("provisioner_volume_import", arrParams)


	def provisioner_cleanup(self):

		arrParams = [
		]

		self.rpc("provisioner_cleanup", arrParams)


	def volume_upload_target_url(self, strInfrastructureID, arrFileInfo):

		arrParams = [
			strInfrastructureID,
			arrFileInfo,
		]

		return self.rpc("volume_upload_target_url", arrParams)


	def volume_upload_max_size(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("volume_upload_max_size", arrParams)


	def resource_utilization_price_changes_apply(self, nUserID = None):

		arrParams = [
			nUserID,
		]

		self.rpc("resource_utilization_price_changes_apply", arrParams)


	def resource_reservation_renew_recurring(self):

		arrParams = [
		]

		self.rpc("resource_reservation_renew_recurring", arrParams)


	def resource_reservation_cancel(self, strProductName, nResourceReservationID, strCancelTimestamp = None):

		arrParams = [
			strProductName,
			nResourceReservationID,
			strCancelTimestamp,
		]

		self.rpc("resource_reservation_cancel", arrParams)


	def resource_reservation_delete(self, strProductName, nResourceReservationID):

		arrParams = [
			strProductName,
			nResourceReservationID,
		]

		self.rpc("resource_reservation_delete", arrParams)


	def server_type_prices(self, strDatacenter, strFranchise, nUserID = None):

		arrParams = [
			strDatacenter,
			strFranchise,
			nUserID,
		]

		return self.rpc("server_type_prices", arrParams)


	def user_server_type_reservations_optimize(self, nUserID, strDatacenterName, bInstanceChanges = False):

		arrParams = [
			nUserID,
			strDatacenterName,
			bInstanceChanges,
		]

		self.rpc("user_server_type_reservations_optimize", arrParams)


	def server_class_update(self, nServerID, strServerClass):

		arrParams = [
			nServerID,
			strServerClass,
		]

		return self.rpc("server_class_update", arrParams)


	def servers_instances_counters(self, arrDatacentersFilter = []):

		arrParams = [
			arrDatacentersFilter,
		]

		return self.rpc("servers_instances_counters", arrParams)


	def server_with_uuid_get(self, strUUID):

		arrParams = [
			strUUID,
		]

		return self.rpc("server_with_uuid_get", arrParams)


	def server_identify(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("server_identify", arrParams)


	def server_power_set(self, nServerID, strPowerCommand):

		arrParams = [
			nServerID,
			strPowerCommand,
		]

		self.rpc("server_power_set", arrParams)


	def server_power_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_power_get", arrParams)


	def server_power_set_batch(self, arrServerIDs, strPowerCommand):

		arrParams = [
			arrServerIDs,
			strPowerCommand,
		]

		self.rpc("server_power_set_batch", arrParams)


	def server_power_get_batch(self, arrServerIDs):

		arrParams = [
			arrServerIDs,
		]

		return self.rpc("server_power_get_batch", arrParams)


	def server_reregister(self, nServerID, bSkipIPMI = False, bUseBDKAgent = False):

		arrParams = [
			nServerID,
			bSkipIPMI,
			bUseBDKAgent,
		]

		self.rpc("server_reregister", arrParams)


	def server_status_update(self, nServerID, strServerStatus):

		arrParams = [
			nServerID,
			strServerStatus,
		]

		return self.rpc("server_status_update", arrParams)


	def server_bdk_debug_toggle(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_bdk_debug_toggle", arrParams)


	def servers_get_by_status(self, strServerStatus):

		arrParams = [
			strServerStatus,
		]

		return self.rpc("servers_get_by_status", arrParams)


	def server_get_internal(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_get_internal", arrParams)


	def server_type_matches_internal(self, strInfrastructureID, objHardwareConfiguration, nInstanceArrayID = None, arrMustKeepServerIDs = [], arrAlreadyAllocatedServerIDs = [], arrServerClasses = ["bigdata"]):

		objHardwareConfiguration = Serializer.serialize(objHardwareConfiguration)

		arrParams = [
			strInfrastructureID,
			objHardwareConfiguration,
			nInstanceArrayID,
			arrMustKeepServerIDs,
			arrAlreadyAllocatedServerIDs,
			arrServerClasses,
		]

		return self.rpc("server_type_matches_internal", arrParams)


	def servers_type_utilization_report(self, strGroupByColumnName, strDatacenterName, bTestingMode = None, bDeveloper = None):

		arrParams = [
			strGroupByColumnName,
			strDatacenterName,
			bTestingMode,
			bDeveloper,
		]

		return self.rpc("servers_type_utilization_report", arrParams)


	def server_match_hardware_configuration(self, nUserID, strDatacenterName, objHardwareTarget, arrMustKeepServerIDs = [], arrAlreadyAllocatedServerIDs = [], arrIgnoreServerIDs = [], nMaximumResults = 1):

		objHardwareTarget = Serializer.serialize(objHardwareTarget)

		arrParams = [
			nUserID,
			strDatacenterName,
			objHardwareTarget,
			arrMustKeepServerIDs,
			arrAlreadyAllocatedServerIDs,
			arrIgnoreServerIDs,
			nMaximumResults,
		]

		return self.rpc("server_match_hardware_configuration", arrParams)


	def server_edit(self, nServerID, objServer, strServerEditType = "complete"):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			nServerID,
			objServer,
			strServerEditType,
		]

		return self.rpc("server_edit", arrParams)


	def server_type_create(self, objServerTypeParams):

		objServerTypeParams = Serializer.serialize(objServerTypeParams)

		arrParams = [
			objServerTypeParams,
		]

		return Deserializer.deserialize(self.rpc("server_type_create", arrParams))

	def server_type_clean_unused(self):

		arrParams = [
		]

		self.rpc("server_type_clean_unused", arrParams)


	def server_bios_info_refresh(self, strServerID):

		arrParams = [
			strServerID,
		]

		return self.rpc("server_bios_info_refresh", arrParams)


	def server_type_reservation_owner_change(self, nServerTypeReservationID, nUserIDOwner, strToday = None):

		arrParams = [
			nServerTypeReservationID,
			nUserIDOwner,
			strToday,
		]

		return self.rpc("server_type_reservation_owner_change", arrParams)


	def server_type_reservation_create_internal(self, strUserID, objReservation, nQuantity = 1, nServerID = None):

		objReservation = Serializer.serialize(objReservation)

		arrParams = [
			strUserID,
			objReservation,
			nQuantity,
			nServerID,
		]

		arrServerTypeReservations = self.rpc("server_type_reservation_create_internal", arrParams)
		for index in range(len(arrServerTypeReservations)):
			arrServerTypeReservations[index] = Deserializer.deserialize(arrServerTypeReservations[index])
		return arrServerTypeReservations

	def server_type_reservation_cancel(self, nServerTypeReservationID, strCancelTimestamp):

		arrParams = [
			nServerTypeReservationID,
			strCancelTimestamp,
		]

		self.rpc("server_type_reservation_cancel", arrParams)


	def server_type_reservation_delete(self, nServerTypeReservationID):

		arrParams = [
			nServerTypeReservationID,
		]

		self.rpc("server_type_reservation_delete", arrParams)


	def server_type_reservation_delete_all(self):

		arrParams = [
		]

		self.rpc("server_type_reservation_delete_all", arrParams)


	def user_server_type_reservations_internal(self, nUserID, strUserPlanType = None):

		arrParams = [
			nUserID,
			strUserPlanType,
		]

		return self.rpc("user_server_type_reservations_internal", arrParams)


	def server_vendor_firmware_version_update(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_vendor_firmware_version_update", arrParams)


	def server_vendor_firmware_version_update_all(self):

		arrParams = [
		]

		self.rpc("server_vendor_firmware_version_update_all", arrParams)


	def drive_move_to_storage(self, nDriveID, nDstStoragePoolID, bAllowDatacenterChange = False, bAllowStorageTypeChange = True):

		arrParams = [
			nDriveID,
			nDstStoragePoolID,
			bAllowDatacenterChange,
			bAllowStorageTypeChange,
		]

		return self.rpc("drive_move_to_storage", arrParams)


	def storage_pool_create(self, objStoragePool):

		objStoragePool = Serializer.serialize(objStoragePool)

		arrParams = [
			objStoragePool,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_create", arrParams))

	def storage_pool_get(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_get", arrParams))

	def storage_pool_delete(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		self.rpc("storage_pool_delete", arrParams)


	def storage_pool_virtual_size_occupied_mb(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		return self.rpc("storage_pool_virtual_size_occupied_mb", arrParams)


	def storage_pool_physical_size_occupied_mb(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		return self.rpc("storage_pool_physical_size_occupied_mb", arrParams)


	def storage_pool_physical_size_mb(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		return self.rpc("storage_pool_physical_size_mb", arrParams)


	def volume_template_create(self, strDriveID, strNewVolumeTemplateLabel, strDescription, strVolumeTemplateDisplayName, strVolumeTemplateBootType, strVolumeTemplateDeprecationStatus, strVolumeTemplateBootMethodsSupported, arrVolumeTemplateTags, strVolumeTemplateOsBootstrapFunctionName, strVolumeTemplateVersion):

		arrParams = [
			strDriveID,
			strNewVolumeTemplateLabel,
			strDescription,
			strVolumeTemplateDisplayName,
			strVolumeTemplateBootType,
			strVolumeTemplateDeprecationStatus,
			strVolumeTemplateBootMethodsSupported,
			arrVolumeTemplateTags,
			strVolumeTemplateOsBootstrapFunctionName,
			strVolumeTemplateVersion,
		]

		return Deserializer.deserialize(self.rpc("volume_template_create", arrParams))

	def volume_template_make_public(self, strVolumeTemplateID, strBootstrapFunctionName):

		arrParams = [
			strVolumeTemplateID,
			strBootstrapFunctionName,
		]

		self.rpc("volume_template_make_public", arrParams)


	def volume_template_replicate(self, nVolumeTemplateID, nSrcStoragePoolID, nDstStoragePoolID):

		arrParams = [
			nVolumeTemplateID,
			nSrcStoragePoolID,
			nDstStoragePoolID,
		]

		return self.rpc("volume_template_replicate", arrParams)


	def volume_template_replicate_all(self, strVolumeTemplateID):

		arrParams = [
			strVolumeTemplateID,
		]

		return self.rpc("volume_template_replicate_all", arrParams)


	def volume_template_delete(self, nVolumeTemplateID):

		arrParams = [
			nVolumeTemplateID,
		]

		self.rpc("volume_template_delete", arrParams)


	def volume_template_storage_pool_get(self, nVolumeTemplateStoragePoolID):

		arrParams = [
			nVolumeTemplateStoragePoolID,
		]

		return self.rpc("volume_template_storage_pool_get", arrParams)


	def volume_template_storage_pool_delete(self, nVolumeTemplateStoragePoolID):

		arrParams = [
			nVolumeTemplateStoragePoolID,
		]

		self.rpc("volume_template_storage_pool_delete", arrParams)


	def volume_template_storage_pools_for_volume_template(self, nVolumeTemplateID):

		arrParams = [
			nVolumeTemplateID,
		]

		return self.rpc("volume_template_storage_pools_for_volume_template", arrParams)


	def volume_template_drives(self, nVolumeTemplateID):

		arrParams = [
			nVolumeTemplateID,
		]

		return self.rpc("volume_template_drives", arrParams)


	def volume_templates_created_from_drive(self, strDriveID):

		arrParams = [
			strDriveID,
		]

		return self.rpc("volume_templates_created_from_drive", arrParams)


	def drive_snapshot_get(self, strSnapshotID):

		arrParams = [
			strSnapshotID,
		]

		return Deserializer.deserialize(self.rpc("drive_snapshot_get", arrParams))

	def storage_pool_iqn_cleanup(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		self.rpc("storage_pool_iqn_cleanup", arrParams)


	def storage_usage_report(self, bPerStorage, bPhysicalSize):

		arrParams = [
			bPerStorage,
			bPhysicalSize,
		]

		return self.rpc("storage_usage_report", arrParams)


	def storage_types(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("storage_types", arrParams)


	def switch_device_network_allocate_primary_subnet(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("switch_device_network_allocate_primary_subnet", arrParams)


	def switch_device_get(self, mxNetworkEquipmentID):

		mxNetworkEquipmentID = Serializer.serialize(mxNetworkEquipmentID)

		arrParams = [
			mxNetworkEquipmentID,
		]

		return self.rpc("switch_device_get", arrParams)


	def switch_device_info(self, mxNetworkEquipmentID):

		mxNetworkEquipmentID = Serializer.serialize(mxNetworkEquipmentID)

		arrParams = [
			mxNetworkEquipmentID,
		]

		return self.rpc("switch_device_info", arrParams)


	def switch_device_delete(self, nNetworkEquipmentID):

		arrParams = [
			nNetworkEquipmentID,
		]

		self.rpc("switch_device_delete", arrParams)


	def switch_device_create(self, objNetworkEquipmentData, bOverwriteWithHostnameFromFetchedSwitch = True):

		objNetworkEquipmentData = Serializer.serialize(objNetworkEquipmentData)

		arrParams = [
			objNetworkEquipmentData,
			bOverwriteWithHostnameFromFetchedSwitch,
		]

		return self.rpc("switch_device_create", arrParams)


	def switch_device_create_auto(self, objNetworkEquipmentData, bAutoDescribe = True):

		objNetworkEquipmentData = Serializer.serialize(objNetworkEquipmentData)

		arrParams = [
			objNetworkEquipmentData,
			bAutoDescribe,
		]

		return self.rpc("switch_device_create_auto", arrParams)


	def switch_device_vpls_get(self, nNetworkID, nNetworkEquipmentID):

		arrParams = [
			nNetworkID,
			nNetworkEquipmentID,
		]

		return self.rpc("switch_device_vpls_get", arrParams)


	def switch_device_simulator_initialize(self, strDatacenterName, nSwitchDeviceID = None):

		arrParams = [
			strDatacenterName,
			nSwitchDeviceID,
		]

		self.rpc("switch_device_simulator_initialize", arrParams)


	def switch_devices(self, strDatacenter = None, strSwitchDeviceType = None):

		arrParams = [
			strDatacenter,
			strSwitchDeviceType,
		]

		return self.rpc("switch_devices", arrParams)


	def switch_device_reprovision_server(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("switch_device_reprovision_server", arrParams)


	def switch_device_reprovision_infrastructure(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("switch_device_reprovision_infrastructure", arrParams)


	def switch_device_reprovision_quarantine(self, nSwitchDeviceID):

		arrParams = [
			nSwitchDeviceID,
		]

		return self.rpc("switch_device_reprovision_quarantine", arrParams)


	def switch_device_reprovision_instance(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("switch_device_reprovision_instance", arrParams)


	def switch_device_reprovision_interfaces(self, arrSwitchInterfaceIDs):

		arrParams = [
			arrSwitchInterfaceIDs,
		]

		return self.rpc("switch_device_reprovision_interfaces", arrParams)


	def switch_device_reprovision(self, nSwitchDeviceID, bIgnoreDirtyBit = True, bForceIPCleanup = False):

		arrParams = [
			nSwitchDeviceID,
			bIgnoreDirtyBit,
			bForceIPCleanup,
		]

		return self.rpc("switch_device_reprovision", arrParams)


	def switch_device_interface_counters(self, objSwitchDeviceInterfaceCountersFilter = None):

		objSwitchDeviceInterfaceCountersFilter = Serializer.serialize(objSwitchDeviceInterfaceCountersFilter)

		arrParams = [
			objSwitchDeviceInterfaceCountersFilter,
		]

		return self.rpc("switch_device_interface_counters", arrParams)


	def switch_device_interface_get(self, mxSwitchDeviceInterface, nSwitchDeviceID = None):

		mxSwitchDeviceInterface = Serializer.serialize(mxSwitchDeviceInterface)

		arrParams = [
			mxSwitchDeviceInterface,
			nSwitchDeviceID,
		]

		return self.rpc("switch_device_interface_get", arrParams)


	def user_sync_push_all_users_to_billing2(self):

		arrParams = [
		]

		self.rpc("user_sync_push_all_users_to_billing2", arrParams)


	def user_password_change_required_set(self, strUserID, bPasswordChangeRequired):

		arrParams = [
			strUserID,
			bPasswordChangeRequired,
		]

		return self.rpc("user_password_change_required_set", arrParams)


	def user_blocked_update(self, nUserID, bBlocked):

		arrParams = [
			nUserID,
			bBlocked,
		]

		return self.rpc("user_blocked_update", arrParams)


	def user_billable_set(self, nUserID, bBillable):

		arrParams = [
			nUserID,
			bBillable,
		]

		return self.rpc("user_billable_set", arrParams)


	def storage_pools(self, strDatacenterName = None, arrStoragePoolTypes = [], bIncludeStoragePoolsInMaintenance = False, bAllowExperimental = False, nUserID = None):

		arrParams = [
			strDatacenterName,
			arrStoragePoolTypes,
			bIncludeStoragePoolsInMaintenance,
			bAllowExperimental,
			nUserID,
		]

		return self.rpc("storage_pools", arrParams)


	def switch_device_interfaces_dirty_bit_set(self, arrSwitchDeviceInterfaceIDs, nInfrastructureID = 0):

		arrParams = [
			arrSwitchDeviceInterfaceIDs,
			nInfrastructureID,
		]

		self.rpc("switch_device_interfaces_dirty_bit_set", arrParams)


	def user_delete(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_delete", arrParams)


	def sync_tables_in_guest_mode(self):

		arrParams = [
		]

		self.rpc("sync_tables_in_guest_mode", arrParams)


	def server_type_reservation_reactivate(self, nServerTypeReservationID):

		arrParams = [
			nServerTypeReservationID,
		]

		self.rpc("server_type_reservation_reactivate", arrParams)


	def user_jwt_salt_regenerate(self, nUserID):

		arrParams = [
			nUserID,
		]

		return self.rpc("user_jwt_salt_regenerate", arrParams)


	def infrastructure_deploy_blockers(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		arrInfrastructureDeployBlockers = self.rpc("infrastructure_deploy_blockers", arrParams)
		for index in range(len(arrInfrastructureDeployBlockers)):
			arrInfrastructureDeployBlockers[index] = Deserializer.deserialize(arrInfrastructureDeployBlockers[index])
		return arrInfrastructureDeployBlockers

	def cluster_suspend(self, strClusterID):

		arrParams = [
			strClusterID,
		]

		return Deserializer.deserialize(self.rpc("cluster_suspend", arrParams))

	def user_suspend_reason_add(self, nUserID, strSuspendReasonType, strSuspendReasonPublicComment, strSuspendReasonPrivateComment = ""):

		arrParams = [
			nUserID,
			strSuspendReasonType,
			strSuspendReasonPublicComment,
			strSuspendReasonPrivateComment,
		]

		return Deserializer.deserialize(self.rpc("user_suspend_reason_add", arrParams))

	def user_suspend_reason_remove(self, nUserID, strSuspendReasonType):

		arrParams = [
			nUserID,
			strSuspendReasonType,
		]

		self.rpc("user_suspend_reason_remove", arrParams)


	def user_suspend_reason_get(self, nUserSuspendReasonID):

		arrParams = [
			nUserSuspendReasonID,
		]

		return Deserializer.deserialize(self.rpc("user_suspend_reason_get", arrParams))

	def user_suspend_reasons(self, nUserID):

		arrParams = [
			nUserID,
		]

		arrUserSuspendReasons = self.rpc("user_suspend_reasons", arrParams)
		for index in range(len(arrUserSuspendReasons)):
			arrUserSuspendReasons[index] = Deserializer.deserialize(arrUserSuspendReasons[index])
		return arrUserSuspendReasons

	def shared_drive_move_to_storage(self, nSharedDriveID, nDstStoragePoolID, bAllowDatacenterChange = False, bAllowStorageTypeChange = True):

		arrParams = [
			nSharedDriveID,
			nDstStoragePoolID,
			bAllowDatacenterChange,
			bAllowStorageTypeChange,
		]

		return Deserializer.deserialize(self.rpc("shared_drive_move_to_storage", arrParams))

	def server_disk_wipe_toggle(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_disk_wipe_toggle", arrParams)


	def storage_pool_maintenance_set(self, nStoragePoolID, bInMaintenance):

		arrParams = [
			nStoragePoolID,
			bInMaintenance,
		]

		self.rpc("storage_pool_maintenance_set", arrParams)


	def volume_template_public_create_from_storage(self, strVolumeTemplateStorageImageName, nStoragePoolID, strVolumeTemplateLabel, strVolumeTemplateDisplayName, strDescription, strBootstrapFunctionName, objOperatingSystem, strVolumeTemplateBootType = "legacy_only", strVolumeTemplateDeprecationStatus = "not_deprecated", strVolumeTemplateVersion = "0.0.0"):

		objOperatingSystem = Serializer.serialize(objOperatingSystem)

		arrParams = [
			strVolumeTemplateStorageImageName,
			nStoragePoolID,
			strVolumeTemplateLabel,
			strVolumeTemplateDisplayName,
			strDescription,
			strBootstrapFunctionName,
			objOperatingSystem,
			strVolumeTemplateBootType,
			strVolumeTemplateDeprecationStatus,
			strVolumeTemplateVersion,
		]

		return self.rpc("volume_template_public_create_from_storage", arrParams)


	def volume_templates_private(self, strUserID, arrVolumeTemplateIDs = None):

		arrParams = [
			strUserID,
			arrVolumeTemplateIDs,
		]

		objVolumeTemplate = self.rpc("volume_templates_private", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def server_disks(self, nServerID):

		arrParams = [
			nServerID,
		]

		arrServerDisks = self.rpc("server_disks", arrParams)
		for index in range(len(arrServerDisks)):
			arrServerDisks[index] = Deserializer.deserialize(arrServerDisks[index])
		return arrServerDisks

	def container_array_gui_settings_save(self, strContainerArrayID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strContainerArrayID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("container_array_gui_settings_save", arrParams)


	def container_platform_gui_settings_save(self, strContainerPlatformID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strContainerPlatformID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("container_platform_gui_settings_save", arrParams)


	def container_array_interface_get(self, nContainerArrayInterfaceID):

		arrParams = [
			nContainerArrayInterfaceID,
		]

		return Deserializer.deserialize(self.rpc("container_array_interface_get", arrParams))

	def container_array_create(self, strInfrastructureID, objContainerArray):

		objContainerArray = Serializer.serialize(objContainerArray)

		arrParams = [
			strInfrastructureID,
			objContainerArray,
		]

		return Deserializer.deserialize(self.rpc("container_array_create", arrParams))

	def container_array_get(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_get", arrParams))

	def container_array_edit(self, strContainerArrayID, objContainerArrayOperation, bKeepDetachingDrives = None):

		objContainerArrayOperation = Serializer.serialize(objContainerArrayOperation)

		arrParams = [
			strContainerArrayID,
			objContainerArrayOperation,
			bKeepDetachingDrives,
		]

		return Deserializer.deserialize(self.rpc("container_array_edit", arrParams))

	def container_array_delete(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_delete", arrParams))

	def container_array_stop(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_stop", arrParams))

	def container_array_start(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_start", arrParams))

	def container_arrays(self, strInfrastructureID, arrContainerArrayIDs = None):

		arrParams = [
			strInfrastructureID,
			arrContainerArrayIDs,
		]

		objContainerArray = self.rpc("container_arrays", arrParams)
		for strKeyContainerArray in objContainerArray:
			objContainerArray[strKeyContainerArray] = Deserializer.deserialize(objContainerArray[strKeyContainerArray])
		return objContainerArray

	def container_platform_create(self, strInfrastructureID, objContainerPlatform):

		objContainerPlatform = Serializer.serialize(objContainerPlatform)

		arrParams = [
			strInfrastructureID,
			objContainerPlatform,
		]

		return Deserializer.deserialize(self.rpc("container_platform_create", arrParams))

	def container_platform_get(self, strContainerPlatformID):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_get", arrParams))

	def container_platform_edit(self, strContainerPlatformID, objContainerPlatformOperation, objServerTypeMatches = None):

		objContainerPlatformOperation = Serializer.serialize(objContainerPlatformOperation)
		objServerTypeMatches = Serializer.serialize(objServerTypeMatches)

		arrParams = [
			strContainerPlatformID,
			objContainerPlatformOperation,
			objServerTypeMatches,
		]

		return Deserializer.deserialize(self.rpc("container_platform_edit", arrParams))

	def container_platform_stop(self, strContainerPlatformID):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_stop", arrParams))

	def container_platform_start(self, strContainerPlatformID):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_start", arrParams))

	def container_platform_delete(self, strContainerPlatformID):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_delete", arrParams))

	def container_platforms(self, strInfrastructureID, arrContainerPlatformIDs = None):

		arrParams = [
			strInfrastructureID,
			arrContainerPlatformIDs,
		]

		objContainerPlatform = self.rpc("container_platforms", arrParams)
		for strKeyContainerPlatform in objContainerPlatform:
			objContainerPlatform[strKeyContainerPlatform] = Deserializer.deserialize(objContainerPlatform[strKeyContainerPlatform])
		return objContainerPlatform

	def container_platform_suspend(self, strContainerPlatformID):

		arrParams = [
			strContainerPlatformID,
		]

		return Deserializer.deserialize(self.rpc("container_platform_suspend", arrParams))

	def subnet_oob_delete(self, nSubnetID):

		arrParams = [
			nSubnetID,
		]

		self.rpc("subnet_oob_delete", arrParams)


	def switch_device_test(self, nSwitchDeviceID):

		arrParams = [
			nSwitchDeviceID,
		]

		return self.rpc("switch_device_test", arrParams)


	def container_platform_container_arrays(self, strContainerPlatformID, arrContainerArrayIDs = None):

		arrParams = [
			strContainerPlatformID,
			arrContainerArrayIDs,
		]

		objContainerArray = self.rpc("container_platform_container_arrays", arrParams)
		for strKeyContainerArray in objContainerArray:
			objContainerArray[strKeyContainerArray] = Deserializer.deserialize(objContainerArray[strKeyContainerArray])
		return objContainerArray

	def container_array_containers(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		objContainer = self.rpc("container_array_containers", arrParams)
		for strKeyContainer in objContainer:
			objContainer[strKeyContainer] = Deserializer.deserialize(objContainer[strKeyContainer])
		return objContainer

	def cluster_password_change(self, strClusterID, strNewPassword):

		arrParams = [
			strClusterID,
			strNewPassword,
		]

		self.rpc("cluster_password_change", arrParams)


	def drive_hook_toggle(self, nDriveID):

		arrParams = [
			nDriveID,
		]

		return self.rpc("drive_hook_toggle", arrParams)


	def cluster_public_key_get(self, strClusterID):

		arrParams = [
			strClusterID,
		]

		return self.rpc("cluster_public_key_get", arrParams)


	def server_requires_manual_cleaning_toggle(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_requires_manual_cleaning_toggle", arrParams)


	def infrastructure_experimental_priority_set(self, nInfrastructureID, strExperimentalPriority):

		arrParams = [
			nInfrastructureID,
			strExperimentalPriority,
		]

		self.rpc("infrastructure_experimental_priority_set", arrParams)


	def infrastructure_experimental_priority_get(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_experimental_priority_get", arrParams)


	def switch_device_interfaces_enable_set(self, arrSwitchInterfaceIDsToLinkState):

		arrParams = [
			arrSwitchInterfaceIDsToLinkState,
		]

		self.rpc("switch_device_interfaces_enable_set", arrParams)


	def instance_public_key_get(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_public_key_get", arrParams)


	def client_ip(self):

		arrParams = [
		]

		return self.rpc("client_ip", arrParams)


	def clusters_software_version_get(self, arrClusterTypes = []):

		arrParams = [
			arrClusterTypes,
		]

		return self.rpc("clusters_software_version_get", arrParams)


	def license_create(self, nLicenseContractID, objLicense):

		objLicense = Serializer.serialize(objLicense)

		arrParams = [
			nLicenseContractID,
			objLicense,
		]

		return Deserializer.deserialize(self.rpc("license_create", arrParams))

	def license_get(self, nLicenseID, bSelectForUpdate = False):

		arrParams = [
			nLicenseID,
			bSelectForUpdate,
		]

		return Deserializer.deserialize(self.rpc("license_get", arrParams))

	def license_edit(self, nLicenseID, objLicense):

		objLicense = Serializer.serialize(objLicense)

		arrParams = [
			nLicenseID,
			objLicense,
		]

		return Deserializer.deserialize(self.rpc("license_edit", arrParams))

	def licenses(self, nLicenseContractID, bIncludeStopped = False):

		arrParams = [
			nLicenseContractID,
			bIncludeStopped,
		]

		return self.rpc("licenses", arrParams)


	def license_installment_create(self, strLicenseType, objLicenseInstallment):

		objLicenseInstallment = Serializer.serialize(objLicenseInstallment)

		arrParams = [
			strLicenseType,
			objLicenseInstallment,
		]

		return Deserializer.deserialize(self.rpc("license_installment_create", arrParams))

	def license_installments_create(self, nLicenseID):

		arrParams = [
			nLicenseID,
		]

		self.rpc("license_installments_create", arrParams)


	def license_installment_get(self, nLicenseInstallmentID, bSelectForUpdate = False):

		arrParams = [
			nLicenseInstallmentID,
			bSelectForUpdate,
		]

		return Deserializer.deserialize(self.rpc("license_installment_get", arrParams))

	def license_installment_edit(self, nLicenseInstallmentID, objLicenseInstallment):

		objLicenseInstallment = Serializer.serialize(objLicenseInstallment)

		arrParams = [
			nLicenseInstallmentID,
			objLicenseInstallment,
		]

		return Deserializer.deserialize(self.rpc("license_installment_edit", arrParams))

	def license_installments(self, nLicenseID):

		arrParams = [
			nLicenseID,
		]

		return self.rpc("license_installments", arrParams)


	def license_contract_create(self, nUserID, strLicenseType, strCycleStartTimestamp = None, bLicenseContractRecurring = True):

		arrParams = [
			nUserID,
			strLicenseType,
			strCycleStartTimestamp,
			bLicenseContractRecurring,
		]

		return Deserializer.deserialize(self.rpc("license_contract_create", arrParams))

	def license_contract_get(self, nLicenseContractID, bSelectForUpdate = False, bIncludeDeletedLicenseContracts = False):

		arrParams = [
			nLicenseContractID,
			bSelectForUpdate,
			bIncludeDeletedLicenseContracts,
		]

		return Deserializer.deserialize(self.rpc("license_contract_get", arrParams))

	def license_contract_edit(self, nLicenseContract, objLicenseContract):

		objLicenseContract = Serializer.serialize(objLicenseContract)

		arrParams = [
			nLicenseContract,
			objLicenseContract,
		]

		return Deserializer.deserialize(self.rpc("license_contract_edit", arrParams))

	def license_contracts(self, nUserID = None, strLicenseType = None):

		arrParams = [
			nUserID,
			strLicenseType,
		]

		return self.rpc("license_contracts", arrParams)


	def license_contract_delete(self, nLicenseContractID):

		arrParams = [
			nLicenseContractID,
		]

		return self.rpc("license_contract_delete", arrParams)


	def sqlselection_views_create(self):

		arrParams = [
		]

		self.rpc("sqlselection_views_create", arrParams)


	def resource_utilization_summary_start_timestamp_default(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("resource_utilization_summary_start_timestamp_default", arrParams)


	def query_parse(self, strSQL):

		arrParams = [
			strSQL,
		]

		return self.rpc("query_parse", arrParams)


	def query_structured(self, strUserID, strTableName, objQueryConditions, strCollapseType = "array_subrows"):

		objQueryConditions = Serializer.serialize(objQueryConditions)

		arrParams = [
			strUserID,
			strTableName,
			objQueryConditions,
			strCollapseType,
		]

		return self.rpc("query_structured", arrParams)


	def infrastructure_public_designs(self):

		arrParams = [
		]

		return self.rpc("infrastructure_public_designs", arrParams)


	def server_type_available_server_count_batch(self, strUserIDOwner, strDatacenterName, arrServerTypeIDs, nMaximumResults, bIncludeReservedForUser = False, nInstanceArrayID = None):

		arrParams = [
			strUserIDOwner,
			strDatacenterName,
			arrServerTypeIDs,
			nMaximumResults,
			bIncludeReservedForUser,
			nInstanceArrayID,
		]

		return self.rpc("server_type_available_server_count_batch", arrParams)


	def cluster_automatic_management_status_set(self, strClusterID, bStatus):

		arrParams = [
			strClusterID,
			bStatus,
		]

		self.rpc("cluster_automatic_management_status_set", arrParams)


	def infrastructure_design_lock_set(self, strInfrastructureID, bLockStatus):

		arrParams = [
			strInfrastructureID,
			bLockStatus,
		]

		self.rpc("infrastructure_design_lock_set", arrParams)


	def instance_server_type_reservation_create(self, strInstanceID, bRecurring, nReservationCycleMonths, nInstallmentCycleMonths):

		arrParams = [
			strInstanceID,
			bRecurring,
			nReservationCycleMonths,
			nInstallmentCycleMonths,
		]

		return Deserializer.deserialize(self.rpc("instance_server_type_reservation_create", arrParams))

	def prices(self):

		arrParams = [
		]

		return self.rpc("prices", arrParams)


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

	def afc_exceptions(self, nAFCID):

		arrParams = [
			nAFCID,
		]

		return self.rpc("afc_exceptions", arrParams)


	def ssh_connect_test(self, strIPAddress, nPort, strClientLibrary = "fsockopen", strDatacenterName = None, strUsername = None, strPassword = ""):

		arrParams = [
			strIPAddress,
			nPort,
			strClientLibrary,
			strDatacenterName,
			strUsername,
			strPassword,
		]

		return self.rpc("ssh_connect_test", arrParams)


	def production_config_secret_encrypt(self, strSecret):

		arrParams = [
			strSecret,
		]

		return self.rpc("production_config_secret_encrypt", arrParams)


	def infrastructure_deployments(self, nInfrastructureID, strStartTimestamp = None, strEndTimestamp = None):

		arrParams = [
			nInfrastructureID,
			strStartTimestamp,
			strEndTimestamp,
		]

		return self.rpc("infrastructure_deployments", arrParams)


	def infrastructure_public_designs_member_set(self, strInfrastructureID, bPublicDesign):

		arrParams = [
			strInfrastructureID,
			bPublicDesign,
		]

		self.rpc("infrastructure_public_designs_member_set", arrParams)


	def license_delete(self, nLicenseID):

		arrParams = [
			nLicenseID,
		]

		return self.rpc("license_delete", arrParams)


	def volume_template_experimental_toggle(self, nVolumeTemplateID):

		arrParams = [
			nVolumeTemplateID,
		]

		return self.rpc("volume_template_experimental_toggle", arrParams)


	def server_comments_set(self, nServerID, strCommentsText):

		arrParams = [
			nServerID,
			strCommentsText,
		]

		return Deserializer.deserialize(self.rpc("server_comments_set", arrParams))

	def user_jwt_check(self, strEncodedCookie, nUserIdBSI):

		arrParams = [
			strEncodedCookie,
			nUserIdBSI,
		]

		return self.rpc("user_jwt_check", arrParams)


	def integration_config_secret_encrypt(self, strSecret):

		arrParams = [
			strSecret,
		]

		return self.rpc("integration_config_secret_encrypt", arrParams)


	def user_server_type_reservations_unused(self, strUserID, strDatacenterName):

		arrParams = [
			strUserID,
			strDatacenterName,
		]

		return self.rpc("user_server_type_reservations_unused", arrParams)


	def user_infrastructure_deployments(self, strUserIDOwner, strStartTimestamp = None, strEndTimestamp = None):

		arrParams = [
			strUserIDOwner,
			strStartTimestamp,
			strEndTimestamp,
		]

		return self.rpc("user_infrastructure_deployments", arrParams)


	def infrastructure_deployment_get(self, nInfrastructureDeployID):

		arrParams = [
			nInfrastructureDeployID,
		]

		return self.rpc("infrastructure_deployment_get", arrParams)


	def user_promotions(self, nUserID):

		arrParams = [
			nUserID,
		]

		return self.rpc("user_promotions", arrParams)


	def users_with_promotion(self, strPromotionName):

		arrParams = [
			strPromotionName,
		]

		return self.rpc("users_with_promotion", arrParams)


	def afc_skip(self, nAFCID):

		arrParams = [
			nAFCID,
		]

		self.rpc("afc_skip", arrParams)


	def product_get_internal(self, strProductName, nProductID, bPublic = False):

		arrParams = [
			strProductName,
			nProductID,
			bPublic,
		]

		return self.rpc("product_get_internal", arrParams)


	def product_children_internal(self, strProductType, nProductID, strChildProductType, bAllowDeleted = False):

		arrParams = [
			strProductType,
			nProductID,
			strChildProductType,
			bAllowDeleted,
		]

		return self.rpc("product_children_internal", arrParams)


	def storage_pool_physical_size_free_mb(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		return self.rpc("storage_pool_physical_size_free_mb", arrParams)


	def storages_update_database_cache_in_parallel(self, arrStoragePoolIDs = None, bLockMustBeBlocking = False):

		arrParams = [
			arrStoragePoolIDs,
			bLockMustBeBlocking,
		]

		return self.rpc("storages_update_database_cache_in_parallel", arrParams)


	def storage_update_database_cache(self, nStoragePoolID, bLockMustBeBlocking = False):

		arrParams = [
			nStoragePoolID,
			bLockMustBeBlocking,
		]

		return self.rpc("storage_update_database_cache", arrParams)


	def shared_drive_container_arrays(self, strSharedDriveID):

		arrParams = [
			strSharedDriveID,
		]

		return self.rpc("shared_drive_container_arrays", arrParams)


	def dev_env_create_vmware(self, nDatacenterIndex, nUserID = None):

		arrParams = [
			nDatacenterIndex,
			nUserID,
		]

		self.rpc("dev_env_create_vmware", arrParams)


	def nics_information_generate(self, nNoNICs):

		arrParams = [
			nNoNICs,
		]

		return self.rpc("nics_information_generate", arrParams)


	def nic_lua_script_generate_url(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("nic_lua_script_generate_url", arrParams)


	def nic_confirm_existance_url(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("nic_confirm_existance_url", arrParams)


	def subnet_create_from_owned_subnet_pool(self, strNetworkID, objSubnet):

		objSubnet = Serializer.serialize(objSubnet)

		arrParams = [
			strNetworkID,
			objSubnet,
		]

		return self.rpc("subnet_create_from_owned_subnet_pool", arrParams)


	def switch_device_complete_driver_dump(self, nSwitchID):

		arrParams = [
			nSwitchID,
		]

		return self.rpc("switch_device_complete_driver_dump", arrParams)


	def user_franchise_get(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_franchise_get", arrParams)


	def switch_update_database_cache(self, nSwitchID, bThrowOnNonBlockingLock = False):

		arrParams = [
			nSwitchID,
			bThrowOnNonBlockingLock,
		]

		return self.rpc("switch_update_database_cache", arrParams)


	def switch_update_database_cache_in_parallel(self):

		arrParams = [
		]

		return self.rpc("switch_update_database_cache_in_parallel", arrParams)


	def subnet_pool_delete(self, nSubnetPoolID):

		arrParams = [
			nSubnetPoolID,
		]

		self.rpc("subnet_pool_delete", arrParams)


	def subnet_pool_prefix_sizes_stats(self, nSubnetPoolID):

		arrParams = [
			nSubnetPoolID,
		]

		return self.rpc("subnet_pool_prefix_sizes_stats", arrParams)


	def subnet_pool_update_database_cache(self, nSubnetPoolID):

		arrParams = [
			nSubnetPoolID,
		]

		self.rpc("subnet_pool_update_database_cache", arrParams)


	def subnet_pools_update_database_cache(self):

		arrParams = [
		]

		return self.rpc("subnet_pools_update_database_cache", arrParams)


	def subnet_allocation_conflicts(self):

		arrParams = [
		]

		return self.rpc("subnet_allocation_conflicts", arrParams)


	def datacenter_master(self):

		arrParams = [
		]

		return self.rpc("datacenter_master", arrParams)


	def switch_device_iscsi_boot_servers(self, nSwitchDeviceID):

		arrParams = [
			nSwitchDeviceID,
		]

		return self.rpc("switch_device_iscsi_boot_servers", arrParams)


	def storage_pool_iscsi_boot_servers(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		return self.rpc("storage_pool_iscsi_boot_servers", arrParams)


	def data_lake_usage(self):

		arrParams = [
		]

		return self.rpc("data_lake_usage", arrParams)


	def server_types_datacenter(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("server_types_datacenter", arrParams)


	def user_authenticator_has(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_authenticator_has", arrParams)


	def prices_history(self, bExcludeFuturePrices = False, bOnlyActivePrices = False):

		arrParams = [
			bExcludeFuturePrices,
			bOnlyActivePrices,
		]

		return self.rpc("prices_history", arrParams)


	def events_expire(self):

		arrParams = [
		]

		self.rpc("events_expire", arrParams)


	def data_lakes_traffic_update(self, arrDataLakesTrafficData):

		arrParams = [
			arrDataLakesTrafficData,
		]

		self.rpc("data_lakes_traffic_update", arrParams)


	def license_vendor_report(self, strLicenseType, strStartTimestamp, strEndTimestamp, objLicenseFilter = None):

		objLicenseFilter = Serializer.serialize(objLicenseFilter)

		arrParams = [
			strLicenseType,
			strStartTimestamp,
			strEndTimestamp,
			objLicenseFilter,
		]

		return self.rpc("license_vendor_report", arrParams)


	def subnet_pool_available_intervals(self, nSubnetPoolID, bLockRow = True):

		arrParams = [
			nSubnetPoolID,
			bLockRow,
		]

		return self.rpc("subnet_pool_available_intervals", arrParams)


	def database_build_000000_sql_url(self):

		arrParams = [
		]

		return self.rpc("database_build_000000_sql_url", arrParams)


	def container_cluster_gui_settings_save(self, strContainerClusterID, objGUIProductSettings, arrPropertyNames):

		objGUIProductSettings = Serializer.serialize(objGUIProductSettings)

		arrParams = [
			strContainerClusterID,
			objGUIProductSettings,
			arrPropertyNames,
		]

		self.rpc("container_cluster_gui_settings_save", arrParams)


	def container_cluster_create(self, strInfrastructureID, objContainerCluster):

		objContainerCluster = Serializer.serialize(objContainerCluster)

		arrParams = [
			strInfrastructureID,
			objContainerCluster,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_create", arrParams))

	def container_cluster_get(self, strContainerClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 10):

		arrParams = [
			strContainerClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_get", arrParams))

	def container_cluster_edit(self, strContainerClusterID, objContainerClusterOperation):

		objContainerClusterOperation = Serializer.serialize(objContainerClusterOperation)

		arrParams = [
			strContainerClusterID,
			objContainerClusterOperation,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_edit", arrParams))

	def container_cluster_stop(self, strContainerClusterID):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_stop", arrParams))

	def container_cluster_start(self, strContainerClusterID):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_start", arrParams))

	def container_cluster_delete(self, strContainerClusterID):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_delete", arrParams))

	def container_clusters(self, strInfrastructureID, arrContainerClusterIDs = None):

		arrParams = [
			strInfrastructureID,
			arrContainerClusterIDs,
		]

		objContainerCluster = self.rpc("container_clusters", arrParams)
		for strKeyContainerCluster in objContainerCluster:
			objContainerCluster[strKeyContainerCluster] = Deserializer.deserialize(objContainerCluster[strKeyContainerCluster])
		return objContainerCluster

	def container_cluster_suspend(self, strContainerClusterID):

		arrParams = [
			strContainerClusterID,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_suspend", arrParams))

	def container_cluster_automatic_management_status_set(self, strContainerClusterID, bStatus):

		arrParams = [
			strContainerClusterID,
			bStatus,
		]

		self.rpc("container_cluster_automatic_management_status_set", arrParams)


	def storage_pool_usage_batch_for_storage_type(self, strDriveStorageType, strDatacenterName, strInfrastructureExperimentalPriority = "disallow", nUserID = None):

		arrParams = [
			strDriveStorageType,
			strDatacenterName,
			strInfrastructureExperimentalPriority,
			nUserID,
		]

		return self.rpc("storage_pool_usage_batch_for_storage_type", arrParams)


	def user_custom_prices_update(self, nUserID, objUserCustomPrices):

		objUserCustomPrices = Serializer.serialize(objUserCustomPrices)

		arrParams = [
			nUserID,
			objUserCustomPrices,
		]

		self.rpc("user_custom_prices_update", arrParams)


	def user_prices_history(self, strUserID, bExcludeFuturePrices = False, bOnlyActivePrices = False, bExpandWithPrivateDatacenters = True):

		arrParams = [
			strUserID,
			bExcludeFuturePrices,
			bOnlyActivePrices,
			bExpandWithPrivateDatacenters,
		]

		return self.rpc("user_prices_history", arrParams)


	def user_prices(self, strUserID):

		arrParams = [
			strUserID,
		]

		return self.rpc("user_prices", arrParams)


	def license_stop(self, nLicenseID):

		arrParams = [
			nLicenseID,
		]

		return self.rpc("license_stop", arrParams)


	def container_clusters_software_version_get(self, arrContainerClusterTypes = []):

		arrParams = [
			arrContainerClusterTypes,
		]

		return self.rpc("container_clusters_software_version_get", arrParams)


	def fs_create(self, strFSURL, strType, strPermission = None):

		arrParams = [
			strFSURL,
			strType,
			strPermission,
		]

		self.rpc("fs_create", arrParams)


	def fs_delete(self, strFSURL, bRecursive = False):

		arrParams = [
			strFSURL,
			bRecursive,
		]

		self.rpc("fs_delete", arrParams)


	def fs_info(self, strFSURL):

		arrParams = [
			strFSURL,
		]

		self.rpc("fs_info", arrParams)


	def fs_list(self, strFSURL):

		arrParams = [
			strFSURL,
		]

		self.rpc("fs_list", arrParams)


	def fs_move(self, strFSURL, strPathNew):

		arrParams = [
			strFSURL,
			strPathNew,
		]

		self.rpc("fs_move", arrParams)


	def fs_owner_set(self, strFSURL, strOwner):

		arrParams = [
			strFSURL,
			strOwner,
		]

		self.rpc("fs_owner_set", arrParams)


	def fs_read(self, strFSURL, strEncoding, nOffset, nLength):

		arrParams = [
			strFSURL,
			strEncoding,
			nOffset,
			nLength,
		]

		self.rpc("fs_read", arrParams)


	def fs_rename(self, strFSURL, strFilenameNew):

		arrParams = [
			strFSURL,
			strFilenameNew,
		]

		self.rpc("fs_rename", arrParams)


	def fs_truncate(self, strFSURL, nLengthNew = 0):

		arrParams = [
			strFSURL,
			nLengthNew,
		]

		self.rpc("fs_truncate", arrParams)


	def fs_write(self, strFSURL, strContents, strEncoding, nOffset = None, bTruncate = True):

		arrParams = [
			strFSURL,
			strContents,
			strEncoding,
			nOffset,
			bTruncate,
		]

		self.rpc("fs_write", arrParams)


	def user_access_level_set(self, nUserID, strAccessLevel):

		arrParams = [
			nUserID,
			strAccessLevel,
		]

		return self.rpc("user_access_level_set", arrParams)


	def afc_queue_asynchronous_archive_and_delete_old(self, arrAFCGroupIDs = None):

		arrParams = [
			arrAFCGroupIDs,
		]

		self.rpc("afc_queue_asynchronous_archive_and_delete_old", arrParams)


	def afc_queue_non_asynchronous_archive_and_delete_old(self):

		arrParams = [
		]

		self.rpc("afc_queue_non_asynchronous_archive_and_delete_old", arrParams)


	def licenses_non_recurring_stop(self):

		arrParams = [
		]

		return self.rpc("licenses_non_recurring_stop", arrParams)


	def server_type_reservations_stopped_unset_reallocated_server_ids(self):

		arrParams = [
		]

		self.rpc("server_type_reservations_stopped_unset_reallocated_server_ids", arrParams)


	def franchises(self):

		arrParams = [
		]

		return self.rpc("franchises", arrParams)


	def user_password_reveal_set(self, nUserID, strResourceType, bEnabled):

		arrParams = [
			nUserID,
			strResourceType,
			bEnabled,
		]

		return self.rpc("user_password_reveal_set", arrParams)


	def user_permissions_config(self, nUserID = None):

		arrParams = [
			nUserID,
		]

		return self.rpc("user_permissions_config", arrParams)


	def user_password_reveal_has(self, nUserID, strResourceType):

		arrParams = [
			nUserID,
			strResourceType,
		]

		return self.rpc("user_password_reveal_has", arrParams)


	def user_update_email_status(self, strUserID, strUserEmailStatus):

		arrParams = [
			strUserID,
			strUserEmailStatus,
		]

		return Deserializer.deserialize(self.rpc("user_update_email_status", arrParams))

	def fs_download_url(self, strFSURL):

		arrParams = [
			strFSURL,
		]

		self.rpc("fs_download_url", arrParams)


	def dns_subdomains_anomalies_fix(self):

		arrParams = [
		]

		self.rpc("dns_subdomains_anomalies_fix", arrParams)


	def server_power_get_batch_datacenter_used(self, strDatacenter, bOnlySANConnected):

		arrParams = [
			strDatacenter,
			bOnlySANConnected,
		]

		return self.rpc("server_power_get_batch_datacenter_used", arrParams)


	def server_power_set_batch_datacenter_used(self, strDatacenter, strPowerCommand, bThrowIfPowerGetFails = True):

		arrParams = [
			strDatacenter,
			strPowerCommand,
			bThrowIfPowerGetFails,
		]

		return self.rpc("server_power_set_batch_datacenter_used", arrParams)


	def port_connect_test(self, strIPAddress, nPort, strClientLibrary = "fsockopen"):

		arrParams = [
			strIPAddress,
			nPort,
			strClientLibrary,
		]

		return self.rpc("port_connect_test", arrParams)


	def datacenter_create(self, objDatacenter, objDatacenterConfig):

		objDatacenter = Serializer.serialize(objDatacenter)
		objDatacenterConfig = Serializer.serialize(objDatacenterConfig)

		arrParams = [
			objDatacenter,
			objDatacenterConfig,
		]

		return Deserializer.deserialize(self.rpc("datacenter_create", arrParams))

	def datacenter_maintenance_set(self, strDatacenterName, bMaintenance):

		arrParams = [
			strDatacenterName,
			bMaintenance,
		]

		self.rpc("datacenter_maintenance_set", arrParams)


	def storage_pool_drive_mappings_recreate(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		self.rpc("storage_pool_drive_mappings_recreate", arrParams)


	def infrastructure_experimental_tags(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_experimental_tags", arrParams)


	def infrastructure_experimental_tag_has(self, nInfrastructureID, strExperimentalTag):

		arrParams = [
			nInfrastructureID,
			strExperimentalTag,
		]

		return self.rpc("infrastructure_experimental_tag_has", arrParams)


	def infrastructure_experimental_tag_add(self, nInfrastructureID, strExperimentalTag):

		arrParams = [
			nInfrastructureID,
			strExperimentalTag,
		]

		return self.rpc("infrastructure_experimental_tag_add", arrParams)


	def infrastructure_experimental_tag_remove(self, nInfrastructureID, strExperimentalTag):

		arrParams = [
			nInfrastructureID,
			strExperimentalTag,
		]

		self.rpc("infrastructure_experimental_tag_remove", arrParams)


	def infrastructures_with_experimental_tag(self, strExperimentalTag):

		arrParams = [
			strExperimentalTag,
		]

		return self.rpc("infrastructures_with_experimental_tag", arrParams)


	def user_experimental_tags(self, nUserID):

		arrParams = [
			nUserID,
		]

		return self.rpc("user_experimental_tags", arrParams)


	def user_experimental_tag_has(self, nUserID, strExperimentalTag):

		arrParams = [
			nUserID,
			strExperimentalTag,
		]

		return self.rpc("user_experimental_tag_has", arrParams)


	def user_experimental_tag_add(self, nUserID, strExperimentalTag):

		arrParams = [
			nUserID,
			strExperimentalTag,
		]

		return self.rpc("user_experimental_tag_add", arrParams)


	def user_experimental_tag_remove(self, nUserID, strExperimentalTag):

		arrParams = [
			nUserID,
			strExperimentalTag,
		]

		self.rpc("user_experimental_tag_remove", arrParams)


	def users_with_experimental_tag(self, strExperimentalTag):

		arrParams = [
			strExperimentalTag,
		]

		return self.rpc("users_with_experimental_tag", arrParams)


	def data_lake_promotion_has(self, nDataLakeID, strPromotionName):

		arrParams = [
			nDataLakeID,
			strPromotionName,
		]

		return self.rpc("data_lake_promotion_has", arrParams)


	def user_promotion_has(self, nUserID, strPromotionName):

		arrParams = [
			nUserID,
			strPromotionName,
		]

		return self.rpc("user_promotion_has", arrParams)


	def user_promotion_add(self, nUserID, strPromotionName):

		arrParams = [
			nUserID,
			strPromotionName,
		]

		return self.rpc("user_promotion_add", arrParams)


	def user_promotion_remove(self, nUserID, strPromotionName):

		arrParams = [
			nUserID,
			strPromotionName,
		]

		self.rpc("user_promotion_remove", arrParams)


	def data_lake_usage_store(self, nDataLakeID):

		arrParams = [
			nDataLakeID,
		]

		return self.rpc("data_lake_usage_store", arrParams)


	def fs_upload_url(self, strFSURL):

		arrParams = [
			strFSURL,
		]

		return self.rpc("fs_upload_url", arrParams)


	def infrastructure_experimental_tags_allowed(self):

		arrParams = [
		]

		return self.rpc("infrastructure_experimental_tags_allowed", arrParams)


	def user_experimental_tags_allowed(self):

		arrParams = [
		]

		return self.rpc("user_experimental_tags_allowed", arrParams)


	def san_ip_search(self, strDatacenterName, strSearchIPAddress):

		arrParams = [
			strDatacenterName,
			strSearchIPAddress,
		]

		self.rpc("san_ip_search", arrParams)


	def chassis_rack_create(self, objChassisRackData):

		objChassisRackData = Serializer.serialize(objChassisRackData)

		arrParams = [
			objChassisRackData,
		]

		return self.rpc("chassis_rack_create", arrParams)


	def chassis_rack_get(self, mxChassisRackID):

		mxChassisRackID = Serializer.serialize(mxChassisRackID)

		arrParams = [
			mxChassisRackID,
		]

		return self.rpc("chassis_rack_get", arrParams)


	def chassis_rack_delete(self, nChassisRackID):

		arrParams = [
			nChassisRackID,
		]

		self.rpc("chassis_rack_delete", arrParams)


	def chassis_racks(self, strDatacenter = None):

		arrParams = [
			strDatacenter,
		]

		return self.rpc("chassis_racks", arrParams)


	def drives_template_usage_report(self, strStartTimestamp, strEndTimestamp, objFilter = None):

		objFilter = Serializer.serialize(objFilter)

		arrParams = [
			strStartTimestamp,
			strEndTimestamp,
			objFilter,
		]

		return self.rpc("drives_template_usage_report", arrParams)


	def infrastructure_deploy_slow_afc_report(self, strSinceTimestamp = None):

		arrParams = [
			strSinceTimestamp,
		]

		return self.rpc("infrastructure_deploy_slow_afc_report", arrParams)


	def user_limits(self, strUserID):

		arrParams = [
			strUserID,
		]

		return Deserializer.deserialize(self.rpc("user_limits", arrParams))

	def user_limits_default(self):

		arrParams = [
		]

		return Deserializer.deserialize(self.rpc("user_limits_default", arrParams))

	def user_limits_custom(self, strUserID):

		arrParams = [
			strUserID,
		]

		return Deserializer.deserialize(self.rpc("user_limits_custom", arrParams))

	def user_limits_update(self, strUserID, objUserLimits):

		objUserLimits = Serializer.serialize(objUserLimits)

		arrParams = [
			strUserID,
			objUserLimits,
		]

		self.rpc("user_limits_update", arrParams)


	def json_schema_get(self, strSchema):

		arrParams = [
			strSchema,
		]

		return self.rpc("json_schema_get", arrParams)


	def storage_pool_experimental_set(self, nStoragePoolID, bIsExperimental):

		arrParams = [
			nStoragePoolID,
			bIsExperimental,
		]

		self.rpc("storage_pool_experimental_set", arrParams)


	def users_for_tickets_impersonated_create(self, arrDatacenterLabels, arrSwitchDeviceIDs, arrStoragePoolIDs, bIncludeDataLake, bOnlyWithWAN, arrExtraUserIDs, arrExtraUserEmails, bCCDelegates, bCCInfrastructureAdmins):

		arrParams = [
			arrDatacenterLabels,
			arrSwitchDeviceIDs,
			arrStoragePoolIDs,
			bIncludeDataLake,
			bOnlyWithWAN,
			arrExtraUserIDs,
			arrExtraUserEmails,
			bCCDelegates,
			bCCInfrastructureAdmins,
		]

		return self.rpc("users_for_tickets_impersonated_create", arrParams)


	def server_delete(self, nServerID, bSkipIPMI = False):

		arrParams = [
			nServerID,
			bSkipIPMI,
		]

		self.rpc("server_delete", arrParams)


	def instance_agent_reboot(self, nInstanceID, bForce, nTimeoutMilliseconds):

		arrParams = [
			nInstanceID,
			bForce,
			nTimeoutMilliseconds,
		]

		return self.rpc("instance_agent_reboot", arrParams)


	def instance_agent_shutdown(self, nInstanceID, bForce, nTimeoutMilliseconds):

		arrParams = [
			nInstanceID,
			bForce,
			nTimeoutMilliseconds,
		]

		return self.rpc("instance_agent_shutdown", arrParams)


	def instance_agent_process_exit(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_agent_process_exit", arrParams)


	def instance_agent_test(self, nInstanceID, nSleepSeconds = 2):

		arrParams = [
			nInstanceID,
			nSleepSeconds,
		]

		return self.rpc("instance_agent_test", arrParams)


	def user_convert_passwords_now(self):

		arrParams = [
		]

		self.rpc("user_convert_passwords_now", arrParams)


	def server_type_boot_type_edit(self, strServerTypeID, strServerTypeBootType):

		arrParams = [
			strServerTypeID,
			strServerTypeBootType,
		]

		return self.rpc("server_type_boot_type_edit", arrParams)


	def volume_template_boot_type_edit(self, nVolumeTemplateID, strVolumeTemplateBootType):

		arrParams = [
			nVolumeTemplateID,
			strVolumeTemplateBootType,
		]

		self.rpc("volume_template_boot_type_edit", arrParams)


	def volume_template_os_local_disk_clone_function_name_edit(self, nVolumeTemplateID, mxVolumeTemplateOSLocalDiskCloneFunctionName = None):

		mxVolumeTemplateOSLocalDiskCloneFunctionName = Serializer.serialize(mxVolumeTemplateOSLocalDiskCloneFunctionName)

		arrParams = [
			nVolumeTemplateID,
			mxVolumeTemplateOSLocalDiskCloneFunctionName,
		]

		self.rpc("volume_template_os_local_disk_clone_function_name_edit", arrParams)


	def volume_template_storage_pool_create_from_repo(self, strVolumeTemplateRepoBaseURL, nStoragePoolID, bCreateTemplateIfNotExists):

		arrParams = [
			strVolumeTemplateRepoBaseURL,
			nStoragePoolID,
			bCreateTemplateIfNotExists,
		]

		self.rpc("volume_template_storage_pool_create_from_repo", arrParams)


	def volume_templates_repo_catalog_get(self, strCatalogURL):

		arrParams = [
			strCatalogURL,
		]

		return self.rpc("volume_templates_repo_catalog_get", arrParams)


	def volume_templates_repo_catalog_urls(self):

		arrParams = [
		]

		return self.rpc("volume_templates_repo_catalog_urls", arrParams)


	def drive_provision(self, nDriveID, strStage, objOptions = []):

		objOptions = Serializer.serialize(objOptions)

		arrParams = [
			nDriveID,
			strStage,
			objOptions,
		]

		self.rpc("drive_provision", arrParams)


	def volume_templates_populate_from_catalogs(self, arrCatalogURLs = None):

		arrParams = [
			arrCatalogURLs,
		]

		objVolumeTemplate = self.rpc("volume_templates_populate_from_catalogs", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def volume_template_create_empty(self, objVolumeTemplate):

		objVolumeTemplate = Serializer.serialize(objVolumeTemplate)

		arrParams = [
			objVolumeTemplate,
		]

		return Deserializer.deserialize(self.rpc("volume_template_create_empty", arrParams))

	def instance_agent_update(self, nInstanceID, strUpdateURL):

		arrParams = [
			nInstanceID,
			strUpdateURL,
		]

		return self.rpc("instance_agent_update", arrParams)


	def instance_monitoring_data_get(self, nInstanceID, nGranularityMinutes = 1, strTimestampStart = None, strTimestampEnd = None):

		arrParams = [
			nInstanceID,
			nGranularityMinutes,
			strTimestampStart,
			strTimestampEnd,
		]

		return self.rpc("instance_monitoring_data_get", arrParams)


	def instance_array_monitoring_data_get(self, nInstanceArrayID, nGranularityMinutes = 1, strTimestampStart = None, strTimestampEnd = None):

		arrParams = [
			nInstanceArrayID,
			nGranularityMinutes,
			strTimestampStart,
			strTimestampEnd,
		]

		return self.rpc("instance_array_monitoring_data_get", arrParams)


	def container_platform_monitoring_data_get(self, nContainerPlatformID, nGranularityMinutes = 1, strTimestampStart = None, strTimestampEnd = None):

		arrParams = [
			nContainerPlatformID,
			nGranularityMinutes,
			strTimestampStart,
			strTimestampEnd,
		]

		return self.rpc("container_platform_monitoring_data_get", arrParams)


	def user_test_account_set(self, nUserID, bUserIsTestAccount):

		arrParams = [
			nUserID,
			bUserIsTestAccount,
		]

		self.rpc("user_test_account_set", arrParams)


	def user_exclude_from_reports_set(self, nUserID, bUserExcludeFromReports):

		arrParams = [
			nUserID,
			bUserExcludeFromReports,
		]

		self.rpc("user_exclude_from_reports_set", arrParams)


	def licenses_recurring_cycle_extend(self):

		arrParams = [
		]

		self.rpc("licenses_recurring_cycle_extend", arrParams)


	def licenses_expired(self, bRecurring):

		arrParams = [
			bRecurring,
		]

		return self.rpc("licenses_expired", arrParams)


	def license_recurring_extend(self, nLicenseID):

		arrParams = [
			nLicenseID,
		]

		return self.rpc("license_recurring_extend", arrParams)


	def data_lake_core_site_conf_download_url(self, strUserID, nDataLakeID):

		arrParams = [
			strUserID,
			nDataLakeID,
		]

		return self.rpc("data_lake_core_site_conf_download_url", arrParams)


	def secure_gateway_proxy_add(self, proxy, strDatacenterName, nFrontendPort):

		proxy = Serializer.serialize(proxy)

		arrParams = [
			proxy,
			strDatacenterName,
			nFrontendPort,
		]

		self.rpc("secure_gateway_proxy_add", arrParams)


	def secure_gateway_proxy_remove(self, nDestinationID, strDiscriminator):

		arrParams = [
			nDestinationID,
			strDiscriminator,
		]

		self.rpc("secure_gateway_proxy_remove", arrParams)


	def secure_gateway_proxy_remove_by_id(self, nID):

		arrParams = [
			nID,
		]

		self.rpc("secure_gateway_proxy_remove_by_id", arrParams)


	def secure_gateway_proxy_update(self, nID, proxy):

		proxy = Serializer.serialize(proxy)

		arrParams = [
			nID,
			proxy,
		]

		self.rpc("secure_gateway_proxy_update", arrParams)


	def secure_gateway_config_refresh(self, nSecureGatewayID, bUploadNewConfig = True):

		arrParams = [
			nSecureGatewayID,
			bUploadNewConfig,
		]

		self.rpc("secure_gateway_config_refresh", arrParams)


	def drive_reservation_create(self, strUserID, objReservation):

		objReservation = Serializer.serialize(objReservation)

		arrParams = [
			strUserID,
			objReservation,
		]

		return Deserializer.deserialize(self.rpc("drive_reservation_create", arrParams))

	def drive_reservation_get(self, nDriveReservationID):

		arrParams = [
			nDriveReservationID,
		]

		return Deserializer.deserialize(self.rpc("drive_reservation_get", arrParams))

	def drive_reservation_edit(self, nDriveReservationID, objDriveReservation):

		objDriveReservation = Serializer.serialize(objDriveReservation)

		arrParams = [
			nDriveReservationID,
			objDriveReservation,
		]

		return Deserializer.deserialize(self.rpc("drive_reservation_edit", arrParams))

	def user_drive_reservations(self, strUserID, strUserPlanType = None):

		arrParams = [
			strUserID,
			strUserPlanType,
		]

		arrDriveReservations = self.rpc("user_drive_reservations", arrParams)
		for index in range(len(arrDriveReservations)):
			arrDriveReservations[index] = Deserializer.deserialize(arrDriveReservations[index])
		return arrDriveReservations

	def drive_reservation_plan_type_change(self, nDriveReservationID, strNewUserPlanType):

		arrParams = [
			nDriveReservationID,
			strNewUserPlanType,
		]

		return Deserializer.deserialize(self.rpc("drive_reservation_plan_type_change", arrParams))

	def subnet_reservation_create(self, strUserID, objReservation):

		objReservation = Serializer.serialize(objReservation)

		arrParams = [
			strUserID,
			objReservation,
		]

		return Deserializer.deserialize(self.rpc("subnet_reservation_create", arrParams))

	def subnet_reservation_get(self, nSubnetReservationID):

		arrParams = [
			nSubnetReservationID,
		]

		return Deserializer.deserialize(self.rpc("subnet_reservation_get", arrParams))

	def subnet_reservation_edit(self, nSubnetReservationID, objSubnetReservation):

		objSubnetReservation = Serializer.serialize(objSubnetReservation)

		arrParams = [
			nSubnetReservationID,
			objSubnetReservation,
		]

		return Deserializer.deserialize(self.rpc("subnet_reservation_edit", arrParams))

	def user_subnet_reservations(self, strUserID, strUserPlanType = None):

		arrParams = [
			strUserID,
			strUserPlanType,
		]

		arrSubnetReservations = self.rpc("user_subnet_reservations", arrParams)
		for index in range(len(arrSubnetReservations)):
			arrSubnetReservations[index] = Deserializer.deserialize(arrSubnetReservations[index])
		return arrSubnetReservations

	def subnet_reservation_plan_type_change(self, nSubnetReservationID, strNewUserPlanType):

		arrParams = [
			nSubnetReservationID,
			strNewUserPlanType,
		]

		return Deserializer.deserialize(self.rpc("subnet_reservation_plan_type_change", arrParams))

	def bdk_agent_reboot(self, nServerID, bForce, nTimeoutMilliseconds):

		arrParams = [
			nServerID,
			bForce,
			nTimeoutMilliseconds,
		]

		return self.rpc("bdk_agent_reboot", arrParams)


	def bdk_agent_shutdown(self, nServerID, bForce, nTimeoutMilliseconds):

		arrParams = [
			nServerID,
			bForce,
			nTimeoutMilliseconds,
		]

		self.rpc("bdk_agent_shutdown", arrParams)


	def bdk_agent_process_exit(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("bdk_agent_process_exit", arrParams)


	def bdk_agent_test(self, nServerID, nSleepSeconds, strCallerName = "unspecified caller"):

		arrParams = [
			nServerID,
			nSleepSeconds,
			strCallerName,
		]

		return self.rpc("bdk_agent_test", arrParams)


	def user_licenses_unused(self, nUserID, strLicenseType = None, objLicensePropertiesFilter = None, strForTimestamp = None, bSelectForUpdate = False):

		objLicensePropertiesFilter = Serializer.serialize(objLicensePropertiesFilter)

		arrParams = [
			nUserID,
			strLicenseType,
			objLicensePropertiesFilter,
			strForTimestamp,
			bSelectForUpdate,
		]

		return self.rpc("user_licenses_unused", arrParams)


	def container_interface_get(self, nContainerInterfaceID):

		arrParams = [
			nContainerInterfaceID,
		]

		return Deserializer.deserialize(self.rpc("container_interface_get", arrParams))

	def storage_pool_user_set(self, nStoragePoolID, nUserID = None):

		arrParams = [
			nStoragePoolID,
			nUserID,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_user_set", arrParams))

	def container_get(self, strContainerID):

		arrParams = [
			strContainerID,
		]

		return Deserializer.deserialize(self.rpc("container_get", arrParams))

	def containers(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		objContainer = self.rpc("containers", arrParams)
		for strKeyContainer in objContainer:
			objContainer[strKeyContainer] = Deserializer.deserialize(objContainer[strKeyContainer])
		return objContainer

	def container_logs(self, strContainerID, strSinceTimestamp = None, nLimitBytes = None):

		arrParams = [
			strContainerID,
			strSinceTimestamp,
			nLimitBytes,
		]

		return self.rpc("container_logs", arrParams)


	def container_drives(self, strContainerID):

		arrParams = [
			strContainerID,
		]

		objDrive = self.rpc("container_drives", arrParams)
		for strKeyDrive in objDrive:
			objDrive[strKeyDrive] = Deserializer.deserialize(objDrive[strKeyDrive])
		return objDrive

	def container_array_shared_drives(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		return self.rpc("container_array_shared_drives", arrParams)


	def server_dhcp_status_update(self, nServerID, strServerDHCPStatus):

		arrParams = [
			nServerID,
			strServerDHCPStatus,
		]

		return self.rpc("server_dhcp_status_update", arrParams)


	def cluster_app(self, strClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 10):

		arrParams = [
			strClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("cluster_app", arrParams))

	def container_array_drive_arrays(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		objDriveArray = self.rpc("container_array_drive_arrays", arrParams)
		for strKeyDriveArray in objDriveArray:
			objDriveArray[strKeyDriveArray] = Deserializer.deserialize(objDriveArray[strKeyDriveArray])
		return objDriveArray

	def container_cluster_app(self, strContainerClusterID, bAccessSaaSAPI = True, nAccessSaaSAPITimeoutSeconds = 10):

		arrParams = [
			strContainerClusterID,
			bAccessSaaSAPI,
			nAccessSaaSAPITimeoutSeconds,
		]

		return Deserializer.deserialize(self.rpc("container_cluster_app", arrParams))

	def hdfs_cluster_app(self, strDatacenter = None):

		arrParams = [
			strDatacenter,
		]

		return Deserializer.deserialize(self.rpc("hdfs_cluster_app", arrParams))

	def storage_pool_drive_priority_set(self, nStoragePoolID, nStoragePoolDrivePriority):

		arrParams = [
			nStoragePoolID,
			nStoragePoolDrivePriority,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_drive_priority_set", arrParams))

	def storage_pool_shared_drive_priority_set(self, nStoragePoolID, nStoragePoolSharedDrivePriority):

		arrParams = [
			nStoragePoolID,
			nStoragePoolSharedDrivePriority,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_shared_drive_priority_set", arrParams))

	def license_reactivate(self, nLicenseID):

		arrParams = [
			nLicenseID,
		]

		return self.rpc("license_reactivate", arrParams)


	def server_decomission(self, nServerID, bSkipIPMI = True):

		arrParams = [
			nServerID,
			bSkipIPMI,
		]

		self.rpc("server_decomission", arrParams)


	def drive_attach_container(self, strDriveID, strContainerID):

		arrParams = [
			strDriveID,
			strContainerID,
		]

		return Deserializer.deserialize(self.rpc("drive_attach_container", arrParams))

	def drive_detach_container(self, strDriveID):

		arrParams = [
			strDriveID,
		]

		return Deserializer.deserialize(self.rpc("drive_detach_container", arrParams))

	def cluster_internal_admin_credentials_get(self, nClusterID = None):

		arrParams = [
			nClusterID,
		]

		return self.rpc("cluster_internal_admin_credentials_get", arrParams)


	def container_platform_information_internal(self, nContainerPlatformID):

		arrParams = [
			nContainerPlatformID,
		]

		return self.rpc("container_platform_information_internal", arrParams)


	def infrastructure_deploy_changes(self, nInfrastructureDeployID):

		arrParams = [
			nInfrastructureDeployID,
		]

		return self.rpc("infrastructure_deploy_changes", arrParams)


	def license_vendor_report_xls_download_url(self, strLicenseType, strStartTimestamp, strEndTimestamp, objLicenseFilter = None):

		arrParams = [
			strLicenseType,
			strStartTimestamp,
			strEndTimestamp,
			objLicenseFilter,
		]

		return self.rpc("license_vendor_report_xls_download_url", arrParams)


	def datacenter_get(self, strUserID, strDatacenterName):

		arrParams = [
			strUserID,
			strDatacenterName,
		]

		return Deserializer.deserialize(self.rpc("datacenter_get", arrParams))

	def datacenter_names_internal(self, bIncludeMaster = False):

		arrParams = [
			bIncludeMaster,
		]

		return self.rpc("datacenter_names_internal", arrParams)


	def license_types_for_volume_template(self, strVolumeTemplateID):

		arrParams = [
			strVolumeTemplateID,
		]

		return self.rpc("license_types_for_volume_template", arrParams)


	def support_ticket_options(self, strUserLanguage):

		arrParams = [
			strUserLanguage,
		]

		return self.rpc("support_ticket_options", arrParams)


	def datacenter_config(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("datacenter_config", arrParams)


	def user_set_brand(self, nUserID, strUserBrand):

		arrParams = [
			nUserID,
			strUserBrand,
		]

		return self.rpc("user_set_brand", arrParams)


	def user_set_is_brand_manager(self, nUserID, bUserIsBrandManager):

		arrParams = [
			nUserID,
			bUserIsBrandManager,
		]

		return self.rpc("user_set_is_brand_manager", arrParams)


	def user_get_brand(self, nUserID):

		arrParams = [
			nUserID,
		]

		return self.rpc("user_get_brand", arrParams)


	def datacenter_config_update(self, strDatacenterName, objDatacenterConfig):

		objDatacenterConfig = Serializer.serialize(objDatacenterConfig)

		arrParams = [
			strDatacenterName,
			objDatacenterConfig,
		]

		self.rpc("datacenter_config_update", arrParams)


	def cloudinit_json_get_url_generation(self, nDriveID):

		arrParams = [
			nDriveID,
		]

		return self.rpc("cloudinit_json_get_url_generation", arrParams)


	def cloudinit_json_get_server_url_generation(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("cloudinit_json_get_server_url_generation", arrParams)


	def cloudinit_json_get_instance_url_generation(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("cloudinit_json_get_instance_url_generation", arrParams)


	def container_status(self, strContainerID):

		arrParams = [
			strContainerID,
		]

		return Deserializer.deserialize(self.rpc("container_status", arrParams))

	def container_array_status(self, strContainerArrayID):

		arrParams = [
			strContainerArrayID,
		]

		return Deserializer.deserialize(self.rpc("container_array_status", arrParams))

	def ip_custom_reverse_records(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("ip_custom_reverse_records", arrParams)


	def ip_custom_reverse_record_remove(self, strInfrastructureID, strIPAddress):

		arrParams = [
			strInfrastructureID,
			strIPAddress,
		]

		self.rpc("ip_custom_reverse_record_remove", arrParams)


	def ip_custom_reverse_record_add(self, strInfrastructureID, strIPAddress, strSubdomainName, strRootDomain):

		arrParams = [
			strInfrastructureID,
			strIPAddress,
			strSubdomainName,
			strRootDomain,
		]

		self.rpc("ip_custom_reverse_record_add", arrParams)


	def instance_agent_bonding_configure(self, nInstanceID, strBondName, arrVLANConfigurations):

		arrParams = [
			nInstanceID,
			strBondName,
			arrVLANConfigurations,
		]

		return self.rpc("instance_agent_bonding_configure", arrParams)


	def instance_agent_vlan_add(self, nInstanceID, objVLANConfig):

		objVLANConfig = Serializer.serialize(objVLANConfig)

		arrParams = [
			nInstanceID,
			objVLANConfig,
		]

		return self.rpc("instance_agent_vlan_add", arrParams)


	def instance_agent_vlan_remove(self, nInstanceID, strVLANName, strBondName):

		arrParams = [
			nInstanceID,
			strVLANName,
			strBondName,
		]

		return self.rpc("instance_agent_vlan_remove", arrParams)


	def instance_agent_network_interface_enable(self, nInstanceID, strNetworkInterface):

		arrParams = [
			nInstanceID,
			strNetworkInterface,
		]

		return self.rpc("instance_agent_network_interface_enable", arrParams)


	def instance_agent_network_interface_disable(self, nInstanceID, strNetworkInterface):

		arrParams = [
			nInstanceID,
			strNetworkInterface,
		]

		return self.rpc("instance_agent_network_interface_disable", arrParams)


	def subnet_reservation_billing_day_change(self, nSubnetReservationID, nBillingDay):

		arrParams = [
			nSubnetReservationID,
			nBillingDay,
		]

		self.rpc("subnet_reservation_billing_day_change", arrParams)


	def subnet_reservation_billing_day_change_all_active(self, nBillingDay):

		arrParams = [
			nBillingDay,
		]

		self.rpc("subnet_reservation_billing_day_change_all_active", arrParams)


	def server_type_reservation_billing_day_change(self, nServerTypeReservationID, nBillingDay):

		arrParams = [
			nServerTypeReservationID,
			nBillingDay,
		]

		self.rpc("server_type_reservation_billing_day_change", arrParams)


	def server_type_reservation_billing_day_change_all_active(self, nBillingDay):

		arrParams = [
			nBillingDay,
		]

		self.rpc("server_type_reservation_billing_day_change_all_active", arrParams)


	def volume_template_deprecation_status_edit(self, nVolumeTemplateID, strVolumeTemplateDeprecationStatus):

		arrParams = [
			nVolumeTemplateID,
			strVolumeTemplateDeprecationStatus,
		]

		self.rpc("volume_template_deprecation_status_edit", arrParams)


	def drive_reservation_billing_day_change(self, nDriveReservationID, nBillingDay):

		arrParams = [
			nDriveReservationID,
			nBillingDay,
		]

		self.rpc("drive_reservation_billing_day_change", arrParams)


	def drive_reservation_billing_day_change_all_active(self, nBillingDay):

		arrParams = [
			nBillingDay,
		]

		self.rpc("drive_reservation_billing_day_change_all_active", arrParams)


	def email_send_custom_batch(self, strEmailsTableName, strLanguageCode, strSubject, strHTMLBodyCustomPart, nAtLeastSentCounter = 0):

		arrParams = [
			strEmailsTableName,
			strLanguageCode,
			strSubject,
			strHTMLBodyCustomPart,
			nAtLeastSentCounter,
		]

		return self.rpc("email_send_custom_batch", arrParams)


	def server_current_boot_type_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_current_boot_type_get", arrParams)


	def dataset_create(self, strUserID, nTemporaryUploadID, objDataset):

		objDataset = Serializer.serialize(objDataset)

		arrParams = [
			strUserID,
			nTemporaryUploadID,
			objDataset,
		]

		return Deserializer.deserialize(self.rpc("dataset_create", arrParams))

	def dataset_publish(self, nDatasetID):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_publish", arrParams)


	def dataset_unpublish(self, nDatasetID):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_unpublish", arrParams)


	def dataset_edit(self, nDatasetID, nTemporaryUploadID, objChangedDataset):

		objChangedDataset = Serializer.serialize(objChangedDataset)

		arrParams = [
			nDatasetID,
			nTemporaryUploadID,
			objChangedDataset,
		]

		return self.rpc("dataset_edit", arrParams)


	def dataset_datapackage_get(self, nDatasetID):

		arrParams = [
			nDatasetID,
		]

		return Deserializer.deserialize(self.rpc("dataset_datapackage_get", arrParams))

	def dataset_get(self, publishedDatasetID):

		arrParams = [
			publishedDatasetID,
		]

		return Deserializer.deserialize(self.rpc("dataset_get", arrParams))

	def dataset_delete(self, nDatasetID):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_delete", arrParams)


	def datacenter_datasets(self, strDatacenterLabel):

		arrParams = [
			strDatacenterLabel,
		]

		arrDatasets = self.rpc("datacenter_datasets", arrParams)
		for index in range(len(arrDatasets)):
			arrDatasets[index] = Deserializer.deserialize(arrDatasets[index])
		return arrDatasets

	def user_datasets_managed(self, strUserIDOwner):

		arrParams = [
			strUserIDOwner,
		]

		return self.rpc("user_datasets_managed", arrParams)


	def dataset_subscription_create(self, strUserIDOwner, datasetID):

		arrParams = [
			strUserIDOwner,
			datasetID,
		]

		return Deserializer.deserialize(self.rpc("dataset_subscription_create", arrParams))

	def dataset_subscription_delete(self, strUserIDOwner, nDatasetSubscriptionID):

		arrParams = [
			strUserIDOwner,
			nDatasetSubscriptionID,
		]

		self.rpc("dataset_subscription_delete", arrParams)


	def user_dataset_subscriptions(self, strUserIDOwner):

		arrParams = [
			strUserIDOwner,
		]

		arrDatasetSubscriptions = self.rpc("user_dataset_subscriptions", arrParams)
		for index in range(len(arrDatasetSubscriptions)):
			arrDatasetSubscriptions[index] = Deserializer.deserialize(arrDatasetSubscriptions[index])
		return arrDatasetSubscriptions

	def datastore_publishers(self):

		arrParams = [
		]

		self.rpc("datastore_publishers", arrParams)


	def datastore_publisher_create(self, nPublisherUserID):

		arrParams = [
			nPublisherUserID,
		]

		self.rpc("datastore_publisher_create", arrParams)


	def datastore_publisher_get(self, nPublisherUserID):

		arrParams = [
			nPublisherUserID,
		]

		self.rpc("datastore_publisher_get", arrParams)


	def datastore_publisher_delete(self, nDatastorePublisherID):

		arrParams = [
			nDatastorePublisherID,
		]

		self.rpc("datastore_publisher_delete", arrParams)


	def instance_agent_self_reset(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_agent_self_reset", arrParams)


	def instance_agent_persistent_logging_enable(self, nInstanceID, bEnabled):

		arrParams = [
			nInstanceID,
			bEnabled,
		]

		return self.rpc("instance_agent_persistent_logging_enable", arrParams)


	def cloudinit_json_get_for_drive(self, nDriveID):

		arrParams = [
			nDriveID,
		]

		return self.rpc("cloudinit_json_get_for_drive", arrParams)


	def cloudinit_json_get_for_server(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("cloudinit_json_get_for_server", arrParams)


	def cloudinit_json_get_for_instance(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("cloudinit_json_get_for_instance", arrParams)


	def infrastructure_agent_allowed_set(self, nInfrastructureID, bIsAllowed):

		arrParams = [
			nInfrastructureID,
			bIsAllowed,
		]

		self.rpc("infrastructure_agent_allowed_set", arrParams)


	def dhcp_ipxe_batch(self, nServerID, bDebugMode = False):

		arrParams = [
			nServerID,
			bDebugMode,
		]

		return self.rpc("dhcp_ipxe_batch", arrParams)


	def production_config_secret_public_key(self, strProductionPrivateKeyVersion = None):

		arrParams = [
			strProductionPrivateKeyVersion,
		]

		return self.rpc("production_config_secret_public_key", arrParams)


	def production_config_secret_private_key_version(self):

		arrParams = [
		]

		return self.rpc("production_config_secret_private_key_version", arrParams)


	def password_decrypt(self, strCipher):

		arrParams = [
			strCipher,
		]

		return self.rpc("password_decrypt", arrParams)


	def dhcp_regenerate(self, arrServerIDs, arrNetworkEquipmentIDs, bRegeneratedCloudInit, bRegenerateIPXE, arrDatacenterNames, bDestroyTrdb = False):

		arrParams = [
			arrServerIDs,
			arrNetworkEquipmentIDs,
			bRegeneratedCloudInit,
			bRegenerateIPXE,
			arrDatacenterNames,
			bDestroyTrdb,
		]

		self.rpc("dhcp_regenerate", arrParams)


	def switch_device_update(self, nNetworkEquipmentID, objNetworkEquipmentData, bOverwriteWithHostnameFromFetchedSwitch):

		objNetworkEquipmentData = Serializer.serialize(objNetworkEquipmentData)

		arrParams = [
			nNetworkEquipmentID,
			objNetworkEquipmentData,
			bOverwriteWithHostnameFromFetchedSwitch,
		]

		return self.rpc("switch_device_update", arrParams)


	def instance_agent_iscsi_setup_and_login(self, nInstanceID, arrNodeInformation):

		arrParams = [
			nInstanceID,
			arrNodeInformation,
		]

		return self.rpc("instance_agent_iscsi_setup_and_login", arrParams)


	def datacenter_agents_config_json_download_url(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("datacenter_agents_config_json_download_url", arrParams)


	def datacenter_keys_rotate_new(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		self.rpc("datacenter_keys_rotate_new", arrParams)


	def datacenter_keys_destroy_index_with_possible_data_loss(self, strDatacenterName, strKeyIndexToDestroy):

		arrParams = [
			strDatacenterName,
			strKeyIndexToDestroy,
		]

		self.rpc("datacenter_keys_destroy_index_with_possible_data_loss", arrParams)


	def datacenter_keys_compromised_flag_set(self, strDatacenterName, strCompromisedKeyIndex, bCompromised = True):

		arrParams = [
			strDatacenterName,
			strCompromisedKeyIndex,
			bCompromised,
		]

		self.rpc("datacenter_keys_compromised_flag_set", arrParams)


	def afc_group_get(self, nAFCGroupID):

		arrParams = [
			nAFCGroupID,
		]

		return self.rpc("afc_group_get", arrParams)


	def afc_groups(self, arrTypes = [], objContext = [], strCreatedTimestamp = None, strFinishedTimestamp = None):

		objContext = Serializer.serialize(objContext)

		arrParams = [
			arrTypes,
			objContext,
			strCreatedTimestamp,
			strFinishedTimestamp,
		]

		return self.rpc("afc_groups", arrParams)


	def afc_group_entries(self, nAFCGroupID):

		arrParams = [
			nAFCGroupID,
		]

		return self.rpc("afc_group_entries", arrParams)


	def afc_groups_archive_finished(self, nLimitOverride = None):

		arrParams = [
			nLimitOverride,
		]

		self.rpc("afc_groups_archive_finished", arrParams)


	def dhcpserver_agent_rules_updated(self, nAgentID, bInvalidateEntireConfig = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireConfig,
		]

		self.rpc("dhcpserver_agent_rules_updated", arrParams)


	def server_type_allowed_vendor_sku_ids(self, nServerTypeID):

		arrParams = [
			nServerTypeID,
		]

		return self.rpc("server_type_allowed_vendor_sku_ids", arrParams)


	def server_type_allowed_vendor_sku_id_has(self, nServerTypeID, strServerVendorSKUID):

		arrParams = [
			nServerTypeID,
			strServerVendorSKUID,
		]

		return self.rpc("server_type_allowed_vendor_sku_id_has", arrParams)


	def server_type_allowed_vendor_sku_id_add(self, nServerTypeID, strServerVendorSKUID):

		arrParams = [
			nServerTypeID,
			strServerVendorSKUID,
		]

		return self.rpc("server_type_allowed_vendor_sku_id_add", arrParams)


	def server_type_allowed_vendor_sku_id_remove(self, nServerTypeID, strServerVendorSKUID):

		arrParams = [
			nServerTypeID,
			strServerVendorSKUID,
		]

		self.rpc("server_type_allowed_vendor_sku_id_remove", arrParams)


	def server_types_with_allowed_vendor_sku_id(self, strServerVendorSKUID):

		arrParams = [
			strServerVendorSKUID,
		]

		return self.rpc("server_types_with_allowed_vendor_sku_id", arrParams)


	def datacenter_agent_process_exit(self, nAgentID, strAgentType):

		arrParams = [
			nAgentID,
			strAgentType,
		]

		return self.rpc("datacenter_agent_process_exit", arrParams)


	def instance_windows_internal_management_credentials_get(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_windows_internal_management_credentials_get", arrParams)


	def server_oob_allow_ip(self, nServerID, strAllowedIP):

		arrParams = [
			nServerID,
			strAllowedIP,
		]

		self.rpc("server_oob_allow_ip", arrParams)


	def server_oob_disallow_ip(self, nServerID, strAllowedIP):

		arrParams = [
			nServerID,
			strAllowedIP,
		]

		self.rpc("server_oob_disallow_ip", arrParams)


	def server_oob_allowed_ips(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_oob_allowed_ips", arrParams)


	def server_instance_oob_allowed_ips(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("server_instance_oob_allowed_ips", arrParams)


	def server_instance_oob_allow_ip(self, strInstanceID, strAllowedIP):

		arrParams = [
			strInstanceID,
			strAllowedIP,
		]

		self.rpc("server_instance_oob_allow_ip", arrParams)


	def server_instance_oob_disallow_ip(self, strInstanceID, strDisallowedIP):

		arrParams = [
			strInstanceID,
			strDisallowedIP,
		]

		self.rpc("server_instance_oob_disallow_ip", arrParams)


	def firewall_reprovision_without_deploy(self, arrInstanceIDs = [], arrInstanceArrayIDs = [], arrInfrastructureIDs = [], strDatacenterName = None, bAllInstances = False, nMaxInstances = 10):

		arrParams = [
			arrInstanceIDs,
			arrInstanceArrayIDs,
			arrInfrastructureIDs,
			strDatacenterName,
			bAllInstances,
			nMaxInstances,
		]

		return self.rpc("firewall_reprovision_without_deploy", arrParams)


	def instance_array_force_unmanage_firewall(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return self.rpc("instance_array_force_unmanage_firewall", arrParams)


	def instance_agent_config_json_download_url(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_agent_config_json_download_url", arrParams)


	def instance_keys_rotate_new(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_keys_rotate_new", arrParams)


	def instance_keys_destroy_index_with_possible_data_loss(self, strInstanceID, strKeyIndexToDestroy):

		arrParams = [
			strInstanceID,
			strKeyIndexToDestroy,
		]

		self.rpc("instance_keys_destroy_index_with_possible_data_loss", arrParams)


	def instance_keys_compromised_flag_set(self, strInstanceID, strCompromisedKeyIndex, bCompromised = True):

		arrParams = [
			strInstanceID,
			strCompromisedKeyIndex,
			bCompromised,
		]

		self.rpc("instance_keys_compromised_flag_set", arrParams)


	def secure_gateway_add(self, strDomain, strVRRPIP, strDatacenterName, arrPeers, strSSLCrtPath, strSSLCAPath = None, arrReservedPorts = []):

		arrParams = [
			strDomain,
			strVRRPIP,
			strDatacenterName,
			arrPeers,
			strSSLCrtPath,
			strSSLCAPath,
			arrReservedPorts,
		]

		return Deserializer.deserialize(self.rpc("secure_gateway_add", arrParams))

	def instance_array_drive_arrays(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		objDriveArray = self.rpc("instance_array_drive_arrays", arrParams)
		for strKeyDriveArray in objDriveArray:
			objDriveArray[strKeyDriveArray] = Deserializer.deserialize(objDriveArray[strKeyDriveArray])
		return objDriveArray

	def afc_mark_for_death(self, nAFCID, strTypeOfMark):

		arrParams = [
			nAFCID,
			strTypeOfMark,
		]

		self.rpc("afc_mark_for_death", arrParams)


	def afc_get_process_info(self, nAFCID):

		arrParams = [
			nAFCID,
		]

		return self.rpc("afc_get_process_info", arrParams)


	def infrastructure_lan_subnet_pools_available(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_lan_subnet_pools_available", arrParams)


	def infrastructure_lan_subnet_prefix_sizes_available(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_lan_subnet_prefix_sizes_available", arrParams)


	def agent_version_build_and_upload(self, strRevision = "master", strRemoteRepositoryFolder = "releases"):

		arrParams = [
			strRevision,
			strRemoteRepositoryFolder,
		]

		self.rpc("agent_version_build_and_upload", arrParams)


	def agent_version_default_set(self, strVersion, strRemoteRepositoryFolder = "releases", strAgentGITRevisionToUseForPublishing = "d5dfad3908f42011b5f6ed2ac6bb70fd949c28ed"):

		arrParams = [
			strVersion,
			strRemoteRepositoryFolder,
			strAgentGITRevisionToUseForPublishing,
		]

		self.rpc("agent_version_default_set", arrParams)


	def dnsserver_agent_entries_updated(self, nAgentID, bInvalidateEntireConfig = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireConfig,
		]

		self.rpc("dnsserver_agent_entries_updated", arrParams)


	def agents_counters(self, arrDatacentersFilter = []):

		arrParams = [
			arrDatacentersFilter,
		]

		return self.rpc("agents_counters", arrParams)


	def datacenter_agent_test(self, nAgentID, strAgentType, nSleepSeconds = 2):

		arrParams = [
			nAgentID,
			strAgentType,
			nSleepSeconds,
		]

		return self.rpc("datacenter_agent_test", arrParams)


	def dataset_readme_upload_url(self):

		arrParams = [
		]

		return self.rpc("dataset_readme_upload_url", arrParams)


	def dataset_readme_download_url(self, nPublicDatasetID):

		arrParams = [
			nPublicDatasetID,
		]

		return self.rpc("dataset_readme_download_url", arrParams)


	def server_oob_proxy_add(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_oob_proxy_add", arrParams)


	def server_dhcp_packet_sniffing_toggle(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_dhcp_packet_sniffing_toggle", arrParams)


	def server_dhcp_sniffed_packets(self, nServerID, strMACAddress):

		arrParams = [
			nServerID,
			strMACAddress,
		]

		return self.rpc("server_dhcp_sniffed_packets", arrParams)


	def infrastructure_agent_repo_folder_set(self, nInfrastructureID, strFolder):

		arrParams = [
			nInfrastructureID,
			strFolder,
		]

		self.rpc("infrastructure_agent_repo_folder_set", arrParams)


	def dataset_readme_delete(self, nDatasetID):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_readme_delete", arrParams)


	def infrastructure_empty_with_active_subnets_get(self, arrSubnetPoolTypes):

		arrParams = [
			arrSubnetPoolTypes,
		]

		objInfrastructure = self.rpc("infrastructure_empty_with_active_subnets_get", arrParams)
		for strKeyInfrastructure in objInfrastructure:
			objInfrastructure[strKeyInfrastructure] = Deserializer.deserialize(objInfrastructure[strKeyInfrastructure])
		return objInfrastructure

	def drive_array_filesystem_types_available(self):

		arrParams = [
		]

		return self.rpc("drive_array_filesystem_types_available", arrParams)


	def drive_array_block_sizes_available(self):

		arrParams = [
		]

		return self.rpc("drive_array_block_sizes_available", arrParams)


	def instance_agent_drive_partition(self, nInstanceID, arrDriveCredentials, arrPartitionTable):

		arrParams = [
			nInstanceID,
			arrDriveCredentials,
			arrPartitionTable,
		]

		return self.rpc("instance_agent_drive_partition", arrParams)


	def instance_agent_drive_partition_format(self, nInstanceID, arrDriveCredentials, nPartitionIndex, arrFilesystemInformation):

		arrParams = [
			nInstanceID,
			arrDriveCredentials,
			nPartitionIndex,
			arrFilesystemInformation,
		]

		return self.rpc("instance_agent_drive_partition_format", arrParams)


	def instance_agent_drive_partition_mount(self, nInstanceID, arrDriveCredentials, nPartitionIndex, arrFilesystemInformation, strMountPoint = None):

		arrParams = [
			nInstanceID,
			arrDriveCredentials,
			nPartitionIndex,
			arrFilesystemInformation,
			strMountPoint,
		]

		return self.rpc("instance_agent_drive_partition_mount", arrParams)


	def instance_agent_disk_partition_unmount(self, nInstanceID, strMountPoint):

		arrParams = [
			nInstanceID,
			strMountPoint,
		]

		return self.rpc("instance_agent_disk_partition_unmount", arrParams)


	def cluster_instance_arrays(self, strClusterID, arrInstanceArrayIDs = None):

		arrParams = [
			strClusterID,
			arrInstanceArrayIDs,
		]

		objInstanceArray = self.rpc("cluster_instance_arrays", arrParams)
		for strKeyInstanceArray in objInstanceArray:
			objInstanceArray[strKeyInstanceArray] = Deserializer.deserialize(objInstanceArray[strKeyInstanceArray])
		return objInstanceArray

	def container_cluster_container_arrays(self, strContainerClusterID, arrContainerArrayIDs = None):

		arrParams = [
			strContainerClusterID,
			arrContainerArrayIDs,
		]

		objContainerArray = self.rpc("container_cluster_container_arrays", arrParams)
		for strKeyContainerArray in objContainerArray:
			objContainerArray[strKeyContainerArray] = Deserializer.deserialize(objContainerArray[strKeyContainerArray])
		return objContainerArray

	def threshold_create(self, strUserIDOwner, objThreshold):

		objThreshold = Serializer.serialize(objThreshold)

		arrParams = [
			strUserIDOwner,
			objThreshold,
		]

		return Deserializer.deserialize(self.rpc("threshold_create", arrParams))

	def thresholds(self, strUserIDOwner):

		arrParams = [
			strUserIDOwner,
		]

		arrThresholds = self.rpc("thresholds", arrParams)
		for index in range(len(arrThresholds)):
			arrThresholds[index] = Deserializer.deserialize(arrThresholds[index])
		return arrThresholds

	def threshold_edit(self, nThresholdID, objThresholdOperation):

		objThresholdOperation = Serializer.serialize(objThresholdOperation)

		arrParams = [
			nThresholdID,
			objThresholdOperation,
		]

		return Deserializer.deserialize(self.rpc("threshold_edit", arrParams))

	def threshold_get(self, nThresholdID):

		arrParams = [
			nThresholdID,
		]

		return Deserializer.deserialize(self.rpc("threshold_get", arrParams))

	def threshold_delete(self, nThresholdID):

		arrParams = [
			nThresholdID,
		]

		self.rpc("threshold_delete", arrParams)


	def users_and_infrastructures_cleanup(self):

		arrParams = [
		]

		self.rpc("users_and_infrastructures_cleanup", arrParams)


	def instance_cloudinit_dhcp_status_set(self, nInstanceID, bEnabled):

		arrParams = [
			nInstanceID,
			bEnabled,
		]

		self.rpc("instance_cloudinit_dhcp_status_set", arrParams)


	def infrastructure_deploy_cleanup(self, nInfrastructureID, objShutdownOptions = None, objDeployOptions = None, bAllowDataLoss = False, bSkipAnsible = False):

		objShutdownOptions = Serializer.serialize(objShutdownOptions)
		objDeployOptions = Serializer.serialize(objDeployOptions)

		arrParams = [
			nInfrastructureID,
			objShutdownOptions,
			objDeployOptions,
			bAllowDataLoss,
			bSkipAnsible,
		]

		return self.rpc("infrastructure_deploy_cleanup", arrParams)


	def infrastructure_delete_cleanup(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		self.rpc("infrastructure_delete_cleanup", arrParams)


	def server_dhcp_relay_security_toggle(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_dhcp_relay_security_toggle", arrParams)


	def server_type_search(self, objServerTypeParams):

		objServerTypeParams = Serializer.serialize(objServerTypeParams)

		arrParams = [
			objServerTypeParams,
		]

		return self.rpc("server_type_search", arrParams)


	def dataset_subscriptions(self, nDatasetID):

		arrParams = [
			nDatasetID,
		]

		self.rpc("dataset_subscriptions", arrParams)


	def instance_label_is_available_assert(self, strUserIDOwner, strInstanceLabel):

		arrParams = [
			strUserIDOwner,
			strInstanceLabel,
		]

		self.rpc("instance_label_is_available_assert", arrParams)


	def independent_instance_create(self, strUserIDOwner, strLabel, strDatacenterName, strServerTypeID, arrFirewallRules = [], objIndependentInstanceBootDriveConfig = None, arrIndependentInstanceExtraDrivesConfig = None):

		arrFirewallRules = Serializer.serialize(arrFirewallRules)
		objIndependentInstanceBootDriveConfig = Serializer.serialize(objIndependentInstanceBootDriveConfig)
		arrIndependentInstanceExtraDrivesConfig = Serializer.serialize(arrIndependentInstanceExtraDrivesConfig)

		arrParams = [
			strUserIDOwner,
			strLabel,
			strDatacenterName,
			strServerTypeID,
			arrFirewallRules,
			objIndependentInstanceBootDriveConfig,
			arrIndependentInstanceExtraDrivesConfig,
		]

		return self.rpc("independent_instance_create", arrParams)


	def instance_rows(self, strUserID, arrInstanceIDs = None):

		arrParams = [
			strUserID,
			arrInstanceIDs,
		]

		return self.rpc("instance_rows", arrParams)


	def independent_instance_delete(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("independent_instance_delete", arrParams)


	def independent_instance_storage_expand(self, strInstanceID, nISCSIStorageSizeMBytes):

		arrParams = [
			strInstanceID,
			nISCSIStorageSizeMBytes,
		]

		return Deserializer.deserialize(self.rpc("independent_instance_storage_expand", arrParams))

	def server_dhcp_sniffed_packets_uuid(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_dhcp_sniffed_packets_uuid", arrParams)


	def switch_device_cache_clear(self, nSwitchID):

		arrParams = [
			nSwitchID,
		]

		self.rpc("switch_device_cache_clear", arrParams)


	def infrastructure_purge(self, nInfrastructureID):

		arrParams = [
			nInfrastructureID,
		]

		return self.rpc("infrastructure_purge", arrParams)


	def datacenter_agent_monitoring_network_traffic_pull_and_save(self):

		arrParams = [
		]

		self.rpc("datacenter_agent_monitoring_network_traffic_pull_and_save", arrParams)


	def subnet_traffic_data_points_get(self, nSubnetID, nStartUnixTimestamp, nLengthSeconds = None):

		arrParams = [
			nSubnetID,
			nStartUnixTimestamp,
			nLengthSeconds,
		]

		self.rpc("subnet_traffic_data_points_get", arrParams)


	def server_keys_compromised_flag_set(self, strServerID, strCompromisedKeyIndex, bCompromised = True):

		arrParams = [
			strServerID,
			strCompromisedKeyIndex,
			bCompromised,
		]

		self.rpc("server_keys_compromised_flag_set", arrParams)


	def server_agent_config_json_download_url(self, nServerID, strAgentVersion, strDatacenterName):

		arrParams = [
			nServerID,
			strAgentVersion,
			strDatacenterName,
		]

		return self.rpc("server_agent_config_json_download_url", arrParams)


	def server_keys_destroy_index_with_possible_data_loss(self, strServerID, strKeyIndexToDestroy):

		arrParams = [
			strServerID,
			strKeyIndexToDestroy,
		]

		self.rpc("server_keys_destroy_index_with_possible_data_loss", arrParams)


	def server_keys_rotate_new(self, strServerID):

		arrParams = [
			strServerID,
		]

		return self.rpc("server_keys_rotate_new", arrParams)


	def server_register(self, nServerID, nAFCGroupID, bServerInfoAvailable = False):

		arrParams = [
			nServerID,
			nAFCGroupID,
			bServerInfoAvailable,
		]

		self.rpc("server_register", arrParams)


	def bdk_agent_register_notify_bsi(self, strAgentVersion, objServer, nAgentIDExisting):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			strAgentVersion,
			objServer,
			nAgentIDExisting,
		]

		self.rpc("bdk_agent_register_notify_bsi", arrParams)


	def bdk_agent_server_info_collect(self, nServerID, nAgentID = None, bForceRegenerate = False):

		arrParams = [
			nServerID,
			nAgentID,
			bForceRegenerate,
		]

		return self.rpc("bdk_agent_server_info_collect", arrParams)


	def bdk_agent_server_cleanup(self, nServerID, objServer, arrServerInterfaces, objIPOOB, arrDNSServers, arrNTPServers):

		objServer = Serializer.serialize(objServer)
		objIPOOB = Serializer.serialize(objIPOOB)

		arrParams = [
			nServerID,
			objServer,
			arrServerInterfaces,
			objIPOOB,
			arrDNSServers,
			arrNTPServers,
		]

		return self.rpc("bdk_agent_server_cleanup", arrParams)


	def independent_instance_firewall_rules_update(self, strInstanceID, arrFirewallRules):

		arrFirewallRules = Serializer.serialize(arrFirewallRules)

		arrParams = [
			strInstanceID,
			arrFirewallRules,
		]

		return Deserializer.deserialize(self.rpc("independent_instance_firewall_rules_update", arrParams))

	def jwt_session_cookies_types_to_cookies_names(self):

		arrParams = [
		]

		return self.rpc("jwt_session_cookies_types_to_cookies_names", arrParams)


	def subnet_prefix_sizes_wan(self, strSubnetType):

		arrParams = [
			strSubnetType,
		]

		return self.rpc("subnet_prefix_sizes_wan", arrParams)


	def datacenter_agent_monitoring_database_get(self, strDatacenterName, strSubnetType, nSubnetID):

		arrParams = [
			strDatacenterName,
			strSubnetType,
			nSubnetID,
		]

		return self.rpc("datacenter_agent_monitoring_database_get", arrParams)


	def datacenter_agent_monitoring_database_persist(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		self.rpc("datacenter_agent_monitoring_database_persist", arrParams)


	def network_traffic_sflow_fail_warning(self):

		arrParams = [
		]

		self.rpc("network_traffic_sflow_fail_warning", arrParams)


	def server_preregister_agent_config_json_download_url(self, nPreregisterID, strAgentVersion, strDatacenterName):

		arrParams = [
			nPreregisterID,
			strAgentVersion,
			strDatacenterName,
		]

		return self.rpc("server_preregister_agent_config_json_download_url", arrParams)


	def server_agent_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_agent_get", arrParams)


	def server_create(self, objServer, bAutoGenerate):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			objServer,
			bAutoGenerate,
		]

		self.rpc("server_create", arrParams)


	def server_cleanup(self, nServerID, bServerInfoAvailable = False):

		arrParams = [
			nServerID,
			bServerInfoAvailable,
		]

		self.rpc("server_cleanup", arrParams)


	def bdk_agent_preregister_install_batch(self, strOSName, strDatacenterName, nPreregisterID = None):

		arrParams = [
			strOSName,
			strDatacenterName,
			nPreregisterID,
		]

		return self.rpc("bdk_agent_preregister_install_batch", arrParams)


	def bdk_agent_preregister_install_batch_download_url(self, strOSName, strDatacenterName, nPreregisterID = None):

		arrParams = [
			strOSName,
			strDatacenterName,
			nPreregisterID,
		]

		return self.rpc("bdk_agent_preregister_install_batch_download_url", arrParams)


	def bdk_agent_networking_intel_cleanup(self, nServerID, objServer):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			nServerID,
			objServer,
		]

		self.rpc("bdk_agent_networking_intel_cleanup", arrParams)


	def bdk_agent_server_interfaces_cleanup(self, nServerID, arrServerInterfaces):

		arrParams = [
			nServerID,
			arrServerInterfaces,
		]

		self.rpc("bdk_agent_server_interfaces_cleanup", arrParams)


	def bdk_agent_ipmi_users_and_networking_cleanup(self, nServerID, objServer, objIPOOB, arrDNSServers, arrNTPServers):

		objServer = Serializer.serialize(objServer)
		objIPOOB = Serializer.serialize(objIPOOB)

		arrParams = [
			nServerID,
			objServer,
			objIPOOB,
			arrDNSServers,
			arrNTPServers,
		]

		self.rpc("bdk_agent_ipmi_users_and_networking_cleanup", arrParams)


	def bdk_agent_efibootmgr_cleanup(self, nServerID, arrNICDetails):

		arrParams = [
			nServerID,
			arrNICDetails,
		]

		self.rpc("bdk_agent_efibootmgr_cleanup", arrParams)


	def bdk_agent_disks_cleanup(self, nServerID, objServer, bCleanOnlyBootloader = False):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			nServerID,
			objServer,
			bCleanOnlyBootloader,
		]

		self.rpc("bdk_agent_disks_cleanup", arrParams)


	def bdk_agent_hba_setup(self, nServerID, arrServerInterfaces, objInstance):

		objInstance = Serializer.serialize(objInstance)

		arrParams = [
			nServerID,
			arrServerInterfaces,
			objInstance,
		]

		self.rpc("bdk_agent_hba_setup", arrParams)


	def bdk_run_command_batch(self, nServerID, strCommand):

		arrParams = [
			nServerID,
			strCommand,
		]

		self.rpc("bdk_run_command_batch", arrParams)


	def subnet_prefix_sizes_wan_cluster_attached(self, strSubnetType):

		arrParams = [
			strSubnetType,
		]

		return self.rpc("subnet_prefix_sizes_wan_cluster_attached", arrParams)


	def bdk_agent_IPMI_setup(self, nServerID, arrConfig):

		arrParams = [
			nServerID,
			arrConfig,
		]

		return self.rpc("bdk_agent_IPMI_setup", arrParams)


	def afc_status_counters(self):

		arrParams = [
		]

		return self.rpc("afc_status_counters", arrParams)


	def datacenters_statistics(self):

		arrParams = [
		]

		return self.rpc("datacenters_statistics", arrParams)


	def server_secure_boot_set(self, nServerID, bSecureBoot):

		arrParams = [
			nServerID,
			bSecureBoot,
		]

		self.rpc("server_secure_boot_set", arrParams)


	def server_firmware_upgrade(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("server_firmware_upgrade", arrParams)


	def server_firmware_component_upgrade(self, nServerID, nServerComponentID, strServerComponentFirmwareNewVersion = None, strFirmwareBinaryUrl = None):

		arrParams = [
			nServerID,
			nServerComponentID,
			strServerComponentFirmwareNewVersion,
			strFirmwareBinaryUrl,
		]

		self.rpc("server_firmware_component_upgrade", arrParams)


	def server_update_ipmi_credentials(self, nServerID, strIPMIHostname, strIPMIUsername, strIPMIPassword, bUpdateInBMC = True):

		arrParams = [
			nServerID,
			strIPMIHostname,
			strIPMIUsername,
			strIPMIPassword,
			bUpdateInBMC,
		]

		self.rpc("server_update_ipmi_credentials", arrParams)


	def storage_pools_statistics(self, bIncludeStoragePoolsInMaintenance = False, bAllowExperimental = False, nMinimumSpace = 0):

		arrParams = [
			bIncludeStoragePoolsInMaintenance,
			bAllowExperimental,
			nMinimumSpace,
		]

		return self.rpc("storage_pools_statistics", arrParams)


	def switch_devices_statistics(self):

		arrParams = [
		]

		return self.rpc("switch_devices_statistics", arrParams)


	def datacenter_agent_listening_sockets(self, nAgentID, strAgentType):

		arrParams = [
			nAgentID,
			strAgentType,
		]

		return self.rpc("datacenter_agent_listening_sockets", arrParams)


	def prices_config_save(self, strJSONPrices):

		arrParams = [
			strJSONPrices,
		]

		self.rpc("prices_config_save", arrParams)


	def infrastructures_statistics(self):

		arrParams = [
		]

		return self.rpc("infrastructures_statistics", arrParams)


	def instance_array_interface_create(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return Deserializer.deserialize(self.rpc("instance_array_interface_create", arrParams))

	def infrastructure_ansible_inventory_get(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return self.rpc("infrastructure_ansible_inventory_get", arrParams)


	def subnet_pools_statistics(self):

		arrParams = [
		]

		return self.rpc("subnet_pools_statistics", arrParams)


	def infrastructure_ansible_bundles(self, strInfrastructureID, strAnsibleBundleType):

		arrParams = [
			strInfrastructureID,
			strAnsibleBundleType,
		]

		return self.rpc("infrastructure_ansible_bundles", arrParams)


	def infrastructure_ansible_bundle_add_into_runlevel(self, strInfrastructureID, nAnsibleBundleID, nRunLevel):

		arrParams = [
			strInfrastructureID,
			nAnsibleBundleID,
			nRunLevel,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_ansible_bundle_add_into_runlevel", arrParams))

	def infrastructure_ansible_bundle_move_into_runlevel(self, strInfrastructureID, nAnsibleBundleID, nSourceRunLevel, nDestinationRunLevel):

		arrParams = [
			strInfrastructureID,
			nAnsibleBundleID,
			nSourceRunLevel,
			nDestinationRunLevel,
		]

		self.rpc("infrastructure_ansible_bundle_move_into_runlevel", arrParams)


	def infrastructure_ansible_bundle_delete_from_runlevel(self, strInfrastructureID, nAnsibleBundleID, nRunLevel):

		arrParams = [
			strInfrastructureID,
			nAnsibleBundleID,
			nRunLevel,
		]

		self.rpc("infrastructure_ansible_bundle_delete_from_runlevel", arrParams)


	def ansible_bundles(self, strUserID):

		arrParams = [
			strUserID,
		]

		objAnsibleBundle = self.rpc("ansible_bundles", arrParams)
		for strKeyAnsibleBundle in objAnsibleBundle:
			objAnsibleBundle[strKeyAnsibleBundle] = Deserializer.deserialize(objAnsibleBundle[strKeyAnsibleBundle])
		return objAnsibleBundle

	def infrastructure_ansible_bundle_exec(self, strInfrastructureID, nInfrastructureAnsibleBundleID, objExtraAnsibleVariables = []):

		objExtraAnsibleVariables = Serializer.serialize(objExtraAnsibleVariables)

		arrParams = [
			strInfrastructureID,
			nInfrastructureAnsibleBundleID,
			objExtraAnsibleVariables,
		]

		return self.rpc("infrastructure_ansible_bundle_exec", arrParams)


	def ansible_bundle_get(self, nAnsibleBundleID):

		arrParams = [
			nAnsibleBundleID,
		]

		return Deserializer.deserialize(self.rpc("ansible_bundle_get", arrParams))

	def ansible_bundle_create(self, strUserID, objAnsibleBundle):

		objAnsibleBundle = Serializer.serialize(objAnsibleBundle)

		arrParams = [
			strUserID,
			objAnsibleBundle,
		]

		return Deserializer.deserialize(self.rpc("ansible_bundle_create", arrParams))

	def ansible_bundle_update(self, nAnsibleBundleID, objAnsibleBundle):

		objAnsibleBundle = Serializer.serialize(objAnsibleBundle)

		arrParams = [
			nAnsibleBundleID,
			objAnsibleBundle,
		]

		return Deserializer.deserialize(self.rpc("ansible_bundle_update", arrParams))

	def ansible_bundle_delete(self, nAnsibleBundleID):

		arrParams = [
			nAnsibleBundleID,
		]

		self.rpc("ansible_bundle_delete", arrParams)


	def secrets(self, strUserID, strUsage = None):

		arrParams = [
			strUserID,
			strUsage,
		]

		objSecret = self.rpc("secrets", arrParams)
		for strKeySecret in objSecret:
			objSecret[strKeySecret] = Deserializer.deserialize(objSecret[strKeySecret])
		return objSecret

	def secret_get(self, nSecretID):

		arrParams = [
			nSecretID,
		]

		return Deserializer.deserialize(self.rpc("secret_get", arrParams))

	def secret_create(self, strUserID, objSecret):

		objSecret = Serializer.serialize(objSecret)

		arrParams = [
			strUserID,
			objSecret,
		]

		return Deserializer.deserialize(self.rpc("secret_create", arrParams))

	def secret_update(self, nSecretID, objSecret):

		objSecret = Serializer.serialize(objSecret)

		arrParams = [
			nSecretID,
			objSecret,
		]

		return Deserializer.deserialize(self.rpc("secret_update", arrParams))

	def secret_delete(self, nSecretID):

		arrParams = [
			nSecretID,
		]

		self.rpc("secret_delete", arrParams)


	def instance_next_boot_config_clear(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		self.rpc("instance_next_boot_config_clear", arrParams)


	def instance_next_boot_config_set(self, nInstanceID, strInstanceReinstallRequiredJSON = "{}"):

		arrParams = [
			nInstanceID,
			strInstanceReinstallRequiredJSON,
		]

		self.rpc("instance_next_boot_config_set", arrParams)


	def instance_next_boot_config_is_set(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		self.rpc("instance_next_boot_config_is_set", arrParams)


	def instance_sdp_for_webrtc(self, strInstanceID, strPurpose, strJSONSDPOffer):

		arrParams = [
			strInstanceID,
			strPurpose,
			strJSONSDPOffer,
		]

		return self.rpc("instance_sdp_for_webrtc", arrParams)


	def instance_ice_for_webrtc_set(self, strInstanceID, strPurpose, strICECandidateJSON, strSSHClientID):

		arrParams = [
			strInstanceID,
			strPurpose,
			strICECandidateJSON,
			strSSHClientID,
		]

		self.rpc("instance_ice_for_webrtc_set", arrParams)


	def server_info_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_info_get", arrParams)


	def server_sdp_for_webrtc(self, nServerID, strPurpose, strJSONSDPOffer):

		arrParams = [
			nServerID,
			strPurpose,
			strJSONSDPOffer,
		]

		return self.rpc("server_sdp_for_webrtc", arrParams)


	def server_ice_for_webrtc_set(self, nServerID, strPurpose, strICECandidateJSON, strSSHClientID):

		arrParams = [
			nServerID,
			strPurpose,
			strICECandidateJSON,
			strSSHClientID,
		]

		self.rpc("server_ice_for_webrtc_set", arrParams)


	def server_raid_controller_disks_get(self, nServerID, strRAIDControllerName = "RAID.Integrated.1-1"):

		arrParams = [
			nServerID,
			strRAIDControllerName,
		]

		return self.rpc("server_raid_controller_disks_get", arrParams)


	def server_pxe_enabled_interfaces_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_pxe_enabled_interfaces_get", arrParams)


	def server_firmware_inventory_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_firmware_inventory_get", arrParams)


	def server_firmware_info_update(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_firmware_info_update", arrParams)


	def server_firmware_component_update_version_preset(self, nServerComponentID, strServerComponentNewVersion):

		arrParams = [
			nServerComponentID,
			strServerComponentNewVersion,
		]

		self.rpc("server_firmware_component_update_version_preset", arrParams)


	def server_component_get(self, nServerComponentID):

		arrParams = [
			nServerComponentID,
		]

		return self.rpc("server_component_get", arrParams)


	def storage_pool_sdp_for_webrtc(self, nStoragePoolID, strPurpose, strJSONSDPOffer):

		arrParams = [
			nStoragePoolID,
			strPurpose,
			strJSONSDPOffer,
		]

		return self.rpc("storage_pool_sdp_for_webrtc", arrParams)


	def storage_pool_ice_for_webrtc_set(self, nStoragePoolID, strPurpose, strICECandidateJSON, strSSHClientID):

		arrParams = [
			nStoragePoolID,
			strPurpose,
			strICECandidateJSON,
			strSSHClientID,
		]

		self.rpc("storage_pool_ice_for_webrtc_set", arrParams)


	def switch_device_san_subnet_pool_create(self, nNetworkEquipmentID):

		arrParams = [
			nNetworkEquipmentID,
		]

		self.rpc("switch_device_san_subnet_pool_create", arrParams)


	def switch_device_sdp_for_webrtc(self, nSwitchDeviceID, strPurpose, strJSONSDPOffer):

		arrParams = [
			nSwitchDeviceID,
			strPurpose,
			strJSONSDPOffer,
		]

		return self.rpc("switch_device_sdp_for_webrtc", arrParams)


	def switch_device_ice_for_webrtc_set(self, nSwitchDeviceID, strPurpose, strICECandidateJSON, strSSHClientID):

		arrParams = [
			nSwitchDeviceID,
			strPurpose,
			strICECandidateJSON,
			strSSHClientID,
		]

		self.rpc("switch_device_ice_for_webrtc_set", arrParams)


	def switch_device_provision(self, nSwitchDeviceID, nInfrastructureID = None, arrDirtyInstanceInterfaceIDs = [], arrDirtySwitchInterfaceIDs = [], bIgnoreDirtyBit = False, arrEnableSwitchInterfaceIDs = []):

		arrParams = [
			nSwitchDeviceID,
			nInfrastructureID,
			arrDirtyInstanceInterfaceIDs,
			arrDirtySwitchInterfaceIDs,
			bIgnoreDirtyBit,
			arrEnableSwitchInterfaceIDs,
		]

		return self.rpc("switch_device_provision", arrParams)


	def switch_device_provision_vpls_north(self, nSwitchDeviceID, nInfrastructureID = None):

		arrParams = [
			nSwitchDeviceID,
			nInfrastructureID,
		]

		return self.rpc("switch_device_provision_vpls_north", arrParams)


	def agent_delete(self, nAgentID):

		arrParams = [
			nAgentID,
		]

		self.rpc("agent_delete", arrParams)


	def secret_get_internal(self, nSecretID):

		arrParams = [
			nSecretID,
		]

		return Deserializer.deserialize(self.rpc("secret_get_internal", arrParams))

	def bdk_agent_server_general_info(self, nServerID, nAgentID = None, bForceRegenerate = False):

		arrParams = [
			nServerID,
			nAgentID,
			bForceRegenerate,
		]

		return self.rpc("bdk_agent_server_general_info", arrParams)


	def bdk_agent_server_cpu_info(self, nServerID, nAgentID = None, bForceRegenerate = False):

		arrParams = [
			nServerID,
			nAgentID,
			bForceRegenerate,
		]

		return self.rpc("bdk_agent_server_cpu_info", arrParams)


	def bdk_agent_server_bios_info(self, nServerID, nAgentID = None, bForceRegenerate = False):

		arrParams = [
			nServerID,
			nAgentID,
			bForceRegenerate,
		]

		return self.rpc("bdk_agent_server_bios_info", arrParams)


	def bdk_agent_server_disks_info(self, nServerID, nAgentID = None, bForceRegenerate = False):

		arrParams = [
			nServerID,
			nAgentID,
			bForceRegenerate,
		]

		return self.rpc("bdk_agent_server_disks_info", arrParams)


	def bdk_agent_server_memory_info(self, nServerID, nAgentID = None, bForceRegenerate = False):

		arrParams = [
			nServerID,
			nAgentID,
			bForceRegenerate,
		]

		return self.rpc("bdk_agent_server_memory_info", arrParams)


	def bdk_agent_server_network_info(self, nServerID, nAgentID = None, bForceRegenerate = False):

		arrParams = [
			nServerID,
			nAgentID,
			bForceRegenerate,
		]

		return self.rpc("bdk_agent_server_network_info", arrParams)


	def server_firmware_component_available_versions_update(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("server_firmware_component_available_versions_update", arrParams)


	def server_firmware_component_available_version_add(self, nServerComponentID, strVersion, strFirmwareBinaryURL):

		arrParams = [
			nServerComponentID,
			strVersion,
			strFirmwareBinaryURL,
		]

		self.rpc("server_firmware_component_available_version_add", arrParams)


	def server_firmware_component_target_version_set(self, nServerComponentID, strServerComponentFirmwareNewVersion):

		arrParams = [
			nServerComponentID,
			strServerComponentFirmwareNewVersion,
		]

		self.rpc("server_firmware_component_target_version_set", arrParams)


	def infrastructure_refresh_usage_stats(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_refresh_usage_stats", arrParams))

	def os_asset_create(self, strUserID, objOSAsset):

		objOSAsset = Serializer.serialize(objOSAsset)

		arrParams = [
			strUserID,
			objOSAsset,
		]

		return Deserializer.deserialize(self.rpc("os_asset_create", arrParams))

	def os_assets(self, strUserID, strUserIDOwner = None):

		arrParams = [
			strUserID,
			strUserIDOwner,
		]

		objOSAsset = self.rpc("os_assets", arrParams)
		for strKeyOSAsset in objOSAsset:
			objOSAsset[strKeyOSAsset] = Deserializer.deserialize(objOSAsset[strKeyOSAsset])
		return objOSAsset

	def os_asset_get(self, nOSAssetID):

		arrParams = [
			nOSAssetID,
		]

		return Deserializer.deserialize(self.rpc("os_asset_get", arrParams))

	def os_asset_update(self, nOSAssetID, objOSAsset):

		objOSAsset = Serializer.serialize(objOSAsset)

		arrParams = [
			nOSAssetID,
			objOSAsset,
		]

		return Deserializer.deserialize(self.rpc("os_asset_update", arrParams))

	def os_asset_delete(self, nOSAssetID):

		arrParams = [
			nOSAssetID,
		]

		self.rpc("os_asset_delete", arrParams)


	def os_asset_get_stored_content(self, nOSAssetID):

		arrParams = [
			nOSAssetID,
		]

		return self.rpc("os_asset_get_stored_content", arrParams)


	def os_template_os_assets(self, nOSTemplateID):

		arrParams = [
			nOSTemplateID,
		]

		return self.rpc("os_template_os_assets", arrParams)


	def os_template_create(self, strUserID, objOSTemplate):

		objOSTemplate = Serializer.serialize(objOSTemplate)

		arrParams = [
			strUserID,
			objOSTemplate,
		]

		return Deserializer.deserialize(self.rpc("os_template_create", arrParams))

	def os_templates(self, strUserID):

		arrParams = [
			strUserID,
		]

		objVolumeTemplate = self.rpc("os_templates", arrParams)
		for strKeyVolumeTemplate in objVolumeTemplate:
			objVolumeTemplate[strKeyVolumeTemplate] = Deserializer.deserialize(objVolumeTemplate[strKeyVolumeTemplate])
		return objVolumeTemplate

	def os_template_get(self, nOSTemplateID):

		arrParams = [
			nOSTemplateID,
		]

		return Deserializer.deserialize(self.rpc("os_template_get", arrParams))

	def os_template_update(self, nOSTemplateID, objOSTemplate):

		objOSTemplate = Serializer.serialize(objOSTemplate)

		arrParams = [
			nOSTemplateID,
			objOSTemplate,
		]

		return Deserializer.deserialize(self.rpc("os_template_update", arrParams))

	def os_template_delete(self, nOSTemplateID):

		arrParams = [
			nOSTemplateID,
		]

		self.rpc("os_template_delete", arrParams)


	def server_tags_add(self, nServerID, arrServerTagsNames):

		arrParams = [
			nServerID,
			arrServerTagsNames,
		]

		return Deserializer.deserialize(self.rpc("server_tags_add", arrParams))

	def infrastructure_tags_add(self, strInfrastructureID, arrInfrastructureTagsNames):

		arrParams = [
			strInfrastructureID,
			arrInfrastructureTagsNames,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_tags_add", arrParams))

	def infrastructure_tags_set(self, strInfrastructureID, arrInfrastructureTagsNames):

		arrParams = [
			strInfrastructureID,
			arrInfrastructureTagsNames,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_tags_set", arrParams))

	def infrastructure_tags(self, strInfrastructureID):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("infrastructure_tags", arrParams)


	def infrastructure_tags_remove(self, strInfrastructureID, arrInfrastructureTagsNames):

		arrParams = [
			strInfrastructureID,
			arrInfrastructureTagsNames,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_tags_remove", arrParams))

	def instance_tags_add(self, strInstanceID, arrInstanceTagsNames):

		arrParams = [
			strInstanceID,
			arrInstanceTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_tags_add", arrParams))

	def instance_tags_set(self, strInstanceID, arrInstanceTagsNames):

		arrParams = [
			strInstanceID,
			arrInstanceTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_tags_set", arrParams))

	def instance_tags(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("instance_tags", arrParams)


	def instance_tags_remove(self, strInstanceID, arrInstanceTagsNames):

		arrParams = [
			strInstanceID,
			arrInstanceTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_tags_remove", arrParams))

	def instance_array_tags_add(self, strInstanceArrayID, arrInstanceArrayTagsNames):

		arrParams = [
			strInstanceArrayID,
			arrInstanceArrayTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_array_tags_add", arrParams))

	def instance_array_tags_set(self, strInstanceArrayID, arrInstanceArrayTagsNames):

		arrParams = [
			strInstanceArrayID,
			arrInstanceArrayTagsNames,
		]

		return Deserializer.deserialize(self.rpc("instance_array_tags_set", arrParams))

	def instance_array_tags(self, strInstanceArrayID):

		arrParams = [
			strInstanceArrayID,
		]

		return self.rpc("instance_array_tags", arrParams)


	def instance_array_tags_remove(self, strInstanceArrayID, arrInstanceArrayTags):

		arrParams = [
			strInstanceArrayID,
			arrInstanceArrayTags,
		]

		return Deserializer.deserialize(self.rpc("instance_array_tags_remove", arrParams))

	def os_template_tags_add(self, strVolumeTemplateID, arrOSTemplateTagsNames):

		arrParams = [
			strVolumeTemplateID,
			arrOSTemplateTagsNames,
		]

		return self.rpc("os_template_tags_add", arrParams)


	def os_template_tags_set(self, strVolumeTemplateID, arrOSTemplateTagsNames):

		arrParams = [
			strVolumeTemplateID,
			arrOSTemplateTagsNames,
		]

		return self.rpc("os_template_tags_set", arrParams)


	def os_template_tags(self, strVolumeTemplateID):

		arrParams = [
			strVolumeTemplateID,
		]

		return self.rpc("os_template_tags", arrParams)


	def os_template_tags_remove(self, strVolumeTemplateID, arrOSTemplateTagsNames):

		arrParams = [
			strVolumeTemplateID,
			arrOSTemplateTagsNames,
		]

		return self.rpc("os_template_tags_remove", arrParams)


	def datacenter_tags_add(self, strDatacenterName, arrDatacenterTagsNames):

		arrParams = [
			strDatacenterName,
			arrDatacenterTagsNames,
		]

		return Deserializer.deserialize(self.rpc("datacenter_tags_add", arrParams))

	def datacenter_tags_set(self, strDatacenterName, arrDatacenterTagsNames):

		arrParams = [
			strDatacenterName,
			arrDatacenterTagsNames,
		]

		return Deserializer.deserialize(self.rpc("datacenter_tags_set", arrParams))

	def datacenter_tags(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		return self.rpc("datacenter_tags", arrParams)


	def datacenter_tags_remove(self, strDatacenterName, arrDatacenterTagsNames):

		arrParams = [
			strDatacenterName,
			arrDatacenterTagsNames,
		]

		return Deserializer.deserialize(self.rpc("datacenter_tags_remove", arrParams))

	def server_type_tags_add(self, strServerTypeID, arrServerTypeTagsNames):

		arrParams = [
			strServerTypeID,
			arrServerTypeTagsNames,
		]

		return Deserializer.deserialize(self.rpc("server_type_tags_add", arrParams))

	def server_type_tags_set(self, strServerTypeID, arrServerTypeTagsNames):

		arrParams = [
			strServerTypeID,
			arrServerTypeTagsNames,
		]

		return Deserializer.deserialize(self.rpc("server_type_tags_set", arrParams))

	def server_type_tags(self, strServerTypeID):

		arrParams = [
			strServerTypeID,
		]

		return self.rpc("server_type_tags", arrParams)


	def server_type_tags_remove(self, strServerTypeID, arrServerTypeTagsNames):

		arrParams = [
			strServerTypeID,
			arrServerTypeTagsNames,
		]

		return Deserializer.deserialize(self.rpc("server_type_tags_remove", arrParams))

	def server_tags_set(self, nServerID, arrServerTagsNames):

		arrParams = [
			nServerID,
			arrServerTagsNames,
		]

		return Deserializer.deserialize(self.rpc("server_tags_set", arrParams))

	def server_tags(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_tags", arrParams)


	def server_tags_remove(self, nServerID, arrServerTagsNames):

		arrParams = [
			nServerID,
			arrServerTagsNames,
		]

		return Deserializer.deserialize(self.rpc("server_tags_remove", arrParams))

	def storage_pool_tags_add(self, nStoragePoolID, arrStoragePoolTagsNames):

		arrParams = [
			nStoragePoolID,
			arrStoragePoolTagsNames,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_tags_add", arrParams))

	def storage_pool_tags_set(self, nStoragePoolID, arrStoragePoolTagsNames):

		arrParams = [
			nStoragePoolID,
			arrStoragePoolTagsNames,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_tags_set", arrParams))

	def storage_pool_tags(self, nStoragePoolID):

		arrParams = [
			nStoragePoolID,
		]

		return self.rpc("storage_pool_tags", arrParams)


	def storage_pool_tags_remove(self, nStoragePoolID, arrStoragePoolTagsNames):

		arrParams = [
			nStoragePoolID,
			arrStoragePoolTagsNames,
		]

		return Deserializer.deserialize(self.rpc("storage_pool_tags_remove", arrParams))

	def volume_template_tags_add(self, strVolumeTemplateID, arrVolumeTemplateTagsNames):

		arrParams = [
			strVolumeTemplateID,
			arrVolumeTemplateTagsNames,
		]

		return Deserializer.deserialize(self.rpc("volume_template_tags_add", arrParams))

	def volume_template_tags_set(self, strVolumeTemplateID, arrVolumeTemplateTagsNames):

		arrParams = [
			strVolumeTemplateID,
			arrVolumeTemplateTagsNames,
		]

		return Deserializer.deserialize(self.rpc("volume_template_tags_set", arrParams))

	def volume_template_tags(self, strVolumeTemplateID):

		arrParams = [
			strVolumeTemplateID,
		]

		return self.rpc("volume_template_tags", arrParams)


	def volume_template_tags_remove(self, strVolumeTemplateID, arrVolumeTemplateTagsNames):

		arrParams = [
			strVolumeTemplateID,
			arrVolumeTemplateTagsNames,
		]

		return Deserializer.deserialize(self.rpc("volume_template_tags_remove", arrParams))

	def switch_device_tags_add(self, nNetworkEquipmentID, arrNetworkEquipmentTagsNames):

		arrParams = [
			nNetworkEquipmentID,
			arrNetworkEquipmentTagsNames,
		]

		return Deserializer.deserialize(self.rpc("switch_device_tags_add", arrParams))

	def switch_device_tags_set(self, nNetworkEquipmentID, arrNetworkEquipmentTagsNames):

		arrParams = [
			nNetworkEquipmentID,
			arrNetworkEquipmentTagsNames,
		]

		return Deserializer.deserialize(self.rpc("switch_device_tags_set", arrParams))

	def switch_device_tags(self, nNetworkEquipmentID):

		arrParams = [
			nNetworkEquipmentID,
		]

		return self.rpc("switch_device_tags", arrParams)


	def switch_device_tags_remove(self, nNetworkEquipmentID, arrNetworkEquipmentTagsNames):

		arrParams = [
			nNetworkEquipmentID,
			arrNetworkEquipmentTagsNames,
		]

		return Deserializer.deserialize(self.rpc("switch_device_tags_remove", arrParams))

	def bdk_exec(self, nServerID, strCommand, nTimeoutSeconds, strTarXZBundleDecrypted, strBundleName, objEnvironmentVariables):

		objEnvironmentVariables = Serializer.serialize(objEnvironmentVariables)

		arrParams = [
			nServerID,
			strCommand,
			nTimeoutSeconds,
			strTarXZBundleDecrypted,
			strBundleName,
			objEnvironmentVariables,
		]

		self.rpc("bdk_exec", arrParams)


	def tftpserver_agent_dhcp_rules_updated(self, nAgentID, bInvalidateEntireConfig = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireConfig,
		]

		self.rpc("tftpserver_agent_dhcp_rules_updated", arrParams)


	def tftpserver_agent_os_templates_os_assets_updated(self, nAgentID, bInvalidateEntireConfig = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireConfig,
		]

		self.rpc("tftpserver_agent_os_templates_os_assets_updated", arrParams)


	def tftpserver_agent_os_assets_updated(self, nAgentID, bInvalidateEntireConfig = False, bWaitForDownload = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireConfig,
			bWaitForDownload,
		]

		self.rpc("tftpserver_agent_os_assets_updated", arrParams)


	def tftpserver_agent_secrets_updated(self, nAgentID, bInvalidateEntireConfig = False, bWaitForDownload = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireConfig,
			bWaitForDownload,
		]

		self.rpc("tftpserver_agent_secrets_updated", arrParams)


	def os_template_add_os_asset(self, nOSTemplateID, nOSAssetID, strOSAssetFilePath, strVolumeTemplateOSAssetVariablesJSON = None):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
			strOSAssetFilePath,
			strVolumeTemplateOSAssetVariablesJSON,
		]

		return self.rpc("os_template_add_os_asset", arrParams)


	def os_template_remove_os_asset(self, nOSTemplateID, nOSAssetID):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
		]

		self.rpc("os_template_remove_os_asset", arrParams)


	def os_template_update_os_asset_path(self, nOSTemplateID, nOSAssetID, strOSAssetFilePath):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
			strOSAssetFilePath,
		]

		self.rpc("os_template_update_os_asset_path", arrParams)


	def os_template_has_os_asset(self, nOSTemplateID, nOSAssetID):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
		]

		return self.rpc("os_template_has_os_asset", arrParams)


	def variables(self, strUserID, strUsage = None):

		arrParams = [
			strUserID,
			strUsage,
		]

		objVariable = self.rpc("variables", arrParams)
		for strKeyVariable in objVariable:
			objVariable[strKeyVariable] = Deserializer.deserialize(objVariable[strKeyVariable])
		return objVariable

	def variable_get(self, nVariableID):

		arrParams = [
			nVariableID,
		]

		return Deserializer.deserialize(self.rpc("variable_get", arrParams))

	def variable_create(self, strUserID, objVariable):

		objVariable = Serializer.serialize(objVariable)

		arrParams = [
			strUserID,
			objVariable,
		]

		return Deserializer.deserialize(self.rpc("variable_create", arrParams))

	def variable_update(self, nVariableID, objVariable):

		objVariable = Serializer.serialize(objVariable)

		arrParams = [
			nVariableID,
			objVariable,
		]

		return Deserializer.deserialize(self.rpc("variable_update", arrParams))

	def variable_delete(self, nVariableID):

		arrParams = [
			nVariableID,
		]

		self.rpc("variable_delete", arrParams)


	def variable_get_internal(self, nVariableID):

		arrParams = [
			nVariableID,
		]

		return Deserializer.deserialize(self.rpc("variable_get_internal", arrParams))

	def infrastructure_deploy_custom_stages(self, strInfrastructureID, strStageRunGroup):

		arrParams = [
			strInfrastructureID,
			strStageRunGroup,
		]

		arrInfrastructureDeployStageDefinitionReferences = self.rpc("infrastructure_deploy_custom_stages", arrParams)
		for index in range(len(arrInfrastructureDeployStageDefinitionReferences)):
			arrInfrastructureDeployStageDefinitionReferences[index] = Deserializer.deserialize(arrInfrastructureDeployStageDefinitionReferences[index])
		return arrInfrastructureDeployStageDefinitionReferences

	def infrastructure_deploy_custom_stage_add_into_runlevel(self, strInfrastructureID, nStageDefinitionID, nRunLevel, strStageRunGroup):

		arrParams = [
			strInfrastructureID,
			nStageDefinitionID,
			nRunLevel,
			strStageRunGroup,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy_custom_stage_add_into_runlevel", arrParams))

	def infrastructure_deploy_custom_stage_move_into_runlevel(self, nInfrastructureCustomDeployStageID, nDestinationRunLevel):

		arrParams = [
			nInfrastructureCustomDeployStageID,
			nDestinationRunLevel,
		]

		self.rpc("infrastructure_deploy_custom_stage_move_into_runlevel", arrParams)


	def infrastructure_deploy_custom_stage_delete_from_runlevel(self, strInfrastructureID, nStageDefinitionID, nRunLevel, strStageRunGroup):

		arrParams = [
			strInfrastructureID,
			nStageDefinitionID,
			nRunLevel,
			strStageRunGroup,
		]

		self.rpc("infrastructure_deploy_custom_stage_delete_from_runlevel", arrParams)


	def infrastructure_deploy_custom_stage_delete(self, nInfrastructureCustomDeployStageID):

		arrParams = [
			nInfrastructureCustomDeployStageID,
		]

		self.rpc("infrastructure_deploy_custom_stage_delete", arrParams)


	def stage_definitions(self, strUserID):

		arrParams = [
			strUserID,
		]

		objStageDefinition = self.rpc("stage_definitions", arrParams)
		for strKeyStageDefinition in objStageDefinition:
			objStageDefinition[strKeyStageDefinition] = Deserializer.deserialize(objStageDefinition[strKeyStageDefinition])
		return objStageDefinition

	def infrastructure_deploy_custom_stage_exec(self, strInfrastructureID, nInfrastructureCustomDeployStageID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strInfrastructureID,
			nInfrastructureCustomDeployStageID,
			objExtraVariables,
		]

		return self.rpc("infrastructure_deploy_custom_stage_exec", arrParams)


	def stage_definition_get(self, nStageDefinitionID):

		arrParams = [
			nStageDefinitionID,
		]

		return Deserializer.deserialize(self.rpc("stage_definition_get", arrParams))

	def stage_definition_create(self, strUserID, objStageDefinition):

		objStageDefinition = Serializer.serialize(objStageDefinition)

		arrParams = [
			strUserID,
			objStageDefinition,
		]

		return Deserializer.deserialize(self.rpc("stage_definition_create", arrParams))

	def stage_definition_update(self, nStageDefinitionID, objStageDefinition):

		objStageDefinition = Serializer.serialize(objStageDefinition)

		arrParams = [
			nStageDefinitionID,
			objStageDefinition,
		]

		return Deserializer.deserialize(self.rpc("stage_definition_update", arrParams))

	def stage_definition_delete(self, nStageDefinitionID):

		arrParams = [
			nStageDefinitionID,
		]

		self.rpc("stage_definition_delete", arrParams)


	def query_agent_for_metric_datapoints_multidc(self, strTarget, strFrom, strFormat = None, strUntil = None, bIncludeMetadata = False):

		arrParams = [
			strTarget,
			strFrom,
			strFormat,
			strUntil,
			bIncludeMetadata,
		]

		self.rpc("query_agent_for_metric_datapoints_multidc", arrParams)


	def os_asset_make_public(self, nOSAssetID):

		arrParams = [
			nOSAssetID,
		]

		return Deserializer.deserialize(self.rpc("os_asset_make_public", arrParams))

	def os_asset_make_private(self, nOSAssetID, strUserIDOwner):

		arrParams = [
			nOSAssetID,
			strUserIDOwner,
		]

		return Deserializer.deserialize(self.rpc("os_asset_make_private", arrParams))

	def os_template_make_public(self, nOSTemplateID):

		arrParams = [
			nOSTemplateID,
		]

		return Deserializer.deserialize(self.rpc("os_template_make_public", arrParams))

	def os_template_make_private(self, nOSTemplateID, strUserIDOwner):

		arrParams = [
			nOSTemplateID,
			strUserIDOwner,
		]

		return Deserializer.deserialize(self.rpc("os_template_make_private", arrParams))

	def stage_definitions_import(self):

		arrParams = [
		]

		self.rpc("stage_definitions_import", arrParams)


	def public_api_export_not_authorized_assert(self):

		arrParams = [
		]

		return self.rpc("public_api_export_not_authorized_assert", arrParams)


	def public_api_export_not_authorized_assert_with_params(self, strUnknownResourceTypeParam):

		arrParams = [
			strUnknownResourceTypeParam,
		]

		return self.rpc("public_api_export_not_authorized_assert_with_params", arrParams)


	def public_api_export_not_authorized_assert_with_nullable_param(self, strInfrastructureID = None):

		arrParams = [
			strInfrastructureID,
		]

		return self.rpc("public_api_export_not_authorized_assert_with_nullable_param", arrParams)


	def server_firmware_component_schedule_upgrade(self, nServerComponentID, strServerComponentFirmwareNewVersion = None, strScheduleUpdateTimestamp = None, bConfirmationRequired = False):

		arrParams = [
			nServerComponentID,
			strServerComponentFirmwareNewVersion,
			strScheduleUpdateTimestamp,
			bConfirmationRequired,
		]

		self.rpc("server_firmware_component_schedule_upgrade", arrParams)


	def server_firmware_policy_create(self, strPolicyLabel, strPolicyAction = None, arrRules = None):

		arrParams = [
			strPolicyLabel,
			strPolicyAction,
			arrRules,
		]

		return self.rpc("server_firmware_policy_create", arrParams)


	def server_firmware_policy_delete(self, nServerFirmwarePolicyID):

		arrParams = [
			nServerFirmwarePolicyID,
		]

		self.rpc("server_firmware_policy_delete", arrParams)


	def server_firmware_policy_get(self, nServerFirmwarePolicyID):

		arrParams = [
			nServerFirmwarePolicyID,
		]

		self.rpc("server_firmware_policy_get", arrParams)


	def server_firmware_policy_add_rule(self, nServerFirmwarePolicyID, objNewRule):

		objNewRule = Serializer.serialize(objNewRule)

		arrParams = [
			nServerFirmwarePolicyID,
			objNewRule,
		]

		self.rpc("server_firmware_policy_add_rule", arrParams)


	def server_firmware_policy_rule_delete(self, nServerFirmwarePolicyID, objRuleToDelete):

		objRuleToDelete = Serializer.serialize(objRuleToDelete)

		arrParams = [
			nServerFirmwarePolicyID,
			objRuleToDelete,
		]

		self.rpc("server_firmware_policy_rule_delete", arrParams)


	def agent_id_to_agent_type(self, nAgentID):

		arrParams = [
			nAgentID,
		]

		return self.rpc("agent_id_to_agent_type", arrParams)


	def server_firmware_policy_apply_all(self):

		arrParams = [
		]

		self.rpc("server_firmware_policy_apply_all", arrParams)


	def server_firmware_policy_matches_get(self, nServerFirmwarePolicyID):

		arrParams = [
			nServerFirmwarePolicyID,
		]

		return self.rpc("server_firmware_policy_matches_get", arrParams)


	def server_firmware_policy_action_set(self, nServerFirmwarePolicyID, strServerFirmwarePolicyAction):

		arrParams = [
			nServerFirmwarePolicyID,
			strServerFirmwarePolicyAction,
		]

		self.rpc("server_firmware_policy_action_set", arrParams)


	def server_firmware_batch_upgrade(self):

		arrParams = [
		]

		self.rpc("server_firmware_batch_upgrade", arrParams)


	def os_asset_tags_add(self, nOSAssetID, arrOSAssetTagsNames):

		arrParams = [
			nOSAssetID,
			arrOSAssetTagsNames,
		]

		return self.rpc("os_asset_tags_add", arrParams)


	def os_asset_tags_set(self, nOSAssetID, arrOSAssetTagsNames):

		arrParams = [
			nOSAssetID,
			arrOSAssetTagsNames,
		]

		return self.rpc("os_asset_tags_set", arrParams)


	def os_asset_tags(self, nOSAssetID):

		arrParams = [
			nOSAssetID,
		]

		return self.rpc("os_asset_tags", arrParams)


	def os_asset_tags_remove(self, nOSAssetID, arrOSAssetTagsNames):

		arrParams = [
			nOSAssetID,
			arrOSAssetTagsNames,
		]

		return self.rpc("os_asset_tags_remove", arrParams)


	def workflow_create(self, strUserID, objWorkflow):

		objWorkflow = Serializer.serialize(objWorkflow)

		arrParams = [
			strUserID,
			objWorkflow,
		]

		return Deserializer.deserialize(self.rpc("workflow_create", arrParams))

	def workflows(self, strUserID, strUsage = None, strUserIDOwner = None):

		arrParams = [
			strUserID,
			strUsage,
			strUserIDOwner,
		]

		objWorkflow = self.rpc("workflows", arrParams)
		for strKeyWorkflow in objWorkflow:
			objWorkflow[strKeyWorkflow] = Deserializer.deserialize(objWorkflow[strKeyWorkflow])
		return objWorkflow

	def workflow_get(self, strWorkflowID):

		arrParams = [
			strWorkflowID,
		]

		return Deserializer.deserialize(self.rpc("workflow_get", arrParams))

	def workflow_update(self, strWorkflowID, objWorkflow):

		objWorkflow = Serializer.serialize(objWorkflow)

		arrParams = [
			strWorkflowID,
			objWorkflow,
		]

		return Deserializer.deserialize(self.rpc("workflow_update", arrParams))

	def workflow_delete(self, strWorkflowID):

		arrParams = [
			strWorkflowID,
		]

		self.rpc("workflow_delete", arrParams)


	def workflow_exec_on_infrastructure(self, strWorkflowID, strInfrastructureID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strWorkflowID,
			strInfrastructureID,
			objExtraVariables,
		]

		self.rpc("workflow_exec_on_infrastructure", arrParams)


	def workflow_exec_on_instance(self, strWorkflowID, strInstanceID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strWorkflowID,
			strInstanceID,
			objExtraVariables,
		]

		self.rpc("workflow_exec_on_instance", arrParams)


	def infrastructure_workflow_stage_exec(self, strInfrastructureID, nWorkflowStageID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strInfrastructureID,
			nWorkflowStageID,
			objExtraVariables,
		]

		return self.rpc("infrastructure_workflow_stage_exec", arrParams)


	def stage_definition_exec_on_infrastructure(self, strStageDefinitionID, strInfrastructureID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strStageDefinitionID,
			strInfrastructureID,
			objExtraVariables,
		]

		return self.rpc("stage_definition_exec_on_infrastructure", arrParams)


	def stage_definition_exec_on_instance(self, strStageDefinitionID, strInstanceID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strStageDefinitionID,
			strInstanceID,
			objExtraVariables,
		]

		return self.rpc("stage_definition_exec_on_instance", arrParams)


	def server_firmware_policy_upgrade_config_get(self):

		arrParams = [
		]

		return self.rpc("server_firmware_policy_upgrade_config_get", arrParams)


	def server_firmware_policy_upgrade_config_set(self, objConfig):

		objConfig = Serializer.serialize(objConfig)

		arrParams = [
			objConfig,
		]

		self.rpc("server_firmware_policy_upgrade_config_set", arrParams)


	def workflow_exec_on_switch_device(self, strWorkflowID, nSwitchDeviceID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strWorkflowID,
			nSwitchDeviceID,
			objExtraVariables,
		]

		self.rpc("workflow_exec_on_switch_device", arrParams)


	def workflow_exec_on_server(self, strWorkflowID, nServerID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strWorkflowID,
			nServerID,
			objExtraVariables,
		]

		self.rpc("workflow_exec_on_server", arrParams)


	def workflow_exec_free_standing(self, strWorkflowID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strWorkflowID,
			objExtraVariables,
		]

		self.rpc("workflow_exec_free_standing", arrParams)


	def workflow_exec_storage_pool(self, strWorkflowID, nStoragePoolID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strWorkflowID,
			nStoragePoolID,
			objExtraVariables,
		]

		self.rpc("workflow_exec_storage_pool", arrParams)


	def workflow_exec_user(self, strWorkflowID, strUserID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strWorkflowID,
			strUserID,
			objExtraVariables,
		]

		self.rpc("workflow_exec_user", arrParams)


	def stage_definition_exec_on_switch_device(self, strStageDefinitionID, nSwitchDeviceID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strStageDefinitionID,
			nSwitchDeviceID,
			objExtraVariables,
		]

		return self.rpc("stage_definition_exec_on_switch_device", arrParams)


	def stage_definition_exec_on_server(self, strStageDefinitionID, nServerID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strStageDefinitionID,
			nServerID,
			objExtraVariables,
		]

		return self.rpc("stage_definition_exec_on_server", arrParams)


	def stage_definition_exec_free_standing(self, strStageDefinitionID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strStageDefinitionID,
			objExtraVariables,
		]

		return self.rpc("stage_definition_exec_free_standing", arrParams)


	def stage_definition_exec_storage_pool(self, strStageDefinitionID, nStoragePoolID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strStageDefinitionID,
			nStoragePoolID,
			objExtraVariables,
		]

		return self.rpc("stage_definition_exec_storage_pool", arrParams)


	def stage_definition_exec_user(self, strStageDefinitionID, strUserID, objExtraVariables = []):

		objExtraVariables = Serializer.serialize(objExtraVariables)

		arrParams = [
			strStageDefinitionID,
			strUserID,
			objExtraVariables,
		]

		return self.rpc("stage_definition_exec_user", arrParams)


	def infrastructure_deploy_custom_stage_add_as_new_runlevel(self, strInfrastructureID, nStageDefinitionID, strStageRunGroup, nDestinationRunLevel):

		arrParams = [
			strInfrastructureID,
			nStageDefinitionID,
			strStageRunGroup,
			nDestinationRunLevel,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy_custom_stage_add_as_new_runlevel", arrParams))

	def infrastructure_deploy_custom_stage_move_as_new_runlevel(self, nInfrastructureCustomDeployStageID, nDestinationRunLevel):

		arrParams = [
			nInfrastructureCustomDeployStageID,
			nDestinationRunLevel,
		]

		self.rpc("infrastructure_deploy_custom_stage_move_as_new_runlevel", arrParams)


	def infrastructure_deploy_custom_stage_get(self, nInfrastructureCustomDeployStageID):

		arrParams = [
			nInfrastructureCustomDeployStageID,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy_custom_stage_get", arrParams))

	def workflow_stages(self, strWorkflowID):

		arrParams = [
			strWorkflowID,
		]

		arrWorkflowStageDefinitionReferences = self.rpc("workflow_stages", arrParams)
		for index in range(len(arrWorkflowStageDefinitionReferences)):
			arrWorkflowStageDefinitionReferences[index] = Deserializer.deserialize(arrWorkflowStageDefinitionReferences[index])
		return arrWorkflowStageDefinitionReferences

	def workflow_stage_move_into_runlevel(self, nWorkflowStageID, nDestinationRunLevel):

		arrParams = [
			nWorkflowStageID,
			nDestinationRunLevel,
		]

		self.rpc("workflow_stage_move_into_runlevel", arrParams)


	def workflow_stage_add_as_new_runlevel(self, strWorkflowID, nStageDefinitionID, nDestinationRunLevel):

		arrParams = [
			strWorkflowID,
			nStageDefinitionID,
			nDestinationRunLevel,
		]

		return Deserializer.deserialize(self.rpc("workflow_stage_add_as_new_runlevel", arrParams))

	def workflow_stage_move_as_new_runlevel(self, nWorkflowStageID, nDestinationRunLevel):

		arrParams = [
			nWorkflowStageID,
			nDestinationRunLevel,
		]

		self.rpc("workflow_stage_move_as_new_runlevel", arrParams)


	def workflow_stage_get(self, nWorkflowStageID):

		arrParams = [
			nWorkflowStageID,
		]

		return Deserializer.deserialize(self.rpc("workflow_stage_get", arrParams))

	def workflow_stage_add_into_runlevel(self, strWorkflowID, nStageDefinitionID, nRunLevel):

		arrParams = [
			strWorkflowID,
			nStageDefinitionID,
			nRunLevel,
		]

		return Deserializer.deserialize(self.rpc("workflow_stage_add_into_runlevel", arrParams))

	def workflow_stage_delete_from_runlevel(self, strWorkflowID, nStageDefinitionID, nRunLevel):

		arrParams = [
			strWorkflowID,
			nStageDefinitionID,
			nRunLevel,
		]

		self.rpc("workflow_stage_delete_from_runlevel", arrParams)


	def workflow_stage_delete(self, nWorkflowStageID):

		arrParams = [
			nWorkflowStageID,
		]

		self.rpc("workflow_stage_delete", arrParams)


	def server_firmware_upgrade_policy_status_set(self, nServerFirmwarePolicyID, strPolicyStatus):

		arrParams = [
			nServerFirmwarePolicyID,
			strPolicyStatus,
		]

		self.rpc("server_firmware_upgrade_policy_status_set", arrParams)


	def volume_template_os_bootstrap_function_name_edit(self, nVolumeTemplateID, strBootstrapFunctionName):

		arrParams = [
			nVolumeTemplateID,
			strBootstrapFunctionName,
		]

		return self.rpc("volume_template_os_bootstrap_function_name_edit", arrParams)


	def volume_template_operating_system_edit(self, nVolumeTemplateID, objOperatingSystem):

		objOperatingSystem = Serializer.serialize(objOperatingSystem)

		arrParams = [
			nVolumeTemplateID,
			objOperatingSystem,
		]

		return self.rpc("volume_template_operating_system_edit", arrParams)


	def infrastructure_deploy_custom_stage_variables_update(self, nInfrastructureCustomDeployStageID, objVariables):

		objVariables = Serializer.serialize(objVariables)

		arrParams = [
			nInfrastructureCustomDeployStageID,
			objVariables,
		]

		self.rpc("infrastructure_deploy_custom_stage_variables_update", arrParams)


	def infrastructure_deploy_custom_stage_update(self, nInfrastructureCustomDeployStageID, objInfrastructureCustomDeployStage):

		objInfrastructureCustomDeployStage = Serializer.serialize(objInfrastructureCustomDeployStage)

		arrParams = [
			nInfrastructureCustomDeployStageID,
			objInfrastructureCustomDeployStage,
		]

		return Deserializer.deserialize(self.rpc("infrastructure_deploy_custom_stage_update", arrParams))

	def server_mgmt_snmp_enable_and_bmcreset(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("server_mgmt_snmp_enable_and_bmcreset", arrParams)


	def workflow_stage_update(self, nWorkflowStageID, objWorkflowStage):

		objWorkflowStage = Serializer.serialize(objWorkflowStage)

		arrParams = [
			nWorkflowStageID,
			objWorkflowStage,
		]

		return Deserializer.deserialize(self.rpc("workflow_stage_update", arrParams))

	def workflow_stage_variables_update(self, nWorkflowStageID, objVariables):

		objVariables = Serializer.serialize(objVariables)

		arrParams = [
			nWorkflowStageID,
			objVariables,
		]

		self.rpc("workflow_stage_variables_update", arrParams)


	def instance_stop(self, strInstanceID, bKeepDetachingDrives):

		arrParams = [
			strInstanceID,
			bKeepDetachingDrives,
		]

		return Deserializer.deserialize(self.rpc("instance_stop", arrParams))

	def instance_start(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return Deserializer.deserialize(self.rpc("instance_start", arrParams))

	def instance_monitoring_paths_get(self, nInstanceID, bRelativePaths):

		arrParams = [
			nInstanceID,
			bRelativePaths,
		]

		return self.rpc("instance_monitoring_paths_get", arrParams)


	def instance_monitoring_paths_get_structured(self, nInstanceID, bRelativePaths):

		arrParams = [
			nInstanceID,
			bRelativePaths,
		]

		return self.rpc("instance_monitoring_paths_get_structured", arrParams)


	def monitoring_agent_all_query_paths_get_structured(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		self.rpc("monitoring_agent_all_query_paths_get_structured", arrParams)


	def monitoring_agent_all_query_paths_get(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		self.rpc("monitoring_agent_all_query_paths_get", arrParams)


	def dhcp_server_lease_get(self, strMACAddress, nServerID = None):

		arrParams = [
			strMACAddress,
			nServerID,
		]

		return self.rpc("dhcp_server_lease_get", arrParams)


	def dhcp_switch_device_lease_get(self, strMACAddress):

		arrParams = [
			strMACAddress,
		]

		return self.rpc("dhcp_switch_device_lease_get", arrParams)


	def dhcp_server_lease_create(self, strMACAddress, strSwitchHostname = None, nExpiryMinutes = 60, strDatacenterName = None, nServerID = None):

		arrParams = [
			strMACAddress,
			strSwitchHostname,
			nExpiryMinutes,
			strDatacenterName,
			nServerID,
		]

		return self.rpc("dhcp_server_lease_create", arrParams)


	def dhcp_switch_device_lease_create(self, strMACAddress, nNetworkEquipmentID, nExpiryMinutes = 60):

		arrParams = [
			strMACAddress,
			nNetworkEquipmentID,
			nExpiryMinutes,
		]

		return self.rpc("dhcp_switch_device_lease_create", arrParams)


	def server_monitoring_metadata_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		return self.rpc("server_monitoring_metadata_get", arrParams)


	def switch_device_create_automatic(self, objNetworkEquipmentData, bOverwriteWithHostnameFromFetchedSwitch = False, bAutoCreateSwitch = True):

		objNetworkEquipmentData = Serializer.serialize(objNetworkEquipmentData)

		arrParams = [
			objNetworkEquipmentData,
			bOverwriteWithHostnameFromFetchedSwitch,
			bAutoCreateSwitch,
		]

		return self.rpc("switch_device_create_automatic", arrParams)


	def stage_definition_make_public(self, nStageDefinitionID):

		arrParams = [
			nStageDefinitionID,
		]

		self.rpc("stage_definition_make_public", arrParams)


	def stage_definition_deprecated_set(self, nStageDefinitionID, bDeprecated):

		arrParams = [
			nStageDefinitionID,
			bDeprecated,
		]

		self.rpc("stage_definition_deprecated_set", arrParams)


	def workflow_make_public(self, nWorkflowID, bMakeAllReferencedStageDefinitionsPublic = False):

		arrParams = [
			nWorkflowID,
			bMakeAllReferencedStageDefinitionsPublic,
		]

		self.rpc("workflow_make_public", arrParams)


	def workflow_deprecated_set(self, nWorkflowID, bDeprecated):

		arrParams = [
			nWorkflowID,
			bDeprecated,
		]

		self.rpc("workflow_deprecated_set", arrParams)


	def drive_array_tags_add(self, strDriveArrayID, arrDriveArrayTagsNames):

		arrParams = [
			strDriveArrayID,
			arrDriveArrayTagsNames,
		]

		return Deserializer.deserialize(self.rpc("drive_array_tags_add", arrParams))

	def drive_array_tags_set(self, strDriveArrayID, arrDriveArrayTagsNames):

		arrParams = [
			strDriveArrayID,
			arrDriveArrayTagsNames,
		]

		return Deserializer.deserialize(self.rpc("drive_array_tags_set", arrParams))

	def drive_array_tags(self, strDriveArrayID):

		arrParams = [
			strDriveArrayID,
		]

		return self.rpc("drive_array_tags", arrParams)


	def drive_array_tags_remove(self, strDriveArrayID, arrDriveArrayTagsNames):

		arrParams = [
			strDriveArrayID,
			arrDriveArrayTagsNames,
		]

		return Deserializer.deserialize(self.rpc("drive_array_tags_remove", arrParams))

	def os_template_network_create(self, strUserID, strNewOSTemplateLabel, strDescription, strOSTemplateDisplayName, objNetworkOperatingSystem, arrOSTemplateTags = [], strOSTemplateVersion = "0.0.0"):

		objNetworkOperatingSystem = Serializer.serialize(objNetworkOperatingSystem)

		arrParams = [
			strUserID,
			strNewOSTemplateLabel,
			strDescription,
			strOSTemplateDisplayName,
			objNetworkOperatingSystem,
			arrOSTemplateTags,
			strOSTemplateVersion,
		]

		return Deserializer.deserialize(self.rpc("os_template_network_create", arrParams))

	def dhcp_server_regenerate(self, arrServerIDs, bRegeneratedCloudInit, bRegenerateIPXE, arrDatacenterNames, bDestroyTrdb = False):

		arrParams = [
			arrServerIDs,
			bRegeneratedCloudInit,
			bRegenerateIPXE,
			arrDatacenterNames,
			bDestroyTrdb,
		]

		self.rpc("dhcp_server_regenerate", arrParams)


	def dhcp_network_equipment_regenerate(self, arrNetworkEquipmentIDs, arrDatacenterNames, bDestroyTrdb = False):

		arrParams = [
			arrNetworkEquipmentIDs,
			arrDatacenterNames,
			bDestroyTrdb,
		]

		self.rpc("dhcp_network_equipment_regenerate", arrParams)


	def volume_template_network_operating_system_edit(self, nVolumeTemplateID, objNetworkOperatingSystem):

		objNetworkOperatingSystem = Serializer.serialize(objNetworkOperatingSystem)

		arrParams = [
			nVolumeTemplateID,
			objNetworkOperatingSystem,
		]

		return self.rpc("volume_template_network_operating_system_edit", arrParams)


	def dhcpserver_server_agent_rules_updated(self, nAgentID, bInvalidateEntireServerConfig = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireServerConfig,
		]

		self.rpc("dhcpserver_server_agent_rules_updated", arrParams)


	def dhcpserver_network_equipment_agent_rules_updated(self, nAgentID, bInvalidateEntireNetworkEquipmentConfig = False):

		arrParams = [
			nAgentID,
			bInvalidateEntireNetworkEquipmentConfig,
		]

		self.rpc("dhcpserver_network_equipment_agent_rules_updated", arrParams)


	def instance_monitoring_agent_data_get(self, nInstanceID, nGranularityMinutes = 1, strTimestampStart = None, strTimestampEnd = None):

		arrParams = [
			nInstanceID,
			nGranularityMinutes,
			strTimestampStart,
			strTimestampEnd,
		]

		return self.rpc("instance_monitoring_agent_data_get", arrParams)


	def kubernetes_token(self, nInfrastructureID, objConnectionDetails):

		objConnectionDetails = Serializer.serialize(objConnectionDetails)

		arrParams = [
			nInfrastructureID,
			objConnectionDetails,
		]

		return self.rpc("kubernetes_token", arrParams)


	def kubernetes_config(self, nInfrastructureID, objConnectionDetails):

		objConnectionDetails = Serializer.serialize(objConnectionDetails)

		arrParams = [
			nInfrastructureID,
			objConnectionDetails,
		]

		return self.rpc("kubernetes_config", arrParams)


	def table_column_name_to_information(self, strTableName):

		arrParams = [
			strTableName,
		]

		return self.rpc("table_column_name_to_information", arrParams)


	def monitoring_network_traffic_parse(self):

		arrParams = [
		]

		self.rpc("monitoring_network_traffic_parse", arrParams)


	def datacenter_agent_subnet_traffic_get_all_agents(self, nSpecificSubnet = None, strFrom = None, strUntil = None):

		arrParams = [
			nSpecificSubnet,
			strFrom,
			strUntil,
		]

		return self.rpc("datacenter_agent_subnet_traffic_get_all_agents", arrParams)


	def datacenter_agent_debug_workload_distribution(self):

		arrParams = [
		]

		return self.rpc("datacenter_agent_debug_workload_distribution", arrParams)


	def server_registering_cartridge_checks(self, nServerID, arrServerInfo = None):

		arrParams = [
			nServerID,
			arrServerInfo,
		]

		self.rpc("server_registering_cartridge_checks", arrParams)


	def server_enable_ipmi_over_lan_via_redfish(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("server_enable_ipmi_over_lan_via_redfish", arrParams)


	def servers_power_status_refresh_manualy(self, arrServerIDs):

		arrParams = [
			arrServerIDs,
		]

		self.rpc("servers_power_status_refresh_manualy", arrParams)


	def volume_template_server_types_whitelist_add(self, nVolumeTemplateID, arrServerTypeIDs):

		arrParams = [
			nVolumeTemplateID,
			arrServerTypeIDs,
		]

		self.rpc("volume_template_server_types_whitelist_add", arrParams)


	def volume_template_server_types_whitelist_delete(self, nVolumeTemplateID, arrServerTypeIDs):

		arrParams = [
			nVolumeTemplateID,
			arrServerTypeIDs,
		]

		self.rpc("volume_template_server_types_whitelist_delete", arrParams)


	def tftpserver_agent_os_templates_os_assets_deleted(self, nAgentID, arrOSTemplatesOSAssetsDeleted):

		arrParams = [
			nAgentID,
			arrOSTemplatesOSAssetsDeleted,
		]

		self.rpc("tftpserver_agent_os_templates_os_assets_deleted", arrParams)


	def independent_instance_label_is_available_assert(self, strUserIDOwner, strInstanceLabel):

		arrParams = [
			strUserIDOwner,
			strInstanceLabel,
		]

		return self.rpc("independent_instance_label_is_available_assert", arrParams)


	def independent_instance_drive_label_is_available_assert(self, strInstanceID, strDriveLabel):

		arrParams = [
			strInstanceID,
			strDriveLabel,
		]

		return self.rpc("independent_instance_drive_label_is_available_assert", arrParams)


	def independent_instance_get(self, strInstanceID):

		arrParams = [
			strInstanceID,
		]

		return self.rpc("independent_instance_get", arrParams)


	def independent_instances(self, strUserIDOwner):

		arrParams = [
			strUserIDOwner,
		]

		return self.rpc("independent_instances", arrParams)


	def independent_instance_boot_drive_replace(self, strInstanceID, objIndependentInstanceBootDriveConfig):

		objIndependentInstanceBootDriveConfig = Serializer.serialize(objIndependentInstanceBootDriveConfig)

		arrParams = [
			strInstanceID,
			objIndependentInstanceBootDriveConfig,
		]

		return self.rpc("independent_instance_boot_drive_replace", arrParams)


	def independent_instance_secondary_drive_create(self, strInstanceID, objIndependentInstanceSecondaryDriveConfig):

		objIndependentInstanceSecondaryDriveConfig = Serializer.serialize(objIndependentInstanceSecondaryDriveConfig)

		arrParams = [
			strInstanceID,
			objIndependentInstanceSecondaryDriveConfig,
		]

		return self.rpc("independent_instance_secondary_drive_create", arrParams)


	def independent_instance_secondary_drive_delete(self, strDriveID):

		arrParams = [
			strDriveID,
		]

		return self.rpc("independent_instance_secondary_drive_delete", arrParams)


	def independent_instance_secondary_drive_replace(self, strDriveID, objIndependentInstanceBootDriveConfig):

		objIndependentInstanceBootDriveConfig = Serializer.serialize(objIndependentInstanceBootDriveConfig)

		arrParams = [
			strDriveID,
			objIndependentInstanceBootDriveConfig,
		]

		return self.rpc("independent_instance_secondary_drive_replace", arrParams)


	def independent_instance_drive_storage_expand(self, strDriveID, nISCSIStorageSizeMBytes):

		arrParams = [
			strDriveID,
			nISCSIStorageSizeMBytes,
		]

		return self.rpc("independent_instance_drive_storage_expand", arrParams)


	def os_template_update_os_asset_variables(self, nOSTemplateID, nOSAssetID, strVolumeTemplateOSAssetVariablesJSON):

		arrParams = [
			nOSTemplateID,
			nOSAssetID,
			strVolumeTemplateOSAssetVariablesJSON,
		]

		self.rpc("os_template_update_os_asset_variables", arrParams)


	def ip_a_record_add(self, nClusterID, strSubdomainName, strRootDomain):

		arrParams = [
			nClusterID,
			strSubdomainName,
			strRootDomain,
		]

		self.rpc("ip_a_record_add", arrParams)


	def ip_a_record_remove(self, nClusterID, strSubdomainName, strRootDomain):

		arrParams = [
			nClusterID,
			strSubdomainName,
			strRootDomain,
		]

		self.rpc("ip_a_record_remove", arrParams)


	def ip_a_records(self, nClusterID, bIPToDomains = False):

		arrParams = [
			nClusterID,
			bIPToDomains,
		]

		return self.rpc("ip_a_records", arrParams)


	def volume_template_create_from_drive(self, strDriveID, objNewVolumeTemplate):

		objNewVolumeTemplate = Serializer.serialize(objNewVolumeTemplate)

		arrParams = [
			strDriveID,
			objNewVolumeTemplate,
		]

		return Deserializer.deserialize(self.rpc("volume_template_create_from_drive", arrParams))

	def datacenter_diagnostics(self, strDatacenterName, nServerID = None, strConnectivityCheckIP = None):

		arrParams = [
			strDatacenterName,
			nServerID,
			strConnectivityCheckIP,
		]

		return self.rpc("datacenter_diagnostics", arrParams)


	def volume_template_make_private(self, nVolumeTemplateID, strUserIDOwner):

		arrParams = [
			nVolumeTemplateID,
			strUserIDOwner,
		]

		return Deserializer.deserialize(self.rpc("volume_template_make_private", arrParams))

	def subnet_pools_forced_only(self, strDatacenterName, nUserID, nInfrastructureID):

		arrParams = [
			strDatacenterName,
			nUserID,
			nInfrastructureID,
		]

		self.rpc("subnet_pools_forced_only", arrParams)


	def server_boot_order_preset(self, nServerID, arrBootSources = []):

		arrParams = [
			nServerID,
			arrBootSources,
		]

		return self.rpc("server_boot_order_preset", arrParams)


	def server_boot_virtual_image(self, nServerID, strImageURL):

		arrParams = [
			nServerID,
			strImageURL,
		]

		self.rpc("server_boot_virtual_image", arrParams)


	def switch_device_link_create(self, nSwitchDeviceID1, nSwitchDeviceID2, strLinkType, objLinkProperties):

		objLinkProperties = Serializer.serialize(objLinkProperties)

		arrParams = [
			nSwitchDeviceID1,
			nSwitchDeviceID2,
			strLinkType,
			objLinkProperties,
		]

		return self.rpc("switch_device_link_create", arrParams)


	def switch_device_links(self):

		arrParams = [
		]

		return self.rpc("switch_device_links", arrParams)


	def switch_device_link_get(self, nSwitchDeviceID1, nSwitchDeviceID2, strLinkType):

		arrParams = [
			nSwitchDeviceID1,
			nSwitchDeviceID2,
			strLinkType,
		]

		return self.rpc("switch_device_link_get", arrParams)


	def switch_device_link_update(self, nSwitchDeviceID1, nSwitchDeviceID2, strLinkType, objLinkProperties):

		objLinkProperties = Serializer.serialize(objLinkProperties)

		arrParams = [
			nSwitchDeviceID1,
			nSwitchDeviceID2,
			strLinkType,
			objLinkProperties,
		]

		return self.rpc("switch_device_link_update", arrParams)


	def switch_device_link_delete(self, nSwitchDeviceID1, nSwitchDeviceID2, strLinkType):

		arrParams = [
			nSwitchDeviceID1,
			nSwitchDeviceID2,
			strLinkType,
		]

		self.rpc("switch_device_link_delete", arrParams)


	def server_create_and_register(self, objServer, strDeviceType = "server"):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			objServer,
			strDeviceType,
		]

		return self.rpc("server_create_and_register", arrParams)


	def volume_templates_statistics(self):

		arrParams = [
		]

		return self.rpc("volume_templates_statistics", arrParams)


	def switch_device_create_from_cisco_aci(self, objNetworkEquipmentData):

		objNetworkEquipmentData = Serializer.serialize(objNetworkEquipmentData)

		arrParams = [
			objNetworkEquipmentData,
		]

		arrSwitchDevices = self.rpc("switch_device_create_from_cisco_aci", arrParams)
		for index in range(len(arrSwitchDevices)):
			arrSwitchDevices[index] = Deserializer.deserialize(arrSwitchDevices[index])
		return arrSwitchDevices

	def server_set_boot_from_device(self, nServerID, strDevice):

		arrParams = [
			nServerID,
			strDevice,
		]

		self.rpc("server_set_boot_from_device", arrParams)


	def volume_template_replicate_to_storages(self, objVolumeTemplate, arrStoragePoolIDs):

		objVolumeTemplate = Serializer.serialize(objVolumeTemplate)

		arrParams = [
			objVolumeTemplate,
			arrStoragePoolIDs,
		]

		return self.rpc("volume_template_replicate_to_storages", arrParams)


	def volume_template_update_storages(self, nOldVolumeTemplateID, objVolumeTemplate, arrDstStoragePoolIDs):

		objVolumeTemplate = Serializer.serialize(objVolumeTemplate)

		arrParams = [
			nOldVolumeTemplateID,
			objVolumeTemplate,
			arrDstStoragePoolIDs,
		]

		return self.rpc("volume_template_update_storages", arrParams)


	def volume_template_replicate_to_storage(self, nVolumeTemplateID, nStoragePoolID):

		arrParams = [
			nVolumeTemplateID,
			nStoragePoolID,
		]

		self.rpc("volume_template_replicate_to_storage", arrParams)


	def switch_device_controller_get(self, mxNetworkEquipmentID):

		mxNetworkEquipmentID = Serializer.serialize(mxNetworkEquipmentID)

		arrParams = [
			mxNetworkEquipmentID,
		]

		return self.rpc("switch_device_controller_get", arrParams)


	def server_license_requirements_get(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("server_license_requirements_get", arrParams)


	def server_license_requirements_set(self, nServerID, objRequiredLicenses):

		objRequiredLicenses = Serializer.serialize(objRequiredLicenses)

		arrParams = [
			nServerID,
			objRequiredLicenses,
		]

		self.rpc("server_license_requirements_set", arrParams)


	def user_get_by_email(self, userEmail):

		arrParams = [
			userEmail,
		]

		return Deserializer.deserialize(self.rpc("user_get_by_email", arrParams))

	def switch_device_decommission(self, nNetworkEquipmentID):

		arrParams = [
			nNetworkEquipmentID,
		]

		self.rpc("switch_device_decommission", arrParams)


	def subnet_ips(self, strSubnetID):

		arrParams = [
			strSubnetID,
		]

		return self.rpc("subnet_ips", arrParams)


	def firewall_profile_create(self, arrFirewallProfileName, arrFirewallProfileRules, strFirewallProfileDescription, arrFirewallProfileTags):

		arrParams = [
			arrFirewallProfileName,
			arrFirewallProfileRules,
			strFirewallProfileDescription,
			arrFirewallProfileTags,
		]

		return self.rpc("firewall_profile_create", arrParams)


	def firewall_profile_rules_get(self, nFirewallProfileID):

		arrParams = [
			nFirewallProfileID,
		]

		return self.rpc("firewall_profile_rules_get", arrParams)


	def firewall_profile_rules_set(self, nFirewallProfileID, arrFirewallProfileRules, bAppend = False):

		arrParams = [
			nFirewallProfileID,
			arrFirewallProfileRules,
			bAppend,
		]

		self.rpc("firewall_profile_rules_set", arrParams)


	def firewall_profiles_get(self):

		arrParams = [
		]

		return self.rpc("firewall_profiles_get", arrParams)


	def firewall_profile_delete(self, nFirewallProfileID):

		arrParams = [
			nFirewallProfileID,
		]

		self.rpc("firewall_profile_delete", arrParams)


	def firewall_profile_name_set(self, nFirewallProfileID, strFirewallProfileName):

		arrParams = [
			nFirewallProfileID,
			strFirewallProfileName,
		]

		self.rpc("firewall_profile_name_set", arrParams)


	def firewall_profile_description_set(self, nFirewallProfileID, strFirewallProfileDescription):

		arrParams = [
			nFirewallProfileID,
			strFirewallProfileDescription,
		]

		self.rpc("firewall_profile_description_set", arrParams)


	def firewall_profile_tags_set(self, nFirewallProfileID, arrFirewallProfileTags, bAppend):

		arrParams = [
			nFirewallProfileID,
			arrFirewallProfileTags,
			bAppend,
		]

		self.rpc("firewall_profile_tags_set", arrParams)


	def firewall_profile_status_set(self, nFirewallProfileID, strFirewallProfileStatus):

		arrParams = [
			nFirewallProfileID,
			strFirewallProfileStatus,
		]

		self.rpc("firewall_profile_status_set", arrParams)


	def server_edit_rack(self, nServerID, objServer):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			nServerID,
			objServer,
		]

		return Deserializer.deserialize(self.rpc("server_edit_rack", arrParams))

	def server_edit_inventory(self, nServerID, objServer):

		objServer = Serializer.serialize(objServer)

		arrParams = [
			nServerID,
			objServer,
		]

		return Deserializer.deserialize(self.rpc("server_edit_inventory", arrParams))

	def datacenter_diagnostics_virtual_media(self, strDatacenterName, nServerID = None, strConnectivityCheckIP = None):

		arrParams = [
			strDatacenterName,
			nServerID,
			strConnectivityCheckIP,
		]

		return self.rpc("datacenter_diagnostics_virtual_media", arrParams)


	def datacenter_diagnostics_server_remove_from_diagnostics(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("datacenter_diagnostics_server_remove_from_diagnostics", arrParams)


	def datacenter_diagnostics_clear_resources(self, strDatacenterName, nServerID = None):

		arrParams = [
			strDatacenterName,
			nServerID,
		]

		self.rpc("datacenter_diagnostics_clear_resources", arrParams)


	def server_eject_virtual_image(self, nServerID):

		arrParams = [
			nServerID,
		]

		self.rpc("server_eject_virtual_image", arrParams)


	def external_connection_create(self, objExternalConnection):

		objExternalConnection = Serializer.serialize(objExternalConnection)

		arrParams = [
			objExternalConnection,
		]

		return Deserializer.deserialize(self.rpc("external_connection_create", arrParams))

	def external_connection_switch_add(self, nExternalConnectionID, objSwitchEntry):

		objSwitchEntry = Serializer.serialize(objSwitchEntry)

		arrParams = [
			nExternalConnectionID,
			objSwitchEntry,
		]

		return Deserializer.deserialize(self.rpc("external_connection_switch_add", arrParams))

	def external_connection_get(self, nExternalConnectionID):

		arrParams = [
			nExternalConnectionID,
		]

		return Deserializer.deserialize(self.rpc("external_connection_get", arrParams))

	def external_connection_switch_remove(self, nExternalConnectionID, nExternalConnectionSwitchID):

		arrParams = [
			nExternalConnectionID,
			nExternalConnectionSwitchID,
		]

		return Deserializer.deserialize(self.rpc("external_connection_switch_remove", arrParams))

	def external_connection_switch_edit(self, nExternalConnectionSwitchID, objSwitchEntry):

		objSwitchEntry = Serializer.serialize(objSwitchEntry)

		arrParams = [
			nExternalConnectionSwitchID,
			objSwitchEntry,
		]

		return Deserializer.deserialize(self.rpc("external_connection_switch_edit", arrParams))

	def external_connection_edit(self, nExternalConnectionID, objExternalConnection):

		objExternalConnection = Serializer.serialize(objExternalConnection)

		arrParams = [
			nExternalConnectionID,
			objExternalConnection,
		]

		return Deserializer.deserialize(self.rpc("external_connection_edit", arrParams))

	def external_connections(self, strDatacenterName):

		arrParams = [
			strDatacenterName,
		]

		objExternalConnection = self.rpc("external_connections", arrParams)
		for strKeyExternalConnection in objExternalConnection:
			objExternalConnection[strKeyExternalConnection] = Deserializer.deserialize(objExternalConnection[strKeyExternalConnection])
		return objExternalConnection

	def external_connection_delete(self, nExternalConnectionID):

		arrParams = [
			nExternalConnectionID,
		]

		self.rpc("external_connection_delete", arrParams)


