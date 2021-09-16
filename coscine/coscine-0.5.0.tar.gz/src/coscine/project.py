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

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .client import Client

import os
import json
from .exceptions import *
from .resource import Resource
from .ResourceForm import ResourceForm
from .ProjectForm import ProjectForm
from .MetadataPresetForm import MetadataPresetForm
from .member import Member

###############################################################################

class Project:

#######################################
# Class member variable declaration
#######################################

	client: Client
	data: dict
	id: str
	name: str
	description: str
	principleInvestigators: str
	startDate: str
	endDate: str
	discipline: list[str]
	organization: list[str]

#######################################

	def __init__(self, client: Client, data: dict):
		self.client = client
		self.data = data
		self.id = data["id"]
		self.name = data["displayName"]
		self.description = data["description"]
		self.principleInvestigators = data["principleInvestigators"]
		self.startDate = data["startDate"]
		self.endDate = data["endDate"]
		self.discipline = []
		self.organization = []

###############################################################################

	def __str__(self) -> str:
		return json.dumps(self.data, indent=4)

###############################################################################

	def subprojects(self, **kwargs) -> list:
		uri = self.client.uri("Project", "SubProject", self.id)
		projects = self.client.get(uri).json()
		filter = []
		for data in projects:
			match = True
			for key, value in kwargs.items():
				if data[key] != value:
					match = False
					break
			if match:
				filter.append(Project(self.client, data))
		return filter

###############################################################################

	def resources(self, **kwargs) -> list[Resource]:
		uri = self.client.uri("Project", "Project", self.id, "resources")
		resources = self.client.get(uri).json()
		filter = []
		for data in resources:
			match = True
			for key, value in kwargs.items():
				if data[key] != value:
					match = False
					break
			if match:
				filter.append(Resource(self, data))
		return filter

###############################################################################

	def resource(self, displayName: str = None, **kwargs) -> Resource:
		if displayName:
			kwargs["displayName"] = displayName
		resources = self.resources(**kwargs)
		if len(resources) == 1:
			return resources[0]
		else:
			raise CoscineException("Undistinguishable resources!")

###############################################################################

	def download(self, path: str = "./"):
		path = os.path.join(path, self.displayName)
		if not os.path.isdir(path):
			os.mkdir(path)
		for resource in self.resources():
			resource.download(path = path)

###############################################################################

	def delete(self):
		uri = self.client.uri("Project", "Project", self.id)
		self.client.delete(uri)

###############################################################################

	def members(self) -> list[Member]:
		uri = self.client.uri("Project", "ProjectRole", self.id)
		data = self.client.get(uri).json()
		members = [Member(self, m) for m in data]
		return members

###############################################################################

	def invite(self, email: str, role: str = "Member"):
		ROLES = {
			"Owner": "be294c5e-4e42-49b3-bec4-4b15f49df9a5",
			"Member": "508b6d4e-c6ac-4aa5-8a8d-caa31dd39527"
		}

		if role not in ROLES:
			raise ValueError("Invalid role '%s'." % role)

		uri = self.client.uri("Project", "Project", "invitation")
		data = {
			"projectId": self.data["id"],
			"role": ROLES[role],
			"email": email
		}

		try:
			self.client.log("Inviting [%s] as [%s] to project [%s]." % 
												(email, role, self.id))
			self.client.post(uri, data = data)
		except ServerError:
			self.client.log("User [%s] has invite pending." % email)

###############################################################################

	def _instance(self, link: str) -> dict:
		uri = self.client.uri("Metadata", "Metadata", "instances", self.id, link)
		return self.client.get(uri).json()

###############################################################################

	def ResourceForm(self) -> ResourceForm:
		vocabulary = {
			"type": self.client.static.resource_types(),
			"applicationProfile": self.client.static.application_profiles(),
			"License": self.client.static.licenses(),
			"Visibility": self.client.static.visibility(),
			"Disciplines": self.client.static.disciplines()
		}
		return ResourceForm(self.client.lang, vocabulary)

###############################################################################

	def create_resource(self, resourceForm: ResourceForm, \
					metadataPreset: MetadataPresetForm = None) -> Resource:
		if type(resourceForm) is ResourceForm:
			resourceForm = resourceForm.generate()
		if metadataPreset:
			if type(metadataPreset) is MetadataPresetForm:
				metadataPreset = metadataPreset.generate()
			resourceForm["fixedValues"] = metadataPreset
		uri = self.client.uri("Resources", "Resource", "Project", self.id)
		return Resource(self, self.client.post(uri, data = resourceForm).json())

###############################################################################

	def form(self) -> ProjectForm:
		form = self.client.ProjectForm()
		form.parse(self.data)
		return form

###############################################################################

	def update(self, form: ProjectForm):
		if type(form) is ProjectForm:
			form = form.generate()
		uri = self.client.uri("Project", "Project", self.id)
		self.client.post(uri, data = form)

###############################################################################