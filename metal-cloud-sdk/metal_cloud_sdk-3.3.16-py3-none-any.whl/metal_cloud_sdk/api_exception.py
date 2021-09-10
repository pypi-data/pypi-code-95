
"""
* Metal Cloud, API v2.7.8"""

class ApiException(Exception):

	

	"""
	Agent not found.
	@private
	
	.
	"""
	AGENT_NOT_FOUND=341


	"""
	Ansible bundle not found.
	@public
	
	.
	"""
	ANSIBLE_BUNDLE_NOT_FOUND=330


	"""
	API key mismatch.
	@public
	
	The API key provided doesn't match the user's API key.
	"""
	API_KEY_MISMATCH=272


	"""
	API key not set.
	@public
	
	.
	"""
	API_KEY_NOT_FOUND=322


	"""
	One time password rejected.
	@public
	
	The provided authenticator one time password is not valid or is expired. Make sure the system time is set correctly.
	"""
	AUTHENTICATOR_OTP_REJECTED=293


	"""
	No bootable Drive found during boot process.
	@private
	
	This error is thrown during the boot process, if an Instance doesn't have a bootable Drive attached to it.
	It is then processed by the dhcp_public_url endpoint and an appropriate message is shown on the iSCSI console (by output of iSCSI script), which can be seen via KVM.
	"""
	BOOT_BOOTABLE_DRIVES_NOT_FOUND=5


	"""
	Cannot automatically manage IP allocation for user managed hosts (containers, VMs, etc.).
	@public
	
	Subnets destined to be used with Kubernetes, virtualization or special multi-IP address needs, need to be managed by user software or manually (must set subnet_automatic_allocation to false).
	"""
	CANNOT_AUTO_MANAGE_IP_ALLOCATION=329


	"""
	Cluster instance array isn't attached to WAN.
	@public
	
	The instance array does not have any interfaces attached to a WAN network, for provisioning to work.
	"""
	CLUSTER_INSTANCE_ARRAY_HAS_NO_WAN_INTERFACE=241


	"""
	Cannot associate one Cluster's products with another.
	@public
	
	Elements created on one Cluster cannot be used on another Cluster. A Drive created on Cluster A cannot be attached to an Instance belonging to Cluster B. API calls that receive this error should create new elements for use with the intended Cluster.
	"""
	CLUSTER_MIXING_NOT_ALLOWED=274


	"""
	Invalid value given to the bKeepDetachingDrives flag.
	@public
	
	The number of Instances in an InstanceArray or ContainerArray was reduced but the bKeepDetachingDrives flag was not set to true or false. The flag is required in order to know if the detaching Drives will be kept or deleted.
	"""
	COMPUTE_NODE_ARRAY_EDIT_DETACHING_DRIVES_INVALID_VALUE=321


	"""
	Not allowed to attach network.
	@public
	
	This error is thrown when an attempt to connect a container array to a network is made. Container array interfaces cannot be attached or detached to networks. They are already connected to the WAN and the SAN and are managed automatically.
	"""
	CONTAINER_ARRAY_INTERFACE_NETWORK_ATTACH_NOT_ALLOWED=282


	"""
	Not allowed to detach network.
	@public
	
	This error is thrown when an attempt to detach a container array from a network is made. Container array interfaces cannot be attached or detached to networks. They are already connected to the WAN and the SAN and are managed automatically.
	"""
	CONTAINER_ARRAY_INTERFACE_NETWORK_DETACH_NOT_ALLOWED=283


	"""
	The ContainerPlatform hardware configuration cannot support the resources demanded by its children.
	@public
	
	.
	"""
	CONTAINER_PLATFORM_NOT_ENOUGH_RESOURCES=312


	"""
	The total size of all Persistent Directories on the ContainerPlatform exceeds the size of the data volume.
	@public
	
	.
	"""
	CONTAINER_PLATFORM_NOT_ENOUGH_SPACE_FOR_PERSISTENT_DIRECTORIES=313


	"""
	Cookie type provided is not allowed.
	@private
	
	.
	"""
	COOKIE_TYPE_NOT_ALLOWED=280


	"""
	Data loss has not been confirmed.
	@public
	
	Data loss has not been confirmed.
	"""
	DATA_LOSS_NOT_CONFIRMED=263


	"""
	Datacenter not found.
	@public
	
	.
	"""
	DATACENTER_NOT_FOUND=269


	"""
	Datacenter parent not found.
	@public
	
	.
	"""
	DATACENTER_PARENT_NOT_FOUND=336


	"""
	Delegate user login email is not verified.
	@public
	
	.
	"""
	DELEGATE_USER_LOGIN_EMAIL_NOT_VERIFIED=325


	"""
	No DHCP lease exists for MAC address.
	@private
	
	This error is thrown when a DHCP request is received from a server with a specified MAC address that does not have a provisioned IP address, or has an already allocated DHCP quarantine lease which does not contain information about the switch the server is plugged into.
	"""
	DHCP_LEASE_COULD_NOT_FIND_FOR_MAC=14


	"""
	Invalid disk type.
	@public
	
	Servers can have their configuration changed whenever needed. This error is thrown when a search for a specific server configuration is made but the provided disk type is invalid. API calls that receive this error should obtain a list of available physical disk types before trying again.
	"""
	DISK_TYPE_INVALID=281


	"""
	DNS label reserved.
	@public
	
	When creating or editing an Infrastructure element a custom label can be provided for ease of use. The label of a product cannot be one of these reserved keywords: "snapshots", "drive-snapshots", "volume-templates", "drive-templates", "shared-drive-templates", "instance-licenses", "licenses", "license-contracts", "license-instalments", "infrastructures", "clusters", "instance-arrays", "instance-array-interfaces", "instances", "instance-interfaces", "instance-licenses", "drive-arrays", "drives", "networks", "subnets", "ips", "shared-drives", "data-lakes", "container-platforms", "container-clusters", "container-arrays", "container-array-interfaces", "containers", "container-interfaces", "drive-arrays", "drives", or "if0" to "if100". API calls that receive this error should change the initial label and attempt the operation again.
	"""
	DNS_LABEL_RESERVED=243


	"""
	Domain label already in use.
	@public
	
	When creating or editing an Infrastructure element a custom label can be provided for ease of use. This error is thrown when the specified label already exists on an element belonging to the same Infrastructure, to avoid confusion. API calls that receive this error should change the label and try the operation again.
	"""
	DOMAIN_LABEL_ALREADY_IN_USE=197


	"""
	DNS domain label invalid.
	@public
	
	When creating or editing an Infrastructure element a custom label can be provided for ease of use. This error is thrown when an invalid label is provided.
	A domain label has to:
	  - be between 1 and 63 characters long
	  - start with a letter
	  - end with a letter or a digit
	  - contain only letters, digits and hyphens(-).
	"""
	DOMAIN_LABEL_INVALID=199


	"""
	Unable to resolve subdomain label.
	@public
	
	When creating or editing an Infrastructure element a custom label can be provided for ease of use. This error is thrown when the provided subdomain label of an Infrastructure element cannot be resolved. API calls that receive this error should reobtain the element's label and try again.
	"""
	DOMAIN_LABEL_UNABLE_TO_RESOLVE=198


	"""
	Drive Array count data safety restriction.
	@public
	
	When shrinking a DriveArray, excess hardware resources are unallocated. To ensure data safety, attached Drives can only be deleted selectively using the drive_delete() function.
	"""
	DRIVE_ARRAY_COUNT_DATA_SAFETY_RESTRICTION=224


	"""
	Drive array cannot be detached from the instance array or the container array.
	@public
	
	The DriveArray cannot be detached from the InstanceArray or ContainerArray. The DriveArray belongs to the same Cluster or ContainerCluster as the InstanceArray or ContainerArray.
	"""
	DRIVE_ARRAY_DETACH_NOT_ALLOWED=320


	"""
	Drive array cannot be detached from instance array.
	@public
	
	The Drive Array and Instance Array belong to the same Cluster and cannot be detached.
	"""
	DRIVE_ARRAY_INSTANCE_ARRAY_DETACH_NOT_ALLOWED=240


	"""
	Drive array is already attached.
	@public
	
	The specified DriveArray is already attached to another InstanceArray. Detach it or find a free DriveArray before trying again.
	"""
	DRIVE_ARRAY_IS_ATTACHED=203


	"""
	Drive array is not attached.
	@public
	
	.
	"""
	DRIVE_ARRAY_IS_NOT_ATTACHED=328


	"""
	A DriveArray cannot be attached to both an InstanceArray and a ContainerArray.
	@public
	
	The specified DriveArray is already attached to an InstanceArray or a ContainerArray.
	"""
	DRIVE_ARRAY_MULTIPLE_ATTACH_NOT_ALLOWED=319


	"""
	A Drive cannot be attached to an instance that is set to be deleted.
	@public
	
	A Drive cannot be attached to an Instance that is set to be deleted. Cancel the delete operation or choose another Instance and try again.
	"""
	DRIVE_CANNOT_BE_ATTACHED_TO_A_DELETED_INSTANCE=228


	"""
	Drive is not attached.
	@public
	
	The Drive is not attached to an Instance. A Drive that is not already attached to an Instance does not support the "drive_detach_instance" operation.
	"""
	DRIVE_IS_NOT_ATTACHED=111


	"""
	Drive not active.
	@public
	
	Drives are required to be active for certain operations to function properly. Make sure the Drive has its service status set to active before trying again.
	"""
	DRIVE_NOT_ACTIVE=80


	"""
	Drive size provided is invalid.
	@public
	
	The Drive size provided for an edit operation is invalid. The new size cannot be less than the original size of the Drive, greater than the maximum allowed or less than the minimum allowed.
	"""
	DRIVE_SIZE_INVALID=91


	"""
	Edit made using an expired object.
	@public
	
	If multiple clients try to edit a product at the same time, only the first edit operation will succeed. The rest of the attempts receive this error in order not to overwrite the recently made changes. API calls that received this error should take the new context into account, and then obtain a new product operation object, edit it, and try again, if the changes should still be applied.
	"""
	EDIT_MADE_WITH_EXPIRED_OBJECT=257


	"""
	Email address already changed.
	@public
	
	.
	"""
	EMAIL_ADDRESS_ALREADY_CHANGED=252


	"""
	Invalid email address.
	@public
	
	Invalid RFC 5321, 5322 and 2821 email address. It is possible for some valid addresses to be rejected because some RFC specifications are not implemented or not allowed (the domain part is not allowed to be an IP address, the domain must have a IANA root and cannot be a simple hostname, comments are not supported and other limitations).
	"""
	EMAIL_ADDRESS_INVALID=54


	"""
	Event not found.
	@public
	
	The event to be operated on was not found.
	"""
	EVENT_NOT_FOUND=148


	"""
	External connection not found.
	@private
	
	External connection not found.
	"""
	EXTERNAL_CONNECTION_NOT_FOUND=352


	"""
	Invalid external connection switch rule.
	@private
	
	The network equipment rule is invalid.
	"""
	EXTERNAL_CONNECTION_SWITCH_INVALID_RULE=354


	"""
	External connection switch entry not found.
	@private
	
	External connection switch entry not found.
	"""
	EXTERNAL_CONNECTION_SWITCH_NOT_FOUND=353


	"""
	Feature not available.
	@public
	
	A specific application or API feature is temporarily, permanently or conditionally disabled.
	"""
	FEATURE_NOT_AVAILABLE=256


	"""
	FileSystemNavigator: Access control exception.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_ACCESS_CONTROL_EXCEPTION=303


	"""
	FileSystemNavigator: Authentication failure.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_AUTHENTICATION_FAILURE=309


	"""
	FileSystemNavigator: Could not resolve URL.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_COULD_NOT_RESOLVE_URL=310


	"""
	FileSystemNavigator: File already exists.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_FILE_ALREADY_EXISTS=308


	"""
	FileSystemNavigator: File not found.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_FILE_NOT_FOUND=304


	"""
	FileSystemNavigator: Illegal argument.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_ILLEGAL_ARGUMENT=301


	"""
	FileSystemNavigator: IO exception.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_IO_EXCEPTION=307


	"""
	FileSystemNavigator: Offset greater than length.
	@public
	
	Error thrown when trying to read a resource with an offset greater than the resource's length.
	"""
	FILESYSTEM_NAVIGATOR_OFFSET_GREATER_THAN_LENGTH=314


	"""
	FileSystemNavigator: Runtime exception.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_RUNTIME_EXCEPTION=306


	"""
	FileSystemNavigator: Security exception.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_SECURITY_EXCEPTION=302


	"""
	FileSystemNavigator: Unsupported operation.
	@public
	
	.
	"""
	FILESYSTEM_NAVIGATOR_UNSUPPORTED_OPERATION=305


	"""
	Generic private error.
	@private
	
	Generic error code for exceptions missing a private error code.
	"""
	GENERIC_PRIVATE_ERROR=227


	"""
	Generic public error.
	@public
	
	Generic error code for exceptions missing a public error code.
	"""
	GENERIC_PUBLIC_ERROR=226


	"""
	Could not find a hardware configuration.
	@public
	
	This error is thrown when a search is made for a specified server configuration an no eligible servers are found. Matching the specified configuration doesn't always work, depending on the target hardware, internal matching algorithms, and hardware availability. API calls that get this error should try again using a different target hardware configuration.
	"""
	HARDWARE_CONFIGURATIONS_NOT_FOUND=141


	"""
	HDFS cluster already exists.
	@private
	
	.
	"""
	HDFS_CLUSTER_ALREADY_EXISTS=246


	"""
	Illegal argument.
	@public
	
	Thrown when an argument or an argument combination is invalid.
	"""
	ILLEGAL_ARGUMENT=315


	"""
	Can't deploy empty infrastructure.
	@public
	
	.
	"""
	INFRASTRUCTURE_DEPLOY_WITH_NO_CHANGES=339


	"""
	Invalid infrastructure experimental priority.
	@private
	
	.
	"""
	INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_INVALID=291


	"""
	Infrastructure not found.
	@public
	
	This error is thrown when a specified infrastructure does not exist or when the user making the function call does not own any infrastructures.
	"""
	INFRASTRUCTURE_NOT_FOUND=152


	"""
	Infrastructure read-only while deploying.
	@public
	
	No modifications can be made while an Infrastructure is deploying. Elements cannot be created, deleted, edited, started or stopped. API calls that receive this error should wait until the operation is complete and try again.
	"""
	INFRASTRUCTURE_READ_ONLY_WHILE_DEPLOYING=216


	"""
	Infrastructure deploy custom stage definition reference not found.
	@public
	
	.
	"""
	INFRASTRUCTURE_STAGE_NOT_FOUND=349


	"""
	Infrastructure user removal is not allowed.
	@public
	
	The infrastructure owner cannot be removed.
	"""
	INFRASTRUCTURE_USER_REMOVE_NOT_ALLOWED=145


	"""
	Infrastructures mixing not allowed.
	@public
	
	Elements belonging to one Infrastructure cannot be used on another one. For example, a Drive created on Infrastructure A cannot be attached to an Instance belonging to Infrastructure B.
	"""
	INFRASTRUCTURES_MIXING_NOT_ALLOWED=110


	"""
	Invalid value given to the bKeepDetachingDrives flag.
	@public
	
	The number of Instances in an InstanceArray was reduced but the bKeepDetachingDrives flag was not set to true or false. The flag is required in order to know if the detaching Drives will be kept or deleted.
	"""
	INSTANCE_ARRAY_EDIT_DETACHING_DRIVES_INVALID_VALUE=265


	"""
	Not allowed to attach network.
	@public
	
	This error is thrown when trying to attach an InstanceArrayInterface to a Network that is pending deletion. Cancel the operation or choose another Network before trying again.
	"""
	INSTANCE_ARRAY_INTERFACE_NETWORK_ATTACH_NOT_ALLOWED=188


	"""
	Not allowed to detach network.
	@public
	
	.
	"""
	INSTANCE_ARRAY_INTERFACE_NETWORK_DETACH_NOT_ALLOWED=187


	"""
	InstanceArray interface not found.
	@public
	
	This error code may be the result of an internal error or anomaly, which cannot be fixed or worked around.
	"""
	INSTANCE_ARRAY_INTERFACE_NOT_FOUND=186


	"""
	Instance array mixing not allowed.
	@public
	
	A Drive can only be attached to an Instance belonging to the Instance Array that the Drive's parent DriveArray is attached to.
	"""
	INSTANCE_ARRAY_MIXING_NOT_ALLOWED=223


	"""
	Cannot delete the last instance from an InstanceArray.
	@public
	
	Some Clusters require that at least one Instance remains active at all times. The last Instance cannot be stopped or deleted. Stop or delete the entire Cluster instead.
	"""
	INSTANCE_IS_LAST_FROM_INSTANCE_ARRAY=178


	"""
	Failed to allocate a server to instance.
	@private
	
	InstanceArrays have a few properties for server matching (such as CPU count, RAM size, etc.). 
	
	During the deployment process of an InstanceArray or when quoting for available hardware, the search for the best server hardware match may fail with this error.
	"""
	INSTANCE_MATCH_SERVER_NOT_FOUND=29


	"""
	Instance not active.
	@public
	
	Some operations require the Instance's service status to be active. For example, powering the Instance on or off requires a server to be allocated to the Instance.
	"""
	INSTANCE_NOT_ACTIVE=100


	"""
	Invalid Column.
	@public
	
	The specified column does not exist. Use query() to retrieve the columns in a particular table.
	"""
	INVALID_COLUMN=259


	"""
	Invalid RSA cipher format.
	@public
	
	RSA ciphers must be prefixed with the ID of the RSA pair and a slash ("/"). See the temp_key_pair_id property of the object returned by transport_request_public_key().
	"""
	INVALID_FORMAT_RSA_CIPHER=163


	"""
	Invalid password characters.
	@public
	
	The password contains invalid characters.
	"""
	INVALID_PASSWORD_CHARACTERS=288


	"""
	Empty string password.
	@public
	
	Password cannot be an empty string.
	"""
	INVALID_PASSWORD_EMPTY=164


	"""
	Invalid absolute HTTP URL.
	@public
	
	Invalid absolute HTTP URL.
	"""
	INVALID_URL_HTTP_ABSOLUTE=165


	"""
	Invalid user type.
	@public
	
	An invalid user type was specified as an object property or function parameter.
	"""
	INVALID_USER_TYPE=162


	"""
	IP address has an invalid format.
	@public
	
	An IP address (IPv4 or IPv6) has an invalid format.
	"""
	IP_ADDRESS_INVALID=153


	"""
	IP address not found.
	@public
	
	The IP address does not exist.
	"""
	IP_ADDRESS_NOT_FOUND=166


	"""
	IP address not found for MAC address.
	@private
	
	This error is thrown when a search for the IP address that corresponds to a specified MAC address is made but nothing is found in the database.
	"""
	IP_COULD_NOT_FIND_FOR_MAC=85


	"""
	Cannot allocate IP addresses from a LAN Subnet.
	@private
	
	For the moment, IP addresses can not be allocated from a LAN Subnet.
	"""
	IP_LAN_ALLOCATION_NOT_SUPPORTED=13


	"""
	IP provision fails because no IP address is available.
	@public
	
	The error is thrown during the IP address provision, if the IP address is not in the Subnet's range.
	"""
	IP_PROVISION_NO_IP_AVAILABLE=83


	"""
	IP address reserve failure.
	@public
	
	The instance network interface and the Subnet must be on the same network (must have the same network_id property value).
	"""
	IP_RESERVE_FAILED=19


	"""
	Kerberos authentication timed out.
	@public
	
	The error is thrown if the API fails to authenticate to the KDC server for cases other than an invalid password.
	"""
	KERBEROS_AUTHENTICATION_TIMED_OUT=294


	"""
	Invalid kerberos principal.
	@private
	
	.
	"""
	KRB_INVALID_PRINCIPAL=249


	"""
	Kerberos operation not allowed.
	@private
	
	.
	"""
	KRB_OPERATION_NOT_ALLOWED=250


	"""
	Kerberos operation not supported.
	@private
	
	.
	"""
	KRB_OPERATION_NOT_SUPPORTED=248


	"""
	Kerberos policy not found.
	@private
	
	.
	"""
	KRB_POLICY_NOT_FOUND=275


	"""
	Kerberos principal already exists.
	@private
	
	.
	"""
	KRB_PRINCIPAL_ALREADY_EXISTS=254


	"""
	Kerberos principal not found.
	@private
	
	.
	"""
	KRB_PRINCIPAL_NOT_FOUND=251


	"""
	Language not available.
	@public
	
	This error is thrown when an attempt to change a user's selected language is made but the specified option is not available. API calls that receive this error should obtain a list of available language options before trying again.
	"""
	LANGUAGE_NOT_AVAILABLE=196


	"""
	Minimum count not met.
	@public
	
	There is a minimum and maximum amount of elements of each product type that a user can have on an infrastructure. This error is thrown when creating or editing an object, if the specified amount of child products is less than the minimum amount allowed. Some products require a minimum count of a particular child product type in order to function.
	"""
	LESS_THAN_MINIMUM_COUNT=244


	"""
	Unknown load balancing algorithm, mode or stats.
	@private
	
	An algorithm, mode, stats or other configuration values are unsupported by the current load balancer type.
	"""
	LOAD_BALANCER_CONFIG_VALUE_UNSUPPORTED=49


	"""
	Load balancer application has no servers connected.
	@private
	
	The chosen load balancer has no servers connected, or the application failed to gather all the connected instances.
	"""
	LOAD_BALANCER_HAS_NO_SERVERS=77


	"""
	The load balancing application does not exist.
	@private
	
	This error is thrown when the user did not choose a load balancing application type or the load balancing application type does not exist. Choose either HAPROXY or CRESCENDO load balancer.
	"""
	LOAD_BALANCER_INVALID_TYPE=20


	"""
	The load balancer server was not connected.
	@private
	
	When a specified server is not connected to the load balancing application, this error is thrown.
	"""
	LOAD_BALANCER_SERVER_CONNECTION_FAILED=33


	"""
	The connection between an instance and a load balancing application has not been edited.
	@private
	
	This error is thrown when the connection properties between an instance and a load balancing application have not been edited. Either the connection properties, or the connection location can be edited.
	"""
	LOAD_BALANCER_SERVER_EDIT_FAILED=41


	"""
	Connections, ports, or load balancer weight are not in the infrastructure limits.
	@private
	
	This error is thrown when the maximum connections, port numbers, or the load balancer weight are not in the instance configuration limit.
	"""
	LOAD_BALANCER_SERVER_INVALID_SETTINGS=72


	"""
	No instance supplied to the target load balancing application.
	@private
	
	When the load balancing application has no instances supplied, this error is thrown. Two or more servers should be enlisted for the operation.
	"""
	LOAD_BALANCER_SERVER_NOT_FOUND=15


	"""
	Maintenance mode.
	@public
	
	The respective API is not available during the current maintenance operation because it would conflict with maintenance commands or put a resource in danger of data corruption.
	"""
	MAINTENANCE_MODE=318


	"""
	Cannot connect to Marathon server.
	@private
	
	.
	"""
	MARATHON_SERVER_IS_UNAVAILABLE=284


	"""
	Maximum element count exceeded.
	@public
	
	There is a minimum and maximum amount of elements of each product type that a user can have on an infrastructure. This error is thrown when creating or editing an object, if the specified amount of elements of a certain type exceeds the maximum amount allowed.
	"""
	MAXIMUM_COUNT_EXCEEDED=204


	"""
	Cannot connect to Mesos server.
	@private
	
	.
	"""
	MESOS_SERVER_IS_UNAVAILABLE=285


	"""
	Only one WAN and SAN network per infrastructure.
	@public
	
	There is a minimum and maximum amount of elements of each product type that a user can have on an infrastructure. This error is thrown when creating a new network, if the maximum amount allowed for that network type is exceeded. An infrastructure can have only one WAN and one SAN attached to it.
	"""
	NETWORK_LIMIT_EXCEEDED=154


	"""
	Network cannot be deleted.
	@public
	
	This error is thrown when an attempt to delete a network is made but the operation is not allowed. WAN and SAN networks cannot be deleted from an infrastructure, and when merging two LAN networks, the network that is marked for deletion cannot be active, in order to prevent IP conflicts.
	"""
	NETWORK_NOT_DELETABLE=155


	"""
	Network type mismatch.
	@public
	
	The subnet destination and the corresponding network type must be the same.
	"""
	NETWORK_TYPE_MISMATCH=222


	"""
	No provisioner infrastructure found.
	@private
	
	A provisioner infrastructure must exist for the Drive import process.
	"""
	NO_PROVISIONER_INFRASTRUCTURES_FOUND=122


	"""
	Not allowed in guest mode.
	@public
	
	Some functions are not allowed in guest mode.
	"""
	NOT_ALLOWED_IN_GUEST_MODE=267


	"""
	Authentication failed.
	@public
	
	Authentication is required for most functions to work. This error is thrown when authentication fails. Possible reasons for failure include invalid request parameters, invalid authentication method, incorrect credentials, or an incorrect signature. The error can also occur on functions that perform authentication, if called directly.
	"""
	NOT_AUTHENTICATED=73


	"""
	Authorization failed.
	@public
	
	Some functions require an authorization check to make sure that the authenticated user is allowed to call a certain function or that the authenticated user is allowed to operate on a specified resource. This error is thrown when the authenticated user fails authorization.
	"""
	NOT_AUTHORIZED=71


	"""
	A feature is not implemented.
	@public
	
	Thrown when a certain feature or capability is not implemented yet, is reserved or is planned.
	"""
	NOT_IMPLEMENTED=3


	"""
	Nothing to update.
	@public
	
	Generic error code for when an update does not produce any results.
	"""
	NOTHING_TO_UPDATE=324


	"""
	The provided object is invalid.
	@public
	
	Objects have to respect a specific structure. This error is thrown when an object provided as a parameter does not respect that structure. API calls that receive this error should create a new object before trying again.
	"""
	OBJECT_IS_INVALID=218


	"""
	Operation type is not valid.
	@private
	
	The system only supports the following operation types that can be used for a product: "create", "edit", "clone", "delete".
	"""
	OPERATION_TYPE_INVALID=89


	"""
	OS asset not found.
	@public
	
	.
	"""
	OS_ASSET_NOT_FOUND=333


	"""
	OS bootstrap failed.
	@private
	
	OS bootstrap failed.
	"""
	OS_BOOTSTRAP_FAILED=229


	"""
	Type of the parameter provided is not as expected.
	@public
	
	Type of the parameter provided is not as expected. For example, any label provided is expected to be a string.
	"""
	PARAM_TYPE_MISMATCH=93


	"""
	Value of parameter is invalid.
	@public
	
	Some parameter values require specific formats of input data, or a specific set of allowed values.
	"""
	PARAM_VALUE_INVALID=143


	"""
	Password complexity is too low.
	@public
	
	This error is thrown when a user attempts to set or change a password to a string that doesn't meet the complexity requirements. The password must be at least 6 characters long and should contain both upper case and lower case letters, digits and punctuation marks.
	"""
	PASSWORD_COMPLEXITY_TOO_LOW=261


	"""
	Incorrect user password.
	@public
	
	Thrown when authentication fails due to incorrect user password.
	"""
	PASSWORD_INCORRECT=45


	"""
	Plugin is not registered.
	@public
	
	.
	"""
	PLUGIN_NOT_REGISTERED=258


	"""
	Primary key not set.
	@private
	
	This error is thrown when an attempt to update a row in a database table is made and the table's primary key is not set.
	"""
	PRIMARY_KEY_NOT_SET=260


	"""
	Product busy.
	@public
	
	.
	"""
	PRODUCT_BUSY_DEPLOY_ONGOING=290


	"""
	Product does not have a change operation.
	@private
	
	A product does not have a change operation.
	"""
	PRODUCT_CHANGE_OPERATION_NOT_FOUND=104


	"""
	Product edit not allowed.
	@public
	
	Some properties of a Product cannot be edited.
	"""
	PRODUCT_EDIT_NOT_ALLOWED=289


	"""
	Product not active.
	@public
	
	Some products are required to be active for certain operations to function properly. Make sure the product has its service status set to active before trying again.
	"""
	PRODUCT_NOT_ACTIVE=286


	"""
	Product does not exist.
	@public
	
	This error is thrown when a requested resource is not found in the database, based on the provided identifier, or does not belong to the infrastructure currently operated on. API calls that receive this error should reobtain the identifier(s) before trying again or look for the products on a different infrastructure.
	"""
	PRODUCT_NOT_FOUND=103


	"""
	Product operation type conflicts with parent operation type.
	@public
	
	Generally, a child product must have the operation type:
	 - delete, if its parent has operation type delete;
	 - delete or stop if a parent has operation type stop;
	 - create or stop or delete if a parent has operation type create;
	 - start, stop, delete if a parent has operation type start.
	
	Operation type edit can only exist on products with active service statuses and operation types create and edit.
	
	There may be exceptions where the rules are even stricter.
	"""
	PRODUCT_OPERATION_TYPE_CONFLICTS_PARENT=273


	"""
	Product with changes cannot be started.
	@public
	
	A product start operation is only allowed if the product's service status is set to stopped, ordered or suspended, or if a stop operation has been issued but not deployed yet.
	"""
	PRODUCT_WITH_CHANGES_CANNOT_BE_STARTED=209


	"""
	Product with changes cannot be stopped.
	@public
	
	A product stop operation is only allowed if the product's service status is set to active, ordered or suspended, or if a start operation has been issued but not deployed yet.
	"""
	PRODUCT_WITH_CHANGES_CANNOT_BE_STOPPED=208


	"""
	Invalid property.
	@public
	
	When creating/editing products or performing database interrogations, some properties and clauses need to be valid in order for the operation to be performed. This error is thrown when a function call has invalid elements.
	"""
	PROPERTY_IS_INVALID=345


	"""
	Mandatory property.
	@public
	
	When creating/editing products or performing database interrogations, some properties and clauses are mandatory in order for the operation to be performed. This error is thrown when a function call is missing some of those mandatory elements, such as storage type or query limits.
	"""
	PROPERTY_IS_MANDATORY=135


	"""
	Unknown property.
	@public
	
	Unknown object properties are sometimes not allowed to help catch caller typos or incorrect calls with objects which have optional properties with defaults.
	"""
	PROPERTY_IS_UNKNOWN=136


	"""
	Read-only property.
	@public
	
	.
	"""
	PROPERTY_READ_ONLY=326


	"""
	Resource reservation not found.
	@public
	
	The specified resource reservation was not found in the database.
	"""
	RESOURCE_RESERVATION_NOT_FOUND=266


	"""
	Secret not found.
	@public
	
	.
	"""
	SECRET_NOT_FOUND=332


	"""
	Selection limit exceeded.
	@public
	
	In a call to infrastructure_selection, user_selection, infrastructure_query or user_query the LIMIT clause was exceeded. Check the documentation for allowed values.
	"""
	SELECTION_LIMIT_EXCEEDED=239


	"""
	Server disk not found.
	@private
	
	.
	"""
	SERVER_DISK_NOT_FOUND=177


	"""
	An instance could not be located for the specified server.
	@private
	
	This error is thrown when a search is made for the active instance that uses the server with the specified ID and no result is found. Some operations require servers to be associated with an instance in order to work.
	"""
	SERVER_DOES_NOT_HAVE_INSTANCE=37


	"""
	Server firmware policy label too long.
	@private
	
	Server firmware policy label too long.
	"""
	SERVER_FIRMWARE_POLICY_LABEL_TOO_LONG=346


	"""
	An operation cannot take place because the server is associated with an instance.
	@private
	
	This error is thrown when an operation cannot be performed because a specified server is associated with an active instance. Some operations (such as marking a server as available or canceling a server reservation) require the server to not be associated with an instance in order to work.
	"""
	SERVER_HAS_INSTANCE=170


	"""
	Server interface not found.
	@private
	
	This error is thrown when a server interface with a certain ID is not found in the database.
	"""
	SERVER_INTERFACE_NOT_FOUND=158


	"""
	Server might not be ready for power status polling.
	@public
	
	This error is thrown when a server's power status is polled, but the server is not ready to respond (either undergoing provisioning or returning an IPMI error). API clients that receive this error should try polling the server's power status again later.
	"""
	SERVER_MIGHT_NOT_BE_READY_FOR_POWER_GET=210


	"""
	No server with given ID exists.
	@private
	
	This error is thrown when a search is made for a server by ID and the server doesn't exist in the database.
	"""
	SERVER_NOT_FOUND=11


	"""
	An operation cannot take place because the server is not reserved.
	@private
	
	Some operations require the server to be reserved for a specified infrastructure. For example, servers_reserve_cancel.
	"""
	SERVER_NOT_RESERVED=169


	"""
	The server power status cannot be changed. A deploy process is currently ongoing.
	@public
	
	Server power cannot be controlled while the Instance's parent Infrastructure's deploy status is "ongoing". Wait for the operation to conclude before trying again.
	"""
	SERVER_POWER_LOCKED_BY_ONGOING_OPERATION=214


	"""
	An operation cannot take place because the server is powered on.
	@public
	
	Some operations, such as unmounting Drives, expanding Drives, swapping an instance's server when a server_type is changed, require the affected servers to already be powered off before a deploy call.
	"""
	SERVER_POWERED_ON=87


	"""
	An operation cannot take place because the server is reserved.
	@private
	
	Some operations require the server to not be reserved for a specified infrastructure.
	"""
	SERVER_RESERVED=168


	"""
	Server type not found.
	@public
	
	Retrieving the server type failed because it does not exist. Use server_types() to obtain a list of existing server types.
	"""
	SERVER_TYPE_NOT_FOUND=175


	"""
	Server type is not available.
	@public
	
	This error is thrown when a request to provision servers is made and no servers matching the desired hardware configuration are available in the datacenter, or not enough matching servers are found. API calls that receive this error should try again later or modify the desired hardware specifications to find an eligible match.
	"""
	SERVER_TYPE_UNAVAILABLE=212


	"""
	Server type is unavailable for use by a ContainerPlatform.
	@public
	
	Variation of SERVER_TYPE_UNAVAILABLE thrown when failing to find an available server of the given server_type for use by a ContainerPlatform.
	"""
	SERVER_TYPE_UNAVAILABLE_FOR_CONTAINER_PLATFORM=311


	"""
	Server not found by UUID.
	@private
	
	This error is thrown during the DHCP boot process, if the server with the provided UUID is not found in the database. Signals that a server is not yet registered.
	"""
	SERVER_UUID_NOT_FOUND=9


	"""
	Service status is not valid.
	@public
	
	The system only supports the following service statuses that can be used for a product: "ordered", "active", "suspended", "stopped", "deleted".
	"""
	SERVICE_STATUS_INVALID=95


	"""
	SharedDrive is already connected.
	@public
	
	The SharedDrive is already connected to an InstanceArray or a ContainerArray.
	"""
	SHARED_DRIVE_IS_ALREADY_CONNECTED=245


	"""
	SharedDrive is not connected.
	@public
	
	The SharedDrive is not connected to an InstanceArray or a ContainerArray, although it is expected to be connected.
	"""
	SHARED_DRIVE_IS_NOT_CONNECTED=292


	"""
	SQL syntax error.
	@public
	
	This error is thrown when a database interrogation query has syntax errors in it, such as missing mandatory conditions or properties or having improperly defined ones.
	"""
	SQL_SYNTAX_ERROR=232


	"""
	SSH key unknown encoding.
	@public
	
	This error is thrown when a provided SSH key fails decoding. Public SSH key data is expected to be encoded in base64.
	"""
	SSH_KEY_DATA_INCORRECT_FORMAT=25


	"""
	Invalid OpenSSH/SSH2 key.
	@public
	
	This error is thrown during the SSH key validation process, if the decoded OpenSSH/SSH2 key data is not valid (invalid algorithm identifier length, invalid exponent size, invalid modulus size, etc. according to the specifications provided in RFC 3447 and  RFC 4716).
	"""
	SSH_KEY_INVALID_DATA_OPENSSH_SSH2=28


	"""
	Invalid PKCS#1 key.
	@public
	
	This error is thrown during the SSH key validation process, if the decoded PKCS 1 key data is not valid according to the specifications provided in RFC 3447.
	"""
	SSH_KEY_INVALID_DATA_PKCS1=31


	"""
	Invalid PKCS#8 key.
	@public
	
	This error is thrown during the SSH key validation process, if the decoded PKCS 8 key data is not valid according to the specifications provided in RFC 2459.
	"""
	SSH_KEY_INVALID_DATA_PKCS8=35


	"""
	SSH key pair not set.
	@private
	
	.
	"""
	SSH_KEY_PAIR_NOT_SET=331


	"""
	Unknown SSH key format.
	@public
	
	This error is thrown during SSH key validation, if the format that the data is stored in is not recognized. The allowed SSH key formats are OpenSSH, SSH2, PKCS #1, PKCS #8.
	"""
	SSH_KEY_UNKNOWN_FORMAT=23


	"""
	Unknown algorithm identifier prefix for a certain SSH key.
	@public
	
	This error is thrown during SSH key validation, if an unknown algorithm identifier prefix is found when decoding the SSH key data. The allowed algorithm identifiers are: ssh-rsa, ssh-dsa, and ssh-dss.
	"""
	SSH_KEY_UNKWOWN_ALGORITHM_IDENTIFIER=21


	"""
	The stage definition is deprecated.
	@public
	
	Once a stage definition is deprecated it can no longer be updated or referenced in workflows. Existing references are preserved.
	"""
	STAGE_DEFINITION_DEPRECATED=340


	"""
	Stage definition not found.
	@public
	
	.
	"""
	STAGE_DEFINITION_NOT_FOUND=337


	"""
	Storage allocation error.
	@public
	
	.
	"""
	STORAGE_ALLOCATION_ERROR=327


	"""
	Storage pool destination is the same as source.
	@private
	
	This error is thrown when moving data between two storage pools, if the provided destination storage pool is the same as the source storage pool.
	"""
	STORAGE_POOL_DESTINATION_SAME_AS_SOURCE=278


	"""
	Storage pool does not have enough free space.
	@private
	
	This error is thrown when moving data between two storage pools, if the provided destination storage pool does not have enough free space to complete the operation.
	"""
	STORAGE_POOL_NOT_ENOUGH_FREE_SPACE=279


	"""
	Storage pool is not found.
	@private
	
	This error is thrown when a storage pool cannot be found based on the provided criteria. This situation can appear if the system cannot find any storage pools that have a certain storage type, if there is no information associated with a certain storage pool ID, or if the provided ID does not exist.
	"""
	STORAGE_POOL_NOT_FOUND=64


	"""
	Snapshot not found.
	@public
	
	This error is thrown when searching for a drive snapshot or attempting to retrieve or operate on a specific snapshot, and no information related to the provided ID is found in the database.
	"""
	STORAGE_SNAPSHOT_NOT_FOUND=94


	"""
	Volume template not found.
	@public
	
	This error is thrown when an attempt to retrieve or use a volume template is made, but the specified volume template is not found on the storage. API clients that receive this error should obtain a list of available templates using volume_templates() before trying again.
	"""
	STORAGE_VOLUME_TEMPLATE_NOT_FOUND=68


	"""
	Snapshot not found for volume template ID.
	@private
	
	When a volume template is created, a snapshot of this template is also created. This error is thrown when something went wrong and the snapshot for the specified volume template ID cannot be found.
	"""
	STORAGE_VOLUME_TEMPLATE_SNAPSHOT_NOT_FOUND=75


	"""
	Subnet create failure.
	@private
	
	This error is thrown when an attempt to create a new subnet is made and the system fails to allocate the necessary resources. If a system runs out of IPv4 or IPv6 addresses, then a new RIPE subnet cannot be created.
	"""
	SUBNET_CREATE_FAILED=16


	"""
	Subnet exhausted.
	@public
	
	This error is thrown when a subnet runs out of available IP addresses.
	"""
	SUBNET_EXHAUSTED=160


	"""
	Maxim count of Subnets reached.
	@public
	
	This error is thrown when attempting to create a new subnet if the maximum count of allowed subnets has already been reached. There is a maximum count of one public IPv6 subnet and 10 public IPv4 subnets for the WAN. Subnets for LAN networks cannot be allocated at the moment.
	"""
	SUBNET_MAXIMUM_COUNT_REACHED=7


	"""
	Not allowed to change the Subnet's parent network.
	@public
	
	This operation is currently unsupported.
	"""
	SUBNET_NETWORK_CHANGING_NOT_ALLOWED=189


	"""
	Switch device interface does not exist.
	@private
	
	This error is thrown when searching for a switch device interface that does not exist. The network equipment might not exist, or it might not be registered in the database yet.
	"""
	SWITCH_DEVICE_INTERFACE_NOT_FOUND=207


	"""
	Switch device does not exist.
	@public
	
	.
	"""
	SWITCH_DEVICE_NOT_FOUND=351


	"""
	Table not found.
	@public
	
	This error is thrown when a database query is made and it contains an incorrect table name (keyword query, or SQL-like query), or a table that is not accessible to the user making the interrogation.
	"""
	TABLE_NOT_FOUND=231


	"""
	Tag already exists.
	@public
	
	.
	"""
	TAG_ALREADY_EXISTS=344


	"""
	Tag not found.
	@public
	
	.
	"""
	TAG_NOT_FOUND=343


	"""
	Specified timespan is greater than allowed.
	@public
	
	Reports cannot span more than 5 years.
	"""
	TIMESPAN_TOO_GREAT=220


	"""
	Invalid timestamp format.
	@public
	
	This error is thrown during timestamp validation, if the provided timpestamp does not match the required format. Timestamps must be in a particular format (ISO 8601) and in UTC time. Example format: "2013-12-31T14:09:12Z".
	"""
	TIMESTAMP_INVALID=149


	"""
	Unsupported hash algorithm.
	@public
	
	This error is thrown when the provided hashing algorithm is not among the supported list. The recommended algorithms are md5, sha256, and sha512.
	"""
	UNSUPPORTED_HASH_ALGO=271


	"""
	File upload failed.
	@private
	
	An error has been encountered while uploading the file.
	"""
	UPLOAD_FAILED=114


	"""
	Upload file creation failed.
	@private
	
	A temporary file for the AJAX upload could not be created.
	"""
	UPLOAD_FILE_CREATION_FAILED=115


	"""
	Upload file move failed.
	@private
	
	The temporary file for the AJAX upload could not be moved.
	"""
	UPLOAD_FILE_MOVE_FAILED=118


	"""
	Upload file open failed.
	@private
	
	The temporary file created for the AJAX upload could not be opened for writing.
	"""
	UPLOAD_FILE_OPEN_FAILED=117


	"""
	Invalid chunk offset.
	@public
	
	.
	"""
	UPLOAD_INVALID_CHUNK_OFFSET=317


	"""
	Invalid upload get requirements.
	@private
	
	Invalid upload get requirements have been provided. The get requirements must contain valid upload object properties.
	"""
	UPLOAD_INVALID_GET_REQUIREMENTS=121


	"""
	Upload POST data is too large.
	@public
	
	.
	"""
	UPLOAD_POST_TOO_LARGE=316


	"""
	Upload stream open failed.
	@private
	
	The AJAX upload stream could not be opened for reading.
	"""
	UPLOAD_STREAM_OPEN_FAILED=116


	"""
	URL_TYPE_UNKNOWN.
	@public
	
	URL type is unknown.
	"""
	URL_TYPE_UNKNOWN=300


	"""
	The logged in account and the one that was requested to change the email adress must be the same.
	@public
	
	You logged in with a different account than the one you requested to change the email address for. The change process was cancelled.
	"""
	USER_CHANGE_LOGIN_EMAIL_WRONG_ACCOUNT_LOGIN=287


	"""
	A user cannot add himself as his own delegate.
	@public
	
	A user cannot add himself as his delegate. Make sure the delegate's email address is different from the currently logged in user's email address before trying again.
	"""
	USER_DELEGATE_CANNOT_ADD_SELF=193


	"""
	User account is disabled.
	@public
	
	Some operations are not allowed on a disabled account. Disabled accounts cannot be authenticated and are restricted from some associations or modifications for security reasons.
	"""
	USER_DISABLED=62


	"""
	Duplicate user login emails are not allowed.
	@public
	
	A login email address is uniquely associated with a single user account. This error is thrown when creating a new user account or when changing an existing user's login email, if the provided email address already exists in the database.
	"""
	USER_LOGIN_EMAIL_ALREADY_EXISTS=57


	"""
	User email is already verified.
	@public
	
	When creating a new user account, a verification email is sent to the specified email address. The email contains a verification HTTP URL which, when accessed, marks the user as verified and enables the user to authenticate. This error is thrown when a request to resend the verification email is made for a user account that has already been verified.
	"""
	USER_LOGIN_EMAIL_ALREADY_VERIFIED=262


	"""
	The new user login email is the same as the existing one.
	@public
	
	This error is thrown when a user login email address change is requested and the new email address is the same as the old one.
	"""
	USER_LOGIN_EMAIL_IS_THE_SAME=192


	"""
	User login email is not verified.
	@public
	
	When creating a new user account, a verification email is sent to the specified email address. For security reasons, most operations are not allowed on newly created user accounts with an unverified login email address. This error is thrown when an authentication request or a password reset request is made for a user that has not yet verified his email address.
	"""
	USER_LOGIN_EMAIL_NOT_VERIFIED=46


	"""
	User login session's AES key not found in cookie.
	@public
	
	The cookies do not have the aes_key property set.
	"""
	USER_LOGIN_SESSION_AES_KEY_NOT_FOUND_IN_COOKIE=297


	"""
	User login session has expired.
	@public
	
	The user login session has expired.
	"""
	USER_LOGIN_SESSION_EXPIRED=298


	"""
	User login session not found.
	@public
	
	The user login session corresponding to a specified user login session ID (object property, function parameter, etc) was not found.
	"""
	USER_LOGIN_SESSION_NOT_FOUND=295


	"""
	User login session not found in cookie.
	@public
	
	The cookies do not have the user_login_session_id property set.
	"""
	USER_LOGIN_SESSION_NOT_FOUND_IN_COOKIE=296


	"""
	User not authenticated with Kerberos.
	@public
	
	The user is not authenticated with Kerberos.
	"""
	USER_NOT_AUTHENTICATED_WITH_KERBEROS=299


	"""
	User is not billable.
	@public
	
	Only billable users can own infrastructures and be charged for resource utilization. This error is thrown when a delegated user tries to create an infrastructure or a server reservation in his own name, when an attempt to change an infrastructure or a reservation's owner to a non-billable user is made, or when an infrastructure owner loses his privileges and attempts to deploy operations other than stopping or deleting elements.
	"""
	USER_NOT_BILLABLE=217


	"""
	User not found.
	@public
	
	The user corresponding to a specified user ID (object property, function parameter, etc) was not found.
	"""
	USER_NOT_FOUND=42


	"""
	Duplicate SSH keys are not allowed.
	@public
	
	A user cannot have duplicate SSH keys. This error is thrown when creating a new SSH key, if the provided key is the same as an already existing, active SSH key.
	"""
	USER_SSH_KEY_DUPLICATE=10


	"""
	SSH key not found.
	@public
	
	This error is thrown when information regarding a specified SSH key is not found in the database, based on the provided SSH key ID (object property, function parameter, etc).
	"""
	USER_SSH_KEY_NOT_FOUND=6


	"""
	User SSH keys maximum count exceeded.
	@public
	
	There is a minimum and maximum amount of elements of each type that a user can have. This error is thrown when adding a new SSH key, if the maximum amount allowed is exceeded. A user can only add a total of 5 SSH keys to his account.
	"""
	USER_SSH_KEYS_MAXIMUM_COUNT_EXCEEDED=8


	"""
	User suspended.
	@public
	
	This error is thrown when an attempt to deploy an operation other than a delete on an infrastructure is made, if the infrastructure owner is suspended, or when an attempt to create a new server reservation or to change the owner of an existing server reservation is made, and the new reservation owner is suspended.
	"""
	USER_SUSPENDED=276


	"""
	Wrong e-mail for password authentication.
	@public
	
	This error is thrown when testing the credentials of the logged in user (stored in a cookie) against the ones received as parameters. The email address of the already logged in user must coincide with the provided login email address.
	"""
	USER_TEST_CREDENTIALS_EMAIL_MISMATCH=268


	"""
	Variable already declared.
	@public
	
	.
	"""
	VARIABLE_ALREADY_DECLARED=342


	"""
	Variable name invalid.
	@public
	
	Variable names must start with a letter (a-z), end with a letter or digit (a-z0-9), and have as interior characters only letters, digits, and underscores. For example: Number_1.
	"""
	VARIABLE_NAME_INVALID=335


	"""
	Variable name reserved.
	@public
	
	The specified variable name is reserved.
	"""
	VARIABLE_NAME_RESERVED=338


	"""
	Variable is not defined.
	@public
	
	A variable referenced in a StageDefinition is not defined in the execution context.
	"""
	VARIABLE_NOT_DEFINED=350


	"""
	Variable not found.
	@public
	
	<schema>Variable</schema> definition object not found.
	"""
	VARIABLE_NOT_FOUND=334


	"""
	Drive import already cancelled.
	@private
	
	The import could not be cancelled as it has already been cancelled.
	"""
	VOLUME_IMPORT_ALREADY_CANCELLED=124


	"""
	Import already finalized.
	@private
	
	The import could not be cancelled as it has already been finalized.
	"""
	VOLUME_IMPORT_ALREADY_FINALIZED=125


	"""
	Provisioner volume import cron function already running.
	@private
	
	The lock could not be acquired. The provisioner_volume_imports_initiate cron function is already running.
	"""
	VOLUME_IMPORT_CRON_FUNCTION_ALREADY_RUNNING=123


	"""
	Flat file size get failed.
	@private
	
	The size of the flat file could not be retrieved.
	"""
	VOLUME_IMPORT_FLAT_FILE_SIZE_GET_FAILED=131


	"""
	Invalid import operation.
	@private
	
	The provided import operation for the data types validation function is not valid. The import operation must be one of the following: "create", "update", "delete".
	"""
	VOLUME_IMPORT_INVALID_OPERATION=132


	"""
	Invalid OVA file.
	@private
	
	The file MIME does not match the required OVA file MIME. The OVA file must be a tar archive.
	"""
	VOLUME_IMPORT_INVALID_OVA=128


	"""
	Import not cancelled.
	@private
	
	The import could not be restarted. Only cancelled imports can be restarted.
	"""
	VOLUME_IMPORT_NOT_CANCELLED=126


	"""
	OVA file deflation failed.
	@private
	
	The OVA file could not be deflated. The OVA file might be broken.
	"""
	VOLUME_IMPORT_OVA_DEFLATION_FAILED=130


	"""
	OVA temporary deflation directory creation failed.
	@private
	
	A temporary directory for the OVA deflation could not be created.
	"""
	VOLUME_IMPORT_OVA_DIRECTORY_CREATION_FAILED=129


	"""
	OVA MIME get failed.
	@private
	
	The OVA file MIME could not be retrieved.
	"""
	VOLUME_IMPORT_OVA_MIME_GET_FAILED=127


	"""
	Volume template is deprecated and cannot be provisioned.
	@public
	
	Volume template is deprecated and cannot be provisioned.
	"""
	VOLUME_TEMPLATE_DEPRECATED=323


	"""
	VPLS instance not found.
	@private
	
	This error is thrown when an attempt to retrieve information regarding a VPLS instance is made, but no information regarding the provided network ID or switch device ID exists in the database.
	"""
	VPLS_INSTANCE_NOT_FOUND=200


	"""
	North switch not found for vpls.
	@private
	
	This error is thrown when an attempt to retrieve information regarding a VPLS instance is made, but no information regarding the provided network ID or north switch device ID exists in the database.
	"""
	VPLS_NORTH_INSTANCE_NOT_FOUND=215


	"""
	Workflow not found.
	@public
	
	.
	"""
	WORKFLOW_NOT_FOUND=347


	"""
	Workflow stage not found.
	@public
	
	.
	"""
	WORKFLOW_STAGE_NOT_FOUND=348
	"""
	* Private error codes are not allowed on public RPC endpoints.
	"""
	arrPrivateErrorIDs=[
		AGENT_NOT_FOUND,
		BOOT_BOOTABLE_DRIVES_NOT_FOUND,
		COOKIE_TYPE_NOT_ALLOWED,
		DHCP_LEASE_COULD_NOT_FIND_FOR_MAC,
		EXTERNAL_CONNECTION_NOT_FOUND,
		EXTERNAL_CONNECTION_SWITCH_INVALID_RULE,
		EXTERNAL_CONNECTION_SWITCH_NOT_FOUND,
		GENERIC_PRIVATE_ERROR,
		HDFS_CLUSTER_ALREADY_EXISTS,
		INFRASTRUCTURE_EXPERIMENTAL_PRIORITY_INVALID,
		INSTANCE_MATCH_SERVER_NOT_FOUND,
		IP_COULD_NOT_FIND_FOR_MAC,
		IP_LAN_ALLOCATION_NOT_SUPPORTED,
		KRB_INVALID_PRINCIPAL,
		KRB_OPERATION_NOT_ALLOWED,
		KRB_OPERATION_NOT_SUPPORTED,
		KRB_POLICY_NOT_FOUND,
		KRB_PRINCIPAL_ALREADY_EXISTS,
		KRB_PRINCIPAL_NOT_FOUND,
		LOAD_BALANCER_CONFIG_VALUE_UNSUPPORTED,
		LOAD_BALANCER_HAS_NO_SERVERS,
		LOAD_BALANCER_INVALID_TYPE,
		LOAD_BALANCER_SERVER_CONNECTION_FAILED,
		LOAD_BALANCER_SERVER_EDIT_FAILED,
		LOAD_BALANCER_SERVER_INVALID_SETTINGS,
		LOAD_BALANCER_SERVER_NOT_FOUND,
		MARATHON_SERVER_IS_UNAVAILABLE,
		MESOS_SERVER_IS_UNAVAILABLE,
		NO_PROVISIONER_INFRASTRUCTURES_FOUND,
		OPERATION_TYPE_INVALID,
		OS_BOOTSTRAP_FAILED,
		PRIMARY_KEY_NOT_SET,
		PRODUCT_CHANGE_OPERATION_NOT_FOUND,
		SERVER_DISK_NOT_FOUND,
		SERVER_DOES_NOT_HAVE_INSTANCE,
		SERVER_FIRMWARE_POLICY_LABEL_TOO_LONG,
		SERVER_HAS_INSTANCE,
		SERVER_INTERFACE_NOT_FOUND,
		SERVER_NOT_FOUND,
		SERVER_NOT_RESERVED,
		SERVER_RESERVED,
		SERVER_UUID_NOT_FOUND,
		SSH_KEY_PAIR_NOT_SET,
		STORAGE_POOL_DESTINATION_SAME_AS_SOURCE,
		STORAGE_POOL_NOT_ENOUGH_FREE_SPACE,
		STORAGE_POOL_NOT_FOUND,
		STORAGE_VOLUME_TEMPLATE_SNAPSHOT_NOT_FOUND,
		SUBNET_CREATE_FAILED,
		SWITCH_DEVICE_INTERFACE_NOT_FOUND,
		UPLOAD_FAILED,
		UPLOAD_FILE_CREATION_FAILED,
		UPLOAD_FILE_MOVE_FAILED,
		UPLOAD_FILE_OPEN_FAILED,
		UPLOAD_INVALID_GET_REQUIREMENTS,
		UPLOAD_STREAM_OPEN_FAILED,
		VOLUME_IMPORT_ALREADY_CANCELLED,
		VOLUME_IMPORT_ALREADY_FINALIZED,
		VOLUME_IMPORT_CRON_FUNCTION_ALREADY_RUNNING,
		VOLUME_IMPORT_FLAT_FILE_SIZE_GET_FAILED,
		VOLUME_IMPORT_INVALID_OPERATION,
		VOLUME_IMPORT_INVALID_OVA,
		VOLUME_IMPORT_NOT_CANCELLED,
		VOLUME_IMPORT_OVA_DEFLATION_FAILED,
		VOLUME_IMPORT_OVA_DIRECTORY_CREATION_FAILED,
		VOLUME_IMPORT_OVA_MIME_GET_FAILED,
		VPLS_INSTANCE_NOT_FOUND,
		VPLS_NORTH_INSTANCE_NOT_FOUND	]


	"""
	* Public error codes are allowed on all endpoints.
	"""
	arrPublicErrorIDs=[
		ANSIBLE_BUNDLE_NOT_FOUND,
		API_KEY_MISMATCH,
		API_KEY_NOT_FOUND,
		AUTHENTICATOR_OTP_REJECTED,
		CANNOT_AUTO_MANAGE_IP_ALLOCATION,
		CLUSTER_INSTANCE_ARRAY_HAS_NO_WAN_INTERFACE,
		CLUSTER_MIXING_NOT_ALLOWED,
		COMPUTE_NODE_ARRAY_EDIT_DETACHING_DRIVES_INVALID_VALUE,
		CONTAINER_ARRAY_INTERFACE_NETWORK_ATTACH_NOT_ALLOWED,
		CONTAINER_ARRAY_INTERFACE_NETWORK_DETACH_NOT_ALLOWED,
		CONTAINER_PLATFORM_NOT_ENOUGH_RESOURCES,
		CONTAINER_PLATFORM_NOT_ENOUGH_SPACE_FOR_PERSISTENT_DIRECTORIES,
		DATA_LOSS_NOT_CONFIRMED,
		DATACENTER_NOT_FOUND,
		DATACENTER_PARENT_NOT_FOUND,
		DELEGATE_USER_LOGIN_EMAIL_NOT_VERIFIED,
		DISK_TYPE_INVALID,
		DNS_LABEL_RESERVED,
		DOMAIN_LABEL_ALREADY_IN_USE,
		DOMAIN_LABEL_INVALID,
		DOMAIN_LABEL_UNABLE_TO_RESOLVE,
		DRIVE_ARRAY_COUNT_DATA_SAFETY_RESTRICTION,
		DRIVE_ARRAY_DETACH_NOT_ALLOWED,
		DRIVE_ARRAY_INSTANCE_ARRAY_DETACH_NOT_ALLOWED,
		DRIVE_ARRAY_IS_ATTACHED,
		DRIVE_ARRAY_IS_NOT_ATTACHED,
		DRIVE_ARRAY_MULTIPLE_ATTACH_NOT_ALLOWED,
		DRIVE_CANNOT_BE_ATTACHED_TO_A_DELETED_INSTANCE,
		DRIVE_IS_NOT_ATTACHED,
		DRIVE_NOT_ACTIVE,
		DRIVE_SIZE_INVALID,
		EDIT_MADE_WITH_EXPIRED_OBJECT,
		EMAIL_ADDRESS_ALREADY_CHANGED,
		EMAIL_ADDRESS_INVALID,
		EVENT_NOT_FOUND,
		FEATURE_NOT_AVAILABLE,
		FILESYSTEM_NAVIGATOR_ACCESS_CONTROL_EXCEPTION,
		FILESYSTEM_NAVIGATOR_AUTHENTICATION_FAILURE,
		FILESYSTEM_NAVIGATOR_COULD_NOT_RESOLVE_URL,
		FILESYSTEM_NAVIGATOR_FILE_ALREADY_EXISTS,
		FILESYSTEM_NAVIGATOR_FILE_NOT_FOUND,
		FILESYSTEM_NAVIGATOR_ILLEGAL_ARGUMENT,
		FILESYSTEM_NAVIGATOR_IO_EXCEPTION,
		FILESYSTEM_NAVIGATOR_OFFSET_GREATER_THAN_LENGTH,
		FILESYSTEM_NAVIGATOR_RUNTIME_EXCEPTION,
		FILESYSTEM_NAVIGATOR_SECURITY_EXCEPTION,
		FILESYSTEM_NAVIGATOR_UNSUPPORTED_OPERATION,
		GENERIC_PUBLIC_ERROR,
		HARDWARE_CONFIGURATIONS_NOT_FOUND,
		ILLEGAL_ARGUMENT,
		INFRASTRUCTURE_DEPLOY_WITH_NO_CHANGES,
		INFRASTRUCTURE_NOT_FOUND,
		INFRASTRUCTURE_READ_ONLY_WHILE_DEPLOYING,
		INFRASTRUCTURE_STAGE_NOT_FOUND,
		INFRASTRUCTURE_USER_REMOVE_NOT_ALLOWED,
		INFRASTRUCTURES_MIXING_NOT_ALLOWED,
		INSTANCE_ARRAY_EDIT_DETACHING_DRIVES_INVALID_VALUE,
		INSTANCE_ARRAY_INTERFACE_NETWORK_ATTACH_NOT_ALLOWED,
		INSTANCE_ARRAY_INTERFACE_NETWORK_DETACH_NOT_ALLOWED,
		INSTANCE_ARRAY_INTERFACE_NOT_FOUND,
		INSTANCE_ARRAY_MIXING_NOT_ALLOWED,
		INSTANCE_IS_LAST_FROM_INSTANCE_ARRAY,
		INSTANCE_NOT_ACTIVE,
		INVALID_COLUMN,
		INVALID_FORMAT_RSA_CIPHER,
		INVALID_PASSWORD_CHARACTERS,
		INVALID_PASSWORD_EMPTY,
		INVALID_URL_HTTP_ABSOLUTE,
		INVALID_USER_TYPE,
		IP_ADDRESS_INVALID,
		IP_ADDRESS_NOT_FOUND,
		IP_PROVISION_NO_IP_AVAILABLE,
		IP_RESERVE_FAILED,
		KERBEROS_AUTHENTICATION_TIMED_OUT,
		LANGUAGE_NOT_AVAILABLE,
		LESS_THAN_MINIMUM_COUNT,
		MAINTENANCE_MODE,
		MAXIMUM_COUNT_EXCEEDED,
		NETWORK_LIMIT_EXCEEDED,
		NETWORK_NOT_DELETABLE,
		NETWORK_TYPE_MISMATCH,
		NOT_ALLOWED_IN_GUEST_MODE,
		NOT_AUTHENTICATED,
		NOT_AUTHORIZED,
		NOT_IMPLEMENTED,
		NOTHING_TO_UPDATE,
		OBJECT_IS_INVALID,
		OS_ASSET_NOT_FOUND,
		PARAM_TYPE_MISMATCH,
		PARAM_VALUE_INVALID,
		PASSWORD_COMPLEXITY_TOO_LOW,
		PASSWORD_INCORRECT,
		PLUGIN_NOT_REGISTERED,
		PRODUCT_BUSY_DEPLOY_ONGOING,
		PRODUCT_EDIT_NOT_ALLOWED,
		PRODUCT_NOT_ACTIVE,
		PRODUCT_NOT_FOUND,
		PRODUCT_OPERATION_TYPE_CONFLICTS_PARENT,
		PRODUCT_WITH_CHANGES_CANNOT_BE_STARTED,
		PRODUCT_WITH_CHANGES_CANNOT_BE_STOPPED,
		PROPERTY_IS_INVALID,
		PROPERTY_IS_MANDATORY,
		PROPERTY_IS_UNKNOWN,
		PROPERTY_READ_ONLY,
		RESOURCE_RESERVATION_NOT_FOUND,
		SECRET_NOT_FOUND,
		SELECTION_LIMIT_EXCEEDED,
		SERVER_MIGHT_NOT_BE_READY_FOR_POWER_GET,
		SERVER_POWER_LOCKED_BY_ONGOING_OPERATION,
		SERVER_POWERED_ON,
		SERVER_TYPE_NOT_FOUND,
		SERVER_TYPE_UNAVAILABLE,
		SERVER_TYPE_UNAVAILABLE_FOR_CONTAINER_PLATFORM,
		SERVICE_STATUS_INVALID,
		SHARED_DRIVE_IS_ALREADY_CONNECTED,
		SHARED_DRIVE_IS_NOT_CONNECTED,
		SQL_SYNTAX_ERROR,
		SSH_KEY_DATA_INCORRECT_FORMAT,
		SSH_KEY_INVALID_DATA_OPENSSH_SSH2,
		SSH_KEY_INVALID_DATA_PKCS1,
		SSH_KEY_INVALID_DATA_PKCS8,
		SSH_KEY_UNKNOWN_FORMAT,
		SSH_KEY_UNKWOWN_ALGORITHM_IDENTIFIER,
		STAGE_DEFINITION_DEPRECATED,
		STAGE_DEFINITION_NOT_FOUND,
		STORAGE_ALLOCATION_ERROR,
		STORAGE_SNAPSHOT_NOT_FOUND,
		STORAGE_VOLUME_TEMPLATE_NOT_FOUND,
		SUBNET_EXHAUSTED,
		SUBNET_MAXIMUM_COUNT_REACHED,
		SUBNET_NETWORK_CHANGING_NOT_ALLOWED,
		SWITCH_DEVICE_NOT_FOUND,
		TABLE_NOT_FOUND,
		TAG_ALREADY_EXISTS,
		TAG_NOT_FOUND,
		TIMESPAN_TOO_GREAT,
		TIMESTAMP_INVALID,
		UNSUPPORTED_HASH_ALGO,
		UPLOAD_INVALID_CHUNK_OFFSET,
		UPLOAD_POST_TOO_LARGE,
		URL_TYPE_UNKNOWN,
		USER_CHANGE_LOGIN_EMAIL_WRONG_ACCOUNT_LOGIN,
		USER_DELEGATE_CANNOT_ADD_SELF,
		USER_DISABLED,
		USER_LOGIN_EMAIL_ALREADY_EXISTS,
		USER_LOGIN_EMAIL_ALREADY_VERIFIED,
		USER_LOGIN_EMAIL_IS_THE_SAME,
		USER_LOGIN_EMAIL_NOT_VERIFIED,
		USER_LOGIN_SESSION_AES_KEY_NOT_FOUND_IN_COOKIE,
		USER_LOGIN_SESSION_EXPIRED,
		USER_LOGIN_SESSION_NOT_FOUND,
		USER_LOGIN_SESSION_NOT_FOUND_IN_COOKIE,
		USER_NOT_AUTHENTICATED_WITH_KERBEROS,
		USER_NOT_BILLABLE,
		USER_NOT_FOUND,
		USER_SSH_KEY_DUPLICATE,
		USER_SSH_KEY_NOT_FOUND,
		USER_SSH_KEYS_MAXIMUM_COUNT_EXCEEDED,
		USER_SUSPENDED,
		USER_TEST_CREDENTIALS_EMAIL_MISMATCH,
		VARIABLE_ALREADY_DECLARED,
		VARIABLE_NAME_INVALID,
		VARIABLE_NAME_RESERVED,
		VARIABLE_NOT_DEFINED,
		VARIABLE_NOT_FOUND,
		VOLUME_TEMPLATE_DEPRECATED,
		WORKFLOW_NOT_FOUND,
		WORKFLOW_STAGE_NOT_FOUND	]

	