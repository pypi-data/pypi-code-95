from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class HealthCheck(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(HealthCheck, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the HealthCheck class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object HealthCheck.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if HealthCheck.__instance is None :
			HealthCheck.__instance = HealthCheck(dictParams, arrFilterPlugins)

		return HealthCheck.__instance


	""" 38 functions available on endpoint. """

	def dns_subdomain_changes_check(self):

		arrParams = [
		]

		self.rpc("dns_subdomain_changes_check", arrParams)


	def dns_subdomains_check(self):

		arrParams = [
		]

		self.rpc("dns_subdomains_check", arrParams)


	def instance_server_allocation_check(self):

		arrParams = [
		]

		return self.rpc("instance_server_allocation_check", arrParams)


	def wan_subnet_pool_availability_check(self):

		arrParams = [
		]

		return self.rpc("wan_subnet_pool_availability_check", arrParams)


	def oob_subnet_availability_check(self):

		arrParams = [
		]

		return self.rpc("oob_subnet_availability_check", arrParams)


	def ip_allocation_check(self):

		arrParams = [
		]

		return self.rpc("ip_allocation_check", arrParams)


	def network_equipment_configuration_check(self):

		arrParams = [
		]

		return self.rpc("network_equipment_configuration_check", arrParams)


	def server_availability_check(self):

		arrParams = [
		]

		return self.rpc("server_availability_check", arrParams)


	def server_status_report(self):

		arrParams = [
		]

		return self.rpc("server_status_report", arrParams)


	def storage_pools_available_physical_space_check(self):

		arrParams = [
		]

		return self.rpc("storage_pools_available_physical_space_check", arrParams)


	def storage_pools_used_virtual_space_check(self):

		arrParams = [
		]

		return self.rpc("storage_pools_used_virtual_space_check", arrParams)


	def storage_pools_used_physical_space_check(self):

		arrParams = [
		]

		return self.rpc("storage_pools_used_physical_space_check", arrParams)


	def volume_templates_public_availability_check(self):

		arrParams = [
		]

		return self.rpc("volume_templates_public_availability_check", arrParams)


	def drive_storage_allocation_check(self):

		arrParams = [
		]

		return self.rpc("drive_storage_allocation_check", arrParams)


	def mysql_max_heap_table_size_check(self):

		arrParams = [
		]

		return self.rpc("mysql_max_heap_table_size_check", arrParams)


	def mysql_heap_tables_size_check(self):

		arrParams = [
		]

		self.rpc("mysql_heap_tables_size_check", arrParams)


	def health_check_function_descriptors(self):

		arrParams = [
		]

		return self.rpc("health_check_function_descriptors", arrParams)


	def health_check_functions_names(self):

		arrParams = [
		]

		return self.rpc("health_check_functions_names", arrParams)


	def storage_to_database_correspondency_check(self):

		arrParams = [
		]

		return self.rpc("storage_to_database_correspondency_check", arrParams)


	def database_to_storage_correspondency_check(self):

		arrParams = [
		]

		return self.rpc("database_to_storage_correspondency_check", arrParams)


	def afc_thrown_errors_check(self):

		arrParams = [
		]

		return self.rpc("afc_thrown_errors_check", arrParams)


	def afc_status_not_updated_check(self):

		arrParams = [
		]

		self.rpc("afc_status_not_updated_check", arrParams)


	def snapshot_database_to_storage_correspondency_check(self):

		arrParams = [
		]

		return self.rpc("snapshot_database_to_storage_correspondency_check", arrParams)


	def snapshot_storage_to_database_correspondency_check(self):

		arrParams = [
		]

		return self.rpc("snapshot_storage_to_database_correspondency_check", arrParams)


	def storage_internal_check(self):

		arrParams = [
		]

		return self.rpc("storage_internal_check", arrParams)


	def instances_iqn_storage_to_database_correspondency_check(self):

		arrParams = [
		]

		return self.rpc("instances_iqn_storage_to_database_correspondency_check", arrParams)


	def instance_debug_all_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_debug_all_check", arrParams)


	def instance_networking_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_networking_check", arrParams)


	def instance_networking_san_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_networking_san_check", arrParams)


	def instance_networking_wan_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_networking_wan_check", arrParams)


	def instance_iscsi_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_iscsi_check", arrParams)


	def instance_ipmi_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_ipmi_check", arrParams)


	def storage_shared_drive_delete_stop_check(self):

		arrParams = [
		]

		self.rpc("storage_shared_drive_delete_stop_check", arrParams)


	def instances_server_types_check(self):

		arrParams = [
		]

		return self.rpc("instances_server_types_check", arrParams)


	def products_consistency_check(self):

		arrParams = [
		]

		return self.rpc("products_consistency_check", arrParams)


	def storage_pools_mappings_check(self):

		arrParams = [
		]

		return self.rpc("storage_pools_mappings_check", arrParams)


	def instance_ssh_and_filesystem_check(self, nInstanceID):

		arrParams = [
			nInstanceID,
		]

		return self.rpc("instance_ssh_and_filesystem_check", arrParams)


	def server_ipmi_check(self):

		arrParams = [
		]

		return self.rpc("server_ipmi_check", arrParams)


