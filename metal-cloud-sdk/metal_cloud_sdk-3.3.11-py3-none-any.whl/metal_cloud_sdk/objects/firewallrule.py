# -*- coding: utf-8 -*-

class FirewallRule(object):
	"""
	A Firewall rule.
	"""

	def __init__(self, firewall_rule_ip_address_type):
		self.firewall_rule_ip_address_type = firewall_rule_ip_address_type;


	"""
	Describes the FirewallRule.
	"""
	firewall_rule_description = "Rule description.";

	"""
	The port range start of the firewall rule. When null, no ports are being
	taken into consideration when applying the firewall rule.
	"""
	firewall_rule_port_range_start = None;

	"""
	The port range end of the firewall rule. When null, no ports are being taken
	into consideration when applying the firewall rule.
	"""
	firewall_rule_port_range_end = None;

	"""
	The IP address range start of the firewall rule. When null, no source IP
	address is taken into consideration when applying the firewall rule.
	"""
	firewall_rule_source_ip_address_range_start = None;

	"""
	The IP address range end of the firewall rule. When null, no source IP
	address is taken into consideration when applying the firewall rule.
	"""
	firewall_rule_source_ip_address_range_end = None;

	"""
	The IP address range start of the firewall rule. When null, no destination
	IP address is taken into consideration when applying the firewall rule.
	"""
	firewall_rule_destination_ip_address_range_start = None;

	"""
	The IP address range end of the firewall rule. When null, no destination IP
	address is taken into consideration when applying the firewall rule.
	"""
	firewall_rule_destination_ip_address_range_end = None;

	"""
	The protocol of the firewall rule.
	"""
	firewall_rule_protocol = "all";

	"""
	The IP address type of the firewall rule.
	"""
	firewall_rule_ip_address_type = None;

	"""
	Specifies if the firewall rule will be applied or not.
	"""
	firewall_rule_enabled = True;

	"""
	The schema type.
	"""
	type = None;
