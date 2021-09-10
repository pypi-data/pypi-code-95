# -*- coding: utf-8 -*-

class Threshold(object):
	"""
	Threshold represents a certain property that if reached an infrastructure
	owner would be notified.
	"""

	def __init__(self, infrastructure_id, threshold_value, threshold_unit):
		self.infrastructure_id = infrastructure_id;
		self.threshold_value = threshold_value;
		self.threshold_unit = threshold_unit;


	"""
	The ID of the Threshold
	"""
	threshold_id = None;

	"""
	The label of the Threshold
	"""
	threshold_label = None;

	"""
	The ID of the user that owns the threshold
	"""
	user_id_owner = None;

	"""
	The ID of the infrastructure
	"""
	infrastructure_id = None;

	"""
	The ID of the network
	"""
	network_id = None;

	"""
	The ID of the instance
	"""
	instance_id = None;

	"""
	A string which provides a description of the threshold.
	"""
	threshold_description = "";

	"""
	The value for the threshold
	"""
	threshold_value = None;

	"""
	The measurement unit associated with the threshold value
	"""
	threshold_unit = None;

	"""
	The period of time in hours that must pass before another warning is issued.
	For a one time warning, null is required
	"""
	threshold_action_repeat_interval_hours = 0;

	"""
	How is the threshold calculated
	"""
	threshold_type = "infrastructure_on_demand_and_metered_costs";

	"""
	Specific customization for certain threshold types.
	"""
	threshold_specifics = None;

	"""
	What action to be taken when the threshold is reached
	"""
	threshold_action = "email";

	"""
	Defines whether the event must be triggered when the measured value is
	greater than or less than the threshold_value
	"""
	threshold_bound_type = "upper";

	"""
	Defines the destination for the threshold value. It can be seen as a subtype
	of the threshold_type
	"""
	threshold_value_destination = "infrastructure_total_costs";

	"""
	The schema type.
	"""
	type = None;
