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

from .exceptions import *
from .form import Form

###############################################################################

class MetadataForm(Form):

	def __init__(self, profile: dict, lang: str, entries: list, vocabulary: dict):
		super().__init__("Metadata Form", lang, entries, vocabulary)
		self.profile = profile

###############################################################################

	def parse(self, data: dict):

		"""
		Parses JSON-LD metadata into a Metadata Input Form
		"""

		k = list(data.keys())[0]
		for path in data[k]:
			for entry in self.profile["graph"]:
				if path == entry["path"]:
					key = entry["name"][self._lang]
					value = data[k][path][0]["value"]
					if self.is_controlled(key):
						voc = self.get_vocabulary(key)
						keys = list(voc.keys())
						values = list(voc.values())
						index = values.index(value)
						value = keys[index]
					self.store[key] = value
					break

###############################################################################

	def generate(self) -> dict:
		metadata = {}
		RDFTYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

		# Set application profile type used by metadata
		metadata[RDFTYPE] = [{
			"type": "uri",
			"value": self.profile["id"]
		}]

		# Collect missing required fields
		missing = []

		# Set metadata fields
		for key in self._keys:
			entry = self._keys[key]
			field = entry["field"]
			if key not in self.store:
				if self.is_required(key):
					missing.append(key)
			else:
				path = entry["path"]
				value = self.store[key]
				if entry["flags"] & MetadataForm.LIST:
					if type(value) is not list and type(value) is not tuple:
						raise ValueError("Expected iterable value for key %s" % key)
				if self.is_controlled(key):
					voc = self.get_vocabulary(key)
					value = voc[value]
				metadata[path] = [{
					"value": value,
					"datatype": entry["datatype"],
					"type": entry["type"]
				}]

		# Check missing field list
		if len(missing) > 0:
			raise RequirementError(missing)

		return metadata

###############################################################################
