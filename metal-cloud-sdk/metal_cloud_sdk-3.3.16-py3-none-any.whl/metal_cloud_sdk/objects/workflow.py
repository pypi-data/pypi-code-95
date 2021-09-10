# -*- coding: utf-8 -*-

class Workflow(object):
	"""
	A group for StageDefinition references which are executed in a particular
	order.
	"""

	def __init__(self, workflow_title):
		self.workflow_title = workflow_title;


	"""
	Unique workflow ID.
	"""
	workflow_id = None;

	"""
	Owner. Delegates of this user can manage his workflows as well. When null,
	defaults to the API authenticated user.
	"""
	user_id_owner = None;

	"""
	The user which last updated the Workflow object.
	"""
	user_id_authenticated = None;

	"""
	"""
	icon_asset_id = None;

	"""
	A label which is unique per owner.
	"""
	workflow_label = None;

	"""
	"""
	workflow_label_unique = None;

	"""
	A particular resource type. The usage type specifies an intended variables
	context with which the workflow is compatible. It also helps users locate
	workflows more easily when picking a workflow from a list.
	"""
	workflow_usage = None;

	"""
	Human readable title.
	"""
	workflow_title = None;

	"""
	Accurate description of what the Workflow is intended to do.
	"""
	workflow_description = "";

	"""
	Adding new references to deprecated workflows is generally prevented.
	"""
	workflow_is_deprecated = False;

	"""
	Icon image file in data URI format like this: data:image/png;base64,iVBOR=
	"""
	icon_asset_data_uri = None;

	"""
	Date and time of the workflow's creation.
	"""
	workflow_created_timestamp = None;

	"""
	Date and time of the variable's update (replace).
	"""
	workflow_updated_timestamp = None;

	"""
	The schema type
	"""
	type = None;
