# -*- coding: utf-8 -*-

class WorkflowReference(object):
	"""
	Points to a Workflow object via its workflow_id. To be used as a stage
	definition.
	"""

	def __init__(self, workflow_id, type):
		self.workflow_id = workflow_id;
		self.type = type;


	"""
	Unique Workflow ID.
	"""
	workflow_id = None;

	"""
	The schema type.
	"""
	type = None;
