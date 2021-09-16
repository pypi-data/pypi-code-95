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

KEYS = [{
		"name": {
			"de": "Ressourcentyp",
			"en": "Resource Type"
		},
		"flags": Form.REQUIRED | Form.CONTROLLED,
		"field": "type"
	},{ # This is REQUIRED for rds and s3, but not for Linked Data!
		"name": {
			"de": "Ressourcengröße",
			"en": "Resource Size"
		},
		"flags": Form.SPECIAL,
		"field": "resourceTypeOption"
	},{
		"name": {
			"de": "Ressourcenname",
			"en": "Resource Name"
		},
		"flags": Form.REQUIRED,
		"field": "ResourceName"
	},{
		"name": {
			"de": "Anzeigename",
			"en": "Display Name"
		},
		"flags": Form.REQUIRED,
		"field": "DisplayName"
	},{
		"name": {
			"de": "Ressourcenbeschreibung",
			"en": "Resource Description"
		},
		"flags": Form.REQUIRED,
		"field": "Description"
	},{
		"name": {
			"de": "Disziplin",
			"en": "Discipline"
		},
		"flags": Form.REQUIRED | Form.CONTROLLED | Form.LIST,
		"field": "Disciplines"
	},{
		"name": {
			"de": "Ressourcenschlagwörter",
			"en": "Resource Keywords"
		},
		"flags": Form.NONE,
		"field": "Keywords"
	},{
		"name": {
			"de": "Lizenz",
			"en": "License"
		},
		"flags": Form.CONTROLLED,
		"field": "License"
	},{
		"name": {
			"de": "Verwendungsrechte",
			"en": "Usage Rights"
		},
		"flags": Form.NONE,
		"field": "UsageRights"
	},{
		"name": {
			"de": "Applikationsprofile",
			"en": "Application Profile"
		},
		"flags": Form.REQUIRED | Form.CONTROLLED,
		"field": "applicationProfile"
}]

MAP = {
	"description": "Description",
	"displayName": "DisplayName",
	"resourceName": "ResourceName",
	"keywords": "Keywords",
	"disciplines": "Disciplines",
	"license": "License",
	"resourceTypeOption": "resourceTypeOption",
	"applicationProfile": "applicationProfile",
	"type": "type",
	"usageRights": "UsageRights"
}

###############################################################################

class ResourceForm(Form):

	"""
	Coscine Input Form for creating and editing resources
	"""

###############################################################################

	def __init__(self, lang: str, vocabulary: dict):
		super().__init__("Resource Form", lang, KEYS, vocabulary)

###############################################################################

	def parse(self, data: dict):

		def _parse_disciplines(self, data):
			LSTR = {"en": "displayNameEn", "de": "displayNameDe"}[self._lang]
			disciplines = []
			for discipline in data:
				disciplines.append(discipline[LSTR])
			return disciplines

		for key in data:
			if key in MAP and data[key] != "":
				entry = self.entry(MAP[key])
				if entry is None:
					continue
				name = entry["name"][self._lang]
				flags = entry["flags"]
				value = data[key]
				if flags & Form.CONTROLLED or flags & Form.LIST or flags & Form.SPECIAL:
					if key == "disciplines":
						self[name] = _parse_disciplines(self, value)
					elif key == "resourceTypeOption":
						self[name] = value["Size"]
					elif key == "applicationProfile":
						values = list(self._vocabulary["applicationProfile"].values())
						keys = list(self._vocabulary["applicationProfile"].keys())
						position = values.index(value)
						self[name] = keys[position]
					elif key == "visibility" or key == "license" or key == "type":
						self[name] = value["displayName"]
				else:
					self[name] = value

###############################################################################

	def generate(self) -> dict:

		"""
		Generates JSON-LD formatted representation of resource data

		Raises
		-------
		RequirementError
			When one or more required fields have not been set
		
		Returns
		--------
		JSON-LD formatted resource data
		"""

		def final_value(key, value):
			if self.is_controlled(key):
				return self._vocabulary[field][value]
			else:
				return value

		data = {}
		missing = []
		for key in self._keys:
			entry = self._keys[key]
			field = entry["field"]
			if key not in self.store:
				if self.is_required(key):
					missing.append(key)
			else:
				value = self.store[key]
				if entry["flags"] & ResourceForm.LIST:
					if type(value) is not list and type(value) is not tuple:
						raise ValueError("Expected iterable value for key %s" % key)
					data[field] = []
					for v in value:
						data[field].append(final_value(key, v))
				else:
					data[field] = final_value(key, value)

		if missing:
			raise RequirementError(missing)

		size = {}
		if "resourceTypeOption" in data:
			size = {
				"Size": data["resourceTypeOption"]
			}
		elif data["type"]["displayName"] in ("rds", "rds-s3"):
			raise RequirementError("rds or rds-s3 require a size parameter!")
		data["resourceTypeOption"] = size

		data["Visibility"] = {
			"displayName": "Project Members",
			"id": "8ab9c883-eb0d-4402-aaad-2e4007badce6"
		}

		return data

###############################################################################