# -*- coding: utf-8 -*-

class InfrastructureDeployStageDefinitionReference(object):
	"""
	Points to a StageDefinition which is to be executed with a specified
	priority. Also contains information on the last execution of this specific
	reference to a StageDefinition. Multiple references to the same
	StageDefinition may coexist on the same Infrastructure.
	"""

	def __init__(self, infrastructure_id, infrastructure_deploy_custom_stage_run_level, stage_definition_id, type):
		self.infrastructure_id = infrastructure_id;
		self.infrastructure_deploy_custom_stage_run_level = infrastructure_deploy_custom_stage_run_level;
		self.stage_definition_id = stage_definition_id;
		self.type = type;


	"""
	Unique StageDefinition reference ID on an Infrastructure.
	"""
	infrastructure_deploy_custom_stage_id = None;

	"""
	Unique Infrastructure ID.
	"""
	infrastructure_id = None;

	"""
	Lowest is first to be executed. Multiple
	InfrastructureDeployStageDefinitionReference items with the same workflow_id
	having the same run level will be executed in parallel. StageDefinition
	items of the WorkflowReference type are unwrapped recursively in-place
	before execution or when added to an infrastructure deploy which means that
	adding, removing or reordering StageDefinition references will have no
	effect on an ongoing Infrastructure deploy.
	"""
	infrastructure_deploy_custom_stage_run_level = None;

	"""
	Unique StageDefinition ID.
	"""
	stage_definition_id = None;

	"""
	Drive Array ID.
	"""
	drive_array_id = None;

	"""
	pre_deploy stages run before anything else in a deploy and are destined to
	be used for preparing for stopping various resource such as stopping or
	deleting instances, removing storage, etc.
	"""
	infrastructure_deploy_custom_stage_type = "post_deploy";

	"""
	Custom variables definitions. Object with variable name as key and variable
	value as value. In case of variable name conflict, the variable defined here
	overrides the variable inherited from any context.
	"""
	infrastructure_deploy_custom_stage_variables = None;

	"""
	Execution context. The stage will be added in the deploy for each child
	instance.
	"""
	instance_array_id = None;

	"""
	Execution context.
	"""
	shared_drive_id = None;

	"""
	Execution context. The stage will be added in the deploy only once. The
	stage will NOT be added in the deploy for any child products.
	"""
	cluster_id = None;

	"""
	Information on the last run. May be of any type and have any properties if
	an object. These properties may be present: successMessage:string|null,
	successMessageTimestamp:string|null, errorMessage:string|null,
	errorMessageTimestamp:string|null
	"""
	infrastructure_deploy_custom_stage_exec_output_json = None;

	"""
	The schema type.
	"""
	type = None;
