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

from .form import Form
from .exceptions import *

###############################################################################

KEYS = [{
		"name": {
			"de": "Projektname",
			"en": "Project Name"
		},
		"flags": Form.REQUIRED,
		"field": "ProjectName"
	},{
		"name": {
			"de": "Anzeigename",
			"en": "Display Name"
		},
		"flags": Form.REQUIRED,
		"field": "DisplayName"
	},{
		"name": {
			"de": "Projektbeschreibung",
			"en": "Project Description"
		},
		"flags": Form.REQUIRED,
		"field": "Description"
	},{
		"name": {
			"de": "Principal Investigators",
			"en": "Principal Investigators"
		},
		"flags": Form.REQUIRED,
		"field": "PrincipleInvestigators"
	},{
		"name": {
			"de": "Projektstart",
			"en": "Project Start"
		},
		"flags": Form.REQUIRED,
		"field": "StartDate"
	},
	{
		"name": {
			"de": "Projektende",
			"en": "Project End"
		},
		"flags": Form.REQUIRED,
		"field": "EndDate"
	},{
		"name": {
			"de": "Disziplin",
			"en": "Discipline"
		},
		"flags": Form.REQUIRED | Form.CONTROLLED | Form.LIST,
		"field": "Discipline"
	},{
		"name": {
			"de": "Teilnehmende Organisation",
			"en": "Participating Organizations"
		},
		"flags": Form.REQUIRED | Form.CONTROLLED | Form.LIST,
		"field": "Organization"
	},{
		"name": {
			"de": "Projektschlagwörter",
			"en": "Project Keywords"
		},
		"flags": Form.NONE,
		"field": "Keywords"
	},{
		"name": {
			"de": "Grant ID",
			"en": "Grant ID"
		},
		"flags": Form.NONE,
		"field": "GrantId"
	},{
		"name": {
			"de": "Features",
			"en": "Features"
		},
		"flags": Form.CONTROLLED,
		"field": "Features"
}]

MAP = {
	"description": "Description",
	"displayName": "DisplayName",
	"startDate": "StartDate",
	"endDate": "EndDate",
	"keywords": "Keywords",
	"projectName": "ProjectName",
	"principleInvestigators": "PrincipleInvestigators",
	"grantId": "GrantId",
	"disciplines": "Discipline",
	"organizations": "Organization"
}

###############################################################################

class ProjectForm(Form):

	def __init__(self, lang, vocabulary, parent):
		super().__init__("Project Form", lang, KEYS, vocabulary)
		self.parent = parent

###############################################################################

	def parse(self, data):

		def _parse_disciplines(self, data):
			LSTR = {"en": "displayNameEn", "de": "displayNameDe"}[self._lang]
			disciplines = []
			for discipline in data:
				disciplines.append(discipline[LSTR])
			return disciplines

		def _parse_organizations(self, data):
			organizations = []
			for organization in data:
				vocabulary = self._vocabulary["Organization"]
				for entry in vocabulary.values():
					if entry["url"] == organization["url"]:
						organizations.append(entry["displayName"])
			return organizations

		for key in data:
			if key in MAP and data[key] != "":
				entry = self.entry(MAP[key])
				if entry is None:
					continue
				name = entry["name"][self._lang]
				flags = entry["flags"]
				value = data[key]
				if flags & Form.CONTROLLED or flags & Form.LIST:
					if key == "disciplines":
						self[name] = _parse_disciplines(self, value)
					elif key == "organizations":
						self[name] = _parse_organizations(self, value)
					elif key == "visibility":
						self[name] = value["displayName"]
				else:
					self[name] = value

###############################################################################

	def generate(self):

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
				if entry["flags"] & ProjectForm.LIST:
					if type(value) is not list and type(value) is not tuple:
						raise ValueError("Expected iterable value for key %s" % key)
					data[field] = []
					for v in value:
						data[field].append(final_value(key, v))
				else:
					data[field] = final_value(key, value)

		if missing:
			raise RequirementError(missing)
		
		if self.parent:
			data["ParentId"] = self.parent.id

		data["Visibility"] = {
			"displayName": "Project Members",
			"id": "8ab9c883-eb0d-4402-aaad-2e4007badce6"
		}

		return data

###############################################################################