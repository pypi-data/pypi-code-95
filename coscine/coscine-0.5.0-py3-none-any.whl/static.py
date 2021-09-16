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

###############################################################################
# The purpose of the StaticServer class defined in this file is to provide
# static data which is not subject to change. Initially a request is made
# to the Coscine REST API to query such data. Upon further requests a
# cached response is used to speed things up and reduce internet traffic.
# Dynamic data such as the metadata of a project cannot be cached as
# it may be invalidated by further requests or interactions with a
# different client such as the web interface.
###############################################################################

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from coscine.client import Client

import urllib
import os

###############################################################################

class StaticServer:

	client: Client
	cache: dict

	def __init__(self, client):
		self.client = client
		self.cache = {}

###############################################################################

	def disciplines(self) -> dict:
		LMAP = {
			"de": "displayNameDe",
			"en": "displayNameEn"
		}
		lang = LMAP[self.client.lang]

		if "disciplines" in self.cache:
			data = self.cache["disciplines"]
		else:
			uri = self.client.uri("Project", "Discipline")
			data = self.client.get(uri).json()
			self.cache["disciplines"] = data

		disciplines = {}
		for entry in data:
			disciplines[entry[lang]] = entry
		return disciplines

###############################################################################

	def organizations(self) -> dict:
		organizations = {}
		if "organizations" in self.cache:
			data = self.cache["organizations"]
		else:
			uri = self.client.uri("Organization", "Organization")
			data = self.client.get(uri).json()
		for entry in data["data"]:
			organizations[entry["displayName"]] = entry
		return organizations

###############################################################################

	def visibility(self) -> dict:
		visibility = {}
		uri = self.client.uri("Project", "Visibility")
		data = self.client.get(uri).json()
		for entry in data:
			visibility[entry["displayName"]] = entry
		return visibility

###############################################################################

	def features(self) -> dict:
		features = {}
		uri = self.client.uri("ActivatedFeatures", "ActivatedFeatures")
		data = self.client.get(uri).json()
		for entry in data:
			features[entry[self.client.lang]] = entry
		return features

###############################################################################

	def licenses(self) -> dict:
		licenses = {}
		uri = self.client.uri("Project", "License")
		data = self.client.get(uri).json()
		for entry in data:
			licenses[entry["displayName"]] = entry
		return licenses

###############################################################################

	def resource_types(self) -> dict:
		uri = self.client.uri("Resources", "ResourceType", "types")
		data = self.client.get(uri).json()
		types = {}
		for it in data:
			if it["isEnabled"]:
				types[it["displayName"]] = it
		return types

###############################################################################

	def application_profiles(self) -> dict:
		profiles = {}
		uri = self.client.uri("Metadata", "Metadata", "profiles")
		data = self.client.get(uri).json()
		for entry in data:
			name = urllib.parse.urlparse(entry)[2]
			name = os.path.relpath(name, "/coscine/ap/")
			name = name.upper()
			profiles[name] = entry
		return profiles

###############################################################################

	@staticmethod
	def _parse_application_profile(profile: dict) -> dict:

		def _get_lang(entry, lang):
			for it in entry:
				if it["@language"] == lang:
					return it
			return None

		"""
		Parses an application profile into a human readable python dict
		"""

		W3PREFIX = "http://www.w3.org/ns/shacl#%s"
		data = {}
		profile = profile[0]
		data["id"] = profile["@id"]
		graph = []
		for entry in profile["@graph"]:
			obj = {}
			if W3PREFIX % "name" not in entry:
				continue
			obj["id"] = entry["@id"]
			obj["path"] = entry[W3PREFIX % "path"][0]["@id"]
			obj["order"] = int(entry[W3PREFIX % "order"][0]["@value"])
			if W3PREFIX % "minCount" in entry:
				obj["minCount"] = int(entry[W3PREFIX % "minCount"][0]["@value"])
			if W3PREFIX % "maxCount" in entry:
				obj["maxCount"] = int(entry[W3PREFIX % "maxCount"][0]["@value"])
			obj["name"] = {
				"de": _get_lang(entry[W3PREFIX % "name"], "de")["@value"],
				"en": _get_lang(entry[W3PREFIX % "name"], "en")["@value"]
			}
			if W3PREFIX % "datatype" in entry:
				obj["datatype"] = entry[W3PREFIX % "datatype"][0]["@id"]
				obj["type"] = "literal"
			if W3PREFIX % "class" in entry:
				obj["class"] = entry[W3PREFIX % "class"][0]["@id"]
				obj["datatype"] = obj["class"]
				obj["type"] = "uri"
			graph.append(obj)
		data["graph"] = graph
		return data

###############################################################################

	def application_profile(self, path: str, id: str = None, parse: bool = False) -> dict:
		uri = self.client.uri("Metadata", "Metadata", "profiles", path, id)
		profile = self.client.get(uri).json()
		if parse:
			profile = self._parse_application_profile(profile)
		return profile

###############################################################################