# -*- coding: utf-8 -*-

class SSHClientOptions(object):
	"""
	SSH client options such as the host, port, user, password, private keys,
	etc. All properties support template-like variables; for example,
	${{instance_credentials_password}} may be used as value for the password
	property.
	"""

	def __init__(self, type):
		self.type = type;


	"""
	Hostname or IP address of the server.
	"""
	host = "localhost";

	"""
	Port number of the server.
	"""
	port = 22;

	"""
	Only connect via resolved IPv4 address for host.
	"""
	forceIPv4 = False;

	"""
	Only connect via resolved IPv6 address for host.
	"""
	forceIPv6 = False;

	"""
	Any valid hash algorithm supported by node. The host's key is hashed using
	this algorithm and passed to the hostVerifier function.
	"""
	hostHash = None;

	"""
	A string hex hash of the host's key for verification purposes.
	"""
	hashedKey = None;

	"""
	Username for authentication.
	"""
	username = None;

	"""
	Password for password-based user authentication.
	"""
	password = None;

	"""
	Contains a private key for key-based user authentication (OpenSSH format).
	"""
	privateKey = None;

	"""
	For an encrypted private key, this is the passphrase used to decrypt it.
	"""
	passphrase = None;

	"""
	How long (in milliseconds) to wait for the SSH handshake to complete.
	"""
	readyTimeout = 20000;

	"""
	Performs a strict server vendor check before sending vendor-specific
	requests, etc. (e.g. check for OpenSSH server when using
	openssh_noMoreSessions()).
	"""
	strictVendor = True;

	"""
	This option allows you to explicitly override the default transport layer
	algorithms used for the connection. Each value must be an array of valid
	algorithms for that category. The order of the algorithms in the arrays are
	important, with the most favorable being first.
	"""
	algorithms = None;

	"""
	Set to true to enable compression if server supports it, 'force' to force
	compression (disconnecting if server does not support it), or false to
	explicitly opt out of compression all of the time. Note: this setting is
	overridden when explicitly setting a compression algorithm in the algorithms
	configuration option. By default compression is negotiated with a preference
	to disable it.
	"""
	compress = None;

	"""
	The schema type
	"""
	type = None;
