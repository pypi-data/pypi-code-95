# -*- coding: utf-8 -*-

class SecureGatewayProxy(object):
	"""
	Secure gateway proxy mapping with metadata
	"""

	def __init__(self, name, mode, host, frontend_ssl_enabled, frontend_authorization_enabled, frontend_allowed_client_ips, backend_balance_strategy, backend_servers, destination_id, destination_discriminator, infrastructure_id):
		self.name = name;
		self.mode = mode;
		self.host = host;
		self.frontend_ssl_enabled = frontend_ssl_enabled;
		self.frontend_authorization_enabled = frontend_authorization_enabled;
		self.frontend_allowed_client_ips = frontend_allowed_client_ips;
		self.backend_balance_strategy = backend_balance_strategy;
		self.backend_servers = backend_servers;
		self.destination_id = destination_id;
		self.destination_discriminator = destination_discriminator;
		self.infrastructure_id = infrastructure_id;


	"""
	The proxy name.
	"""
	name = None;

	"""
	The proxy protocol: HTTP/TCP
	"""
	mode = None;

	"""
	The start port of the range that the proxy listens to
	"""
	start_port = None;

	"""
	The end port of the range that the proxy listens to
	"""
	end_port = None;

	"""
	The value of the Host header
	"""
	host = None;

	"""
	Should Secure Gateway listen for SSL connections
	"""
	frontend_ssl_enabled = None;

	"""
	Should Secure Gateway authenthicate users that want to connect to it?
	"""
	frontend_authorization_enabled = None;

	"""
	List of client IPs allowed to connect to the secure gateway
	"""
	frontend_allowed_client_ips = [];

	"""
	The strategy used to balance the backends: leastconn / roundrobin
	"""
	backend_balance_strategy = None;

	"""
	An array listing the backends that are proxied by this proxy
	"""
	backend_servers = [];

	"""
	The id of the service asociated with this proxy
	"""
	destination_id = None;

	"""
	The type of service that the secure gateway proxies
	"""
	destination_discriminator = None;

	"""
	The infrastructure id asociated with this proxy
	"""
	infrastructure_id = None;

	"""
	The schema type.
	"""
	type = None;
