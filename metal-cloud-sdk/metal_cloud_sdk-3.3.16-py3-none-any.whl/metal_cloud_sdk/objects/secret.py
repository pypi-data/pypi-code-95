# -*- coding: utf-8 -*-

class Secret(object):
	"""
	Secret item in a vault.
	"""

	def __init__(self, secret_name):
		self.secret_name = secret_name;


	"""
	Unique secret ID.
	"""
	secret_id = None;

	"""
	Owner. Delegates of this user can manage his secrets as well. When null,
	defaults to the API authenticated user.
	"""
	user_id_owner = None;

	"""
	The user which last updated the secret.
	"""
	user_id_authenticated = None;

	"""
	Must start with a letter and end with a letter or digit. May contain
	underscores, latin characters and digits. When copied into the generated
	variables JSON of an AnsibleBundle execution context, the secret name is
	used as-is.
	"""
	secret_name = None;

	"""
	Auto generated label for the secret. If the secret is generated in some
	user's scope, then this field will be the concatenation of secret_name and
	user id owner fields.
	"""
	secret_name_unique = None;

	"""
	If null, any kind of usage is enabled. Otherwise, a comma separated list of
	allowed usage types.
	"""
	secret_usage = None;

	"""
	Secret in base64 format. If the base64 contains binary data, it has to be
	utf8 encoded to work with Ansible. Cannot be null with
	<code>secret_create</code>. The secret_base64 property is always returned as
	<code>null</code> by <code>secrets()</code> and <code>secret_get()</code>
	(it is not retrievable). When using <code>secret_update()</code> null is
	allowed, in which case the secret contents are not updated.
	"""
	secret_base64 = None;

	"""
	Date and time of the secret's creation.
	"""
	secret_created_timestamp = None;

	"""
	Date and time of the secret's update (replace).
	"""
	secret_updated_timestamp = None;

	"""
	The schema type
	"""
	type = None;
