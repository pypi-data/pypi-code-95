import inspect
import json
import importlib

class Constants(object):

	"""
	* Metal Cloud, API v2.7.8
	"""
	AFC_GROUP_TYPE_INFRASTRUCTURE_DEPLOYMENT="infrastructure_deployment"
	AFC_GROUP_TYPE_SERVER_CLEANUP="server_cleanup"
	AFC_GROUP_TYPE_SERVER_REGISTER="server_register"
	AFC_GROUP_TYPE_SERVERS_CLEANUP_BATCH="servers_cleanup_batch"
	AFC_OPTION_ALL="all"
	AFC_OPTION_EVERYTHING="everything"
	AFC_OPTION_NONE="none"
	AFC_STATUS_NOT_CALLED="not_called"
	AFC_STATUS_RETURNED_SUCCESS="returned_success"
	AFC_STATUS_RUNNING="running"
	AFC_STATUS_SKIPPED="skipped"
	AFC_STATUS_THROWN_ERROR="thrown_error"
	AFC_STATUS_THROWN_ERROR_RETRYING="thrown_error_retrying"
	AFC_STATUS_THROWN_ERROR_SILENCED="thrown_error_silenced"
	AFC_TYPE_ASYNCHRONOUS="asynchronous"
	AFC_TYPE_DEBUG_NORMAL="debug_normal"
	AFC_TYPE_DEBUG_RPC_SERVER="debug_rpc_server"
	AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_CREATE_SECONDARY_DRIVE="create_secondary_drive"
	AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_DELETE_SECONDARY_DRIVE="delete_secondary_drive"
	AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_EXPAND="expand_drive"
	AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_REPLACE_BOOT_DRIVE="replace_boot_drive"
	CHILD_DATACENTER_MANAGEMENT_SUBNET="managementSubnet"
	CHILD_DATACENTER_MANAGEMENT_SUBNET_GATEWAY_INDEX="managementSubnetGatewayIndex"
	CHILD_DATACENTER_MANAGEMENT_SUBNET_MASK="managementSubnetMask"
	CHILD_DATACENTER_MANAGEMENT_SUBNET_RANGE="managementSubnetRange"
	CISCO_ACI_POD_ID=1
	CLUSTER_TYPE_CLOUDERA="cloudera"
	CLUSTER_TYPE_CONTAINER_PLATFORM_KUBERNETES="container_platform_kubernetes"
	CLUSTER_TYPE_CONTAINER_PLATFORM_MESOS="container_platform_mesos"
	CLUSTER_TYPE_COUCHBASE="couchbase"
	CLUSTER_TYPE_DATAMEER="datameer"
	CLUSTER_TYPE_DATASTAX="datastax"
	CLUSTER_TYPE_ELASTICSEARCH="elasticsearch"
	CLUSTER_TYPE_ELASTICSEARCH_LEGACY="elasticsearch_legacy"
	CLUSTER_TYPE_EXASOL="exasol"
	CLUSTER_TYPE_HDFS="hdfs"
	CLUSTER_TYPE_HORTONWORKS="hortonworks"
	CLUSTER_TYPE_KUBERNETES="kubernetes"
	CLUSTER_TYPE_MAPR="mapr"
	CLUSTER_TYPE_MAPR_LEGACY="mapr_legacy"
	CLUSTER_TYPE_MESOS="mesos"
	CLUSTER_TYPE_MYSQL_PERCONA="mysql_percona"
	CLUSTER_TYPE_SPLUNK="splunk"
	CLUSTER_TYPE_TABLEAU="tableau"
	CLUSTER_TYPE_VANILLA="vanilla"
	CLUSTER_TYPE_VMWARE_VSPHERE="vmware_vsphere"
	COLLAPSE_ARRAY_ROW_SPAN="array_row_span"
	COLLAPSE_ARRAY_SUBROWS="array_subrows"
	COLLAPSE_ARRAY_SUBROWS_TABLE="array_subrows_table"
	COLLAPSE_AUTOCOMPLETE_DICTIONARY="autocomplete_dictionary"
	COLLAPSE_HTML_ROWS_ARRAY="html_rows_array"
	COLLAPSE_HTML_ROWS_STRING="html_rows_string"
	COLLAPSE_NONE="none"
	CONTAINER_ARRAY_ACTION_EXECUTE_COMMAND="execute_command"
	CONTAINER_ARRAY_ACTION_HTTP_GET="http_get"
	CONTAINER_ARRAY_ACTION_TCP_SOCKET="tcp_socket"
	CONTAINER_ARRAY_INTERFACE_INDEX_0=0
	CONTAINER_ARRAY_INTERFACE_INDEX_1=1
	CONTAINER_ARRAY_INTERFACE_INDEX_2=2
	CONTAINER_CLUSTER_TYPE_ELASTICSEARCH="elasticsearch"
	CONTAINER_CLUSTER_TYPE_KAFKA="kafka"
	CONTAINER_CLUSTER_TYPE_POSTGRESQL="postgresql"
	CONTAINER_CLUSTER_TYPE_SPARK="spark"
	CONTAINER_CLUSTER_TYPE_SPARKSQL="sparksql"
	CONTAINER_CLUSTER_TYPE_STREAMSETS="streamsets"
	CONTAINER_CLUSTER_TYPE_VANILLA="vanilla"
	CONTAINER_CLUSTER_TYPE_ZOOKEEPER="zookeeper"
	CONTAINER_CLUSTER_TYPE_ZOOMDATA="zoomdata"
	CONTAINER_STATUS_PHASE_FAILED="failed"
	CONTAINER_STATUS_PHASE_PENDING="pending"
	CONTAINER_STATUS_PHASE_RUNNING="running"
	CONTAINER_STATUS_PHASE_SUCCEEDED="succeeded"
	CONTAINER_STATUS_PHASE_UNKNOWN="unknown"
	DATA_LAKE_TYPE_HDFS="hdfs"
	DATACENTER_CONFIG_SWITCH_PROVISIONER_LAN="LANProvisioner"
	DATACENTER_CONFIG_SWITCH_PROVISIONER_SDN="SDNProvisioner"
	DATACENTER_CONFIG_SWITCH_PROVISIONER_VLAN="VLANProvisioner"
	DATACENTER_CONFIG_SWITCH_PROVISIONER_VPLS="VPLSProvisioner"
	DATACENTER_CONFIG_SWITCH_PROVISIONER_VXLAN="VXLANProvisioner"
	DISK_TYPE_AUTO="auto"
	DISK_TYPE_HDD="HDD"
	DISK_TYPE_NONE="none"
	DISK_TYPE_NVME="NVME"
	DISK_TYPE_SSD="SSD"
	DNS_RECORD_TYPE_A="A"
	DNS_RECORD_TYPE_AAAA="AAAA"
	DNS_RECORD_TYPE_CNAME="CNAME"
	DNS_RECORD_TYPE_MX="MX"
	DNS_RECORD_TYPE_NS="NS"
	DNS_RECORD_TYPE_PTR="PTR"
	DNS_RECORD_TYPE_SOA="SOA"
	DNS_RECORD_TYPE_TXT="TXT"
	DRIVE_STORAGE_TYPE_AUTO="auto"
	DRIVE_STORAGE_TYPE_DUMMY="dummy"
	DRIVE_STORAGE_TYPE_ISCSI_HDD="iscsi_hdd"
	DRIVE_STORAGE_TYPE_ISCSI_SSD="iscsi_ssd"
	DRIVE_STORAGE_TYPE_NONE="none"
	ENDPOINT_PHPUNIT="phpunit"
	EVENT_SEVERITY_DEBUG="debug"
	EVENT_SEVERITY_IMPORTANT="important"
	EVENT_SEVERITY_INFO="info"
	EVENT_SEVERITY_SECURITY="security"
	EVENT_SEVERITY_SUCCESS="success"
	EVENT_SEVERITY_TRIGGER="trigger"
	EVENT_SEVERITY_WARNING="warning"
	EVENT_VISIBILITY_PRIVATE="private"
	EVENT_VISIBILITY_PUBLIC="public"
	FILESYSTEM_NAVIGATOR_DRIVER_TYPE_DATASET_README="dataset_readme"
	FILESYSTEM_NAVIGATOR_DRIVER_TYPE_WEBHDFS="webhdfs"
	FILESYSTEM_TYPE_EXT2="ext2"
	FILESYSTEM_TYPE_EXT3="ext3"
	FILESYSTEM_TYPE_EXT4="ext4"
	FILESYSTEM_TYPE_NONE="none"
	FILESYSTEM_TYPE_XFS="xfs"
	FIREWALL_RULE_IP_ADDRESS_TYPE_IPV4="ipv4"
	FIREWALL_RULE_IP_ADDRESS_TYPE_IPV6="ipv6"
	FIREWALL_RULE_PROTOCOL_ALL="all"
	FIREWALL_RULE_PROTOCOL_ICMP="icmp"
	FIREWALL_RULE_PROTOCOL_TCP="tcp"
	FIREWALL_RULE_PROTOCOL_UDP="udp"
	GUEST_DISPLAY_NAME="Guest"
	HARDWARE_CONFIGURATIONS_PREDEFINED="predefined"
	HARDWARE_CONFIGURATIONS_USER_PREDEFINED="user_predefined"
	HEALTH_CHECK_STATUS_ERROR="error"
	HEALTH_CHECK_STATUS_SUCCESS="success"
	HEALTH_CHECK_STATUS_WARNING="warning"
	INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_AVOID="avoid"
	INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_DISALLOW="disallow"
	INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_EQUAL="equal"
	INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_PREFER="prefer"
	INFRASTRUCTURE_STAGE_FINAL_CALLBACK="infrastructure_stage_final_callback"
	INFRASTRUCTURE_STAGE_SWITCH_PROVISION="infrastructure_stage_switch_provision"
	INSTANCE_ARRAY_BOOT_METHOD_LOCAL_DRIVES="local_drives"
	INSTANCE_ARRAY_BOOT_METHOD_PXE_ISCSI="pxe_iscsi"
	INSTANCE_ARRAY_INTERFACE_INDEX_0=0
	INSTANCE_ARRAY_INTERFACE_INDEX_1=1
	INSTANCE_ARRAY_INTERFACE_INDEX_2=2
	INSTANCE_ARRAY_INTERFACE_INDEX_3=3
	INSTANCE_OS_READY_STATUS_CALLED="called"
	INSTANCE_OS_READY_STATUS_CALLED_WITH_WAIT_FOR_POWEROFF="called_with_wait_for_poweroff"
	INSTANCE_OS_READY_STATUS_NOT_CALLED="not_called"
	IP_TYPE_IPV4="ipv4"
	IP_TYPE_IPV6="ipv6"
	IPC_HEALTH_CHECK="health_check"
	JWT_COOKIE_TYPE_HTTPONLY="HTTPOnly"
	JWT_COOKIE_TYPE_SCRIPT="script"
	LICENSE_MICROSOFT_CORE_MIN_COUNT=16
	LICENSE_MICROSOFT_PROCESSOR_MIN_COUNT=8
	LICENSE_TYPE_CLOUDERA="cloudera"
	LICENSE_TYPE_COUCHBASE="couchbase"
	LICENSE_TYPE_MAPR="mapr"
	LICENSE_TYPE_NONE="none"
	LICENSE_TYPE_WINDOWS_SERVER="windows_server"
	LICENSE_TYPE_WINDOWS_SERVER_STANDARD="windows_server_standard"
	LICENSE_UTILIZATION_TYPE_DEMAND="demand"
	LICENSE_UTILIZATION_TYPE_NONE="none"
	LICENSE_UTILIZATION_TYPE_SUBSCRIPTION="subscription"
	LIMITS_BILLABLE="billable"
	LIMITS_DEFAULT="default"
	LIMITS_DEMO="demo"
	LIMITS_DEVELOPER="developer"
	LOAD_BALANCER_CRESCENDO="crescendo"
	LOAD_BALANCER_HAPROXY="haproxy"
	NETWORK_CUSTOM_TYPE_SAAS="saas"
	NETWORK_EQUIPMENT_STATUS_ACTIVE="active"
	NETWORK_EQUIPMENT_STATUS_DECOMMISSIONED="decommissioned"
	NETWORK_SUSPEND_STATUS_NOT_SUSPENDED="not_suspended"
	NETWORK_SUSPEND_STATUS_SUSPENDED="suspended"
	NETWORK_SUSPEND_STATUS_SUSPENDING="suspending"
	NETWORK_SUSPEND_STATUS_UNSUSPENDING="unsuspending"
	NETWORK_TYPE_LAN="lan"
	NETWORK_TYPE_SAN="san"
	NETWORK_TYPE_WAN="wan"
	NODE_MEASUREMENT_TYPE_CPU_LOAD="cpu_load"
	NODE_MEASUREMENT_TYPE_DISK_SIZE="disk_size"
	NODE_MEASUREMENT_TYPE_DISK_USED="disk_used"
	NODE_MEASUREMENT_TYPE_NETWORK_INTERFACE_INPUT="net_if_input"
	NODE_MEASUREMENT_TYPE_NETWORK_INTERFACE_OUTPUT="net_if_output"
	NODE_MEASUREMENT_TYPE_RAM_SIZE="ram_size"
	NODE_MEASUREMENT_TYPE_RAM_USED="ram_used"
	OPERATING_SYSTEM_CENTOS="CentOS"
	OPERATING_SYSTEM_ESXI="ESXi"
	OPERATING_SYSTEM_NONE="none"
	OPERATING_SYSTEM_RHEL="RHEL"
	OPERATING_SYSTEM_UBUNTU="Ubuntu"
	OPERATING_SYSTEM_WINDOWS="Windows"
	OPERATION_TYPE_CREATE="create"
	OPERATION_TYPE_DELETE="delete"
	OPERATION_TYPE_EDIT="edit"
	OPERATION_TYPE_ORDERED="ordered"
	OPERATION_TYPE_START="start"
	OPERATION_TYPE_STOP="stop"
	OPERATION_TYPE_SUSPEND="suspend"
	OS_ASSET_USAGE_BOOTLOADER="bootloader"
	PERMISSION_ADMIN_MAINTENANCE_WRITE="admin_maintenance_write"
	PERMISSION_AFC_READ="afc_read"
	PERMISSION_AFC_WRITE="afc_write"
	PERMISSION_CLOUD_INIT_READ="cloudinit_read"
	PERMISSION_CLUSTER_READ="cluster_read"
	PERMISSION_CLUSTER_WRITE="cluster_write"
	PERMISSION_CONTAINER_PLATFORM_READ="container_platform_read"
	PERMISSION_CONTAINER_PLATFORM_WRITE="container_platform_write"
	PERMISSION_DATACENTER_READ="datacenter_read"
	PERMISSION_DATACENTER_WRITE="datacenter_write"
	PERMISSION_DATALAKE_READ="datalake_read"
	PERMISSION_DATALAKE_WRITE="datalake_write"
	PERMISSION_DATASET_READ="dataset_read"
	PERMISSION_DATASET_WRITE="dataset_write"
	PERMISSION_EMAILS_WRITE="emails_write"
	PERMISSION_EVENTS_READ="events_read"
	PERMISSION_EVENTS_WRITE="events_write"
	PERMISSION_FIRMWARE_UPGRADE_READ="firmware_upgrade_read"
	PERMISSION_FIRMWARE_UPGRADE_WRITE="firmware_upgrade_write"
	PERMISSION_FRANCHISES_WRITE="franchises_write"
	PERMISSION_INFRASTRUCTURES_READ="infrastructures_read"
	PERMISSION_INFRASTRUCTURES_WRITE="infrastructures_write"
	PERMISSION_LICENSES_READ="licenses_read"
	PERMISSION_LICENSES_WRITE="licenses_write"
	PERMISSION_MAINTENANCE_READ="maintenance_read"
	PERMISSION_MAINTENANCE_WRITE="maintenance_write"
	PERMISSION_MONITORING_AGENT_READ="monitoring_agent_read"
	PERMISSION_MONITORING_AGENT_WRITE="monitoring_agent_write"
	PERMISSION_PRICES_READ="prices_read"
	PERMISSION_PRICES_WRITE="prices_write"
	PERMISSION_RESOURCES_WRITE="resources_write"
	PERMISSION_SERVER_TYPES_READ="server_types_read"
	PERMISSION_SERVERS_READ="servers_read"
	PERMISSION_SERVERS_WRITE="servers_write"
	PERMISSION_SKIP_AUTHENTICATOR="skip_authenticator"
	PERMISSION_SKIP_USER_LIMITS="skip_user_limits"
	PERMISSION_STORAGE_READ="storage_read"
	PERMISSION_STORAGE_WRITE="storage_write"
	PERMISSION_SUBNETS_READ="subnets_read"
	PERMISSION_SUBNETS_WRITE="subnets_write"
	PERMISSION_SUSPEND_REASONS_WRITE="suspend_reasons_write"
	PERMISSION_SWITCHES_READ="switches_read"
	PERMISSION_SWITCHES_WRITE="switches_write"
	PERMISSION_TEMPLATES_READ="templates_read"
	PERMISSION_TEMPLATES_WRITE="templates_write"
	PERMISSION_THRESHOLD_READ="threshold_read"
	PERMISSION_THRESHOLD_WRITE="threshold_write"
	PERMISSION_USERS_AND_PERMISSIONS_READ="users_and_permissions_read"
	PERMISSION_USERS_AND_PERMISSIONS_WRITE="users_and_permissions_write"
	PERMISSION_UTILIZATION_REPORTS_READ="utilization_reports_read"
	PERMISSION_VARIABLES_AND_SECRETS_READ="variables_and_secrets_read"
	PERMISSION_VARIABLES_AND_SECRETS_WRITE="variables_and_secrets_write"
	PERMISSION_WORKFLOWS_READ="workflows_read"
	PERMISSION_WORKFLOWS_WRITE="workflows_write"
	PRICES_PRIVATE_DATACENTER_KEY="private-dc-default"
	PROVISION_STAGE_PREPROVISION_SYNCHRONOUS="preprovision_synchronous"
	PROVISION_STATUS_FINISHED="finished"
	PROVISION_STATUS_NOT_STARTED="not_started"
	PROVISION_STATUS_ONGOING="ongoing"
	REDIS_CRITICAL_TOKEN="critical"
	REDIS_INVALID_TOKEN="invalid"
	REDIS_TOKEN="token"
	REDIS_VALID_TOKEN="valid"
	RESERVATION_DRIVE="drive"
	RESERVATION_INSTALLMENT_STATUS_ACTIVE="active"
	RESERVATION_INSTALLMENT_STATUS_STOPPED="stopped"
	RESERVATION_SERVER_TYPE="server_type"
	RESERVATION_STATUS_ACTIVE="active"
	RESERVATION_STATUS_STOPPED="stopped"
	RESERVATION_SUBNET="subnet"
	RESOURCE_TYPE_CHASSIS_RACK="chassis_rack"
	RESOURCE_TYPE_NETWORK_EQUIPMENT="network_equipment"
	RESOURCE_TYPE_NETWORK_EQUIPMENT_CONTROLLER="network_equipment_controllers"
	RESOURCE_TYPE_SERVER="server"
	RESOURCE_TYPE_SERVER_INTERFACE="server_interface"
	RESOURCE_TYPE_SUBNET_POOL="subnet_pool"
	RESOURCE_TYPE_VOLUME="volume"
	RESOURCE_UTILIZATION_TYPE_DEMAND="demand"
	RESOURCE_UTILIZATION_TYPE_RESERVATION="reservation"
	SAMBA_SERVER_HOSTNAME="samba_server_hostname"
	SAMBA_SERVER_IP="samba_server_ip"
	SAMBA_SERVER_PASSWORD="samba_server_password"
	SAMBA_SERVER_USERNAME="samba_server_username"
	SAMBA_SERVER_WINDOWS_KIT_SHARE_NAME="samba_server_windows_kit_share_name"
	SDN_LAN_RANGE="LANVLANRange"
	SDN_QUARANTINE_VLAN_ID="quarantineVLANID"
	SDN_SAN_RANGE="SANVLANRange"
	SDN_WAN_RANGE="WANVLANRange"
	SERVER_BOOT_TYPE_CLASSIC="classic"
	SERVER_BOOT_TYPE_UEFI="uefi"
	SERVER_CLASS_BIGDATA="bigdata"
	SERVER_CLASS_HDFS="hdfs"
	SERVER_CLASS_UNKNOWN="unknown"
	SERVER_DHCP_STATUS_ALLOW="allow_requests"
	SERVER_DHCP_STATUS_ANSIBLE="ansible_provision"
	SERVER_DHCP_STATUS_DENY="deny_requests"
	SERVER_DHCP_STATUS_QUARANTINE="quarantine"
	SERVER_DISK_INSTALLED="installed"
	SERVER_DISK_SPARE="spare"
	SERVER_EDIT_TYPE_AVAILABILITY="availability"
	SERVER_EDIT_TYPE_COMPLETE="complete"
	SERVER_EDIT_TYPE_INVENTORY="inventory"
	SERVER_EDIT_TYPE_IPMI="ipmi"
	SERVER_EDIT_TYPE_RACK="rack"
	SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_ACCEPT="accept"
	SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_ACCEPT_WITH_CONFIRMATION="accept_with_confirmation"
	SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_DENY="deny"
	SERVER_FIRMWARE_UPGRADE_POLICY_STATUS_ACTIVE="active"
	SERVER_FIRMWARE_UPGRADE_POLICY_STATUS_STOPPED="stopped"
	SERVER_INTERFACE_ADD_ON_HBA="hba"
	SERVER_INTERFACE_ADD_ON_OFFLOAD="offload"
	SERVER_POWER_STATUS_NONE="none"
	SERVER_POWER_STATUS_OFF="off"
	SERVER_POWER_STATUS_ON="on"
	SERVER_POWER_STATUS_RESET="reset"
	SERVER_POWER_STATUS_SOFT="soft"
	SERVER_POWER_STATUS_UNKNOWN="unknown"
	SERVER_STATUS_AVAILABLE="available"
	SERVER_STATUS_AVAILABLE_RESERVED="available_reserved"
	SERVER_STATUS_CLEANING="cleaning"
	SERVER_STATUS_CLEANING_REQUIRED="cleaning_required"
	SERVER_STATUS_DECOMISSIONED="decommissioned"
	SERVER_STATUS_DEFECTIVE="defective"
	SERVER_STATUS_REGISTERING="registering"
	SERVER_STATUS_REMOVED_FROM_RACK="removed_from_rack"
	SERVER_STATUS_UNAVAILABLE="unavailable"
	SERVER_STATUS_UPDATING_FIRMWARE="updating_firmware"
	SERVER_STATUS_USED="used"
	SERVER_STATUS_USED_DIAGNOSTICS="used_diagnostics"
	SERVER_STATUS_USED_REGISTERING="used_registering"
	SERVER_TYPE_BOOT_HYBRID_DEFAULT_LEGACY="hybrid_default_legacy"
	SERVER_TYPE_BOOT_HYBRID_DEFAULT_UEFI="hybrid_default_uefi"
	SERVER_TYPE_BOOT_LEGACY_ONLY="legacy_only"
	SERVER_TYPE_BOOT_UEFI_ONLY="uefi_only"
	SERVICE_STATUS_ACTIVE="active"
	SERVICE_STATUS_DELETED="deleted"
	SERVICE_STATUS_ORDERED="ordered"
	SERVICE_STATUS_STOPPED="stopped"
	SERVICE_STATUS_SUSPENDED="suspended"
	SHARED_DRIVE_CONNECTED="connected"
	SHARED_DRIVE_CONNECTED_CONTAINER_ARRAY="connected_container_array"
	SHARED_DRIVE_DISCONNECTED="disconnected"
	SHARED_DRIVE_DISCONNECTED_CONTAINER_ARRAY="disconnected_container_array"
	SHARED_DRIVE_WILL_BE_CONNECTED="will_be_connected"
	SHARED_DRIVE_WILL_BE_CONNECTED_CONTAINER_ARRAY="will_be_connected_container_array"
	SHARED_DRIVE_WILL_BE_DISCONNECTED="will_be_disconnected"
	SHARED_DRIVE_WILL_BE_DISCONNECTED_CONTAINER_ARRAY="will_be_disconnected_container_array"
	SOLUTION_TYPE_DATALAB_SPARK="datalab_spark"
	SQL_KEYWORD_NULL="SQL_KEYWORD_NULL"
	SSH_DSA_ALGORITHM_IDENTIFIER="ssh-dsa"
	SSH_DSS_ALGORITHM_IDENTIFIER="ssh-dss"
	SSH_KEY_FORMAT_OPENSSH="openssh"
	SSH_KEY_FORMAT_PKCS1="pkcs#1"
	SSH_KEY_FORMAT_PKCS8="pkcs#8"
	SSH_KEY_FORMAT_SSH2="ssh2"
	SSH_RSA_ALGORITHM_IDENTIFIER="ssh-rsa"
	STAGE_DEFINITION_TYPE_ANSIBLE_BUNDLE="AnsibleBundle"
	STAGE_DEFINITION_TYPE_API_CALL="APICall"
	STAGE_DEFINITION_TYPE_COPY="Copy"
	STAGE_DEFINITION_TYPE_EXEC_SSH="SSHExec"
	STAGE_DEFINITION_TYPE_HTTP_REQUEST="HTTPRequest"
	STAGE_DEFINITION_TYPE_JAVASCRIPT="JavaScript"
	STAGE_DEFINITION_TYPE_WORKFLOW_REFERENCE="WorkflowReference"
	STAGE_EXEC_POST_DEPLOY="post_deploy"
	STAGE_EXEC_PRE_DEPLOY="pre_deploy"
	STORAGE_DRIVE="Drive"
	STORAGE_DRIVER_DUMMY="dummy_driver"
	STORAGE_DRIVER_FMSA="bigstep_storage"
	STORAGE_DRIVER_HP_MSA_1040="hp_msa_1040"
	STORAGE_DRIVER_NEXENTA3="nexenta3"
	STORAGE_DRIVER_NEXENTA4="nexenta4"
	STORAGE_DRIVER_UNITY="unity_storage"
	STORAGE_POOL_STATUS_ACTIVE="active"
	STORAGE_POOL_STATUS_DELETED="deleted"
	STORAGE_TEMPLATE="Template"
	SUBNET_DESTINATION_DISABLED="disabled"
	SUBNET_DESTINATION_LAN="lan"
	SUBNET_DESTINATION_OOB="oob"
	SUBNET_DESTINATION_SAN="san"
	SUBNET_DESTINATION_TMP="tmp"
	SUBNET_DESTINATION_WAN="wan"
	SUBNET_TYPE_IPV4="ipv4"
	SUBNET_TYPE_IPV6="ipv6"
	SWITCH_DEVICE_DRIVER_5800="hp5800"
	SWITCH_DEVICE_DRIVER_5900="hp5900"
	SWITCH_DEVICE_DRIVER_CISCO_ACI_51="cisco_aci51"
	SWITCH_DEVICE_DRIVER_CUMULUS_LINUX_42="cumulus42"
	SWITCH_DEVICE_LEAF="leaf"
	SWITCH_DEVICE_LINK_MLAG_BACKUP_IP="backupIp"
	SWITCH_DEVICE_LINK_MLAG_MAC_ADDRESS="MACAddress"
	SWITCH_DEVICE_LINK_MLAG_PHYSICAL_INTERFACES="physicalInterfaces"
	SWITCH_DEVICE_LINK_TYPE_MLAG="mlag"
	SWITCH_DEVICE_NORTH="north"
	SWITCH_DEVICE_OTHER="other"
	SWITCH_DEVICE_PROVISIONER_LAN="lan"
	SWITCH_DEVICE_PROVISIONER_SDN="sdn"
	SWITCH_DEVICE_PROVISIONER_VLAN="vlan"
	SWITCH_DEVICE_PROVISIONER_VPLS="vpls"
	SWITCH_DEVICE_PROVISIONER_VXLAN="vxlan"
	SWITCH_DEVICE_SDN_APPLICATION_PROFILE="ApplicationProfile"
	SWITCH_DEVICE_SDN_BRIDGE_DOMAIN="BridgeDomain"
	SWITCH_DEVICE_SDN_CONTRACT="Contract"
	SWITCH_DEVICE_SDN_CONTRACT_FILTER="ContractFilter"
	SWITCH_DEVICE_SDN_CONTRACT_SUBJECT="ContractSubject"
	SWITCH_DEVICE_SDN_DHCP_RELAY_POLICY="DHCPRelayPolicy"
	SWITCH_DEVICE_SDN_DHCP_RELAY_PROVIDER="DHCPRelayProvider"
	SWITCH_DEVICE_SDN_EPG="EPG"
	SWITCH_DEVICE_SDN_IMPORTED_CONTRACT="ImportedContract"
	SWITCH_DEVICE_SDN_PHYSICAL_DOMAIN="PhysicalDomain"
	SWITCH_DEVICE_SDN_SUBNET="Subnet"
	SWITCH_DEVICE_SDN_TENANT="Tenant"
	SWITCH_DEVICE_SDN_VLAN_POOL="VLANPool"
	SWITCH_DEVICE_SDN_VRF="VRF"
	SWITCH_DEVICE_SPINE="spine"
	SWITCH_DEVICE_TOR="tor"
	URL_TYPE_HDFS="hdfs"
	USER_ACCESS_LEVEL_BASIC_ADMIN="basic_admin"
	USER_ACCESS_LEVEL_FULL_ADMIN="full_admin"
	USER_ACCESS_LEVEL_ROOT="root"
	USER_ACCESS_LEVEL_SALES_ADMIN="sales_admin"
	USER_ACCESS_LEVEL_SUPPORT_ADMIN="support_admin"
	USER_ACCESS_LEVEL_USER="user"
	USER_LOGIN_EMAIL_STATUS_NOT_VERIFIED="not_verified"
	USER_LOGIN_EMAIL_STATUS_VERIFIED="verified"
	USER_PLAN_TYPE_CUSTOM="custom"
	USER_PLAN_TYPE_STARTER="starter"
	USER_PLAN_TYPE_STARTER_REDUNDANT="starter_redundant"
	USER_PLAN_TYPE_VANILLA="vanilla"
	USER_SSH_KEY_STATUS_ACTIVE="active"
	USER_SSH_KEY_STATUS_DELETED="deleted"
	USER_SUSPEND_REASON_CUSTOM="custom"
	USER_SUSPEND_REASON_UNPAID="unpaid"
	USER_TEST_ACCOUNT_KEYWORD="_erasable_"
	USER_TYPE_ADMIN="admin"
	USER_TYPE_BILLABLE="billable"
	VLAN_LAN_RANGE="LANVLANRange"
	VLAN_QUARANTINE_VLAN_ID="quarantineVLANID"
	VLAN_WAN_RANGE="WANVLANRange"
	VOLUME_TEMPLATE_ANSIBLE_BUNDLE_OS_BOOT_POST_INSTALL="ansible_bundle_os_boot_post_install"
	VOLUME_TEMPLATE_ANSIBLE_BUNDLE_OS_INSTALL="ansible_bundle_os_install"
	VOLUME_TEMPLATE_BOOT_HYBRID="hybrid"
	VOLUME_TEMPLATE_BOOT_LEGACY_ONLY="legacy_only"
	VOLUME_TEMPLATE_BOOT_UEFI_ONLY="uefi_only"
	VOLUME_TEMPLATE_BOOTLOADER_EFI_LOCAL_INSTALL="bootloader_c7_efi_local_install"
	VOLUME_TEMPLATE_BOOTLOADER_EFI_OS_BOOT="bootloader_c7_efi_os_boot"
	VOLUME_TEMPLATE_BOOTLOADER_PCX86_LOCAL_INSTALL="bootloader_c0_pcx86_local_install"
	VOLUME_TEMPLATE_BOOTLOADER_PCX86_OS_BOOT="bootloader_c0_pcx86_os_boot"
	VOLUME_TEMPLATE_DEPRECATION_STATUS_DEPRECATED_ALLOW_EXPAND="deprecated_allow_expand"
	VOLUME_TEMPLATE_DEPRECATION_STATUS_DEPRECATED_DENY_PROVISION="deprecated_deny_provision"
	VOLUME_TEMPLATE_DEPRECATION_STATUS_NOT_DEPRECATED="not_deprecated"
	VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_CENTOS="provisioner_os_cloudinit_prepare_centos"
	VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_GENERIC_UNIX="provisioner_os_cloudinit_prepare_generic_unix"
	VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_RHEL="provisioner_os_cloudinit_prepare_rhel"
	VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_UBUNTU="provisioner_os_cloudinit_prepare_ubuntu"
	VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_WINDOWS="provisioner_os_cloudinit_prepare_windows"
	VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_PREPARE_GENERIC_NON_CLOUDINIT="provisioner_os_bootstrap_generic_non_cloudinit"
	VOLUME_TEMPLATE_OS_READY_METHOD_WAIT_FOR_SIGNAL_FROM_OS="wait_for_signal_from_os"
	VOLUME_TEMPLATE_OS_READY_METHOD_WAIT_FOR_SSH="wait_for_ssh"
	VOLUME_TEMPLATE_STATUS_ACTIVE="active"
	VOLUME_TEMPLATE_STATUS_DELETED="deleted"
	VOLUME_TEMPLATE_VERSION_DEFAULT="0.0.0"
	VPLS_ACL_SAN="ACLSAN"
	VPLS_ACL_WAN="ACLWAN"
	VPLS_NORTH_WAN_VLAN_RANGE="NorthWANVLANRange"
	VPLS_QUARANTINE_VLAN_ID="quarantineVLANID"
	VPLS_SAN_ACL_RANGE="SANACLRange"
	VPLS_TOR_LAN_VLAN_RANGE="ToRLANVLANRange"
	VPLS_TOR_SAN_VLAN_RANGE="ToRSANVLANRange"
	VPLS_TOR_WAN_VLAN_RANGE="ToRWANVLANRange"
	WEB_PROXY_PASSWORD="web_proxy_password"
	WEB_PROXY_SERVER_IP="web_proxy_server_ip"
	WEB_PROXY_SERVER_PORT="web_proxy_server_port"
	WEB_PROXY_USERNAME="web_proxy_username"
	
	dictConstants = {
		AFC_GROUP_TYPE_INFRASTRUCTURE_DEPLOYMENT:{
				'title':'Infrastructure deployment AFC group type',
				'description':'Infrastructure deployment AFC group type',
				'value_json':'"infrastructure_deployment"',
				'visibility':'private',
			},
		AFC_GROUP_TYPE_SERVER_CLEANUP:{
				'title':'Server cleanup',
				'description':'Server cleanup AFC group type',
				'value_json':'"server_cleanup"',
				'visibility':'private',
			},
		AFC_GROUP_TYPE_SERVER_REGISTER:{
				'title':'Server register',
				'description':'Server registering AFC group type',
				'value_json':'"server_register"',
				'visibility':'private',
			},
		AFC_GROUP_TYPE_SERVERS_CLEANUP_BATCH:{
				'title':'Servers cleanup batch',
				'description':'',
				'value_json':'"servers_cleanup_batch"',
				'visibility':'private',
			},
		AFC_OPTION_ALL:{
				'title':'AFC Dropdown option all.',
				'description':'',
				'value_json':'"all"',
				'visibility':'private',
			},
		AFC_OPTION_EVERYTHING:{
				'title':'AFC Dropdown option everything.',
				'description':'',
				'value_json':'"everything"',
				'visibility':'private',
			},
		AFC_OPTION_NONE:{
				'title':'AFC Dropdown option none.',
				'description':'',
				'value_json':'"none"',
				'visibility':'private',
			},
		AFC_STATUS_NOT_CALLED:{
				'title':'Not called AFC queue status.',
				'description':'',
				'value_json':'"not_called"',
				'visibility':'private',
			},
		AFC_STATUS_RETURNED_SUCCESS:{
				'title':'Successful AFC queue status.',
				'description':'',
				'value_json':'"returned_success"',
				'visibility':'private',
			},
		AFC_STATUS_RUNNING:{
				'title':'This afc is currently running.',
				'description':'',
				'value_json':'"running"',
				'visibility':'private',
			},
		AFC_STATUS_SKIPPED:{
				'title':'Intentionally skipped AFC job',
				'description':'A developer, sysops engineer or administrator may decide to skip a failed AFC job after carefully analyzing the consequences and if the job is not required to succeed (or has succeeded by manual intervention).',
				'value_json':'"skipped"',
				'visibility':'private',
			},
		AFC_STATUS_THROWN_ERROR:{
				'title':'Error AFC queue status.',
				'description':'',
				'value_json':'"thrown_error"',
				'visibility':'private',
			},
		AFC_STATUS_THROWN_ERROR_RETRYING:{
				'title':'Error while retrying AFC queue status.',
				'description':'',
				'value_json':'"thrown_error_retrying"',
				'visibility':'private',
			},
		AFC_STATUS_THROWN_ERROR_SILENCED:{
				'title':'Error silenced AFC queue status.',
				'description':'',
				'value_json':'"thrown_error_silenced"',
				'visibility':'private',
			},
		AFC_TYPE_ASYNCHRONOUS:{
				'title':'Asynchronous AFC queue.',
				'description':'',
				'value_json':'"asynchronous"',
				'visibility':'private',
			},
		AFC_TYPE_DEBUG_NORMAL:{
				'title':'Normal debug AFC queue.',
				'description':'',
				'value_json':'"debug_normal"',
				'visibility':'private',
			},
		AFC_TYPE_DEBUG_RPC_SERVER:{
				'title':'Debug RPC server AFC queue.',
				'description':'',
				'value_json':'"debug_rpc_server"',
				'visibility':'private',
			},
		AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_CREATE_SECONDARY_DRIVE:{
				'title':'Automanaged instance deferred drive operation create secondary drive',
				'description':'',
				'value_json':'"create_secondary_drive"',
				'visibility':'public',
			},
		AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_DELETE_SECONDARY_DRIVE:{
				'title':'Automanaged instance deferred drive operation delete secondary drive',
				'description':'',
				'value_json':'"delete_secondary_drive"',
				'visibility':'public',
			},
		AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_EXPAND:{
				'title':'Automanaged instance deferred drive operation expand drive',
				'description':'',
				'value_json':'"expand_drive"',
				'visibility':'public',
			},
		AUTOMANAGED_INSTANCE_DEFERRED_DRIVE_OPERATION_TYPE_REPLACE_BOOT_DRIVE:{
				'title':'Automanaged instance deferred drive operation replace boot drive',
				'description':'',
				'value_json':'"replace_boot_drive"',
				'visibility':'public',
			},
		CHILD_DATACENTER_MANAGEMENT_SUBNET:{
				'title':'Child datacenter management subnet',
				'description':'Management subnet used for allocating IP addresses to network equipments on child datacenters.',
				'value_json':'"managementSubnet"',
				'visibility':'private',
			},
		CHILD_DATACENTER_MANAGEMENT_SUBNET_GATEWAY_INDEX:{
				'title':'Child datacenter management subnet gateway index',
				'description':'Management subnet used for allocating IP addresses to network equipments on child datacenters.',
				'value_json':'"managementSubnetGatewayIndex"',
				'visibility':'private',
			},
		CHILD_DATACENTER_MANAGEMENT_SUBNET_MASK:{
				'title':'Child datacenter management subnet mask',
				'description':'Management subnet used for allocating IP addresses to network equipments on child datacenters.',
				'value_json':'"managementSubnetMask"',
				'visibility':'private',
			},
		CHILD_DATACENTER_MANAGEMENT_SUBNET_RANGE:{
				'title':'Child datacenter management subnet range',
				'description':'Management subnet range indexes used for allocating IP addresses to network equipments on child datacenters. Range extremities must be separated by \'-\'.',
				'value_json':'"managementSubnetRange"',
				'visibility':'private',
			},
		CISCO_ACI_POD_ID:{
				'title':'Cisco ACI pod id',
				'description':'This is the hardcoded pod id for Cisco ACI. It could be removed in the future, but for now we will use it.',
				'value_json':'1',
				'visibility':'private',
			},
		CLUSTER_TYPE_CLOUDERA:{
				'title':'SaaS cluster of type Cloudera',
				'description':'See http://www.cloudera.com/ for more information on this software.',
				'value_json':'"cloudera"',
				'visibility':'public',
			},
		CLUSTER_TYPE_CONTAINER_PLATFORM_KUBERNETES:{
				'title':'SaaS cluster of type ContainerPlatformKubernetes',
				'description':'SaaS cluster of type ContainerPlatformKubernetes',
				'value_json':'"container_platform_kubernetes"',
				'visibility':'private',
			},
		CLUSTER_TYPE_CONTAINER_PLATFORM_MESOS:{
				'title':'SaaS cluster of type ContainerPlatformMesos',
				'description':'SaaS cluster of type ContainerPlatformMesos',
				'value_json':'"container_platform_mesos"',
				'visibility':'private',
			},
		CLUSTER_TYPE_COUCHBASE:{
				'title':'SaaS cluster of type Couchbase.',
				'description':'See http://www.couchbase.com/ for information on this software.',
				'value_json':'"couchbase"',
				'visibility':'public',
			},
		CLUSTER_TYPE_DATAMEER:{
				'title':'SaaS cluster of type Datameer.',
				'description':'See http://www.datameer.com/ for information on this software.',
				'value_json':'"datameer"',
				'visibility':'public',
			},
		CLUSTER_TYPE_DATASTAX:{
				'title':'Datastax cluster type',
				'description':'',
				'value_json':'"datastax"',
				'visibility':'public',
			},
		CLUSTER_TYPE_ELASTICSEARCH:{
				'title':'SaaS cluster of type ElasticSearch',
				'description':'See http://www.elasticsearch.org/ for more information on this software.',
				'value_json':'"elasticsearch"',
				'visibility':'public',
			},
		CLUSTER_TYPE_ELASTICSEARCH_LEGACY:{
				'title':'SaaS cluster of type ElasticSearch',
				'description':'See http://www.elasticsearch.org/ for more information on this software.',
				'value_json':'"elasticsearch_legacy"',
				'visibility':'public',
			},
		CLUSTER_TYPE_EXASOL:{
				'title':'Exasol cluster type',
				'description':'',
				'value_json':'"exasol"',
				'visibility':'public',
			},
		CLUSTER_TYPE_HDFS:{
				'title':'HDFS Cluster',
				'description':'',
				'value_json':'"hdfs"',
				'visibility':'public',
			},
		CLUSTER_TYPE_HORTONWORKS:{
				'title':'SaaS cluster of type Hortonworks',
				'description':'SaaS cluster of type MapR',
				'value_json':'"hortonworks"',
				'visibility':'public',
			},
		CLUSTER_TYPE_KUBERNETES:{
				'title':'Kubernetes cluster type',
				'description':'SaaS cluster of type Kubernetes',
				'value_json':'"kubernetes"',
				'visibility':'public',
			},
		CLUSTER_TYPE_MAPR:{
				'title':'SaaS cluster of type MapR',
				'description':'SaaS cluster of type MapR',
				'value_json':'"mapr"',
				'visibility':'public',
			},
		CLUSTER_TYPE_MAPR_LEGACY:{
				'title':'SaaS cluster of type MapRLegacy',
				'description':'SaaS cluster of type MapRLegacy',
				'value_json':'"mapr_legacy"',
				'visibility':'public',
			},
		CLUSTER_TYPE_MESOS:{
				'title':'Mesos cluster type',
				'description':'',
				'value_json':'"mesos"',
				'visibility':'public',
			},
		CLUSTER_TYPE_MYSQL_PERCONA:{
				'title':'Percona MySQL cluster',
				'description':'See https://www.percona.com/software/mysql-database/percona-xtradb-cluster for information on this software.',
				'value_json':'"mysql_percona"',
				'visibility':'public',
			},
		CLUSTER_TYPE_SPLUNK:{
				'title':'SaaS cluster of type Splunk',
				'description':'See http://www.splunk.com/ for information on this software.',
				'value_json':'"splunk"',
				'visibility':'public',
			},
		CLUSTER_TYPE_TABLEAU:{
				'title':'SaaS cluster of type Tableau.',
				'description':'See http://www.tableau.com/ for information on this software.',
				'value_json':'"tableau"',
				'visibility':'public',
			},
		CLUSTER_TYPE_VANILLA:{
				'title':'Vanilla cluster type (blank)',
				'description':'Default cluster, with blank behaviour (does nothing special and installs no special [SaaS] software). It is a singleton per Infrastructure product.',
				'value_json':'"vanilla"',
				'visibility':'public',
			},
		CLUSTER_TYPE_VMWARE_VSPHERE:{
				'title':'VMware vSphere cluster type.',
				'description':'',
				'value_json':'"vmware_vsphere"',
				'visibility':'public',
			},
		COLLAPSE_ARRAY_ROW_SPAN:{
				'title':'SQLSelection array row span',
				'description':'',
				'value_json':'"array_row_span"',
				'visibility':'public',
			},
		COLLAPSE_ARRAY_SUBROWS:{
				'title':'SQLSelection array subrows',
				'description':'',
				'value_json':'"array_subrows"',
				'visibility':'public',
			},
		COLLAPSE_ARRAY_SUBROWS_TABLE:{
				'title':'SQLSelection array subrows table',
				'description':'',
				'value_json':'"array_subrows_table"',
				'visibility':'public',
			},
		COLLAPSE_AUTOCOMPLETE_DICTIONARY:{
				'title':'SQLSelection autocomplete dictionary.',
				'description':'',
				'value_json':'"autocomplete_dictionary"',
				'visibility':'public',
			},
		COLLAPSE_HTML_ROWS_ARRAY:{
				'title':'SQLSelection HTML rows array',
				'description':'',
				'value_json':'"html_rows_array"',
				'visibility':'public',
			},
		COLLAPSE_HTML_ROWS_STRING:{
				'title':'SQLSelection HTML rows string',
				'description':'',
				'value_json':'"html_rows_string"',
				'visibility':'public',
			},
		COLLAPSE_NONE:{
				'title':'SQLSelection none',
				'description':'',
				'value_json':'"none"',
				'visibility':'public',
			},
		CONTAINER_ARRAY_ACTION_EXECUTE_COMMAND:{
				'title':'ContainerArray execute command action.',
				'description':'ContainerArray action that executes a given command.',
				'value_json':'"execute_command"',
				'visibility':'public',
			},
		CONTAINER_ARRAY_ACTION_HTTP_GET:{
				'title':'ContainerArray HTTP get action.',
				'description':'ContainerArray action that makes a HTTP get request.',
				'value_json':'"http_get"',
				'visibility':'public',
			},
		CONTAINER_ARRAY_ACTION_TCP_SOCKET:{
				'title':'ContainerArray TCP socket action.',
				'description':'ContainerArray action that opens a TCP connection to a given port.',
				'value_json':'"tcp_socket"',
				'visibility':'public',
			},
		CONTAINER_ARRAY_INTERFACE_INDEX_0:{
				'title':'SAN ContainerArray interface.',
				'description':'ContainerArray interface index reserved for SAN networks.',
				'value_json':'0',
				'visibility':'public',
			},
		CONTAINER_ARRAY_INTERFACE_INDEX_1:{
				'title':'ContainerArray interface index 1',
				'description':'',
				'value_json':'1',
				'visibility':'public',
			},
		CONTAINER_ARRAY_INTERFACE_INDEX_2:{
				'title':'ContainerArray interface index 2',
				'description':'',
				'value_json':'2',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_ELASTICSEARCH:{
				'title':'Elasticsearch container cluster type',
				'description':'',
				'value_json':'"elasticsearch"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_KAFKA:{
				'title':'Kafka container cluster type',
				'description':'',
				'value_json':'"kafka"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_POSTGRESQL:{
				'title':'PostgreSQL container cluster type',
				'description':'',
				'value_json':'"postgresql"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_SPARK:{
				'title':'Spark container cluster type',
				'description':'',
				'value_json':'"spark"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_SPARKSQL:{
				'title':'SparkSQL container cluster type',
				'description':'',
				'value_json':'"sparksql"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_STREAMSETS:{
				'title':'StreamSets container cluster type',
				'description':'StreamSets container cluster type',
				'value_json':'"streamsets"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_VANILLA:{
				'title':'Vanilla container cluster type',
				'description':'Default container cluster, with blank behaviour. It is a singleton per ContainerPlatform product.',
				'value_json':'"vanilla"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_ZOOKEEPER:{
				'title':'Zookeeper container cluster type',
				'description':'',
				'value_json':'"zookeeper"',
				'visibility':'public',
			},
		CONTAINER_CLUSTER_TYPE_ZOOMDATA:{
				'title':'Zoomdata container cluster type',
				'description':'',
				'value_json':'"zoomdata"',
				'visibility':'public',
			},
		CONTAINER_STATUS_PHASE_FAILED:{
				'title':'Container failed phase.',
				'description':'The Container has failed.',
				'value_json':'"failed"',
				'visibility':'public',
			},
		CONTAINER_STATUS_PHASE_PENDING:{
				'title':'Container pending phase.',
				'description':'The Container has been created and awaits scheduling and execution.',
				'value_json':'"pending"',
				'visibility':'public',
			},
		CONTAINER_STATUS_PHASE_RUNNING:{
				'title':'Container running phase.',
				'description':'Container is running.',
				'value_json':'"running"',
				'visibility':'public',
			},
		CONTAINER_STATUS_PHASE_SUCCEEDED:{
				'title':'Container succeeded phase.',
				'description':'The Container has been executed successfully.',
				'value_json':'"succeeded"',
				'visibility':'public',
			},
		CONTAINER_STATUS_PHASE_UNKNOWN:{
				'title':'Container unknown phase.',
				'description':'The Container state phase could not be retrieved due to internal errors.',
				'value_json':'"unknown"',
				'visibility':'public',
			},
		DATA_LAKE_TYPE_HDFS:{
				'title':'HDFS DataLake type',
				'description':'',
				'value_json':'"hdfs"',
				'visibility':'public',
			},
		DATACENTER_CONFIG_SWITCH_PROVISIONER_LAN:{
				'title':'Datacenter config LAN switch provisioner',
				'description':'',
				'value_json':'"LANProvisioner"',
				'visibility':'private',
			},
		DATACENTER_CONFIG_SWITCH_PROVISIONER_SDN:{
				'title':'Datacenter config SDN switch provisioner',
				'description':'',
				'value_json':'"SDNProvisioner"',
				'visibility':'private',
			},
		DATACENTER_CONFIG_SWITCH_PROVISIONER_VLAN:{
				'title':'Datacenter config VLAN switch provisioner',
				'description':'',
				'value_json':'"VLANProvisioner"',
				'visibility':'private',
			},
		DATACENTER_CONFIG_SWITCH_PROVISIONER_VPLS:{
				'title':'Datacenter config VPLS switch provisioner',
				'description':'',
				'value_json':'"VPLSProvisioner"',
				'visibility':'private',
			},
		DATACENTER_CONFIG_SWITCH_PROVISIONER_VXLAN:{
				'title':'Datacenter config VXLAN switch provisioner',
				'description':'',
				'value_json':'"VXLANProvisioner"',
				'visibility':'private',
			},
		DISK_TYPE_AUTO:{
				'title':'Automatically pick a disk type',
				'description':'',
				'value_json':'"auto"',
				'visibility':'public',
			},
		DISK_TYPE_HDD:{
				'title':'Disk Type HDD',
				'description':'Type of server local disk',
				'value_json':'"HDD"',
				'visibility':'public',
			},
		DISK_TYPE_NONE:{
				'title':'Disk Type none',
				'description':'Server local disk type',
				'value_json':'"none"',
				'visibility':'public',
			},
		DISK_TYPE_NVME:{
				'title':'Disk Type NVME',
				'description':'Type of server local disk',
				'value_json':'"NVME"',
				'visibility':'public',
			},
		DISK_TYPE_SSD:{
				'title':'Disk Type SSD',
				'description':'Type of server local disk',
				'value_json':'"SSD"',
				'visibility':'public',
			},
		DNS_RECORD_TYPE_A:{
				'title':'DNS address record.',
				'description':'Returns a 32-bit IPv4 address, most commonly used to map hostnames to an IP address of the host, but it is also used for DNSBLs, storing subnet masks in RFC 1101, etc.',
				'value_json':'"A"',
				'visibility':'private',
			},
		DNS_RECORD_TYPE_AAAA:{
				'title':'DNS IPv6 address record',
				'description':'Returns a 128-bit IPv6 address, most commonly used to map hostnames to an IP address of the host.',
				'value_json':'"AAAA"',
				'visibility':'private',
			},
		DNS_RECORD_TYPE_CNAME:{
				'title':'DNS canonical name record',
				'description':'Alias of one name to another: the DNS lookup will continue by retrying the lookup with the new name.',
				'value_json':'"CNAME"',
				'visibility':'private',
			},
		DNS_RECORD_TYPE_MX:{
				'title':'DNS mail exchange record',
				'description':'Maps a domain name to a list of message transfer agents for that domain.',
				'value_json':'"MX"',
				'visibility':'private',
			},
		DNS_RECORD_TYPE_NS:{
				'title':'DNS nameserver record',
				'description':'Delegates a DNS zone to use the given authoritative name servers.',
				'value_json':'"NS"',
				'visibility':'private',
			},
		DNS_RECORD_TYPE_PTR:{
				'title':'DNS pointer record',
				'description':'Pointer to a canonical name. Unlike a CNAME, DNS processing stops and just the name is returned. The most common use is for implementing reverse DNS lookups, but other uses include such things as DNS-SD.',
				'value_json':'"PTR"',
				'visibility':'private',
			},
		DNS_RECORD_TYPE_SOA:{
				'title':'DNS Start of authority record',
				'description':'Specifies authoritative information about a DNS zone, including the primary name server, the email of the domain administrator, the domain serial number, and several timers relating to refreshing the zone.',
				'value_json':'"SOA"',
				'visibility':'private',
			},
		DNS_RECORD_TYPE_TXT:{
				'title':'DNS text record',
				'description':'Originally for arbitrary human-readable text in a DNS record. Since the early 1990s, however, this record more often carries machine-readable data, such as specified by RFC 1464, opportunistic encryption, Sender Policy Framework, DKIM, DMARC, DNS-SD, etc.',
				'value_json':'"TXT"',
				'visibility':'private',
			},
		DRIVE_STORAGE_TYPE_AUTO:{
				'title':'Automatically pick a drive storage type',
				'description':'',
				'value_json':'"auto"',
				'visibility':'public',
			},
		DRIVE_STORAGE_TYPE_DUMMY:{
				'title':'Dummy drive',
				'description':'Demo drive.',
				'value_json':'"dummy"',
				'visibility':'private',
			},
		DRIVE_STORAGE_TYPE_ISCSI_HDD:{
				'title':'HDD drive',
				'description':'',
				'value_json':'"iscsi_hdd"',
				'visibility':'public',
			},
		DRIVE_STORAGE_TYPE_ISCSI_SSD:{
				'title':'SSD drive',
				'description':'',
				'value_json':'"iscsi_ssd"',
				'visibility':'public',
			},
		DRIVE_STORAGE_TYPE_NONE:{
				'title':'Don\'t create a drive option',
				'description':'Used when indicating the absence of a drive (like NULL).',
				'value_json':'"none"',
				'visibility':'public',
			},
		ENDPOINT_PHPUNIT:{
				'title':'PHPUnit endpoint.',
				'description':'',
				'value_json':'"phpunit"',
				'visibility':'private',
			},
		EVENT_SEVERITY_DEBUG:{
				'title':'Debugging event',
				'description':'',
				'value_json':'"debug"',
				'visibility':'private',
			},
		EVENT_SEVERITY_IMPORTANT:{
				'title':'Important event',
				'description':'',
				'value_json':'"important"',
				'visibility':'public',
			},
		EVENT_SEVERITY_INFO:{
				'title':'Info event',
				'description':'',
				'value_json':'"info"',
				'visibility':'public',
			},
		EVENT_SEVERITY_SECURITY:{
				'title':'Security event',
				'description':'Events such as log-in, log out, password changes, account recovery, authenticator added or removed, etc.',
				'value_json':'"security"',
				'visibility':'public',
			},
		EVENT_SEVERITY_SUCCESS:{
				'title':'Success event',
				'description':'',
				'value_json':'"success"',
				'visibility':'public',
			},
		EVENT_SEVERITY_TRIGGER:{
				'title':'Trigger event',
				'description':'',
				'value_json':'"trigger"',
				'visibility':'public',
			},
		EVENT_SEVERITY_WARNING:{
				'title':'Warning event',
				'description':'',
				'value_json':'"warning"',
				'visibility':'public',
			},
		EVENT_VISIBILITY_PRIVATE:{
				'title':'Private event',
				'description':'',
				'value_json':'"private"',
				'visibility':'private',
			},
		EVENT_VISIBILITY_PUBLIC:{
				'title':'Public event',
				'description':'',
				'value_json':'"public"',
				'visibility':'private',
			},
		FILESYSTEM_NAVIGATOR_DRIVER_TYPE_DATASET_README:{
				'title':'Filesystem navigator driver dataset readme',
				'description':'',
				'value_json':'"dataset_readme"',
				'visibility':'public',
			},
		FILESYSTEM_NAVIGATOR_DRIVER_TYPE_WEBHDFS:{
				'title':'FileSystemNavigator driver of type WebHDFS.',
				'description':'',
				'value_json':'"webhdfs"',
				'visibility':'public',
			},
		FILESYSTEM_TYPE_EXT2:{
				'title':'EXT2 filesystem.',
				'description':'',
				'value_json':'"ext2"',
				'visibility':'public',
			},
		FILESYSTEM_TYPE_EXT3:{
				'title':'EXT3 filesystem.',
				'description':'',
				'value_json':'"ext3"',
				'visibility':'public',
			},
		FILESYSTEM_TYPE_EXT4:{
				'title':'EXT4 filesystem.',
				'description':'',
				'value_json':'"ext4"',
				'visibility':'public',
			},
		FILESYSTEM_TYPE_NONE:{
				'title':'None filesystem.',
				'description':'Value used when no file system is specified.',
				'value_json':'"none"',
				'visibility':'public',
			},
		FILESYSTEM_TYPE_XFS:{
				'title':'XFS filesystem.',
				'description':'',
				'value_json':'"xfs"',
				'visibility':'public',
			},
		FIREWALL_RULE_IP_ADDRESS_TYPE_IPV4:{
				'title':'FirewallRule IPV4',
				'description':'',
				'value_json':'"ipv4"',
				'visibility':'public',
			},
		FIREWALL_RULE_IP_ADDRESS_TYPE_IPV6:{
				'title':'FirewallRule IPV6',
				'description':'',
				'value_json':'"ipv6"',
				'visibility':'public',
			},
		FIREWALL_RULE_PROTOCOL_ALL:{
				'title':'FirewallRule Protocol All',
				'description':'',
				'value_json':'"all"',
				'visibility':'public',
			},
		FIREWALL_RULE_PROTOCOL_ICMP:{
				'title':'FirewallRule Protocol ICMP',
				'description':'',
				'value_json':'"icmp"',
				'visibility':'public',
			},
		FIREWALL_RULE_PROTOCOL_TCP:{
				'title':'FirewallRule Protocol TCP',
				'description':'',
				'value_json':'"tcp"',
				'visibility':'public',
			},
		FIREWALL_RULE_PROTOCOL_UDP:{
				'title':'FirewallRule Protocol UDP',
				'description':'',
				'value_json':'"udp"',
				'visibility':'public',
			},
		GUEST_DISPLAY_NAME:{
				'title':'Guest',
				'description':'',
				'value_json':'"Guest"',
				'visibility':'public',
			},
		HARDWARE_CONFIGURATIONS_PREDEFINED:{
				'title':'Predefined hardware configurations',
				'description':'',
				'value_json':'"predefined"',
				'visibility':'public',
			},
		HARDWARE_CONFIGURATIONS_USER_PREDEFINED:{
				'title':'User predefined hardware configurations',
				'description':'',
				'value_json':'"user_predefined"',
				'visibility':'public',
			},
		HEALTH_CHECK_STATUS_ERROR:{
				'title':'Health check error status',
				'description':'',
				'value_json':'"error"',
				'visibility':'private',
			},
		HEALTH_CHECK_STATUS_SUCCESS:{
				'title':'Health check success status',
				'description':'',
				'value_json':'"success"',
				'visibility':'private',
			},
		HEALTH_CHECK_STATUS_WARNING:{
				'title':'Health check warning status',
				'description':'',
				'value_json':'"warning"',
				'visibility':'private',
			},
		INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_AVOID:{
				'title':'Infrastructure experimental priority avoid',
				'description':'',
				'value_json':'"avoid"',
				'visibility':'private',
			},
		INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_DISALLOW:{
				'title':'Infrastructure experimental priority disallow',
				'description':'',
				'value_json':'"disallow"',
				'visibility':'private',
			},
		INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_EQUAL:{
				'title':'Infrastructure experimental priority equal',
				'description':'',
				'value_json':'"equal"',
				'visibility':'private',
			},
		INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_PREFER:{
				'title':'Infrastructure experimental priority prefer',
				'description':'',
				'value_json':'"prefer"',
				'visibility':'private',
			},
		INFRASTRUCTURE_STAGE_FINAL_CALLBACK:{
				'title':'Infrastructure provision stage final',
				'description':'Final stage for infrastructure provision callback. Sets infrastructure to active.',
				'value_json':'"infrastructure_stage_final_callback"',
				'visibility':'private',
			},
		INFRASTRUCTURE_STAGE_SWITCH_PROVISION:{
				'title':'Infrastructure provision stage switch provision',
				'description':'First stage of infrastructure callback. Adds switch provisions to afc queue.',
				'value_json':'"infrastructure_stage_switch_provision"',
				'visibility':'private',
			},
		INSTANCE_ARRAY_BOOT_METHOD_LOCAL_DRIVES:{
				'title':'Instance array boot method local drives',
				'description':'Instance array boot method local drives',
				'value_json':'"local_drives"',
				'visibility':'public',
			},
		INSTANCE_ARRAY_BOOT_METHOD_PXE_ISCSI:{
				'title':'Instance array boot method PXE ISCSI',
				'description':'Instance array boot method PXE ISCSI',
				'value_json':'"pxe_iscsi"',
				'visibility':'public',
			},
		INSTANCE_ARRAY_INTERFACE_INDEX_0:{
				'title':'SAN InstanceArray interface.',
				'description':'InstanceArray interface index reserved for SAN networks.',
				'value_json':'0',
				'visibility':'public',
			},
		INSTANCE_ARRAY_INTERFACE_INDEX_1:{
				'title':'InstanceArray interface index 1',
				'description':'',
				'value_json':'1',
				'visibility':'public',
			},
		INSTANCE_ARRAY_INTERFACE_INDEX_2:{
				'title':'InstanceArray interface index 2',
				'description':'',
				'value_json':'2',
				'visibility':'public',
			},
		INSTANCE_ARRAY_INTERFACE_INDEX_3:{
				'title':'InstanceArray interface index 3',
				'description':'',
				'value_json':'3',
				'visibility':'public',
			},
		INSTANCE_OS_READY_STATUS_CALLED:{
				'title':'Instance OS ready status called',
				'description':'',
				'value_json':'"called"',
				'visibility':'private',
			},
		INSTANCE_OS_READY_STATUS_CALLED_WITH_WAIT_FOR_POWEROFF:{
				'title':'Instance OS ready status called with wait for poweroff',
				'description':'',
				'value_json':'"called_with_wait_for_poweroff"',
				'visibility':'private',
			},
		INSTANCE_OS_READY_STATUS_NOT_CALLED:{
				'title':'Instance OS ready status not called',
				'description':'',
				'value_json':'"not_called"',
				'visibility':'private',
			},
		IP_TYPE_IPV4:{
				'title':'IPv4 IP',
				'description':'',
				'value_json':'"ipv4"',
				'visibility':'public',
			},
		IP_TYPE_IPV6:{
				'title':'IPv6 IP',
				'description':'',
				'value_json':'"ipv6"',
				'visibility':'public',
			},
		IPC_HEALTH_CHECK:{
				'title':'Health checks endpoint.',
				'description':'',
				'value_json':'"health_check"',
				'visibility':'private',
			},
		JWT_COOKIE_TYPE_HTTPONLY:{
				'title':'HTTPOnly jwt cookie',
				'description':'',
				'value_json':'"HTTPOnly"',
				'visibility':'private',
			},
		JWT_COOKIE_TYPE_SCRIPT:{
				'title':'Script jwt cookie',
				'description':'',
				'value_json':'"script"',
				'visibility':'private',
			},
		LICENSE_MICROSOFT_CORE_MIN_COUNT:{
				'title':'Microsoft minimum number of cores for two core license pack',
				'description':'',
				'value_json':'16',
				'visibility':'private',
			},
		LICENSE_MICROSOFT_PROCESSOR_MIN_COUNT:{
				'title':'Microsoft minimum number of processors for two core license pack',
				'description':'',
				'value_json':'8',
				'visibility':'public',
			},
		LICENSE_TYPE_CLOUDERA:{
				'title':'License type cloudera',
				'description':'',
				'value_json':'"cloudera"',
				'visibility':'private',
			},
		LICENSE_TYPE_COUCHBASE:{
				'title':'License type couchbase',
				'description':'',
				'value_json':'"couchbase"',
				'visibility':'private',
			},
		LICENSE_TYPE_MAPR:{
				'title':'License type MAPR',
				'description':'',
				'value_json':'"mapr"',
				'visibility':'private',
			},
		LICENSE_TYPE_NONE:{
				'title':'License Type None',
				'description':'',
				'value_json':'"none"',
				'visibility':'public',
			},
		LICENSE_TYPE_WINDOWS_SERVER:{
				'title':'License type windows server',
				'description':'',
				'value_json':'"windows_server"',
				'visibility':'public',
			},
		LICENSE_TYPE_WINDOWS_SERVER_STANDARD:{
				'title':'License type Windows Server Standard',
				'description':'',
				'value_json':'"windows_server_standard"',
				'visibility':'public',
			},
		LICENSE_UTILIZATION_TYPE_DEMAND:{
				'title':'Demand license utilization',
				'description':'',
				'value_json':'"demand"',
				'visibility':'public',
			},
		LICENSE_UTILIZATION_TYPE_NONE:{
				'title':'License Utilization Type None',
				'description':'',
				'value_json':'"none"',
				'visibility':'public',
			},
		LICENSE_UTILIZATION_TYPE_SUBSCRIPTION:{
				'title':'Subscribe license utilization.',
				'description':'',
				'value_json':'"subscription"',
				'visibility':'public',
			},
		LIMITS_BILLABLE:{
				'title':'Limits for a paying user',
				'description':'',
				'value_json':'"billable"',
				'visibility':'private',
			},
		LIMITS_DEFAULT:{
				'title':'Default limits for a user',
				'description':'',
				'value_json':'"default"',
				'visibility':'private',
			},
		LIMITS_DEMO:{
				'title':'Limits for a user that has received demo time',
				'description':'',
				'value_json':'"demo"',
				'visibility':'private',
			},
		LIMITS_DEVELOPER:{
				'title':'Limits for a user that has at least sales rank',
				'description':'',
				'value_json':'"developer"',
				'visibility':'private',
			},
		LOAD_BALANCER_CRESCENDO:{
				'title':'Crescendo firewall',
				'description':'',
				'value_json':'"crescendo"',
				'visibility':'private',
			},
		LOAD_BALANCER_HAPROXY:{
				'title':'HAProxy load balancer',
				'description':'',
				'value_json':'"haproxy"',
				'visibility':'private',
			},
		NETWORK_CUSTOM_TYPE_SAAS:{
				'title':'SaaS LAN Network',
				'description':'SaaS flag for LAN network',
				'value_json':'"saas"',
				'visibility':'public',
			},
		NETWORK_EQUIPMENT_STATUS_ACTIVE:{
				'title':'Network equipment status active',
				'description':'Active network equipment',
				'value_json':'"active"',
				'visibility':'private',
			},
		NETWORK_EQUIPMENT_STATUS_DECOMMISSIONED:{
				'title':'Network equipment status decommissioned',
				'description':'Decommissioned network equipment',
				'value_json':'"decommissioned"',
				'visibility':'private',
			},
		NETWORK_SUSPEND_STATUS_NOT_SUSPENDED:{
				'title':'Network suspend status not suspended',
				'description':'',
				'value_json':'"not_suspended"',
				'visibility':'public',
			},
		NETWORK_SUSPEND_STATUS_SUSPENDED:{
				'title':'Network suspend status suspended',
				'description':'',
				'value_json':'"suspended"',
				'visibility':'public',
			},
		NETWORK_SUSPEND_STATUS_SUSPENDING:{
				'title':'Network suspend status suspending',
				'description':'',
				'value_json':'"suspending"',
				'visibility':'public',
			},
		NETWORK_SUSPEND_STATUS_UNSUSPENDING:{
				'title':'Network suspend status unsuspending',
				'description':'',
				'value_json':'"unsuspending"',
				'visibility':'public',
			},
		NETWORK_TYPE_LAN:{
				'title':'LAN network',
				'description':'',
				'value_json':'"lan"',
				'visibility':'public',
			},
		NETWORK_TYPE_SAN:{
				'title':'SAN network',
				'description':'',
				'value_json':'"san"',
				'visibility':'public',
			},
		NETWORK_TYPE_WAN:{
				'title':'WAN network',
				'description':'',
				'value_json':'"wan"',
				'visibility':'public',
			},
		NODE_MEASUREMENT_TYPE_CPU_LOAD:{
				'title':'CPU Load node measurement type',
				'description':'',
				'value_json':'"cpu_load"',
				'visibility':'public',
			},
		NODE_MEASUREMENT_TYPE_DISK_SIZE:{
				'title':'Disk size node measurement type',
				'description':'',
				'value_json':'"disk_size"',
				'visibility':'public',
			},
		NODE_MEASUREMENT_TYPE_DISK_USED:{
				'title':'Disk used node measurement type',
				'description':'',
				'value_json':'"disk_used"',
				'visibility':'public',
			},
		NODE_MEASUREMENT_TYPE_NETWORK_INTERFACE_INPUT:{
				'title':'Network interface input node measurement type',
				'description':'',
				'value_json':'"net_if_input"',
				'visibility':'public',
			},
		NODE_MEASUREMENT_TYPE_NETWORK_INTERFACE_OUTPUT:{
				'title':'Network interface output node measurement type',
				'description':'',
				'value_json':'"net_if_output"',
				'visibility':'public',
			},
		NODE_MEASUREMENT_TYPE_RAM_SIZE:{
				'title':'RAM size node measurement type',
				'description':'',
				'value_json':'"ram_size"',
				'visibility':'public',
			},
		NODE_MEASUREMENT_TYPE_RAM_USED:{
				'title':'RAM used node measurement type',
				'description':'',
				'value_json':'"ram_used"',
				'visibility':'public',
			},
		OPERATING_SYSTEM_CENTOS:{
				'title':'Operating System Centos',
				'description':'',
				'value_json':'"CentOS"',
				'visibility':'public',
			},
		OPERATING_SYSTEM_ESXI:{
				'title':'Operating System ESXi',
				'description':'',
				'value_json':'"ESXi"',
				'visibility':'public',
			},
		OPERATING_SYSTEM_NONE:{
				'title':'Operating System None',
				'description':'',
				'value_json':'"none"',
				'visibility':'public',
			},
		OPERATING_SYSTEM_RHEL:{
				'title':'Operating System RHEL',
				'description':'',
				'value_json':'"RHEL"',
				'visibility':'public',
			},
		OPERATING_SYSTEM_UBUNTU:{
				'title':'Operating System Ubuntu',
				'description':'',
				'value_json':'"Ubuntu"',
				'visibility':'public',
			},
		OPERATING_SYSTEM_WINDOWS:{
				'title':'Operating System Windows',
				'description':'',
				'value_json':'"Windows"',
				'visibility':'public',
			},
		OPERATION_TYPE_CREATE:{
				'title':'Create operation',
				'description':'',
				'value_json':'"create"',
				'visibility':'public',
			},
		OPERATION_TYPE_DELETE:{
				'title':'Delete operation',
				'description':'',
				'value_json':'"delete"',
				'visibility':'public',
			},
		OPERATION_TYPE_EDIT:{
				'title':'Edit operation',
				'description':'',
				'value_json':'"edit"',
				'visibility':'public',
			},
		OPERATION_TYPE_ORDERED:{
				'title':'Order operation',
				'description':'',
				'value_json':'"ordered"',
				'visibility':'public',
			},
		OPERATION_TYPE_START:{
				'title':'Start operation',
				'description':'',
				'value_json':'"start"',
				'visibility':'public',
			},
		OPERATION_TYPE_STOP:{
				'title':'Stop operation',
				'description':'',
				'value_json':'"stop"',
				'visibility':'public',
			},
		OPERATION_TYPE_SUSPEND:{
				'title':'Suspend operation',
				'description':'',
				'value_json':'"suspend"',
				'visibility':'public',
			},
		OS_ASSET_USAGE_BOOTLOADER:{
				'title':'OSAsset usage bootloader.',
				'description':'',
				'value_json':'"bootloader"',
				'visibility':'public',
			},
		PERMISSION_ADMIN_MAINTENANCE_WRITE:{
				'title':'Admin maintenance write permission.',
				'description':'',
				'value_json':'"admin_maintenance_write"',
				'visibility':'private',
			},
		PERMISSION_AFC_READ:{
				'title':'AFC Read permission.',
				'description':'',
				'value_json':'"afc_read"',
				'visibility':'private',
			},
		PERMISSION_AFC_WRITE:{
				'title':'AFC Write permission.',
				'description':'',
				'value_json':'"afc_write"',
				'visibility':'private',
			},
		PERMISSION_CLOUD_INIT_READ:{
				'title':'Cloudinit read permission.',
				'description':'',
				'value_json':'"cloudinit_read"',
				'visibility':'private',
			},
		PERMISSION_CLUSTER_READ:{
				'title':'Cluster read permission.',
				'description':'',
				'value_json':'"cluster_read"',
				'visibility':'private',
			},
		PERMISSION_CLUSTER_WRITE:{
				'title':'Cluster write permission.',
				'description':'',
				'value_json':'"cluster_write"',
				'visibility':'private',
			},
		PERMISSION_CONTAINER_PLATFORM_READ:{
				'title':'Container platform read permission.',
				'description':'',
				'value_json':'"container_platform_read"',
				'visibility':'private',
			},
		PERMISSION_CONTAINER_PLATFORM_WRITE:{
				'title':'Container platform write permission.',
				'description':'',
				'value_json':'"container_platform_write"',
				'visibility':'private',
			},
		PERMISSION_DATACENTER_READ:{
				'title':'Datacenter read permission.',
				'description':'',
				'value_json':'"datacenter_read"',
				'visibility':'private',
			},
		PERMISSION_DATACENTER_WRITE:{
				'title':'Datacenter write permission.',
				'description':'',
				'value_json':'"datacenter_write"',
				'visibility':'private',
			},
		PERMISSION_DATALAKE_READ:{
				'title':'Datalake read permission.',
				'description':'',
				'value_json':'"datalake_read"',
				'visibility':'private',
			},
		PERMISSION_DATALAKE_WRITE:{
				'title':'Datalake write permission.',
				'description':'',
				'value_json':'"datalake_write"',
				'visibility':'private',
			},
		PERMISSION_DATASET_READ:{
				'title':'Dataset read permission.',
				'description':'',
				'value_json':'"dataset_read"',
				'visibility':'private',
			},
		PERMISSION_DATASET_WRITE:{
				'title':'Dataset write permission.',
				'description':'',
				'value_json':'"dataset_write"',
				'visibility':'private',
			},
		PERMISSION_EMAILS_WRITE:{
				'title':'Permission for emails.',
				'description':'',
				'value_json':'"emails_write"',
				'visibility':'private',
			},
		PERMISSION_EVENTS_READ:{
				'title':'Events read permission.',
				'description':'',
				'value_json':'"events_read"',
				'visibility':'private',
			},
		PERMISSION_EVENTS_WRITE:{
				'title':'Events write permission.',
				'description':'',
				'value_json':'"events_write"',
				'visibility':'private',
			},
		PERMISSION_FIRMWARE_UPGRADE_READ:{
				'title':'Permission for firmware upgrade read.',
				'description':'',
				'value_json':'"firmware_upgrade_read"',
				'visibility':'private',
			},
		PERMISSION_FIRMWARE_UPGRADE_WRITE:{
				'title':'Permission for firmware upgrade write.',
				'description':'',
				'value_json':'"firmware_upgrade_write"',
				'visibility':'private',
			},
		PERMISSION_FRANCHISES_WRITE:{
				'title':'Permission for franchises.',
				'description':'',
				'value_json':'"franchises_write"',
				'visibility':'private',
			},
		PERMISSION_INFRASTRUCTURES_READ:{
				'title':'Infrastructures read permission.',
				'description':'',
				'value_json':'"infrastructures_read"',
				'visibility':'private',
			},
		PERMISSION_INFRASTRUCTURES_WRITE:{
				'title':'Infrastructures write permission.',
				'description':'',
				'value_json':'"infrastructures_write"',
				'visibility':'private',
			},
		PERMISSION_LICENSES_READ:{
				'title':'Licenses read permission.',
				'description':'',
				'value_json':'"licenses_read"',
				'visibility':'private',
			},
		PERMISSION_LICENSES_WRITE:{
				'title':'Licenses write permission.',
				'description':'',
				'value_json':'"licenses_write"',
				'visibility':'private',
			},
		PERMISSION_MAINTENANCE_READ:{
				'title':'Maintenance read permission.',
				'description':'',
				'value_json':'"maintenance_read"',
				'visibility':'private',
			},
		PERMISSION_MAINTENANCE_WRITE:{
				'title':'Maintenance write permission.',
				'description':'',
				'value_json':'"maintenance_write"',
				'visibility':'private',
			},
		PERMISSION_MONITORING_AGENT_READ:{
				'title':'Permission for reading from monitoring agent.',
				'description':'',
				'value_json':'"monitoring_agent_read"',
				'visibility':'private',
			},
		PERMISSION_MONITORING_AGENT_WRITE:{
				'title':'Permission for writing to monitoring agent.',
				'description':'',
				'value_json':'"monitoring_agent_write"',
				'visibility':'private',
			},
		PERMISSION_PRICES_READ:{
				'title':'Prices read permission.',
				'description':'',
				'value_json':'"prices_read"',
				'visibility':'private',
			},
		PERMISSION_PRICES_WRITE:{
				'title':'Prices write permission.',
				'description':'',
				'value_json':'"prices_write"',
				'visibility':'private',
			},
		PERMISSION_RESOURCES_WRITE:{
				'title':'Permission for accessing and manipulating resources.',
				'description':'',
				'value_json':'"resources_write"',
				'visibility':'private',
			},
		PERMISSION_SERVER_TYPES_READ:{
				'title':'Server types read permission.',
				'description':'',
				'value_json':'"server_types_read"',
				'visibility':'private',
			},
		PERMISSION_SERVERS_READ:{
				'title':'Servers read permission.',
				'description':'',
				'value_json':'"servers_read"',
				'visibility':'private',
			},
		PERMISSION_SERVERS_WRITE:{
				'title':'Servers write permission.',
				'description':'',
				'value_json':'"servers_write"',
				'visibility':'private',
			},
		PERMISSION_SKIP_AUTHENTICATOR:{
				'title':'Skip user authenticator.',
				'description':'Use this permission to allow user to not configure a 2FA one time password.',
				'value_json':'"skip_authenticator"',
				'visibility':'private',
			},
		PERMISSION_SKIP_USER_LIMITS:{
				'title':'Skip user limits.',
				'description':'Use this permission to remove user limits.',
				'value_json':'"skip_user_limits"',
				'visibility':'private',
			},
		PERMISSION_STORAGE_READ:{
				'title':'Storage read permission.',
				'description':'',
				'value_json':'"storage_read"',
				'visibility':'private',
			},
		PERMISSION_STORAGE_WRITE:{
				'title':'Storage write permission.',
				'description':'',
				'value_json':'"storage_write"',
				'visibility':'private',
			},
		PERMISSION_SUBNETS_READ:{
				'title':'Subnets read permission.',
				'description':'',
				'value_json':'"subnets_read"',
				'visibility':'private',
			},
		PERMISSION_SUBNETS_WRITE:{
				'title':'Subnets write permission.',
				'description':'',
				'value_json':'"subnets_write"',
				'visibility':'private',
			},
		PERMISSION_SUSPEND_REASONS_WRITE:{
				'title':'Suspend reasons write permission.',
				'description':'',
				'value_json':'"suspend_reasons_write"',
				'visibility':'private',
			},
		PERMISSION_SWITCHES_READ:{
				'title':'Switches read permission.',
				'description':'',
				'value_json':'"switches_read"',
				'visibility':'private',
			},
		PERMISSION_SWITCHES_WRITE:{
				'title':'Switches write permission.',
				'description':'',
				'value_json':'"switches_write"',
				'visibility':'private',
			},
		PERMISSION_TEMPLATES_READ:{
				'title':'Templates read permission.',
				'description':'',
				'value_json':'"templates_read"',
				'visibility':'private',
			},
		PERMISSION_TEMPLATES_WRITE:{
				'title':'Templates write permission.',
				'description':'',
				'value_json':'"templates_write"',
				'visibility':'private',
			},
		PERMISSION_THRESHOLD_READ:{
				'title':'Threshold read permission.',
				'description':'',
				'value_json':'"threshold_read"',
				'visibility':'private',
			},
		PERMISSION_THRESHOLD_WRITE:{
				'title':'Threshold write permission.',
				'description':'',
				'value_json':'"threshold_write"',
				'visibility':'private',
			},
		PERMISSION_USERS_AND_PERMISSIONS_READ:{
				'title':'Users and permission read permission.',
				'description':'',
				'value_json':'"users_and_permissions_read"',
				'visibility':'private',
			},
		PERMISSION_USERS_AND_PERMISSIONS_WRITE:{
				'title':'Users and permission write permission.',
				'description':'',
				'value_json':'"users_and_permissions_write"',
				'visibility':'private',
			},
		PERMISSION_UTILIZATION_REPORTS_READ:{
				'title':'Utilization reports read permission.',
				'description':'',
				'value_json':'"utilization_reports_read"',
				'visibility':'private',
			},
		PERMISSION_VARIABLES_AND_SECRETS_READ:{
				'title':'Variables and secrets read permission.',
				'description':'',
				'value_json':'"variables_and_secrets_read"',
				'visibility':'private',
			},
		PERMISSION_VARIABLES_AND_SECRETS_WRITE:{
				'title':'Variables and secrets write permission.',
				'description':'',
				'value_json':'"variables_and_secrets_write"',
				'visibility':'private',
			},
		PERMISSION_WORKFLOWS_READ:{
				'title':'Workflows read permission.',
				'description':'',
				'value_json':'"workflows_read"',
				'visibility':'private',
			},
		PERMISSION_WORKFLOWS_WRITE:{
				'title':'Workflows write permission.',
				'description':'',
				'value_json':'"workflows_write"',
				'visibility':'private',
			},
		PRICES_PRIVATE_DATACENTER_KEY:{
				'title':'Prices key for private datacenters default prices',
				'description':'',
				'value_json':'"private-dc-default"',
				'visibility':'public',
			},
		PROVISION_STAGE_PREPROVISION_SYNCHRONOUS:{
				'title':'Synchronous provisioning stage',
				'description':'First provisioning stage. Called directly by the deploy functions. This stage should contain as much validation as possible in order to limit or eliminate the possibility of failure (out of resources, incomplete information, etc.) of future asynchronous stages. There should be as many public error codes as possible for thrown errors to give the user a chance to fix and retry.',
				'value_json':'"preprovision_synchronous"',
				'visibility':'private',
			},
		PROVISION_STATUS_FINISHED:{
				'title':'Finished provision status',
				'description':'',
				'value_json':'"finished"',
				'visibility':'public',
			},
		PROVISION_STATUS_NOT_STARTED:{
				'title':'Not started provision status',
				'description':'',
				'value_json':'"not_started"',
				'visibility':'public',
			},
		PROVISION_STATUS_ONGOING:{
				'title':'Ongoing provision status',
				'description':'',
				'value_json':'"ongoing"',
				'visibility':'public',
			},
		REDIS_CRITICAL_TOKEN:{
				'title':'Redis critical token',
				'description':'Redis critical token',
				'value_json':'"critical"',
				'visibility':'public',
			},
		REDIS_INVALID_TOKEN:{
				'title':'Invalid redis token.',
				'description':'',
				'value_json':'"invalid"',
				'visibility':'public',
			},
		REDIS_TOKEN:{
				'title':'Redis token.',
				'description':'',
				'value_json':'"token"',
				'visibility':'public',
			},
		REDIS_VALID_TOKEN:{
				'title':'Valid redis token',
				'description':'',
				'value_json':'"valid"',
				'visibility':'public',
			},
		RESERVATION_DRIVE:{
				'title':'Drive resource reservation',
				'description':'',
				'value_json':'"drive"',
				'visibility':'private',
			},
		RESERVATION_INSTALLMENT_STATUS_ACTIVE:{
				'title':'Active reservation installment',
				'description':'',
				'value_json':'"active"',
				'visibility':'public',
			},
		RESERVATION_INSTALLMENT_STATUS_STOPPED:{
				'title':'Stopped reservation installment',
				'description':'',
				'value_json':'"stopped"',
				'visibility':'public',
			},
		RESERVATION_SERVER_TYPE:{
				'title':'Server type resource reservation',
				'description':'',
				'value_json':'"server_type"',
				'visibility':'private',
			},
		RESERVATION_STATUS_ACTIVE:{
				'title':'Active reservation',
				'description':'',
				'value_json':'"active"',
				'visibility':'public',
			},
		RESERVATION_STATUS_STOPPED:{
				'title':'Stopped reservation',
				'description':'',
				'value_json':'"stopped"',
				'visibility':'public',
			},
		RESERVATION_SUBNET:{
				'title':'Subnet resource reservation',
				'description':'',
				'value_json':'"subnet"',
				'visibility':'public',
			},
		RESOURCE_TYPE_CHASSIS_RACK:{
				'title':'Resource type chassis rack',
				'description':'',
				'value_json':'"chassis_rack"',
				'visibility':'private',
			},
		RESOURCE_TYPE_NETWORK_EQUIPMENT:{
				'title':'Resource type network_equipment',
				'description':'',
				'value_json':'"network_equipment"',
				'visibility':'private',
			},
		RESOURCE_TYPE_NETWORK_EQUIPMENT_CONTROLLER:{
				'title':'Resource type network_equipment_controller',
				'description':'',
				'value_json':'"network_equipment_controllers"',
				'visibility':'private',
			},
		RESOURCE_TYPE_SERVER:{
				'title':'Resource type server',
				'description':'',
				'value_json':'"server"',
				'visibility':'private',
			},
		RESOURCE_TYPE_SERVER_INTERFACE:{
				'title':'Resource type server_interface',
				'description':'',
				'value_json':'"server_interface"',
				'visibility':'private',
			},
		RESOURCE_TYPE_SUBNET_POOL:{
				'title':'Resource type subnet_pool',
				'description':'',
				'value_json':'"subnet_pool"',
				'visibility':'private',
			},
		RESOURCE_TYPE_VOLUME:{
				'title':'Resource type volume',
				'description':'',
				'value_json':'"volume"',
				'visibility':'private',
			},
		RESOURCE_UTILIZATION_TYPE_DEMAND:{
				'title':'Demand resource utilization',
				'description':'',
				'value_json':'"demand"',
				'visibility':'public',
			},
		RESOURCE_UTILIZATION_TYPE_RESERVATION:{
				'title':'Reserve resource utilization',
				'description':'',
				'value_json':'"reservation"',
				'visibility':'public',
			},
		SAMBA_SERVER_HOSTNAME:{
				'title':'Samba server hostname',
				'description':'',
				'value_json':'"samba_server_hostname"',
				'visibility':'public',
			},
		SAMBA_SERVER_IP:{
				'title':'Samba server ip',
				'description':'',
				'value_json':'"samba_server_ip"',
				'visibility':'public',
			},
		SAMBA_SERVER_PASSWORD:{
				'title':'Samba server password',
				'description':'',
				'value_json':'"samba_server_password"',
				'visibility':'public',
			},
		SAMBA_SERVER_USERNAME:{
				'title':'Samba server username',
				'description':'',
				'value_json':'"samba_server_username"',
				'visibility':'public',
			},
		SAMBA_SERVER_WINDOWS_KIT_SHARE_NAME:{
				'title':'Samba server Windows kit share name',
				'description':'',
				'value_json':'"samba_server_windows_kit_share_name"',
				'visibility':'public',
			},
		SDN_LAN_RANGE:{
				'title':'SDN provisioner LAN range',
				'description':'Datacenter config constant used in SDN provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"LANVLANRange"',
				'visibility':'private',
			},
		SDN_QUARANTINE_VLAN_ID:{
				'title':'SDN provisioner VLAN quarantine ID',
				'description':'Datacenter config constant used in SDN provisioning.',
				'value_json':'"quarantineVLANID"',
				'visibility':'private',
			},
		SDN_SAN_RANGE:{
				'title':'SDN provisioner SAN range',
				'description':'Datacenter config constant used in SDN provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"SANVLANRange"',
				'visibility':'private',
			},
		SDN_WAN_RANGE:{
				'title':'SDN provisioner WAN range',
				'description':'Datacenter config constant used in SDN provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"WANVLANRange"',
				'visibility':'private',
			},
		SERVER_BOOT_TYPE_CLASSIC:{
				'title':'Server boot type classic',
				'description':'Server boot type for servers which boot with classic BIOS and iPXE. Default value for servers.',
				'value_json':'"classic"',
				'visibility':'private',
			},
		SERVER_BOOT_TYPE_UEFI:{
				'title':'Server boot type UEFI',
				'description':'Server boot type for servers which boot using UEFI.',
				'value_json':'"uefi"',
				'visibility':'private',
			},
		SERVER_CLASS_BIGDATA:{
				'title':'Big data server class',
				'description':'Very general workload type designation.',
				'value_json':'"bigdata"',
				'visibility':'public',
			},
		SERVER_CLASS_HDFS:{
				'title':'HDFS server class',
				'description':'Very general workload type designation.',
				'value_json':'"hdfs"',
				'visibility':'public',
			},
		SERVER_CLASS_UNKNOWN:{
				'title':'Unknown server class',
				'description':'Very general workload type designation. Unknown class servers cannot be used.',
				'value_json':'"unknown"',
				'visibility':'public',
			},
		SERVER_DHCP_STATUS_ALLOW:{
				'title':'Server DHCP status allow',
				'description':'DHCP server responds to the provisioned server\'s requests with the IPs allocated in the user\'s infrastructure. The server has all the interfaces in the client\'s networks, allowing for requests to be made, or are in status down on the switch.',
				'value_json':'"allow_requests"',
				'visibility':'private',
			},
		SERVER_DHCP_STATUS_ANSIBLE:{
				'title':'Server DHCP status Ansible',
				'description':'During Ansible provisioning, the DHCP server treats the server in a different way compared to the moment when the server is actually allocated to the client. Thus, it uses special IPs and not the IPs allocated in the client\'s infrastructure, when responding to the server\'s requests.',
				'value_json':'"ansible_provision"',
				'visibility':'private',
			},
		SERVER_DHCP_STATUS_DENY:{
				'title':'Server DHCP status deny',
				'description':'The DHCP server ignores all DHCP requests from the server, as it does not belong to a client or isn\'t doing maintanance operations in quarantine network (registration, disk wiping).',
				'value_json':'"deny_requests"',
				'visibility':'private',
			},
		SERVER_DHCP_STATUS_QUARANTINE:{
				'title':'Server DHCP status quarantine',
				'description':'Server with this DHCP status is in the quarantine network with its interfaces, making DHCP requests during registering, reregistering or disk wiping. The DHCP server responds with a quarantine IP to the server\'s requests.',
				'value_json':'"quarantine"',
				'visibility':'private',
			},
		SERVER_DISK_INSTALLED:{
				'title':'Server disk installed on server.',
				'description':'',
				'value_json':'"installed"',
				'visibility':'private',
			},
		SERVER_DISK_SPARE:{
				'title':'Server drive not installed on any server.',
				'description':'',
				'value_json':'"spare"',
				'visibility':'private',
			},
		SERVER_EDIT_TYPE_AVAILABILITY:{
				'title':'Server edit type availability change',
				'description':'Notes that server_edit changes only the availability of the server.',
				'value_json':'"availability"',
				'visibility':'private',
			},
		SERVER_EDIT_TYPE_COMPLETE:{
				'title':'Server edit type complete',
				'description':'',
				'value_json':'"complete"',
				'visibility':'private',
			},
		SERVER_EDIT_TYPE_INVENTORY:{
				'title':'Server edit type inventory change',
				'description':'',
				'value_json':'"inventory"',
				'visibility':'private',
			},
		SERVER_EDIT_TYPE_IPMI:{
				'title':'Server edit type IPMI',
				'description':'',
				'value_json':'"ipmi"',
				'visibility':'private',
			},
		SERVER_EDIT_TYPE_RACK:{
				'title':'Server edit type rack change',
				'description':'',
				'value_json':'"rack"',
				'visibility':'private',
			},
		SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_ACCEPT:{
				'title':'SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_ACCEPT',
				'description':'',
				'value_json':'"accept"',
				'visibility':'public',
			},
		SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_ACCEPT_WITH_CONFIRMATION:{
				'title':'SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_ACCEPT_WITH_CONFIRMATION',
				'description':'',
				'value_json':'"accept_with_confirmation"',
				'visibility':'public',
			},
		SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_DENY:{
				'title':'SERVER_FIRMWARE_UPGRADE_POLICY_ACTION_DENY',
				'description':'',
				'value_json':'"deny"',
				'visibility':'public',
			},
		SERVER_FIRMWARE_UPGRADE_POLICY_STATUS_ACTIVE:{
				'title':'SERVER_FIRMWARE_UPGRADE_POLICY_STATUS_ACTIVE',
				'description':'',
				'value_json':'"active"',
				'visibility':'public',
			},
		SERVER_FIRMWARE_UPGRADE_POLICY_STATUS_STOPPED:{
				'title':'SERVER_FIRMWARE_UPGRADE_POLICY_STATUS_STOPPED',
				'description':'',
				'value_json':'"stopped"',
				'visibility':'public',
			},
		SERVER_INTERFACE_ADD_ON_HBA:{
				'title':'Server interface add-on device role HBA',
				'description':'The role for the server_interface_add_on_role for add-on devices which are used as HBAs.',
				'value_json':'"hba"',
				'visibility':'private',
			},
		SERVER_INTERFACE_ADD_ON_OFFLOAD:{
				'title':'Server interface add-on device role offload',
				'description':'The role for the server_interface_add_on_role for NIC devices which are used for iSCSI offloading.',
				'value_json':'"offload"',
				'visibility':'private',
			},
		SERVER_POWER_STATUS_NONE:{
				'title':'Null power command. No action.',
				'description':'Used with some power functions which are both setter and getter to just interrogate without action.',
				'value_json':'"none"',
				'visibility':'public',
			},
		SERVER_POWER_STATUS_OFF:{
				'title':'Server powered off',
				'description':'Power down chassis into soft off (S4/S5 state). WARNING: This command does not initiate a clean shutdown of the operating system prior to powering down the system.',
				'value_json':'"off"',
				'visibility':'public',
			},
		SERVER_POWER_STATUS_ON:{
				'title':'Server powered on',
				'description':'Power up chassis.',
				'value_json':'"on"',
				'visibility':'public',
			},
		SERVER_POWER_STATUS_RESET:{
				'title':'Server power reset',
				'description':'This command will perform a hard reset.',
				'value_json':'"reset"',
				'visibility':'public',
			},
		SERVER_POWER_STATUS_SOFT:{
				'title':'Server power status soft',
				'description':'Initiate a soft-shutdown of OS via ACPI. This can be done in a number of ways, commonly by simulating an overtemperture or by simulating a power button press. It is necessary for there to be Operating System support for ACPI and some sort of daemon watching for events for this soft power to work.',
				'value_json':'"soft"',
				'visibility':'public',
			},
		SERVER_POWER_STATUS_UNKNOWN:{
				'title':'Server power status unknown',
				'description':'Returned when a server is not allocated to an instance, the instance is not deployed or has an ongoing deploy operation.',
				'value_json':'"unknown"',
				'visibility':'public',
			},
		SERVER_STATUS_AVAILABLE:{
				'title':'Available server',
				'description':'',
				'value_json':'"available"',
				'visibility':'private',
			},
		SERVER_STATUS_AVAILABLE_RESERVED:{
				'title':'Reserved available server',
				'description':'',
				'value_json':'"available_reserved"',
				'visibility':'private',
			},
		SERVER_STATUS_CLEANING:{
				'title':'Server status cleaning',
				'description':'',
				'value_json':'"cleaning"',
				'visibility':'private',
			},
		SERVER_STATUS_CLEANING_REQUIRED:{
				'title':'Server requires cleaning',
				'description':'',
				'value_json':'"cleaning_required"',
				'visibility':'private',
			},
		SERVER_STATUS_DECOMISSIONED:{
				'title':'Server decommissioned',
				'description':'The server has been decommissioned and will not be used further.',
				'value_json':'"decommissioned"',
				'visibility':'private',
			},
		SERVER_STATUS_DEFECTIVE:{
				'title':'Defective server status',
				'description':'The server has defective components or is just not working.',
				'value_json':'"defective"',
				'visibility':'private',
			},
		SERVER_STATUS_REGISTERING:{
				'title':'Server is registering or will be registering',
				'description':'',
				'value_json':'"registering"',
				'visibility':'private',
			},
		SERVER_STATUS_REMOVED_FROM_RACK:{
				'title':'Server removed from rack',
				'description':'The server has been sent to warranty, grinder or has gone wondering and may never come back!',
				'value_json':'"removed_from_rack"',
				'visibility':'private',
			},
		SERVER_STATUS_UNAVAILABLE:{
				'title':'Not available server',
				'description':'',
				'value_json':'"unavailable"',
				'visibility':'private',
			},
		SERVER_STATUS_UPDATING_FIRMWARE:{
				'title':'Server is updating the firmware of one or more components.',
				'description':'Server is updating the firmware of one or more components.',
				'value_json':'"updating_firmware"',
				'visibility':'private',
			},
		SERVER_STATUS_USED:{
				'title':'Used server',
				'description':'',
				'value_json':'"used"',
				'visibility':'private',
			},
		SERVER_STATUS_USED_DIAGNOSTICS:{
				'title':'Server is used for datacenter diagnostics',
				'description':'',
				'value_json':'"used_diagnostics"',
				'visibility':'private',
			},
		SERVER_STATUS_USED_REGISTERING:{
				'title':'Server status used registering',
				'description':'When reregister is run on a used server, it is put in this status.',
				'value_json':'"used_registering"',
				'visibility':'private',
			},
		SERVER_TYPE_BOOT_HYBRID_DEFAULT_LEGACY:{
				'title':'Server type permits hybrid boot, with legacy as default',
				'description':'',
				'value_json':'"hybrid_default_legacy"',
				'visibility':'private',
			},
		SERVER_TYPE_BOOT_HYBRID_DEFAULT_UEFI:{
				'title':'Server type permits hybrid boot, with UEFI as default',
				'description':'',
				'value_json':'"hybrid_default_uefi"',
				'visibility':'private',
			},
		SERVER_TYPE_BOOT_LEGACY_ONLY:{
				'title':'Server type permits legacy boot only',
				'description':'',
				'value_json':'"legacy_only"',
				'visibility':'private',
			},
		SERVER_TYPE_BOOT_UEFI_ONLY:{
				'title':'Server type permits UEFI boot only',
				'description':'',
				'value_json':'"uefi_only"',
				'visibility':'private',
			},
		SERVICE_STATUS_ACTIVE:{
				'title':'Active service status',
				'description':'',
				'value_json':'"active"',
				'visibility':'public',
			},
		SERVICE_STATUS_DELETED:{
				'title':'Deleted service status',
				'description':'',
				'value_json':'"deleted"',
				'visibility':'public',
			},
		SERVICE_STATUS_ORDERED:{
				'title':'Ordered service status',
				'description':'',
				'value_json':'"ordered"',
				'visibility':'public',
			},
		SERVICE_STATUS_STOPPED:{
				'title':'Stopped service status',
				'description':'',
				'value_json':'"stopped"',
				'visibility':'public',
			},
		SERVICE_STATUS_SUSPENDED:{
				'title':'Suspended service status',
				'description':'',
				'value_json':'"suspended"',
				'visibility':'public',
			},
		SHARED_DRIVE_CONNECTED:{
				'title':'Shared drive - connection type "connected"',
				'description':'When an instance array or a container array is attached to a shared drive and the infrastructure is deployed, this kind of connection will be made.',
				'value_json':'"connected"',
				'visibility':'public',
			},
		SHARED_DRIVE_CONNECTED_CONTAINER_ARRAY:{
				'title':'Shared drive - connection type "connected"',
				'description':'',
				'value_json':'"connected_container_array"',
				'visibility':'public',
			},
		SHARED_DRIVE_DISCONNECTED:{
				'title':'Shared drive - connection type "disconnected"',
				'description':'When an instance array or a container array is detached from a shared drive (or the shared drive / instance array / container array belonging to the connection is deleted) and the infrastructure is deployed, this type of connection will be made.',
				'value_json':'"disconnected"',
				'visibility':'private',
			},
		SHARED_DRIVE_DISCONNECTED_CONTAINER_ARRAY:{
				'title':'Shared drive - connection type "disconnected"',
				'description':'',
				'value_json':'"disconnected_container_array"',
				'visibility':'public',
			},
		SHARED_DRIVE_WILL_BE_CONNECTED:{
				'title':'Shared drive connection type "will be connected"',
				'description':'When an instance array or a container array is attached to a shared drive, this type of connection will be made.',
				'value_json':'"will_be_connected"',
				'visibility':'public',
			},
		SHARED_DRIVE_WILL_BE_CONNECTED_CONTAINER_ARRAY:{
				'title':'Shared drive connection type "will be connected"',
				'description':'',
				'value_json':'"will_be_connected_container_array"',
				'visibility':'public',
			},
		SHARED_DRIVE_WILL_BE_DISCONNECTED:{
				'title':'Shared drive - connection type "will_be_disconnected"',
				'description':'When an instance array / container array is detached from a shared drive (or the shared drive / instance array / container array belonging to the connection is deleted), this type of connection will be made.',
				'value_json':'"will_be_disconnected"',
				'visibility':'public',
			},
		SHARED_DRIVE_WILL_BE_DISCONNECTED_CONTAINER_ARRAY:{
				'title':'Shared drive - connection type "will_be_disconnected"',
				'description':'',
				'value_json':'"will_be_disconnected_container_array"',
				'visibility':'public',
			},
		SOLUTION_TYPE_DATALAB_SPARK:{
				'title':'Solution of type Datalab Spark',
				'description':'',
				'value_json':'"datalab_spark"',
				'visibility':'public',
			},
		SQL_KEYWORD_NULL:{
				'title':'SQL_KEYWORD_NULL',
				'description':'This constant allows the search API to query for NULL/NOT NULL columns.',
				'value_json':'"SQL_KEYWORD_NULL"',
				'visibility':'public',
			},
		SSH_DSA_ALGORITHM_IDENTIFIER:{
				'title':'DSA algorithm',
				'description':'',
				'value_json':'"ssh-dsa"',
				'visibility':'public',
			},
		SSH_DSS_ALGORITHM_IDENTIFIER:{
				'title':'DSS algorithm',
				'description':'',
				'value_json':'"ssh-dss"',
				'visibility':'public',
			},
		SSH_KEY_FORMAT_OPENSSH:{
				'title':'OpenSSH SSH key',
				'description':'',
				'value_json':'"openssh"',
				'visibility':'public',
			},
		SSH_KEY_FORMAT_PKCS1:{
				'title':'PKCS1 SSH key',
				'description':'',
				'value_json':'"pkcs#1"',
				'visibility':'public',
			},
		SSH_KEY_FORMAT_PKCS8:{
				'title':'PKCS8 SSH key',
				'description':'',
				'value_json':'"pkcs#8"',
				'visibility':'public',
			},
		SSH_KEY_FORMAT_SSH2:{
				'title':'SSH2 SSH key',
				'description':'',
				'value_json':'"ssh2"',
				'visibility':'public',
			},
		SSH_RSA_ALGORITHM_IDENTIFIER:{
				'title':'RSA algorithm',
				'description':'',
				'value_json':'"ssh-rsa"',
				'visibility':'public',
			},
		STAGE_DEFINITION_TYPE_ANSIBLE_BUNDLE:{
				'title':'Ansible bundle stage definition',
				'description':'',
				'value_json':'"AnsibleBundle"',
				'visibility':'public',
			},
		STAGE_DEFINITION_TYPE_API_CALL:{
				'title':'API call stage definition',
				'description':'',
				'value_json':'"APICall"',
				'visibility':'public',
			},
		STAGE_DEFINITION_TYPE_COPY:{
				'title':'Copy operation',
				'description':'The copy operation has to have a source and a destination. Multiple resource types are supported (HTTP request or SCP location as source, etc.).',
				'value_json':'"Copy"',
				'visibility':'public',
			},
		STAGE_DEFINITION_TYPE_EXEC_SSH:{
				'title':'SSH exec command',
				'description':'',
				'value_json':'"SSHExec"',
				'visibility':'public',
			},
		STAGE_DEFINITION_TYPE_HTTP_REQUEST:{
				'title':'HTTP request stage definition',
				'description':'',
				'value_json':'"HTTPRequest"',
				'visibility':'public',
			},
		STAGE_DEFINITION_TYPE_JAVASCRIPT:{
				'title':'JavaScript stage definition',
				'description':'',
				'value_json':'"JavaScript"',
				'visibility':'public',
			},
		STAGE_DEFINITION_TYPE_WORKFLOW_REFERENCE:{
				'title':'Workflow stage definition type',
				'description':'',
				'value_json':'"WorkflowReference"',
				'visibility':'public',
			},
		STAGE_EXEC_POST_DEPLOY:{
				'title':'Execute the stage at the end of a deploy',
				'description':'',
				'value_json':'"post_deploy"',
				'visibility':'public',
			},
		STAGE_EXEC_PRE_DEPLOY:{
				'title':'Execute the stage before a deploy starts',
				'description':'Useful in cases such as rebalancing a cluster before removing healthy nodes.',
				'value_json':'"pre_deploy"',
				'visibility':'public',
			},
		STORAGE_DRIVE:{
				'title':'Storage Drive',
				'description':'',
				'value_json':'"Drive"',
				'visibility':'private',
			},
		STORAGE_DRIVER_DUMMY:{
				'title':'Storage Dummy driver',
				'description':'',
				'value_json':'"dummy_driver"',
				'visibility':'private',
			},
		STORAGE_DRIVER_FMSA:{
				'title':'Storage driver type for FMSA',
				'description':'Storage driver type for FMSA',
				'value_json':'"bigstep_storage"',
				'visibility':'private',
			},
		STORAGE_DRIVER_HP_MSA_1040:{
				'title':'HP MSA 1040 storage',
				'description':'',
				'value_json':'"hp_msa_1040"',
				'visibility':'private',
			},
		STORAGE_DRIVER_NEXENTA3:{
				'title':'Nexenta Version 3 storage driver',
				'description':'',
				'value_json':'"nexenta3"',
				'visibility':'private',
			},
		STORAGE_DRIVER_NEXENTA4:{
				'title':'Nexenta Version 4 storage driver',
				'description':'',
				'value_json':'"nexenta4"',
				'visibility':'private',
			},
		STORAGE_DRIVER_UNITY:{
				'title':'Unity storage driver',
				'description':'',
				'value_json':'"unity_storage"',
				'visibility':'private',
			},
		STORAGE_POOL_STATUS_ACTIVE:{
				'title':'Active storage pool',
				'description':'',
				'value_json':'"active"',
				'visibility':'private',
			},
		STORAGE_POOL_STATUS_DELETED:{
				'title':'Deleted storage pool',
				'description':'',
				'value_json':'"deleted"',
				'visibility':'private',
			},
		STORAGE_TEMPLATE:{
				'title':'Storage Template',
				'description':'',
				'value_json':'"Template"',
				'visibility':'private',
			},
		SUBNET_DESTINATION_DISABLED:{
				'title':'SUBNET_DESTINATION_DISABLED',
				'description':'',
				'value_json':'"disabled"',
				'visibility':'private',
			},
		SUBNET_DESTINATION_LAN:{
				'title':'LAN Subnet',
				'description':'',
				'value_json':'"lan"',
				'visibility':'public',
			},
		SUBNET_DESTINATION_OOB:{
				'title':'OOB Subnet',
				'description':'',
				'value_json':'"oob"',
				'visibility':'private',
			},
		SUBNET_DESTINATION_SAN:{
				'title':'SAN Subnet',
				'description':'',
				'value_json':'"san"',
				'visibility':'public',
			},
		SUBNET_DESTINATION_TMP:{
				'title':'Temporay Subnet',
				'description':'',
				'value_json':'"tmp"',
				'visibility':'private',
			},
		SUBNET_DESTINATION_WAN:{
				'title':'WAN Subnet',
				'description':'',
				'value_json':'"wan"',
				'visibility':'public',
			},
		SUBNET_TYPE_IPV4:{
				'title':'IPv4 Subnet',
				'description':'',
				'value_json':'"ipv4"',
				'visibility':'public',
			},
		SUBNET_TYPE_IPV6:{
				'title':'IPv6 Subnet',
				'description':'',
				'value_json':'"ipv6"',
				'visibility':'public',
			},
		SWITCH_DEVICE_DRIVER_5800:{
				'title':'Switch device driver 5800',
				'description':'',
				'value_json':'"hp5800"',
				'visibility':'private',
			},
		SWITCH_DEVICE_DRIVER_5900:{
				'title':'Switch device driver 5900',
				'description':'',
				'value_json':'"hp5900"',
				'visibility':'private',
			},
		SWITCH_DEVICE_DRIVER_CISCO_ACI_51:{
				'title':'Switch device Cisco ACI 5.1',
				'description':'',
				'value_json':'"cisco_aci51"',
				'visibility':'private',
			},
		SWITCH_DEVICE_DRIVER_CUMULUS_LINUX_42:{
				'title':'Switch device driver Cumulus Linux 42',
				'description':'',
				'value_json':'"cumulus42"',
				'visibility':'public',
			},
		SWITCH_DEVICE_LEAF:{
				'title':'Leaf switch type in topology',
				'description':'',
				'value_json':'"leaf"',
				'visibility':'private',
			},
		SWITCH_DEVICE_LINK_MLAG_BACKUP_IP:{
				'title':'Switch device mLAG link backup IP',
				'description':'',
				'value_json':'"backupIp"',
				'visibility':'private',
			},
		SWITCH_DEVICE_LINK_MLAG_MAC_ADDRESS:{
				'title':'Switch device mLAG link MAC address',
				'description':'',
				'value_json':'"MACAddress"',
				'visibility':'private',
			},
		SWITCH_DEVICE_LINK_MLAG_PHYSICAL_INTERFACES:{
				'title':'Switch device mLAG link physical interfaces',
				'description':'',
				'value_json':'"physicalInterfaces"',
				'visibility':'private',
			},
		SWITCH_DEVICE_LINK_TYPE_MLAG:{
				'title':'Switch device mLAG link',
				'description':'',
				'value_json':'"mlag"',
				'visibility':'private',
			},
		SWITCH_DEVICE_NORTH:{
				'title':'North switch device',
				'description':'North switch device',
				'value_json':'"north"',
				'visibility':'private',
			},
		SWITCH_DEVICE_OTHER:{
				'title':'Other switch device',
				'description':'',
				'value_json':'"other"',
				'visibility':'private',
			},
		SWITCH_DEVICE_PROVISIONER_LAN:{
				'title':'Switch device LAN provisioner',
				'description':'',
				'value_json':'"lan"',
				'visibility':'private',
			},
		SWITCH_DEVICE_PROVISIONER_SDN:{
				'title':'Switch device SDN provisioner',
				'description':'',
				'value_json':'"sdn"',
				'visibility':'private',
			},
		SWITCH_DEVICE_PROVISIONER_VLAN:{
				'title':'Switch device VLAN provisioner',
				'description':'',
				'value_json':'"vlan"',
				'visibility':'private',
			},
		SWITCH_DEVICE_PROVISIONER_VPLS:{
				'title':'Switch device VPLS provisioner',
				'description':'',
				'value_json':'"vpls"',
				'visibility':'private',
			},
		SWITCH_DEVICE_PROVISIONER_VXLAN:{
				'title':'Switch device VXLAN provisioner',
				'description':'',
				'value_json':'"vxlan"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_APPLICATION_PROFILE:{
				'title':'Application Profile object for SDN switches',
				'description':'',
				'value_json':'"ApplicationProfile"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_BRIDGE_DOMAIN:{
				'title':'Bridge Domain object for SDN switches',
				'description':'',
				'value_json':'"BridgeDomain"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_CONTRACT:{
				'title':'Contract object for SDN switches',
				'description':'',
				'value_json':'"Contract"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_CONTRACT_FILTER:{
				'title':'Contract filter object for SDN switches',
				'description':'',
				'value_json':'"ContractFilter"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_CONTRACT_SUBJECT:{
				'title':'Contract Subject object for SDN switches',
				'description':'',
				'value_json':'"ContractSubject"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_DHCP_RELAY_POLICY:{
				'title':'DHCP Relay Policy object for SDN switches',
				'description':'',
				'value_json':'"DHCPRelayPolicy"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_DHCP_RELAY_PROVIDER:{
				'title':'DHCP Relay Provider object for SDN switches',
				'description':'',
				'value_json':'"DHCPRelayProvider"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_EPG:{
				'title':'EPG object for SDN switches',
				'description':'',
				'value_json':'"EPG"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_IMPORTED_CONTRACT:{
				'title':'Imported contract object for SDN switches',
				'description':'',
				'value_json':'"ImportedContract"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_PHYSICAL_DOMAIN:{
				'title':'Physical Domain object for SDN switches',
				'description':'',
				'value_json':'"PhysicalDomain"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_SUBNET:{
				'title':'Subnet object for SDN switches',
				'description':'',
				'value_json':'"Subnet"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_TENANT:{
				'title':'Tenant object for SDN switches',
				'description':'',
				'value_json':'"Tenant"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_VLAN_POOL:{
				'title':'VLAN Pool object for SDN switches',
				'description':'',
				'value_json':'"VLANPool"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SDN_VRF:{
				'title':'VRF object for SDN switches',
				'description':'',
				'value_json':'"VRF"',
				'visibility':'private',
			},
		SWITCH_DEVICE_SPINE:{
				'title':'Spine switch type in topology',
				'description':'',
				'value_json':'"spine"',
				'visibility':'private',
			},
		SWITCH_DEVICE_TOR:{
				'title':'Top of rack switch device',
				'description':'Top of Rack switch device',
				'value_json':'"tor"',
				'visibility':'private',
			},
		URL_TYPE_HDFS:{
				'title':'URL Type HDFS',
				'description':'',
				'value_json':'"hdfs"',
				'visibility':'public',
			},
		USER_ACCESS_LEVEL_BASIC_ADMIN:{
				'title':'User access level - basic admin',
				'description':'',
				'value_json':'"basic_admin"',
				'visibility':'private',
			},
		USER_ACCESS_LEVEL_FULL_ADMIN:{
				'title':'User access level - full admin',
				'description':'',
				'value_json':'"full_admin"',
				'visibility':'private',
			},
		USER_ACCESS_LEVEL_ROOT:{
				'title':'User access level - root',
				'description':'Maximum powers, and may change the user access level of other users!',
				'value_json':'"root"',
				'visibility':'private',
			},
		USER_ACCESS_LEVEL_SALES_ADMIN:{
				'title':'User access level - sales admin',
				'description':'',
				'value_json':'"sales_admin"',
				'visibility':'private',
			},
		USER_ACCESS_LEVEL_SUPPORT_ADMIN:{
				'title':'User access level - support admin',
				'description':'',
				'value_json':'"support_admin"',
				'visibility':'private',
			},
		USER_ACCESS_LEVEL_USER:{
				'title':'User access level - user',
				'description':'',
				'value_json':'"user"',
				'visibility':'public',
			},
		USER_LOGIN_EMAIL_STATUS_NOT_VERIFIED:{
				'title':'Not verified user e-mail address',
				'description':'',
				'value_json':'"not_verified"',
				'visibility':'public',
			},
		USER_LOGIN_EMAIL_STATUS_VERIFIED:{
				'title':'Verified user e-mail address',
				'description':'',
				'value_json':'"verified"',
				'visibility':'public',
			},
		USER_PLAN_TYPE_CUSTOM:{
				'title':'User Plan Type Custom',
				'description':'',
				'value_json':'"custom"',
				'visibility':'public',
			},
		USER_PLAN_TYPE_STARTER:{
				'title':'User Plan Type Starter',
				'description':'',
				'value_json':'"starter"',
				'visibility':'public',
			},
		USER_PLAN_TYPE_STARTER_REDUNDANT:{
				'title':'User Plan Type Starter Redundant',
				'description':'',
				'value_json':'"starter_redundant"',
				'visibility':'public',
			},
		USER_PLAN_TYPE_VANILLA:{
				'title':'User Plan Type Vanilla',
				'description':'',
				'value_json':'"vanilla"',
				'visibility':'public',
			},
		USER_SSH_KEY_STATUS_ACTIVE:{
				'title':'Active user SSH key',
				'description':'',
				'value_json':'"active"',
				'visibility':'public',
			},
		USER_SSH_KEY_STATUS_DELETED:{
				'title':'Deleted user SSH key',
				'description':'',
				'value_json':'"deleted"',
				'visibility':'public',
			},
		USER_SUSPEND_REASON_CUSTOM:{
				'title':'User suspend reason custom',
				'description':'',
				'value_json':'"custom"',
				'visibility':'public',
			},
		USER_SUSPEND_REASON_UNPAID:{
				'title':'User suspend reason unpaid',
				'description':'',
				'value_json':'"unpaid"',
				'visibility':'public',
			},
		USER_TEST_ACCOUNT_KEYWORD:{
				'title':'User test account keyword identifier',
				'description':'It is used to identify the erasable test accounts.',
				'value_json':'"_erasable_"',
				'visibility':'public',
			},
		USER_TYPE_ADMIN:{
				'title':'Admin user',
				'description':'',
				'value_json':'"admin"',
				'visibility':'public',
			},
		USER_TYPE_BILLABLE:{
				'title':'Billable user',
				'description':'',
				'value_json':'"billable"',
				'visibility':'public',
			},
		VLAN_LAN_RANGE:{
				'title':'VLAN provisioner LAN range',
				'description':'Datacenter config constant used in VLAN provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"LANVLANRange"',
				'visibility':'private',
			},
		VLAN_QUARANTINE_VLAN_ID:{
				'title':'VLAN provisioner VLAN quarantine ID',
				'description':'Datacenter config constant used in VLAN provisioning.',
				'value_json':'"quarantineVLANID"',
				'visibility':'private',
			},
		VLAN_WAN_RANGE:{
				'title':'VLAN provisioner WAN range',
				'description':'Datacenter config constant used in VLAN provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"WANVLANRange"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_ANSIBLE_BUNDLE_OS_BOOT_POST_INSTALL:{
				'title':'Volume template ansible bundle OS boot post install.',
				'description':'Ansible bundle for OS boot post install.',
				'value_json':'"ansible_bundle_os_boot_post_install"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_ANSIBLE_BUNDLE_OS_INSTALL:{
				'title':'Volume template ansible bundle OS install',
				'description':'Ansible bundle for the OS install.',
				'value_json':'"ansible_bundle_os_install"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_BOOT_HYBRID:{
				'title':'Volume template boots hybrid, both legacy and UEFI',
				'description':'',
				'value_json':'"hybrid"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_BOOT_LEGACY_ONLY:{
				'title':'Volume template boots on legacy only',
				'description':'',
				'value_json':'"legacy_only"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_BOOT_UEFI_ONLY:{
				'title':'Volume template boots on uefi only',
				'description':'',
				'value_json':'"uefi_only"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_BOOTLOADER_EFI_LOCAL_INSTALL:{
				'title':'Volume template bootloader EFI local install',
				'description':'',
				'value_json':'"bootloader_c7_efi_local_install"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_BOOTLOADER_EFI_OS_BOOT:{
				'title':'Volume template bootloader EFI OS boot',
				'description':'EFI bootloader for OS boot.',
				'value_json':'"bootloader_c7_efi_os_boot"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_BOOTLOADER_PCX86_LOCAL_INSTALL:{
				'title':'Volume template bootloader PCX86 local install',
				'description':'PCX86 bootloader for local install.',
				'value_json':'"bootloader_c0_pcx86_local_install"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_BOOTLOADER_PCX86_OS_BOOT:{
				'title':'Volume template bootloader PCX86 OS boot',
				'description':'PCX86 bootloader for OS boot.',
				'value_json':'"bootloader_c0_pcx86_os_boot"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_DEPRECATION_STATUS_DEPRECATED_ALLOW_EXPAND:{
				'title':'Volume template deprecation status deprecated allow expand',
				'description':'Volume template deprecation status deprecated allow expand',
				'value_json':'"deprecated_allow_expand"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_DEPRECATION_STATUS_DEPRECATED_DENY_PROVISION:{
				'title':'Volume template deprecation status deprecated deny provision',
				'description':'Volume template deprecation status deprecated deny provision',
				'value_json':'"deprecated_deny_provision"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_DEPRECATION_STATUS_NOT_DEPRECATED:{
				'title':'Volume template deprecation status not deprecated',
				'description':'Volume template deprecation status not deprecated',
				'value_json':'"not_deprecated"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_CENTOS:{
				'title':'Volume template os bootstrap function provisioner_os_cloudinit_prepare_centos',
				'description':'',
				'value_json':'"provisioner_os_cloudinit_prepare_centos"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_GENERIC_UNIX:{
				'title':'Volume template os bootstrap function provisioner_os_cloudinit_prepare_generic_unix',
				'description':'',
				'value_json':'"provisioner_os_cloudinit_prepare_generic_unix"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_RHEL:{
				'title':'Volume template os bootstrap function provisioner_os_cloudinit_prepare_rhel',
				'description':'',
				'value_json':'"provisioner_os_cloudinit_prepare_rhel"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_UBUNTU:{
				'title':'Volume template os bootstrap function provisioner_os_cloudinit_prepare_ubuntu',
				'description':'',
				'value_json':'"provisioner_os_cloudinit_prepare_ubuntu"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_CLOUDINIT_PREPARE_WINDOWS:{
				'title':'Volume template os bootstrap function provisioner_os_cloudinit_prepare_windows',
				'description':'',
				'value_json':'"provisioner_os_cloudinit_prepare_windows"',
				'visibility':'private',
			},
		VOLUME_TEMPLATE_OS_BOOTSTRAP_FUNCTION_NAME_PROVISIONER_OS_PREPARE_GENERIC_NON_CLOUDINIT:{
				'title':'Volume template os bootstrap function provisioner_os_bootstrap_generic_non_cloudinit',
				'description':'',
				'value_json':'"provisioner_os_bootstrap_generic_non_cloudinit"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_OS_READY_METHOD_WAIT_FOR_SIGNAL_FROM_OS:{
				'title':'Volume template OS ready method wait for signal from OS',
				'description':'',
				'value_json':'"wait_for_signal_from_os"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_OS_READY_METHOD_WAIT_FOR_SSH:{
				'title':'Volume template OS ready method wait for SSH',
				'description':'',
				'value_json':'"wait_for_ssh"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_STATUS_ACTIVE:{
				'title':'Active status volume template',
				'description':'',
				'value_json':'"active"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_STATUS_DELETED:{
				'title':'Deleted status volume template',
				'description':'',
				'value_json':'"deleted"',
				'visibility':'public',
			},
		VOLUME_TEMPLATE_VERSION_DEFAULT:{
				'title':'The default value for volume_template_version',
				'description':'',
				'value_json':'"0.0.0"',
				'visibility':'private',
			},
		VPLS_ACL_SAN:{
				'title':'VPLS provisioner ACL SAN',
				'description':'Datacenter config constant used in VPLS provisioning.',
				'value_json':'"ACLSAN"',
				'visibility':'private',
			},
		VPLS_ACL_WAN:{
				'title':'VPLS provisioner ACL WAN',
				'description':'Datacenter config constant used in VPLS provisioning.',
				'value_json':'"ACLWAN"',
				'visibility':'private',
			},
		VPLS_NORTH_WAN_VLAN_RANGE:{
				'title':'VPLS provisioner North WAN VLAN range',
				'description':'Datacenter config constant used in VPLS provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"NorthWANVLANRange"',
				'visibility':'private',
			},
		VPLS_QUARANTINE_VLAN_ID:{
				'title':'VPLS provisioner VLAN quarantine ID',
				'description':'Datacenter config constant used in VPLS provisioning.',
				'value_json':'"quarantineVLANID"',
				'visibility':'private',
			},
		VPLS_SAN_ACL_RANGE:{
				'title':'VPLS provisioner SAN ACL RANGE',
				'description':'Datacenter config constant used in VPLS provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"SANACLRange"',
				'visibility':'private',
			},
		VPLS_TOR_LAN_VLAN_RANGE:{
				'title':'VPLS provisioner ToR LAN VLAN range',
				'description':'Datacenter config constant used in VPLS provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"ToRLANVLANRange"',
				'visibility':'private',
			},
		VPLS_TOR_SAN_VLAN_RANGE:{
				'title':'VPLS provisioner ToR SAN VLAN range',
				'description':'Datacenter config constant used in VPLS provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"ToRSANVLANRange"',
				'visibility':'private',
			},
		VPLS_TOR_WAN_VLAN_RANGE:{
				'title':'VPLS provisioner ToR WAN VLAN range',
				'description':'Datacenter config constant used in VPLS provisioning that contains two numbers separated by \'-\'.',
				'value_json':'"ToRWANVLANRange"',
				'visibility':'private',
			},
		WEB_PROXY_PASSWORD:{
				'title':'Web proxy password',
				'description':'',
				'value_json':'"web_proxy_password"',
				'visibility':'public',
			},
		WEB_PROXY_SERVER_IP:{
				'title':'Web proxy server IP',
				'description':'',
				'value_json':'"web_proxy_server_ip"',
				'visibility':'public',
			},
		WEB_PROXY_SERVER_PORT:{
				'title':'Web proxy port',
				'description':'',
				'value_json':'"web_proxy_server_port"',
				'visibility':'public',
			},
		WEB_PROXY_USERNAME:{
				'title':'Web proxy username',
				'description':'',
				'value_json':'"web_proxy_username"',
				'visibility':'public',
			},
	}