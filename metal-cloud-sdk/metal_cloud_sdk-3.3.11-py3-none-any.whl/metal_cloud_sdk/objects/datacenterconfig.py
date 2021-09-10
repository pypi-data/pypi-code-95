# -*- coding: utf-8 -*-

class DatacenterConfig(object):
	"""
	Configuration specific to a particular datacenter.
	"""

	def __init__(self, SANRoutedSubnet, BSIMachinesSubnetIPv4CIDR, BSIVRRPListenIPv4, BSIMachineListenIPv4List, BSIExternallyVisibleIPv4, repoURLRoot, repoURLRootQuarantineNetwork, NTPServers, DNSServers, TFTPServerWANVRRPListenIPv4, dataLakeEnabled, allowVLANOverrides, switchProvisioner):
		self.SANRoutedSubnet = SANRoutedSubnet;
		self.BSIMachinesSubnetIPv4CIDR = BSIMachinesSubnetIPv4CIDR;
		self.BSIVRRPListenIPv4 = BSIVRRPListenIPv4;
		self.BSIMachineListenIPv4List = BSIMachineListenIPv4List;
		self.BSIExternallyVisibleIPv4 = BSIExternallyVisibleIPv4;
		self.repoURLRoot = repoURLRoot;
		self.repoURLRootQuarantineNetwork = repoURLRootQuarantineNetwork;
		self.NTPServers = NTPServers;
		self.DNSServers = DNSServers;
		self.TFTPServerWANVRRPListenIPv4 = TFTPServerWANVRRPListenIPv4;
		self.dataLakeEnabled = dataLakeEnabled;
		self.allowVLANOverrides = allowVLANOverrides;
		self.switchProvisioner = switchProvisioner;


	"""
	CIDR format subnet. The datacenter SAN subnet, routed and protected by ACLs
	on switches.
	"""
	SANRoutedSubnet = None;

	"""
	BSI servers primary IPs subnet, in CIDR format. All IP addresses in
	BSIMachineListenIPv4List and BSIVRRPListenIPv4 should be part of this
	subnet. This subnet is configured on SAN ACLs, other ACLs, customer server's
	firewall rules, traffic subnet exclusion list for traffic monitoring, etc.
	"""
	BSIMachinesSubnetIPv4CIDR = None;

	"""
	This IPv4 address is whitelisted in the switch ACLs as the Metal Cloud head
	server - for HTTP/HTTPS calls. VRRP, movable IP. Metal Cloud services listen
	on this IP (usually by listening on 0.0.0.0). The IP address moves to
	another Metal Cloud machine in case of a fallback.
	"""
	BSIVRRPListenIPv4 = None;

	"""
	An array of IP addresses, which are the primary permanent IP addresses of
	Metal Cloud head machines of a specific datacenter.
	"""
	BSIMachineListenIPv4List = [];

	"""
	Metal Cloud services do not listen on this IP and it is not configured on
	Metal Cloud head machines. This is a router IP. Metal Cloud head servers
	appear to be initiating connections from this IP, so it is used to allow
	Metal Cloud through other system firewalls.
	"""
	BSIExternallyVisibleIPv4 = None;

	"""
	HTTP(S) root URL for the general purpose HTTP repository (package manager
	resources, deploy setup files, etc.). It does not end in a slash.
	"""
	repoURLRoot = None;

	"""
	Repo URL root for the quarantine network (installation network) where DNS is
	not available yet.
	"""
	repoURLRootQuarantineNetwork = None;

	"""
	IP addresses of NTP servers to be used in cloudinit and iLO and other
	places. Try to specify at least two.
	"""
	NTPServers = [];

	"""
	IP addresses of DNS servers to be used in the DHCP response and in utility
	OS for setting DNS servers in iLO. Try to specify at least two.
	"""
	DNSServers = [];

	"""
	Host (IP:port) of the Windows machine hosting the Key Management Service.
	Set to empty string to disable.
	"""
	KMS = "";

	"""
	VRRP movable IP. The TFTP service listens on this IP, normally through
	0.0.0.0.
	"""
	TFTPServerWANVRRPListenIPv4 = None;

	"""
	True if Data Lake is set up and available.
	"""
	dataLakeEnabled = None;

	"""
	Allows the end-user to force a VLAN ID (or EPG in CISCO ACI environments).
	This enables the user to connect to pre-existing VLANs in the established
	infrastructure.
	"""
	allowVLANOverrides = None;

	"""
	Graphite host (IPv4:port) for the plain text protocol socket. Set to empty
	string to disable.
	"""
	monitoringGraphitePlainTextSocketHost = "";

	"""
	Graphite host (IPv4:port) for the HTTP Render URL API. Set to empty string
	to disable.
	"""
	monitoringGraphiteRenderURLHost = "";

	"""
	Coordinates latitude in decimal degrees.
	"""
	latitude = 0;

	"""
	Coordinates longitude in decimal degrees.
	"""
	longitude = 0;

	"""
	Address, such as: Chez Gusteau, Paris, France.
	"""
	address = "";

	"""
	Constants used when provisioning network equipment.
	"""
	switchProvisioner = None;

	"""
	Credentials for the Samba server of the datacenter.
	"""
	SambaServer = None;

	"""
	Credentials for the Web proxy server of the datacenter.
	"""
	webProxy = None;

	"""
	The schema type
	"""
	type = None;
