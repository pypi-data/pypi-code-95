# -*- coding: utf-8 -*-

class WebFetchAPIRequestHeaders(object):
	"""
	HTTP request headers. <code>null</code> means undefined (the default for
	most) so the header will not be included with the request. Header values
	support template-like variables. Example value for an Authorization header:
	Basic ${{variable_name_for_user_and_password_base64}}
	"""

	def __init__(self):
		pass;


	"""
	Read-only. Always set and overriden automatically using the hostname (FQDN
	or IP address) and port extracted from the request URL. Example values:
	<code>domain.org:8080</code>, <code>127.0.0.1</code>, etc.
	"""
	Host = "";

	"""
	<code>gzip,deflate</code> (when WebFetchAPI.options.compress === true)
	"""
	Accept-Encoding = None;

	"""
	"""
	Accept = "*/*";

	"""
	"""
	Connection = "close";

	"""
	Calculated and sent automatically based on the WebFetchAPI.options.body
	property (or the value set into .body after decoding
	WebFetchAPI.options.bodyBufferBase64).
	"""
	Content-Length = None;

	"""
	Determined automatically. The default here is ignored.
	"""
	Transfer-Encoding = None;

	"""
	To help tracing the source of a request (debugging), more information about
	the execution context may be appended automatically to the User-Agent if and
	only if the default is left unchanged. You should avoid faking or even just
	setting a custom User-Agent (overriding the default set here) unless
	absolutely necessary.
	"""
	User-Agent = "MetalCloud/1.0 (WebFetchAPI)";

	"""
	"""
	Cache-Control = "no-cache";

	"""
	"""
	Pragma = "no-cache";

	"""
	Upgrading to other protocols is not supported. Only the HTTP protocol is
	supported, for example HTTP/2, WebSocket, etc. are not supported.
	"""
	Upgrade = None;

	"""
	For example: <code>utf-8</code>. Textual data might be assumed to be utf-8
	and/or may be converted to utf-8 because of the way this API is implemented
	and the underlying technologies (programming languages, execution VMs,
	platforms, RPC JSON serialization because it only supports UTF-8, etc.).
	"""
	Accept-Charset = None;

	"""
	"""
	Content-Type = None;

	"""
	"""
	Cookie = None;

	"""
	For example: <code>Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==</code>
	"""
	Authorization = None;

	"""
	For example: <code>Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==</code>
	"""
	Proxy-Authorization = None;

	"""
	The email address of the user making the request.
	"""
	From = None;

	"""
	"""
	A-IM = None;

	"""
	"""
	Accept-Datetime = None;

	"""
	"""
	Accept-Language = None;

	"""
	"""
	Access-Control-Request-Method = None;

	"""
	"""
	Access-Control-Request-Headers = None;

	"""
	A Base64-encoded binary MD5 sum of the content of the request body.
	"""
	Content-MD5 = None;

	"""
	The date and time at which the message was originated (in HTTP-date format
	as defined by RFC 7231 Date/Time Formats.
	"""
	Date = None;

	"""
	"""
	Expect = None;

	"""
	"""
	Forwarded = None;

	"""
	"""
	HTTP2-Settings = None;

	"""
	"""
	If-Match = None;

	"""
	"""
	If-Modified-Since = None;

	"""
	"""
	If-None-Match = None;

	"""
	"""
	If-Range = None;

	"""
	"""
	If-Unmodified-Since = None;

	"""
	Limit the number of times the message can be forwarded through proxies or
	gateways. For example: <code>10</code>.
	"""
	Max-Forwards = None;

	"""
	"""
	Origin = None;

	"""
	Don't use this header for requests which likely don't support it, like REST
	API endpoints and such even if the HTTP server is not configured correctly
	and advertises Accept-Ranges: bytes. Example: <code>bytes=500-999</code>
	"""
	Range = None;

	"""
	"""
	Referer = None;

	"""
	"""
	TE = None;

	"""
	"""
	Via = None;

	"""
	"""
	Warning = None;

	"""
	"""
	Upgrade-Insecure-Requests = None;

	"""
	"""
	X-Requested-With = None;

	"""
	"""
	DNT = None;

	"""
	"""
	X-Forwarded-For = None;

	"""
	"""
	X-Forwarded-Host = None;

	"""
	"""
	X-Forwarded-Proto = None;

	"""
	"""
	Front-End-Https = None;

	"""
	"""
	X-Http-Method-Override = None;

	"""
	"""
	X-ATT-DeviceId = None;

	"""
	"""
	X-Wap-Profile = None;

	"""
	"""
	Proxy-Connection = None;

	"""
	"""
	X-UIDH = None;

	"""
	"""
	X-Csrf-Token = None;

	"""
	"""
	X-Request-ID = None;

	"""
	"""
	X-Correlation-ID = None;

	"""
	"""
	Save-Data = None;

	"""
	"""
	Sec-Fetch-Dest = None;

	"""
	"""
	Sec-Fetch-Mode = None;

	"""
	"""
	Sec-Fetch-Site = None;

	"""
	"""
	Sec-Fetch-User = None;

	"""
	The schema type
	"""
	type = None;
