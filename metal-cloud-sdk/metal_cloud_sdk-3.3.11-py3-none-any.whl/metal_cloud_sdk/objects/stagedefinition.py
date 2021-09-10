# -*- coding: utf-8 -*-

class StageDefinition(object):
	"""
	A stage definition contains a JavaScript file, HTTP request url and options,
	an AnsibleBundle or an API call template.
	"""

	def __init__(self, stage_definition_label, stage_definition_type, stage_definition, type):
		self.stage_definition_label = stage_definition_label;
		self.stage_definition_type = stage_definition_type;
		self.stage_definition = stage_definition;
		self.type = type;


	"""
	Unique ID.
	"""
	stage_definition_id = None;

	"""
	Owner. Delegates of this user can manage his stage definitions as well. When
	null and creating a StageDefinition, defaults to the API caller's
	authenticated user ID. This property cannot be updated on an existing
	resource.
	"""
	user_id_owner = None;

	"""
	The user which last updated the stage definition.
	"""
	user_id_authenticated = None;

	"""
	The stage definition's label is unique per user_id_owner. Read-only when
	updating a stage definition.
	"""
	stage_definition_label = None;

	"""
	Icon image file in data URI format like this: data:image/png;base64,iVBOR=
	"""
	icon_asset_data_uri = None;

	"""
	For example: Hello World!
	"""
	stage_definition_title = "No title specified";

	"""
	"""
	stage_definition_description = None;

	"""
	"""
	stage_definition_type = None;

	"""
	JSON array of strings. These must be available in the execution context,
	otherwise the stage cannot run.
	"""
	stage_definition_variable_names_required = [];

	"""
	"""
	stage_definition = None;

	"""
	Date and time of the stage definition's creation.
	"""
	stage_definition_created_timestamp = None;

	"""
	Date and time of the stage definition's update (replace).
	"""
	stage_definition_updated_timestamp = None;

	"""
	Deprecated stage definitions can no longer be referenced, but existing
	references will be preserved.
	"""
	stage_definition_is_deprecated = False;

	"""
	Stage definition json.
	"""
	stage_definition_json = "";

	"""
	The schema type
	"""
	type = None;
