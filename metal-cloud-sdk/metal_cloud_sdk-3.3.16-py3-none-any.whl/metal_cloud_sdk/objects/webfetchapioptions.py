# -*- coding: utf-8 -*-

class WebFetchAPIOptions(object):
	"""
	node-fetch options which is follows the Web API Fetch specification. See
	https://github.com/node-fetch/node-fetch
	"""

	def __init__(self):
		pass;


	"""
	HTTP request method.
	"""
	method = "GET";

	"""
	Set to <code>manual</code> to extract redirect headers or <code>error</code>
	to reject redirect.
	"""
	redirect = "follow";

	"""
	Maximum redirect count. 0 to not follow redirect.
	"""
	follow = 40;

	"""
	Support gzip/deflate content encoding. false to disable.
	"""
	compress = True;

	"""
	Req/res timeout in ms, it resets on redirect. Default is 4 minutes.
	"""
	timeout = 240000;

	"""
	Maximum response body size in bytes. Default is 64 MB.
	"""
	size = 67108864;

	"""
	HTTP request headers. The object keys are header names, such as
	<code>Content-Type</code>.
	"""
	headers = None;

	"""
	Request body. If you need to provide binary data, it is better to use the
	<code>bodyBufferBase64</code> property. <code>Null</code> signifies the
	absence of a body.
	"""
	body = None;

	"""
	Request body in base64 format. It is automatically decoded from base64
	before making the request. This value overrides the <code>body</code>
	property. <code>Null</code> signifies the absence of a body and does not
	override the <code>body</code> property.
	"""
	bodyBufferBase64 = None;

	"""
	The schema type
	"""
	type = None;
