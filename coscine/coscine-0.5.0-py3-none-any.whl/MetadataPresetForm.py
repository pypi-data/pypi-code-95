###############################################################################
# Coscine Python Client
# Copyright (c) 2018-2021 RWTH Aachen University
# Contact: coscine@itc.rwth-aachen.de
# Git: https://git.rwth-aachen.de/coscine/docs/public/coscine-python-client
# Please direct bug reports, feature requests or questions at the URL above
# by opening an issue.
###############################################################################
# Coscine is an open source project at RWTH Aachen University for
# the management of research data.
# Visit https://coscine.de for more information.
###############################################################################

#
# The MetadataPreset form allows for the configuration of default
# values in an application profile.
#


from .form import Form

###############################################################################

class MetadataPresetForm(Form):
	
	def __init__(self, profile: dict, lang: str, entries: list, vocabulary: dict):
		super().__init__("Metadata Preset", lang, entries, vocabulary)
		self.profile = profile

###############################################################################

	def enable(self, key: str, enable: bool = True):
		self._keys[key]["enabled"] = enable

###############################################################################

	def lock(self, key: str, lock: bool = True):
		self._keys[key]["locked"] = lock

###############################################################################

	def generate(self) -> dict:
		metadata = {}

		# Set metadata fields
		for key in self._keys:
			field = self._keys[key]
			path = field["path"]

			if key not in self.store:
				value = None
				metadata[path] = {
					"https://purl.org/coscine/defaultValue": [],
					"https://purl.org/coscine/invisible": [{
						"type": "literal",
						"value": "0"
					}]
				}
				continue
			else:
				value = self.store[key]
			if self.is_controlled(key):
				voc = self.get_vocabulary(key)
				value = voc[value]
			metadata[path] = {
				"https://purl.org/coscine/defaultValue": [{
					"type": field["type"],
					"value": value
				}],
				"https://purl.org/coscine/invisible": [{
					"type": "literal",
					"value": "0"
				}]
			}

		return metadata

###############################################################################