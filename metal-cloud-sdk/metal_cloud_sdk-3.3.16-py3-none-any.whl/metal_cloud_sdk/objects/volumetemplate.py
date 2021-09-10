# -*- coding: utf-8 -*-

class VolumeTemplate(object):
	"""
	A template can be created based on a drive and it has the same
	characteristics and holds the same information as the parent drive.
	"""

	def __init__(self, volume_template_label, volume_template_size_mbytes, volume_template_boot_type):
		self.volume_template_label = volume_template_label;
		self.volume_template_size_mbytes = volume_template_size_mbytes;
		self.volume_template_boot_type = volume_template_boot_type;


	"""
	The ID of the volume template.
	"""
	volume_template_id = None;

	"""
	The volume template's label. It is editable and can be used to call API
	functions.
	"""
	volume_template_label = None;

	"""
	The volume template's unique label. Is <volume_template_label>@<user_id>.
	"""
	volume_template_label_unique = None;

	"""
	The volume template's display name.
	"""
	volume_template_display_name = None;

	"""
	Size of the template.
	"""
	volume_template_size_mbytes = None;

	"""
	Whether the template supports booting and running from local disks.
	"""
	volume_template_local_disk_supported = False;

	"""
	Whether the template is an OS template.
	"""
	volume_template_is_os_template = False;

	"""
	A set of all supported methods
	"""
	volume_template_boot_methods_supported = "pxe_iscsi";

	"""
	An arbitrary UTF-8 string which provides a description of the template.
	"""
	volume_template_description = "";

	"""
	Date and time of the template's creation. ISO 8601 timestamp. Example
	format: 2013-11-29T13:00:01Z
	"""
	volume_template_created_timestamp = None;

	"""
	ISO 8601 timestamp which holds the date and time when the VolumeTemplate was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	volume_template_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	User owner ID.
	"""
	user_id = None;

	"""
	The server needs to have the given boot type to use the volume template.
	"""
	volume_template_boot_type = None;

	"""
	OperatingSystem
	"""
	volume_template_operating_system = None;

	"""
	http(s) template base URL.
	"""
	volume_template_repo_url = None;

	"""
	The deprecation status of the volume template.
	"""
	volume_template_deprecation_status = "not_deprecated";

	"""
	Server types that are compatible with this template. If null, no server
	types are filtered by this.
	"""
	volume_template_server_types_whitelist = None;

	"""
	OSTemplate credentials.
	"""
	os_template_credentials = None;

	"""
	Bootloader used for the local install of OS templates.
	"""
	os_asset_id_bootloader_local_install = None;

	"""
	Bootloader used for the OS boot of OS templates.
	"""
	os_asset_id_bootloader_os_boot = None;

	"""
	List of tags representative for the VolumeTemplate.
	"""
	volume_template_tags = [];

	"""
	The volume template version.
	"""
	volume_template_version = "0.0.0";

	"""
	Custom variables definitions. Deserializes into an object of form
	<variable_name>:<variable_value>. In case of a variable name conflict, the
	variables defined here override the variables inherited from any context
	except an VolumeTemplate OSAsset association custom variable definition
	(volume_template_os_asset_variables_json).
	"""
	volume_template_variables_json = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	The status of the volume template.
	"""
	volume_template_service_status = "active";

	"""
	The id of the drive used to create the volume template.
	"""
	volume_template_created_from_drive_id = None;

	"""
	OS bootstrap function name.
	"""
	volume_template_os_bootstrap_function_name = None;

	"""
	OS bootstrap function parameters.
	"""
	volume_template_os_bootstrap_function_params = [];

	"""
	Whether the template is experimental.
	"""
	volume_template_is_experimental = False;

	"""
	Local disk clone function name.
	"""
	volume_template_os_local_disk_clone_function_name = None;

	"""
	Stage definition id for os install.
	"""
	stage_definition_id_ansible_bundle_os_install = None;

	"""
	Stage definition id for os boot post install .
	"""
	stage_definition_id_ansible_bundle_os_boot_post_install = None;

	"""
	Whether the template is for a switch.
	"""
	volume_template_is_for_switch = False;

	"""
	NetworkOperatingSystem
	"""
	volume_template_network_operating_system = None;
