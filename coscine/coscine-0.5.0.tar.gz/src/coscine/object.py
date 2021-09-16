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
	from .resource import Resource
	from .MetadataForm import MetadataForm
import os
import json
from .progress import ProgressBar

###############################################################################

class Object:

###############################################################################

	client: Client
	resource: Resource
	data: dict
	metadata: dict
	name: str
	size: int
	type: str

###############################################################################

	CHUNK_SIZE = 4096

###############################################################################

	def __init__(self, resource: Resource, data: dict, metadata: dict):
		self.client = resource.client
		self.resource = resource
		self.data = data
		self.metadata = metadata
		self.name = data["Name"]
		self.size = data["Size"]
		self.type = data["Kind"]

###############################################################################

	def __str__(self) -> str:
		return json.dumps(self.data, indent = 4)

###############################################################################

	def content(self) -> bytes:
		uri = self.client.uri("Blob", "Blob", self.resource.id, self.name)
		data = self.client.get(uri).content
		return data

###############################################################################

	def download(self, path = "./", callback = None):
		# uri = self.data["Action"]["Download"] # Not working, Duh!
		uri = self.client.uri("Blob", "Blob", self.resource.id, self.name)
		response = self.client.get(uri, stream = True)
		path = os.path.join(path, self.name)
		fd = open(path, "wb")
		bar = ProgressBar(self.client, self.size, self.name, "DOWN", callback)
		for chunk in response.iter_content(chunk_size = self.CHUNK_SIZE):
			fd.write(chunk)
			bar.update(len(chunk))
		fd.close()

###############################################################################

	def delete(self):
		uri = self.client.uri("Blob", "Blob", self.resource.id, self.name)
		self.client.delete(uri)

###############################################################################

	def update(self, metadata: MetadataForm):
		if type(metadata) is MetadataForm:
			metadata = metadata.generate()
		uri = self.client.uri("Tree", "Tree", self.resource.id, self.name)
		self.client.put(uri, data = metadata)

###############################################################################

	def MetadataForm(self) -> MetadataForm:
		form = self.resource.MetadataForm()
		form.parse(self.metadata)
		return form

###############################################################################