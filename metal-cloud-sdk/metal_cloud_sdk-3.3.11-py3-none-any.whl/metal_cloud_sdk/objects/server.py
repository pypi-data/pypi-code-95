# -*- coding: utf-8 -*-

class Server(object):
	"""
	Represents a server in a datacenter.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the server. It is automatically generated and cannot be edited.
	"""
	server_id = None;

	"""
	Server UUID.
	"""
	server_uuid = None;

	"""
	Full bandwidth available.
	"""
	server_network_total_capacity_mbps = None;

	"""
	The server power status which can have one of the values:
	<code>SERVER_POWER_STATUS_ON</code>, <code>SERVER_POWER_STATUS_OFF</code>.
	"""
	server_power_status = None;

	"""
	The cores of a CPU.
	"""
	server_processor_core_count = 1;

	"""
	The clock speed of a CPU.
	"""
	server_processor_core_mhz = 1000;

	"""
	The CPU count on the server.
	"""
	server_processor_count = 1;

	"""
	The RAM capacity.
	"""
	server_ram_gbytes = 1;

	"""
	The minimum number of physical disks.
	"""
	server_disk_count = 0;

	"""
	The minimum size of a single disk.
	"""
	server_disk_size_mbytes = 0;

	"""
	The type of physical disks.
	"""
	server_disk_type = "none";

	"""
	The name of the processor.
	"""
	server_processor_name = None;

	"""
	The name of the server.
	"""
	server_product_name = None;

	"""
	The ID of the server type. See <code>server_types()</code> for more detalis.
	"""
	server_type_id = None;

	"""
	The <a:schema>ServerInterface</a:schema> objects.
	"""
	server_interfaces = None;

	"""
	The <a:schema>ServerDisk</a:schema> objects
	"""
	server_disks = None;

	"""
	List of tags representative for the Server.
	"""
	server_tags = [];

	"""
	Name of the rack
	"""
	server_rack_name = None;

	"""
	Server rack position lower unit
	"""
	server_rack_position_lower_unit = None;

	"""
	Server rack position upper unit
	"""
	server_rack_position_upper_unit = None;

	"""
	Server inventory id
	"""
	server_inventory_id = None;

	"""
	Server dhcp status
	"""
	server_dhcp_status = "quarantine";

	"""
	Server status
	"""
	server_status = "registering";

	"""
	Server serial number
	"""
	server_serial_number = None;

	"""
	Server cartridge custom json
	"""
	server_custom_json = None;

	"""
	Server reregister flag
	"""
	server_requires_reregister = False;

	"""
	Server cartridge rack id
	"""
	chassis_rack_id = None;

	"""
	Server ipmi internal username
	"""
	server_ipmi_internal_username = None;

	"""
	Server BMC mac address
	"""
	server_bmc_mac_address = None;

	"""
	Server IPMI channel
	"""
	server_ipmi_channel = None;

	"""
	Server ILO reset timestamp
	"""
	server_ilo_reset_timestamp = "0000-00-00T00:00:00Z";

	"""
	Server disk wipe flag, allowing or disallowing the wiping of data from the
	servers during BDK boot.
	"""
	server_disk_wipe = False;

	"""
	Server chipset name
	"""
	server_chipset_name = None;

	"""
	Server class
	"""
	server_class = "unknown";

	"""
	Server allocation timestamp
	"""
	server_allocation_timestamp = None;

	"""
	Server created timestamp
	"""
	server_created_timestamp = None;

	"""
	Server vendor SKU id
	"""
	server_vendor_sku_id = None;

	"""
	Marks the server as unavailable instead of marking it as cleaning, when it
	is freed from an instance.
	"""
	server_requires_manual_cleaning = False;

	"""
	Server boot type
	"""
	server_boot_type = "classic";

	"""
	Datacenter name
	"""
	datacenter_name = None;

	"""
	Server last cleanup start timestamp
	"""
	server_last_cleanup_start = None;

	"""
	SNMP cummunity password
	"""
	snmp_community_password_dcencrypted = None;

	"""
	Server secure boot flag
	"""
	server_secure_boot_is_enabled = False;

	"""
	Server boot last update timestamp
	"""
	server_boot_last_update_timestamp = "0000-00-00T00:00:00Z";

	"""
	Server GPU count
	"""
	server_gpu_count = 0;

	"""
	Server GPU vendor
	"""
	server_gpu_vendor = None;

	"""
	Server vendor
	"""
	server_vendor = None;

	"""
	Agent id
	"""
	agent_id = None;

	"""
	Server CPU mark
	"""
	server_processor_cpu_mark = None;

	"""
	Server comments
	"""
	server_comments = None;

	"""
	Server instance custom JSON
	"""
	server_instance_custom_json = None;

	"""
	Server ipmi host
	"""
	server_ipmi_host = None;

	"""
	Server SNMP port
	"""
	server_mgmt_snmp_port = 161;

	"""
	Subnet OOB id
	"""
	subnet_oob_id = None;

	"""
	Server IPMI credentials need update flag
	"""
	server_ipmi_credentials_need_update = False;

	"""
	Server verdor info JSON
	"""
	server_vendor_info_json = None;

	"""
	Server BDK debug flag
	"""
	server_bdk_debug = False;

	"""
	Server OOB index
	"""
	subnet_oob_index = 0;

	"""
	Server processor threads
	"""
	server_processor_threads = 0;

	"""
	Server management SNMP community password
	"""
	server_mgmt_snmp_community_password_dcencrypted = None;

	"""
	Server ipmi version
	"""
	server_ipmi_version = None;

	"""
	Server management SNMP version
	"""
	server_mgmt_snmp_version = 2;

	"""
	Information about the server from bdk agent or provided when the server was
	created.
	"""
	server_info_json = None;

	"""
	Server power status last update timestamp
	"""
	server_power_status_last_update_timestamp = "0000-00-00T00:00:00Z";

	"""
	Server DHCP packet sniffing flag
	"""
	server_dhcp_packet_sniffing_is_enabled = True;

	"""
	Server bios informations in JSON format
	"""
	server_bios_info_json = None;

	"""
	Server encryption keys in JSON format
	"""
	server_keys_json = None;

	"""
	Server GPU model
	"""
	server_gpu_model = None;

	"""
	Server IPMI interna password encrypted
	"""
	server_ipmi_internal_password_encrypted = None;

	"""
	Server DHCP relay security flag
	"""
	server_dhcp_relay_security_is_enabled = True;

	"""
	Server details in XML format
	"""
	server_details_xml = None;

	"""
	Server metrics metadata in JSON format
	"""
	server_metrics_metadata_json = None;

	"""
	Server is currently used for diagnostics
	"""
	server_is_in_diagnostics = False;

	"""
	Server has SOL support through Redfish
	"""
	server_supports_sol = True;

	"""
	Server has virtual media support through Redfish
	"""
	server_supports_virtual_media = True;

	"""
	The schema type
	"""
	type = None;
