# -*- coding: utf-8 -*-

class WorkflowStageDefinitionReference(object):
	"""
	Points to a StageDefinition which is to be executed with a specified
	priority. Also contains information on the last execution of this specific
	reference to a StageDefinition. Multiple references to the same
	StageDefinition may coexist in the same Workflow.
	"""

	def __init__(self, workflow_id, workflow_stage_run_level, stage_definition_id, type):
		self.workflow_id = workflow_id;
		self.workflow_stage_run_level = workflow_stage_run_level;
		self.stage_definition_id = stage_definition_id;
		self.type = type;


	"""
	Unique StageDefinition reference ID on an Workflow.
	"""
	workflow_stage_id = None;

	"""
	Unique Workflow ID.
	"""
	workflow_id = None;

	"""
	Lowest is first to be executed. Multiple WorkflowStageDefinitionReference
	items with the same workflow_id having the same run level will be executed
	in parallel. StageDefinition items of the WorkflowReference type are
	unwrapped recursively in-place before execution or when added to an
	infrastructure deploy which means that adding, removing or reordering
	StageDefinition references will have no effect on an ongoing Workflow
	execution.
	"""
	workflow_stage_run_level = None;

	"""
	Unique StageDefinition ID.
	"""
	stage_definition_id = None;

	"""
	Custom variables definitions. Object with variable name as key and variable
	value as value. In case of variable name conflict, the variable defined here
	overrides the variable inherited from any context.
	"""
	workflow_stage_variables = None;

	"""
	Execution context. Weak reference which is resolved to an instance_array_id
	at runtime, based on the instance_array_label from instance_array_operation.
	The stage will be added in the deploy for each child instance.
	"""
	instance_array_label = None;

	"""
	Execution context. Weak reference which is resolved to a drive_array_id at
	runtime, based on the drive_array_label from drive_array_operation. The
	stage will be added in the deploy for each child drive.
	"""
	drive_array_label = None;

	"""
	Execution context. Weak reference which is resolved to a shared_drive_id at
	runtime, based on the shared_drive_label from shared_drive_changes.
	"""
	shared_drive_label = None;

	"""
	Execution context. Weak reference which is resolved to a cluster_id at
	runtime, based on the cluster_label from cluster_changes. The stage will be
	added in the deploy only once. The stage will NOT be added in the deploy for
	any child products.
	"""
	cluster_label = None;

	"""
	Information on the last run. May be of any type and have any properties if
	an object. These properties may be present: successMessage:string|null,
	successMessageTimestamp:string|null, errorMessage:string|null,
	errorMessageTimestamp:string|null
	"""
	workflow_stage_exec_output_json = None;

	"""
	The schema type.
	"""
	type = None;
