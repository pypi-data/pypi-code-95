# -*- coding: utf-8 -*-

class InfrastructureCustomDeployStage(object):
	"""
	An Infrastructure custom deploy stage is an association of an
	StageDefinition, an Infrastructure and a run level priority index.
	"""

	def __init__(self, infrastructure_deploy_custom_stage_id, stage_definition_id, infrastructure_id, infrastructure_deploy_custom_stage_run_level):
		self.infrastructure_deploy_custom_stage_id = infrastructure_deploy_custom_stage_id;
		self.stage_definition_id = stage_definition_id;
		self.infrastructure_id = infrastructure_id;
		self.infrastructure_deploy_custom_stage_run_level = infrastructure_deploy_custom_stage_run_level;


	"""
	Unique Infrastructure, StageDefinition and run level index association ID.
	"""
	infrastructure_deploy_custom_stage_id = None;

	"""
	Represents an <a:schema>StageDefinition</a:schema>.
	"""
	stage_definition_id = None;

	"""
	Represents an <a:schema>Infrastructure</a:schema>
	"""
	infrastructure_id = None;

	"""
	Run priority index. 0 runs first. If multiple StageDefinitions are on the
	same priority they run in parallel.
	"""
	infrastructure_deploy_custom_stage_run_level = None;

	"""
	Unstructured JSON.
	"""
	infrastructure_deploy_custom_stage_exec_output_json = None;

	"""
	The schema type
	"""
	type = None;
