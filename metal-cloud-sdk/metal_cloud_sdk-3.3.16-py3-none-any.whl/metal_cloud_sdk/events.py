"""
* Metal Cloud, API v2.7.8"""
class Events(object):



	"""
	New authenticator enabled.
	Severity: security.
	
	An authenticator was added to the account or the existing one was replaced.
	"""
	AUTHENTICATOR_ENABLED_NEW=251


	"""
	Authenticator removed.
	Severity: security.
	
	The authenticator was removed from the account.
	"""
	AUTHENTICATOR_REMOVED=252


	"""
	Deploy Agent VLAN Configuration finished.
	Severity: success.
	
	Deploy Agent VLAN Configuration finished.
	"""
	BSI_AGENT_DEPLOY_CONFIGURATION_FINISHED=384


	"""
	Agent drive partition finished.
	Severity: success.
	
	Agent drive partitioning has finished on all instances.
	"""
	BSI_AGENT_DRIVE_PARTITION_FINISHED=396


	"""
	Agent drive partition format finished.
	Severity: success.
	
	Agent drive partition formatting has finished on all instances.
	"""
	BSI_AGENT_DRIVE_PARTITION_FORMAT_FINISHED=397


	"""
	Agent drive partition mount finished.
	Severity: success.
	
	Drive partition mounting has finished on all instances.
	"""
	BSI_AGENT_DRIVE_PARTITION_MOUNT_FINISHED=398


	"""
	Agent drive partition unmount finished.
	Severity: success.
	
	Drive partition unmount has finished on all instances.
	"""
	BSI_AGENT_DRIVE_PARTITION_UNMOUNT_FINISHED=399


	"""
	BSI Agent Installed.
	Severity: success.
	
	BSI Agent has been successfully installed on all instances.
	"""
	BSI_AGENT_INSTALLED=276


	"""
	Agent iSCSI setup finished.
	Severity: success.
	
	iSCSI setup and login has successfully finished on all instances.
	"""
	BSI_AGENT_ISCSI_SETUP_FINISHED=395


	"""
	Deploy Agent Live.
	Severity: success.
	
	Deploy Agent Live.
	"""
	BSI_AGENT_LIVE=294


	"""
	Reserved servers cleaning finished.
	Severity: success.
	
	.
	"""
	CLEANING_RESERVED_SERVERS_FINISHED=197


	"""
	Reserved servers cleaning started.
	Severity: info.
	
	.
	"""
	CLEANING_RESERVED_SERVERS_STARTED=196


	"""
	Cluster created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CLUSTER_CREATED=153


	"""
	Cluster deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CLUSTER_DELETED=156


	"""
	Cluster deployed.
	Severity: success.
	
	Deploy completed for Cluster operation.
	"""
	CLUSTER_DEPLOYED=157


	"""
	Cluster edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	CLUSTER_EDITED=154


	"""
	Cluster software version updated.
	Severity: info.
	
	A new cluster software version was detected. The corresponding cluster object property has been automatically updated.
	"""
	CLUSTER_SOFTWARE_VERSION_AUTOMATIC_UPDATE=249


	"""
	Cluster started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CLUSTER_STARTED=171


	"""
	Cluster stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CLUSTER_STOPPED=155


	"""
	Cluster suspended.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned. All active Drives will remain provisioned.
	"""
	CLUSTER_SUSPENDED=206


	"""
	Finished Cluster SaaS linking.
	Severity: success.
	
	.
	"""
	CLUSTERS_SAAS_LINKING_FINISHED=239


	"""
	Started Cluster SaaS linking.
	Severity: info.
	
	.
	"""
	CLUSTERS_SAAS_LINKING_STARTED=240


	"""
	Finished Cluster SaaS setup.
	Severity: success.
	
	.
	"""
	CLUSTERS_SAAS_SETUP_FINISHED=195


	"""
	Started Cluster SaaS setup.
	Severity: info.
	
	.
	"""
	CLUSTERS_SAAS_SETUP_STARTED=194


	"""
	ContainerArray created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_ARRAY_CREATED=215


	"""
	ContainerArray deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_ARRAY_DELETED=220


	"""
	ContainerArray deployed.
	Severity: success.
	
	Deploy completed for ContainerArray operation.
	"""
	CONTAINER_ARRAY_DEPLOYED=222


	"""
	ContainerArray edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	CONTAINER_ARRAY_EDITED=223


	"""
	ContainerArray not connected to WAN.
	Severity: warning.
	
	ContainerArray is not connected to WAN Network.
	"""
	CONTAINER_ARRAY_NOT_CONNECTED_TO_WAN=250


	"""
	ContainerArray started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_ARRAY_STARTED=224


	"""
	ContainerArray stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_ARRAY_STOPPED=225


	"""
	ContainerArray suspended.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_ARRAY_SUSPENDED=226


	"""
	ContainerCluster created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_CLUSTER_CREATED=254


	"""
	ContainerCluster deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_CLUSTER_DELETED=255


	"""
	ContainerCluster deployed.
	Severity: success.
	
	Deploy completed for ContainerCluster operation.
	"""
	CONTAINER_CLUSTER_DEPLOYED=257


	"""
	ContainerCluster edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	CONTAINER_CLUSTER_EDITED=258


	"""
	ContainerCluster software version updated.
	Severity: info.
	
	A new ContainerCluster software version was detected. The corresponding cluster object property has been automatically updated.
	"""
	CONTAINER_CLUSTER_SOFTWARE_VERSION_AUTOMATIC_UPDATE=266


	"""
	ContainerCluster started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_CLUSTER_STARTED=259


	"""
	ContainerCluster stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_CLUSTER_STOPPED=260


	"""
	ContainerCluster suspended.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_CLUSTER_SUSPENDED=261


	"""
	Container created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_CREATED=277


	"""
	Container deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_DELETED=278


	"""
	Container deployed.
	Severity: success.
	
	Deploy completed for Container operation.
	"""
	CONTAINER_DEPLOYED=280


	"""
	Container edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	CONTAINER_EDITED=281


	"""
	ContainerInterface edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	CONTAINER_INTERFACE_EDITED=286


	"""
	ContainerPlatform created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_PLATFORM_CREATED=207


	"""
	ContainerPlatform deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_PLATFORM_DELETED=208


	"""
	ContainerPlatform deployed.
	Severity: success.
	
	Deploy completed for ContainerPlatform operation.
	"""
	CONTAINER_PLATFORM_DEPLOYED=210


	"""
	ContainerPlatform edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	CONTAINER_PLATFORM_EDITED=211


	"""
	ContainerPlatform started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_PLATFORM_STARTED=212


	"""
	ContainerPlatform stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_PLATFORM_STOPPED=213


	"""
	ContainerPlatform suspended.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned. Active storage will remain provisioned.
	"""
	CONTAINER_PLATFORM_SUSPENDED=214


	"""
	Container started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	CONTAINER_STARTED=290


	"""
	Container stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	CONTAINER_STOPPED=291


	"""
	DataLake created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	DATA_LAKE_CREATED=186


	"""
	DataLake deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	DATA_LAKE_DELETED=187


	"""
	DataLake deployed.
	Severity: success.
	
	Deploy completed for Data Lake operation.
	"""
	DATA_LAKE_DEPLOYED=189


	"""
	DataLake edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	DATA_LAKE_EDITED=190


	"""
	Data Lake has promotion.
	Severity: info.
	
	Data Lake has a promotion.
	"""
	DATA_LAKE_HAS_PROMOTION=299


	"""
	DataLake started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	DATA_LAKE_STARTED=191


	"""
	DataLake stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	DATA_LAKE_STOPPED=192


	"""
	Blocked datacenter diagnostics AFCs cleaned up.
	Severity: info.
	
	Cleanup blocked AFCS as a result of running the datacenter_diagnostics function.
	"""
	DATACENTER_DIAGNOSTICS_BLOCKED_AFC_CLEANED_UP=429


	"""
	Datacenter diagnostics agent to server.
	Severity: info.
	
	Check that the datacenter agents are able to reach a provisioned server.
	"""
	DATACENTER_DIAGNOSTICS_DC_AGENT_TO_SERVER_CONNECTION_CHECKED=438


	"""
	Datacenter diagnostics l3 SAN interfaces.
	Severity: info.
	
	Check that the datacenter agents are able to reach a server's L3 SAN interfaces.
	"""
	DATACENTER_DIAGNOSTICS_L3_SAN_INTERFACES_CHECKED=434


	"""
	Datacenter diagnostics quarantine server to dc agents.
	Severity: info.
	
	Check that a server can reach the datacenter agents from the quarantine network.
	"""
	DATACENTER_DIAGNOSTICS_QUARANTINE_SERVER_TO_AGENT_CONNECTION_CHECKED=437


	"""
	Datacenter diagnostics agents can reach the quarantine L3 interface.
	Severity: info.
	
	Check that the datacenter agents machine is able to reach the quarantine L3 interface.
	"""
	DATACENTER_DIAGNOSTICS_REACH_L3_INTERFACE_CHECKED=431


	"""
	Datacenter diagnostics agents can reach OOB network.
	Severity: info.
	
	Check that the datacenter agents machine is able to reach the OOB network.
	"""
	DATACENTER_DIAGNOSTICS_REACH_OOB_NETWORK_CHECKED=430


	"""
	Datacenter diagnostics repository DNS record overridden.
	Severity: info.
	
	Check that repository DNS record is overridden by the DNS agent.
	"""
	DATACENTER_DIAGNOSTICS_REPO_DNS_RECORD_CHECKED=440


	"""
	Datacenter diagnostics resolve repository hostname.
	Severity: info.
	
	Check that the datacenter agents machine is able to resolve the repository hostname using one of the DNS servers configured in the datacenter configuration.
	"""
	DATACENTER_DIAGNOSTICS_RESOLVE_REPO_CHECKED=433


	"""
	Datacenter diagnostics storage SAN interface.
	Severity: info.
	
	Check that the datacenter agents machine is able to reach the storage's SAN interface.
	"""
	DATACENTER_DIAGNOSTICS_SAN_ARRAY_INTERFACE_CHECKED=435


	"""
	Datacenter diagnostics deploy server.
	Severity: info.
	
	Deploy a server with a SAN network if there is an active storage in the datacenter.
	"""
	DATACENTER_DIAGNOSTICS_SERVER_DEPLOYED=442


	"""
	Datacenter diagnostics internet connection.
	Severity: info.
	
	Check that a provisioned server is able to reach the internet from the WAN network.
	"""
	DATACENTER_DIAGNOSTICS_SERVER_INTERNET_CONNECTION_CHECKED=439


	"""
	Datacenter diagnostics static routes.
	Severity: info.
	
	Check that a SAN booted server receives static routes.
	"""
	DATACENTER_DIAGNOSTICS_STATIC_ROUTES_CHECKED=441


	"""
	Datacenter diagnostics switch configured.
	Severity: info.
	
	Check that the datacenter has at least one switch configured.
	"""
	DATACENTER_DIAGNOSTICS_SWITCH_CONFIGURED_CHECKED=432


	"""
	Datacenter diagnostics switch interfaces.
	Severity: info.
	
	Check that the datacenter agents machine is able to reach all in-band interfaces.
	"""
	DATACENTER_DIAGNOSTICS_SWITCH_INTERFACES_CHECKED=436


	"""
	DriveArray created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	DRIVE_ARRAY_CREATED=121


	"""
	DriveArray deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	DRIVE_ARRAY_DELETED=123


	"""
	DriveArray deployed.
	Severity: success.
	
	Deploy completed for DriveArray operation.
	"""
	DRIVE_ARRAY_DEPLOYED=124


	"""
	DriveArray Drive count is zero.
	Severity: warning.
	
	DriveArray is configured with zero Drives.
	"""
	DRIVE_ARRAY_DRIVE_COUNT_ZERO=150


	"""
	DriveArray edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	DRIVE_ARRAY_EDITED=118


	"""
	DriveArray started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	DRIVE_ARRAY_STARTED=119


	"""
	DriveArray stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	DRIVE_ARRAY_STOPPED=120


	"""
	Drive attached to Container.
	Severity: info.
	
	A Drive has been successfully attached to a Container.
	"""
	DRIVE_ATTACHED_CONTAINER=328


	"""
	Drive attached to Instance.
	Severity: info.
	
	A Drive has been successfully attached to an Instance.
	"""
	DRIVE_ATTACHED_INSTANCE=90


	"""
	Drive created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	DRIVE_CREATED=73


	"""
	Drive deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	DRIVE_DELETED=75


	"""
	Drive deployed.
	Severity: success.
	
	Deploy completed for Drive operation.
	"""
	DRIVE_DEPLOYED=32


	"""
	Drive detached from Container.
	Severity: info.
	
	A Drive has been successfully detached from a Container.
	"""
	DRIVE_DETACHED_CONTAINER=329


	"""
	Drive detached from Instance.
	Severity: info.
	
	A Drive has been successfully detached from an instance.
	"""
	DRIVE_DETACHED_INSTANCE=94


	"""
	Drive edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	DRIVE_EDITED=97


	"""
	Drive free space running low.
	Severity: warning.
	
	Free space on the Drive is less than 10% of the total disk size.
	"""
	DRIVE_FREE_SPACE_RUNNING_LOW=147


	"""
	Drive was rolled back to a snapshot.
	Severity: important.
	
	The drive was rolled back to a snapshot.
	"""
	DRIVE_ROLLED_BACK_TO_SNAPSHOT=185


	"""
	Drive started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	DRIVE_STARTED=115


	"""
	Drive stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	DRIVE_STOPPED=114


	"""
	Events deleted.
	Severity: info.
	
	Events were deleted.
	"""
	EVENTS_DELETED=271


	"""
	Firewall rules deployed.
	Severity: success.
	
	Firewall rules have been successfully deployed on all instances.
	"""
	FIREWALL_RULES_DEPLOYED=238


	"""
	Infrastructure created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	INFRASTRUCTURE_CREATED=76


	"""
	Infrastructure deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	INFRASTRUCTURE_DELETED=152


	"""
	Infrastructure deploy blocker triggered.
	Severity: warning.
	
	An infrastructure deploy blocker was triggered and it blocked the deployment of the infrastructure.
	"""
	INFRASTRUCTURE_DEPLOY_BLOCKER_TRIGGERED=323


	"""
	Infrastructure deploy started.
	Severity: info.
	
	The infrastructure deploy is starting.
	"""
	INFRASTRUCTURE_DEPLOY_STARTED=127


	"""
	Infrastructure deployed.
	Severity: success.
	
	Deploy completed for every operation on the specified infrastructure.
	"""
	INFRASTRUCTURE_DEPLOYED=39


	"""
	Infrastructure design was locked.
	Severity: info.
	
	The infrastructure design was locked. No edits, reverts or deploys are allowed on the infrastructure.
	"""
	INFRASTRUCTURE_DESIGN_LOCKED=262


	"""
	Infrastructure design was unlocked.
	Severity: info.
	
	The infrastructure design was unlocked.
	"""
	INFRASTRUCTURE_DESIGN_UNLOCKED=273


	"""
	Infrastructure edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	INFRASTRUCTURE_EDITED=159


	"""
	Infrastructure experimental priority set.
	Severity: info.
	
	The experimental priority of the infrastructure is set.
	"""
	INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_SET=296


	"""
	Infrastructure instances info.
	Severity: info.
	
	Internal info for all instances of the Infrastructure was returned.
	"""
	INFRASTRUCTURE_INSTANCES_INFO=297


	"""
	Infrastructure public design member is set.
	Severity: info.
	
	The infrastructure was made a member of public designs. Public designs members are locked by default.
	"""
	INFRASTRUCTURE_PUBLIC_DESIGNS_MEMBER_SET=295


	"""
	Infrastructure started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	INFRASTRUCTURE_STARTED=234


	"""
	Infrastructure stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	INFRASTRUCTURE_STOPPED=233


	"""
	Infrastructure user added.
	Severity: security.
	
	A user has been granted administrative privileges over an infrastructure.
	"""
	INFRASTRUCTURE_USER_ADDED=77


	"""
	Infrastructure user removed.
	Severity: security.
	
	A user's administrative privileges over an infrastructure have been revoked.
	"""
	INFRASTRUCTURE_USER_REMOVED=80


	"""
	Infrastructure user updated.
	Severity: security.
	
	A user's privileges or security settings concerning an infrastructure have been modified.
	"""
	INFRASTRUCTURE_USER_UPDATED=79


	"""
	InstanceArray created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	INSTANCE_ARRAY_CREATED=61


	"""
	InstanceArray deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	INSTANCE_ARRAY_DELETED=64


	"""
	InstanceArray deployed.
	Severity: success.
	
	Deploy completed for InstanceArray operation.
	"""
	INSTANCE_ARRAY_DEPLOYED=12


	"""
	InstanceArray edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	INSTANCE_ARRAY_EDITED=65


	"""
	InstanceArray instance count is zero.
	Severity: warning.
	
	InstanceArray is configured with zero instances.
	"""
	INSTANCE_ARRAY_INSTANCE_COUNT_ZERO=49


	"""
	InstanceArrayInterface edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	INSTANCE_ARRAY_INTERFACE_EDITED=88


	"""
	InstanceArray not connected to the WAN Network.
	Severity: warning.
	
	The InstanceArray does not have direct internet connectivity.
	"""
	INSTANCE_ARRAY_NOT_CONNECTED_TO_WAN=57


	"""
	InstanceArray started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	INSTANCE_ARRAY_STARTED=99


	"""
	InstanceArray stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	INSTANCE_ARRAY_STOPPED=98


	"""
	Instance created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	INSTANCE_CREATED=63


	"""
	Instance deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	INSTANCE_DELETED=66


	"""
	Instance deployed.
	Severity: success.
	
	Deploy completed for instance operation.
	"""
	INSTANCE_DEPLOYED=8


	"""
	Instance edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	INSTANCE_EDITED=67


	"""
	InstanceInterface edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	INSTANCE_INTERFACE_EDITED=71


	"""
	InstanceLicense created.
	Severity: info.
	
	.
	"""
	INSTANCE_LICENSE_CREATED=243


	"""
	InstanceLicense deleted.
	Severity: info.
	
	.
	"""
	INSTANCE_LICENSE_DELETED=244


	"""
	InstanceLicense deployed.
	Severity: success.
	
	.
	"""
	INSTANCE_LICENSE_DEPLOYED=242


	"""
	InstanceLicense edited.
	Severity: info.
	
	.
	"""
	INSTANCE_LICENSE_EDITED=248


	"""
	InstanceLicense started.
	Severity: info.
	
	.
	"""
	INSTANCE_LICENSE_STARTED=245


	"""
	InstanceLicense stopped.
	Severity: info.
	
	.
	"""
	INSTANCE_LICENSE_STOPPED=246


	"""
	InstanceLicense suspended.
	Severity: info.
	
	.
	"""
	INSTANCE_LICENSE_SUSPENDED=247


	"""
	Instance might not be bootable.
	Severity: warning.
	
	An Instance is not connected to any Drives that have an OS template installed.
	"""
	INSTANCE_MIGHT_NOT_BE_BOOTABLE=236


	"""
	Instance not bootable.
	Severity: warning.
	
	Instance will not be able to boot. An OS template must be selected for the attached drive in order for the server to be able to boot.
	"""
	INSTANCE_NOT_BOOTABLE=47


	"""
	Instance public key retrieved.
	Severity: info.
	
	Public key for instance was retrieved.
	"""
	INSTANCE_PUBLIC_KEY_RETRIEVED=268


	"""
	Instance server power status was set.
	Severity: info.
	
	Power status was changed for the server associated to provided instance.
	"""
	INSTANCE_SERVER_POWER_STATUS_SET=267


	"""
	Instance server type reservation was created.
	Severity: info.
	
	A new server type reservation for the provided instance was created.
	"""
	INSTANCE_SERVER_TYPE_RESERVATION_CREATED=269


	"""
	Instance started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	INSTANCE_STARTED=172


	"""
	Instance stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	INSTANCE_STOPPED=101


	"""
	Instance might not be bootable.
	Severity: info.
	
	Instance might not be able to boot. An OS template must be selected for the attached Drive in order for the server to be able to boot.
	"""
	INSTANCE_WITH_LOCAL_DISKS_MIGHT_NOT_BE_BOOTABLE=237


	"""
	IP deployed.
	Severity: success.
	
	Deploy completed for IP operation.
	"""
	IP_DEPLOYED=177


	"""
	Network created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	NETWORK_CREATED=81


	"""
	Network deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	NETWORK_DELETED=83


	"""
	Network deployed.
	Severity: success.
	
	Deploy completed for network operation.
	"""
	NETWORK_DEPLOYED=24


	"""
	Network edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	NETWORK_EDITED=82


	"""
	Network setup finished.
	Severity: success.
	
	Network devices finished configuring.
	"""
	NETWORK_SETUP_FINISHED=135


	"""
	Network setup started.
	Severity: info.
	
	Setting up network devices.
	"""
	NETWORK_SETUP_STARTED=134


	"""
	Network started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	NETWORK_STARTED=107


	"""
	Network stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	NETWORK_STOPPED=106


	"""
	Remote console accessed.
	Severity: security.
	
	Remote console was accessed.
	"""
	REMOTE_CONSOLE_ACCESSED=274


	"""
	Resource reservation created.
	Severity: info.
	
	A new resource reservation was created.
	"""
	RESOURCE_RESERVATION_CREATED=331


	"""
	Resource reservation deleted.
	Severity: info.
	
	The resource reservation was deleted.
	"""
	RESOURCE_RESERVATION_DELETED=330


	"""
	Resource reservation edited.
	Severity: info.
	
	A resource reservation was edited.
	"""
	RESOURCE_RESERVATION_EDITED=332


	"""
	Server type reservation cancelled.
	Severity: info.
	
	.
	"""
	SERVE=364


	"""
	Server OOB IP allow.
	Severity: info.
	
	Allow access to server OOB.
	"""
	SERVER_OOB_IP_ALLOW=392


	"""
	Server OOB IP disallow.
	Severity: info.
	
	Disallow access to server OOB.
	"""
	SERVER_OOB_IP_DISALLOW=393


	"""
	Server hot swap.
	Severity: important.
	
	A server was hot swapped.
	"""
	SERVER_SWAPPED=151


	"""
	Server type reservation cancelled.
	Severity: info.
	
	A server type reservation has been cancelled.
	"""
	SERVER_TYPE_RESERVATION_CANCELLED=365


	"""
	Server type reservation ownership changed.
	Severity: info.
	
	The ownership of a server type reservation has been changed.
	"""
	SERVER_TYPE_RESERVATION_OWNERSHIP_CHANGED=367


	"""
	Server type reservation reactivated.
	Severity: info.
	
	A server type reservation has been reactivated.
	"""
	SERVER_TYPE_RESERVATION_REACTIVATED=366


	"""
	A SharedDrive was connected to a ContainerArray.
	Severity: info.
	
	A SharedDrive was connected to a ContainerArray.
	"""
	SHARED_DRIVE_CONNECTED_TO_CONTAINER_ARRAY=361


	"""
	A SharedDrive was connected to an InstanceArray.
	Severity: info.
	
	A SharedDrive was connected to an InstanceArray.
	"""
	SHARED_DRIVE_CONNECTED_TO_INSTANCE_ARRAY=179


	"""
	SharedDrive created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	SHARED_DRIVE_CREATED=161


	"""
	SharedDrive deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	SHARED_DRIVE_DELETED=162


	"""
	SharedDrive deployed.
	Severity: success.
	
	Deploy completed for SharedDrive operation.
	"""
	SHARED_DRIVE_DEPLOYED=163


	"""
	A SharedDrive was disconnected from a ContainerArray.
	Severity: info.
	
	A SharedDrive was disconnected from a ContainerArray.
	"""
	SHARED_DRIVE_DISCONNECTED_FROM_CONTAINER_ARRAY=362


	"""
	A SharedDrive was disconnected from an InstanceArray.
	Severity: info.
	
	A SharedDrive was disconnected from an InstanceArray.
	"""
	SHARED_DRIVE_DISCONNECTED_FROM_INSTANCE_ARRAY=181


	"""
	SharedDrive edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	SHARED_DRIVE_EDITED=164


	"""
	SharedDrive started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	SHARED_DRIVE_STARTED=165


	"""
	SharedDrive stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	SHARED_DRIVE_STOPPED=167


	"""
	A SharedDrive will be connected to a ContainerArray.
	Severity: info.
	
	The SharedDrive will be connected to a ContainerArray.
	"""
	SHARED_DRIVE_WILL_BE_CONNECTED_TO_CONTAINER_ARRAY=359


	"""
	A SharedDrive will be connected to an InstanceArray.
	Severity: info.
	
	The SharedDrive will be connected to an InstanceArray.
	"""
	SHARED_DRIVE_WILL_BE_CONNECTED_TO_INSTANCE_ARRAY=178


	"""
	A SharedDrive will be disconnected from a ContainerArray.
	Severity: info.
	
	A SharedDrive will be disconnected from a ContainerArray.
	"""
	SHARED_DRIVE_WILL_BE_DISCONNECTED_FROM_CONTAINER_ARRAY=360


	"""
	A SharedDrive will be disconnected from an InstanceArray.
	Severity: info.
	
	A SharedDrive will be disconnected from an InstanceArray.
	"""
	SHARED_DRIVE_WILL_BE_DISCONNECTED_FROM_INSTANCE_ARRAY=180


	"""
	Snapshot created.
	Severity: success.
	
	A snapshot was created from a drive.
	"""
	SNAPSHOT_CREATED=183


	"""
	Snapshot deleted.
	Severity: important.
	
	A snapshot was deleted.
	"""
	SNAPSHOT_DELETED=184


	"""
	Storage pool created.
	Severity: info.
	
	A new storage pool was created.
	"""
	STORAGE_POOL_CREATED=333


	"""
	Storage pool deleted.
	Severity: info.
	
	A storage pool was deleted.
	"""
	STORAGE_POOL_DELETED=334


	"""
	Storage pool experimental set.
	Severity: info.
	
	The storage_pool_is_experimental was updated.
	"""
	STORAGE_POOL_EXPERIMENTAL_SET=335


	"""
	Storage Pool IQN Cleaned.
	Severity: info.
	
	The iscsi initiators that are no longer used in storage was deleted.
	"""
	STORAGE_POOL_IQN_CLEANED=336


	"""
	Storage Pool Maintenance Set.
	Severity: info.
	
	The flag storage_pool_in_maintenance was set.
	"""
	STORAGE_POOL_MAINTENANCE_SET=337


	"""
	Subnet cleared.
	Severity: info.
	
	Subnet's IP addresses were deallocated.
	"""
	SUBNET_CLEARED=105


	"""
	Subnet created.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	SUBNET_CREATED=85


	"""
	Subnet deleted.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	SUBNET_DELETED=86


	"""
	Subnet deployed.
	Severity: success.
	
	Deploy completed for Subnet operation.
	"""
	SUBNET_DEPLOYED=28


	"""
	Subnet edited.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for the changes to take effect.
	"""
	SUBNET_EDITED=84


	"""
	Subnet needs start.
	Severity: warning.
	
	At least one instance interface is associated to a stopped subnet. Start the subnet and deploy.
	"""
	SUBNET_NEEDS_START=149


	"""
	OOB subnet created.
	Severity: info.
	
	An OOB subnet has been successfully created.
	"""
	SUBNET_OOB_CREATED=379


	"""
	OOB subnet deleted.
	Severity: info.
	
	An OOB subnet has been successfully deleted.
	"""
	SUBNET_OOB_DELETED=380


	"""
	Subnet pool created.
	Severity: info.
	
	A subnet pool has been successfully created.
	"""
	SUBNET_POOL_CREATED=377


	"""
	Subnet pool deleted.
	Severity: info.
	
	A subnet pool has been successfully deleted.
	"""
	SUBNET_POOL_DELETED=378


	"""
	Subnet started.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order to provision hardware resources.
	"""
	SUBNET_STARTED=174


	"""
	Subnet stopped.
	Severity: info.
	
	The operation was performed in design mode. A deploy is required in order for hardware resources to be deprovisioned.
	"""
	SUBNET_STOPPED=100


	"""
	Switch device network allocated primary subnet.
	Severity: info.
	
	Primary WAN IPv4 subnet was allocated for a network from the infrastructure switches.
	"""
	SWITCH_DEVICE_NETWORK_ALLOCATED_PRIMARY_SUBNET=338


	"""
	Threshold created.
	Severity: info.
	
	A threshold was created.
	"""
	THRESHOLD_CREATED=401


	"""
	Threshold deleted.
	Severity: info.
	
	A threshold was deleted.
	"""
	THRESHOLD_DELETED=405


	"""
	Threshold edited.
	Severity: info.
	
	A threshold was edited.
	"""
	THRESHOLD_EDITED=402


	"""
	Threshold infrastructure on-demand and metered costs notification sent.
	Severity: info.
	
	A notification was sent to a user for a threshold of type infrastructure_on_demand_and_metered_costs.
	"""
	THRESHOLD_INFRASTRUCTURE_ON_DEMAND_AND_METERED_COSTS_NOTIFICATION_SENT=404


	"""
	Threshold network traffic per billing cycle notification sent.
	Severity: info.
	
	A notification was sent to a user for a network traffic threshold.
	"""
	THRESHOLD_NETWORK_TRAFFIC_NOTIFICATION_SENT=403


	"""
	User access level set.
	Severity: info.
	
	The access level for a user has been changed.
	"""
	USER_ACCESS_LEVEL_SET=368


	"""
	User API key regenerated.
	Severity: security.
	
	An user's API key was regenerated.
	"""
	USER_API_KEY_REGENERATED=110


	"""
	User authenticated with password.
	Severity: security.
	
	An user has been authenticated using his password.
	"""
	USER_AUTHENTICATED_PASSWORD=109


	"""
	User created.
	Severity: security.
	
	A user has been successfully created.
	"""
	USER_CREATED=93


	"""
	User delegate added.
	Severity: security.
	
	A user has delegated another user to be his representative. The delegate can now create and deploy infrastructures on behalf of the represented user.
	"""
	USER_DELEGATE_ADDED=91


	"""
	User delegate removed.
	Severity: security.
	
	A user is no longer the delegate of another user.
	"""
	USER_DELEGATE_REMOVED=92


	"""
	User JWT salt regenerated.
	Severity: security.
	
	An user's JWT salt was regenerated. This invalidates all logged-in existing sessions.
	"""
	USER_JWT_SALT_REGENERATED=182


	"""
	User login email updated via verification URL.
	Severity: security.
	
	The login email change verification URL was accessed, and the user's login email address has been updated, while the user was logged-in already. The login email change does not happen if the user is not authenticated when accessing the URL.
	"""
	USER_LOGIN_EMAIL_UPDATED_VERIFICATION_URL=108


	"""
	User password changed.
	Severity: security.
	
	The user's password has been updated.
	"""
	USER_PASSWORD_CHANGED=111


	"""
	Promotion added to user.
	Severity: info.
	
	A promotion has been added to the user.
	"""
	USER_PROMOTION_ADD=318


	"""
	Promotion removed from user.
	Severity: info.
	
	A promotion has been removed from the user.
	"""
	USER_REMOVE_PROMOTION=319


	"""
	User SSH key successfully created.
	Severity: security.
	
	The user's SSH key has been successfully created.
	"""
	USER_SSH_KEY_CREATED=59


	"""
	User SSH key deleted.
	Severity: security.
	
	The user's SSH key has been successfully deleted.
	"""
	USER_SSH_KEY_DELETED=89


	"""
	User suspended.
	Severity: important.
	
	A suspend reason has been created for a specific owner account.
	"""
	USER_SUSPENDED=218


	"""
	User unsuspended.
	Severity: important.
	
	A suspend reason has been removed for a specific owner account. Unless all suspend reasons are removed, the account remains suspended.
	"""
	USER_UNSUSPENDED=219
