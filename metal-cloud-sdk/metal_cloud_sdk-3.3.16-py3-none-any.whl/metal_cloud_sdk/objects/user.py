# -*- coding: utf-8 -*-

class User(object):
	"""
	This object's properties describe user account specifications.
	"""

	def __init__(self, user_id, user_display_name, user_email, user_brand):
		self.user_id = user_id;
		self.user_display_name = user_display_name;
		self.user_email = user_email;
		self.user_brand = user_brand;


	"""
	The ID of the user.
	"""
	user_id = None;

	"""
	The user's region. It links the user to a company with which he is making
	business legally.
	"""
	franchise = None;

	"""
	The user's name.
	"""
	user_display_name = None;

	"""
	The user's email.
	"""
	user_email = None;

	"""
	Date and time of the user's creation.
	"""
	user_created_timestamp = None;

	"""
	Date and time of the user's last login.
	"""
	user_last_login_timestamp = None;

	"""
	Counts the failed authentication attempts since the user's last login.
	"""
	user_auth_failed_attempts_since_last_login = None;

	"""
	Indicates if a user's change of password has been required or not.
	"""
	user_password_change_required = None;

	"""
	Authenticator shared secret. Base 32 string. <code>null</code> by default.
	Use <code>user_authenticate_password()</code> to obtain an object containing
	the authenticator's shared secret (note this also requires having the
	authenticator already set up).
	"""
	user_authenticator_secret_base32 = None;

	"""
	A mandatory authenticator means that a logged-on user without an
	authenticator would be forced to setup an authenticator in the GUI (there's
	no API enforcement).
	"""
	user_authenticator_is_mandatory = False;

	"""
	This flag forces a logged-on user to setup a new authenticator in the GUI,
	replacing the old one (there's no API enforcement).
	"""
	user_authenticator_must_change = False;

	"""
	ISO 8601 timestamp which holds the date and time when an authenticator was
	created or removed. Example format: 2013-11-29T13:00:01Z.
	"""
	user_authenticator_created_timestamp = "1970-01-01T00:00:00Z";

	"""
	The email status.
	"""
	user_email_status = None;

	"""
	Indicates if a user is blocked or not.
	"""
	user_blocked = None;

	"""
	User's API key. <code>null</code> by default. Use
	<code>user_authenticate_password()</code> to obtain an object containing the
	API key.
	"""
	user_api_key = None;

	"""
	"""
	user_access_level = "customer";

	"""
	The user's permissions as they are retrieved from the auth-microserivce
	"""
	user_permissions = None;

	"""
	"""
	user_external_ids_json = None;

	"""
	"""
	user_limits_json = None;

	"""
	"""
	user_permissions_json = None;

	"""
	"""
	user_custom_prices_json = None;

	"""
	"""
	user_is_testing_mode = None;

	"""
	"""
	user_plan_type = None;

	"""
	"""
	user_last_login_type = None;

	"""
	"""
	user_external_ids = [];

	"""
	Indicates if a user is billable or not.
	"""
	user_is_billable = None;

	"""
	Indicates if a user is suspended or not.
	"""
	user_is_suspended = None;

	"""
	User’s updated language which should respect the ISO 639-1 format (2
	letter code. Examples: "en", "ro", "fr", "jp").
	"""
	user_language = "en";

	"""
	User's parent delegates. Contains <a:schema>User</a:schema> objects
	"""
	user_delegate_parents = [];

	"""
	User's children delegates. Contains <a:schema>User</a:schema> objects
	"""
	user_delegate_children = [];

	"""
	The current default infrastructure ID.
	"""
	user_infrastructure_id_default = None;

	"""
	User GUI settings.
	"""
	user_gui_settings_json = "";

	"""
	Internal property. Indicates if this is a test account.
	"""
	user_is_test_account = False;

	"""
	Internal property. Indicates if the user should be ignored in usage reports.
	"""
	user_exclude_from_reports = False;

	"""
	Used to group users based on their brand.
	"""
	user_brand = None;

	"""
	Determines if the user is a brand manager. Direct delegates will be asigned
	to the same brand.
	"""
	user_is_brand_manager = False;

	"""
	Determines if the user is a datastore publisher.
	"""
	user_is_datastore_publisher = False;

	"""
	The schema type
	"""
	type = None;
