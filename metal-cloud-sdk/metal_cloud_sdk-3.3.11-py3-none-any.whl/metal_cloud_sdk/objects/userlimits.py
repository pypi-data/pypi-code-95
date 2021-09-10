# -*- coding: utf-8 -*-

class UserLimits(object):
	"""
	Contains information regarding the availability and quantity of
	Infrastructures and Infrastructure elements that a user can create.
	"""

	def __init__(self, infrastructure_active_max_count, server_type_reservation_max_quantity, server_type_reservation_max_count, infrastructure_inactive_max_count, infrastructure_deleted_max_count, infrastructure_drive_array_max_count, infrastructure_instance_array_max_count, infrastructure_container_platform_max_count, infrastructure_volume_template_experimental_allowed, infrastructure_container_cluster_zookeeper_allowed, infrastructure_container_cluster_zoomdata_allowed, infrastructure_cluster_mysql_allowed, infrastructure_container_cluster_postgresql_allowed, infrastructure_container_cluster_spark_array_allowed, infrastructure_container_cluster_sparksql_allowed, infrastructure_container_cluster_kafka_allowed, infrastructure_container_cluster_streamsets_allowed, container_platform_container_array_max_count, infrastructure_data_lake_max_count, infrastructure_data_lake_enabled, infrastructure_wan_max_count, infrastructure_lan_max_count, infrastructure_san_max_count, infrastructure_container_cluster_max_count, infrastructure_cluster_max_count, wan_subnet_ipv4_max_count, wan_subnet_ipv6_max_count, instance_array_instances_min_count, instance_array_instances_max_count, container_array_drive_arrays_min_count, container_array_drive_arrays_max_count, container_array_containers_min_count, container_array_containers_max_count, container_array_secrets_max_count, drive_array_drives_min_count, drive_array_drives_max_count, drive_max_size_mbytes, drive_min_size_mbytes, shared_drive_max_size_mbytes, shared_drive_min_size_mbytes, infrastructure_shared_drive_max_count, storage_types, user_resource_servers_max_count, user_resource_iscsi_storage_space_max_gbytes, owner_is_billable, user_ssh_keys_count_max, threshold_max_count, show_legacy_pages, show_experimental_pages, show_diagram_apps_global, show_diagram_app_cluster_type_cloudera, show_diagram_app_cluster_type_couchbase, show_diagram_app_cluster_type_datameer, show_diagram_app_cluster_type_datastax, show_diagram_app_cluster_type_elasticsearch, show_diagram_app_cluster_type_exasol, show_diagram_app_cluster_type_hortonworks, show_diagram_app_cluster_type_kubernetes, show_diagram_app_cluster_type_mapr, show_diagram_app_cluster_type_mesos, show_diagram_app_cluster_type_mysql_percona, show_diagram_app_cluster_type_splunk, show_diagram_app_cluster_type_vmware_vsphere):
		self.infrastructure_active_max_count = infrastructure_active_max_count;
		self.server_type_reservation_max_quantity = server_type_reservation_max_quantity;
		self.server_type_reservation_max_count = server_type_reservation_max_count;
		self.infrastructure_inactive_max_count = infrastructure_inactive_max_count;
		self.infrastructure_deleted_max_count = infrastructure_deleted_max_count;
		self.infrastructure_drive_array_max_count = infrastructure_drive_array_max_count;
		self.infrastructure_instance_array_max_count = infrastructure_instance_array_max_count;
		self.infrastructure_container_platform_max_count = infrastructure_container_platform_max_count;
		self.infrastructure_volume_template_experimental_allowed = infrastructure_volume_template_experimental_allowed;
		self.infrastructure_container_cluster_zookeeper_allowed = infrastructure_container_cluster_zookeeper_allowed;
		self.infrastructure_container_cluster_zoomdata_allowed = infrastructure_container_cluster_zoomdata_allowed;
		self.infrastructure_cluster_mysql_allowed = infrastructure_cluster_mysql_allowed;
		self.infrastructure_container_cluster_postgresql_allowed = infrastructure_container_cluster_postgresql_allowed;
		self.infrastructure_container_cluster_spark_array_allowed = infrastructure_container_cluster_spark_array_allowed;
		self.infrastructure_container_cluster_sparksql_allowed = infrastructure_container_cluster_sparksql_allowed;
		self.infrastructure_container_cluster_kafka_allowed = infrastructure_container_cluster_kafka_allowed;
		self.infrastructure_container_cluster_streamsets_allowed = infrastructure_container_cluster_streamsets_allowed;
		self.container_platform_container_array_max_count = container_platform_container_array_max_count;
		self.infrastructure_data_lake_max_count = infrastructure_data_lake_max_count;
		self.infrastructure_data_lake_enabled = infrastructure_data_lake_enabled;
		self.infrastructure_wan_max_count = infrastructure_wan_max_count;
		self.infrastructure_lan_max_count = infrastructure_lan_max_count;
		self.infrastructure_san_max_count = infrastructure_san_max_count;
		self.infrastructure_container_cluster_max_count = infrastructure_container_cluster_max_count;
		self.infrastructure_cluster_max_count = infrastructure_cluster_max_count;
		self.wan_subnet_ipv4_max_count = wan_subnet_ipv4_max_count;
		self.wan_subnet_ipv6_max_count = wan_subnet_ipv6_max_count;
		self.instance_array_instances_min_count = instance_array_instances_min_count;
		self.instance_array_instances_max_count = instance_array_instances_max_count;
		self.container_array_drive_arrays_min_count = container_array_drive_arrays_min_count;
		self.container_array_drive_arrays_max_count = container_array_drive_arrays_max_count;
		self.container_array_containers_min_count = container_array_containers_min_count;
		self.container_array_containers_max_count = container_array_containers_max_count;
		self.container_array_secrets_max_count = container_array_secrets_max_count;
		self.drive_array_drives_min_count = drive_array_drives_min_count;
		self.drive_array_drives_max_count = drive_array_drives_max_count;
		self.drive_max_size_mbytes = drive_max_size_mbytes;
		self.drive_min_size_mbytes = drive_min_size_mbytes;
		self.shared_drive_max_size_mbytes = shared_drive_max_size_mbytes;
		self.shared_drive_min_size_mbytes = shared_drive_min_size_mbytes;
		self.infrastructure_shared_drive_max_count = infrastructure_shared_drive_max_count;
		self.storage_types = storage_types;
		self.user_resource_servers_max_count = user_resource_servers_max_count;
		self.user_resource_iscsi_storage_space_max_gbytes = user_resource_iscsi_storage_space_max_gbytes;
		self.owner_is_billable = owner_is_billable;
		self.user_ssh_keys_count_max = user_ssh_keys_count_max;
		self.threshold_max_count = threshold_max_count;
		self.show_legacy_pages = show_legacy_pages;
		self.show_experimental_pages = show_experimental_pages;
		self.show_diagram_apps_global = show_diagram_apps_global;
		self.show_diagram_app_cluster_type_cloudera = show_diagram_app_cluster_type_cloudera;
		self.show_diagram_app_cluster_type_couchbase = show_diagram_app_cluster_type_couchbase;
		self.show_diagram_app_cluster_type_datameer = show_diagram_app_cluster_type_datameer;
		self.show_diagram_app_cluster_type_datastax = show_diagram_app_cluster_type_datastax;
		self.show_diagram_app_cluster_type_elasticsearch = show_diagram_app_cluster_type_elasticsearch;
		self.show_diagram_app_cluster_type_exasol = show_diagram_app_cluster_type_exasol;
		self.show_diagram_app_cluster_type_hortonworks = show_diagram_app_cluster_type_hortonworks;
		self.show_diagram_app_cluster_type_kubernetes = show_diagram_app_cluster_type_kubernetes;
		self.show_diagram_app_cluster_type_mapr = show_diagram_app_cluster_type_mapr;
		self.show_diagram_app_cluster_type_mesos = show_diagram_app_cluster_type_mesos;
		self.show_diagram_app_cluster_type_mysql_percona = show_diagram_app_cluster_type_mysql_percona;
		self.show_diagram_app_cluster_type_splunk = show_diagram_app_cluster_type_splunk;
		self.show_diagram_app_cluster_type_vmware_vsphere = show_diagram_app_cluster_type_vmware_vsphere;


	"""
	The maximum number of active Infrastructures that a user can own.
	"""
	infrastructure_active_max_count = None;

	"""
	The maximum number of server reservations (limit for the quantity param).
	"""
	server_type_reservation_max_quantity = None;

	"""
	The maximum number of server reservations.
	"""
	server_type_reservation_max_count = None;

	"""
	The maximum number of ordered Infrastructures that a user can own.
	"""
	infrastructure_inactive_max_count = None;

	"""
	The maximum number of deleted Infrastructures per user.
	"""
	infrastructure_deleted_max_count = None;

	"""
	The maximum number of Drive Arrays that can be created on a single
	Infrastructure.
	"""
	infrastructure_drive_array_max_count = None;

	"""
	The maximum number of Instance Arrays that can be created on a single
	Infrastructure.
	"""
	infrastructure_instance_array_max_count = None;

	"""
	The maximum number of Container Platforms that can be created on a single
	Infrastructure.
	"""
	infrastructure_container_platform_max_count = None;

	"""
	1 if an experimental volume_template is allowed on a infrastructure, 0
	otherwise
	"""
	infrastructure_volume_template_experimental_allowed = None;

	"""
	1 if a Zookeeper container cluster is allowed on a infrastructure, 0
	otherwise
	"""
	infrastructure_container_cluster_zookeeper_allowed = None;

	"""
	1 if a Zoomdata container cluster is allowed on a infrastructure, 0
	otherwise
	"""
	infrastructure_container_cluster_zoomdata_allowed = None;

	"""
	1 if a Mysql cluster is allowed on a infrastructure, 0 otherwise
	"""
	infrastructure_cluster_mysql_allowed = None;

	"""
	1 if a PostgreSQL container cluster is allowed on a infrastructure, 0
	otherwise
	"""
	infrastructure_container_cluster_postgresql_allowed = None;

	"""
	Specifies whether the user (or his delegates) can create SparkArrays on his
	Infrastructures.
	"""
	infrastructure_container_cluster_spark_array_allowed = None;

	"""
	1 if a SparkSQL container cluster is allowed on a infrastructure, 0
	otherwise
	"""
	infrastructure_container_cluster_sparksql_allowed = None;

	"""
	1 if a Kafka container cluster is allowed on a infrastructure, 0 otherwise
	"""
	infrastructure_container_cluster_kafka_allowed = None;

	"""
	1 if a StreamSets container cluster is allowed on a infrastructure, 0
	otherwise
	"""
	infrastructure_container_cluster_streamsets_allowed = None;

	"""
	The maximum number of Container Arrays that can be created on a single
	ContainerPlatform.
	"""
	container_platform_container_array_max_count = None;

	"""
	The maximum number of Data Lakes that can be created on a single
	Infrastructure.
	"""
	infrastructure_data_lake_max_count = None;

	"""
	Specifies whether the user (or his delegates) can create Data Lakes on his
	Infrastructures.
	"""
	infrastructure_data_lake_enabled = None;

	"""
	The maximum number of WAN networks that can be created on a single
	Infrastructure.
	"""
	infrastructure_wan_max_count = None;

	"""
	The maximum number of LAN networks that can be created on a single
	Infrastructure.
	"""
	infrastructure_lan_max_count = None;

	"""
	The maximum number of SAN networks that can be created on a single
	Infrastructure.
	"""
	infrastructure_san_max_count = None;

	"""
	The maximum number of Container Clusters that can be created on a single
	Infrastructure.
	"""
	infrastructure_container_cluster_max_count = None;

	"""
	The maximum number of Clusters that can be created on a single
	Infrastructure.
	"""
	infrastructure_cluster_max_count = None;

	"""
	The maximum number of IPv4 addresses that can be provisioned on a single WAN
	subnet.
	"""
	wan_subnet_ipv4_max_count = None;

	"""
	The maximum number of IPv6 addresses that can be provisioned on a single WAN
	subnet.
	"""
	wan_subnet_ipv6_max_count = None;

	"""
	The minimum number of Instances that an Instance Array can have at any given
	time.
	"""
	instance_array_instances_min_count = None;

	"""
	The maximum number of Instances that an Instance Array can have at any given
	time.
	"""
	instance_array_instances_max_count = None;

	"""
	The minimum number of Drive Arrays that can be attached to an Instance Array
	at any given time.
	"""
	container_array_drive_arrays_min_count = None;

	"""
	The maximum number of Drive Arrays that can be attached to an Instance Array
	at any given time.
	"""
	container_array_drive_arrays_max_count = None;

	"""
	The minimum number of Drive Arrays that can be attached to an Instance Array
	at any given time.
	"""
	container_array_containers_min_count = None;

	"""
	The maximum number of Drive Arrays that can be attached to an Instance Array
	at any given time.
	"""
	container_array_containers_max_count = None;

	"""
	The maximum number of Secrets that can asociated with a container array.
	"""
	container_array_secrets_max_count = None;

	"""
	The minimum number of Drives that a Drive Array can have at any given time.
	"""
	drive_array_drives_min_count = None;

	"""
	The maximum number of Drives that a Drive Array can have at any given time.
	"""
	drive_array_drives_max_count = None;

	"""
	The maximum size (in megabytes) that a Drive can have at any given time.
	"""
	drive_max_size_mbytes = None;

	"""
	The minimum size (in megabytes) that a Drive can have at any given time.
	"""
	drive_min_size_mbytes = None;

	"""
	The maximum size (in megabytes) that a Shared Drive can have at any given
	time.
	"""
	shared_drive_max_size_mbytes = None;

	"""
	The minimum size (in megabytes) that a Shared Drive can have at any given
	time.
	"""
	shared_drive_min_size_mbytes = None;

	"""
	The maximum number of Shared Drives that can be created on a single
	Infrastructure.
	"""
	infrastructure_shared_drive_max_count = None;

	"""
	An array listing the available storage types that the user can utilize.
	"""
	storage_types = [];

	"""
	The maximum number of servers a specific user account can allocate. Over all
	infrastructures.
	"""
	user_resource_servers_max_count = None;

	"""
	The maximum iSCSI storage space (Drive, SharedDrive) a specific user account
	can allocate. Over all infrastructures.
	"""
	user_resource_iscsi_storage_space_max_gbytes = None;

	"""
	Specifies whether the user is billable (can deploy infrastructures) or not.
	"""
	owner_is_billable = None;

	"""
	The maximum number of ssh keys.
	"""
	user_ssh_keys_count_max = None;

	"""
	The maximum number of thresholds.
	"""
	threshold_max_count = None;

	"""
	Specifies whether the user should see some legacy pages in the user
	interface or not.
	"""
	show_legacy_pages = None;

	"""
	Specifies whether the user should see some experimental pages in the user
	interface or not.
	"""
	show_experimental_pages = None;

	"""
	Specifies whether the user should see the app pop-over button in the
	diagram.
	"""
	show_diagram_apps_global = None;

	"""
	Specifies whether the user should see the Cloudera app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_cloudera = None;

	"""
	Specifies whether the user should see the Couchbase app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_couchbase = None;

	"""
	Specifies whether the user should see the Datameer app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_datameer = None;

	"""
	Specifies whether the user should see the Datastax app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_datastax = None;

	"""
	Specifies whether the user should see the ElasticSearch app in the app
	pop-over (diagram).
	"""
	show_diagram_app_cluster_type_elasticsearch = None;

	"""
	Specifies whether the user should see the Exasol app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_exasol = None;

	"""
	Specifies whether the user should see the HortonWorks app in the app
	pop-over (diagram).
	"""
	show_diagram_app_cluster_type_hortonworks = None;

	"""
	Specifies whether the user should see the Kubernetes app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_kubernetes = None;

	"""
	Specifies whether the user should see the Mapr app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_mapr = None;

	"""
	Specifies whether the user should see the Mesos app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_mesos = None;

	"""
	Specifies whether the user should see the MySQL Percona app in the app
	pop-over (diagram).
	"""
	show_diagram_app_cluster_type_mysql_percona = None;

	"""
	Specifies whether the user should see the splunk app in the app pop-over
	(diagram).
	"""
	show_diagram_app_cluster_type_splunk = None;

	"""
	Specifies whether the user should see the VMWARE vSphere app in the app
	pop-over (diagram).
	"""
	show_diagram_app_cluster_type_vmware_vsphere = None;

	"""
	The schema type
	"""
	type = None;
