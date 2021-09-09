import os
import yaml


class IUBConfiguration:

	mainSection = 'GlobalSettings'

	def __init__(self, path, logging_handler):
		self.logging = logging_handler
		self.config = self.load_config(path)
		self.logging.getLogger().setLevel(self.config[self.mainSection]['logLevel'])
		self.logging.info('Loaded settings started')

	def load_config(self, path):
		"""
		Load from a Yaml file the settings
		:param path: The path to use to load settings
		:return: The read configuration or stop the script execution
		"""
		with open(path, 'r') as stream:
			try:
				config = yaml.safe_load(stream)
				return config
			except yaml.YAMLError as exc:
				print("Cannot load file: [" + path + "] - Error: " + str(exc))
				self.logging.error("Cannot load file: [" + path + "] - Error: " + str(exc))
				exit()

	@staticmethod
	def create_absolute_path(path):
		# Check if the given path is an absolute path
		if not os.path.isabs(path):
			current_dir = os.path.dirname(os.path.abspath(__file__))
			path = os.path.join(current_dir, path)
		return path

	def set_config(self, section, name, newValue):
		"""
		Updates a configuration value
		:param section: The name of the section interested by the modify
		:param name: The name of the parameter to update
		:param newValue: The new value to insert
		:return: None
		"""
		if section in self.config and name in self.config[section]:
			self.config[section]['name'] = newValue
		else:
			self.logging.warning(
				"Missing value [" + section + "][" + name + "] from loaded configuration, cannot substitute")

	def get_config(self, section, name=None, fail_silently=True):
		"""
		Retrieve a configuration parameter from loaded settings
		:param section: The name of the section that is requested
		:param name: The name of the parameter inside a section that is requested
		:param fail_silently: True to avoid Exception raise
		:return: The requested configuration value (or set of values)
		"""
		if section not in self.config and name is None:
			# Requested not existent section - Error
			self.logging.warning("Missing section [" + section + "] from loaded configuration, checking in main section")
			if fail_silently:
				return None
			else:
				raise Exception("Missing required section [" + section + "] from loaded configuration")
		elif section in self.config and name is None:
			# Requested existent section - Return entire section
			self.logging.info("Retrieving entire section: [" + section + "]")
			return self.coalesce_section(self.config[section])
		else:
			# Requested specific value
			if name not in self.coalesce_section(self.config[section]):
				self.logging.warning("Missing value [" + name + "] from section [" + section + "]")
				if fail_silently:
					return None
				else:
					raise Exception("Missing required value [" + name + "] from section [" + section + "]")
			else:
				self.logging.debug("Retrieving value [" + name + "] from section: [" + section + "]")
				return self.coalesce_section(self.config[section])[name]

	def coalesce_section(self, first_section, second_section=None):
		"""
		Join the first passed section with the second one. If missing the second section, join with main section
		:param first_section: The first section to join, all parameters and values in this section will be kept
		:param second_section: The second section to join, in case of value already existing in the first one this
								value will not be considered
		:return: The joined values
		"""
		if second_section is None:
			second_section = self.config[self.mainSection]
		return {**second_section, **first_section}
