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
	from .project import Project

###############################################################################

class Member:

# Member variables (only for type hinting, not static!)
###############################################################################

	id: str
	role: str
	data: dict
	client: Client
	project: Project

###############################################################################

	def __init__(self, project: Project, data: dict):
		self.client = project.client
		self.project = project
		self.data = data
		self.name = data["user"]["displayName"]
		self.email = data["user"]["emailAddress"]
		self.id = data["user"]["id"]
		self.role = data["role"]["displayName"]

###############################################################################

	def set_role(self, role: str):
		ROLES = {
			"Owner": "be294c5e-4e42-49b3-bec4-4b15f49df9a5",
			"Member": "508b6d4e-c6ac-4aa5-8a8d-caa31dd39527"
		}

		if role not in ROLES:
			raise ValueError("Invalid role '%s'." % role)

		uri = self.client.uri("Project", "ProjectRole")
		self.data["role"]["id"] = ROLES[role]
		self.data["role"]["displayName"] = role
		self.client.post(uri, data = self.data)

###############################################################################

	def remove(self):
		uri = self.client.uri("Project", "ProjectRole", "project", \
			self.project.id, "user", self.id, "role", self.data["role"]["id"])
		self.client.delete(uri)

###############################################################################