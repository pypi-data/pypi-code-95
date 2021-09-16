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
import os
import json
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from .exceptions import *
from .object import Object
from .MetadataForm import MetadataForm
from .MetadataPresetForm import MetadataPresetForm
from .ResourceForm import ResourceForm
from .progress import ProgressBar

###############################################################################

class Resource:

	client: Client
	project: Project
	data: dict
	id: str
	name: str

	def __init__(self, project, data):
		self.client = project.client
		self.project = project
		self.data = data
		self.id = data["id"]
		self.name = data["displayName"]

###############################################################################

	def __str__(self) -> str:
		return json.dumps(self.data, indent=4)

###############################################################################

	def upload(self, key: str, file, metadata: dict = None, callback: function = None):
		if hasattr(file, "read"):
			fd = file
			filename = "MEM"
		elif type(file) is str:
			fd = open(file, "rb")
			filename = file
		else:
			raise CoscineException()

		if metadata:
			if type(metadata) is MetadataForm:
				metadata = metadata.generate()
			uri = self.client.uri("Tree", "Tree", self.id, key)
			self.client.put(uri, data = metadata)

		uri = self.client.uri("Blob", "Blob", self.id, key)
		fields = {"files": (key, fd, "application/octect-stream")}
		encoder = MultipartEncoder(fields = fields)
		bar = ProgressBar(self.client, encoder.len, filename, "UP", callback)
		monitor = MultipartEncoderMonitor(encoder, callback = lambda monitor: \
										bar.update(monitor.bytes_read - bar.n))
		headers = {"Content-Type": monitor.content_type}
		self.client.put(uri, data = monitor, headers = headers)

###############################################################################

	def download(self, path = "./"):
		path = os.path.join(path, self.name)
		if not os.path.isdir(path):
			os.mkdir(path)
		for file in self.objects():
			file.download(path)

###############################################################################

	def delete(self):
		uri = self.client.uri("Resources", "Resource", self.id)
		self.client.delete(uri)

###############################################################################

	def quota(self) -> int:
		uri = self.client.uri("Blob", "Blob", self.id, "quota")
		data = self.client.get(uri).json()
		return int(data("data")["usedSizeByte"])

###############################################################################

	def objects(self, **kwargs) -> list[Object]:
		uri = self.client.uri("Tree", "Tree", self.id)
		data = self.client.get(uri).json()
		fileStorage = data["data"]["fileStorage"]
		metadataStorage = data["data"]["metadataStorage"]
		objects = zip(fileStorage, metadataStorage)
		filter = []
		for f in objects:
			match = True
			for key, value in kwargs.items():
				if f[0][key] != value:
					match = False
					break
			if match:
				filter.append(Object(self, f[0], f[1]))
		return filter

###############################################################################

	def object(self, displayName: str = None) -> Object:
		objects = self.objects()
		for it in objects:
			if it.name == displayName:
				return it
		return None

###############################################################################

	def applicationProfile(self, parse = False):
		return self.client.static.application_profile(
				self.data["applicationProfile"], self.id, parse)

###############################################################################

	def MetadataForm(self, data = None):
		entries = []
		vocabulary = {}
		lang = self.client.lang
		profile = self.applicationProfile(parse = True)
		for element in profile["graph"]:
			flags = MetadataForm.NONE
			if "minCount" in element and element["minCount"] > 0:
				flags |= MetadataForm.REQUIRED
			if "maxCount" in element and element["maxCount"] > 1:
				flags |= MetadataForm.LIST

			if "class" in element:
				flags |= MetadataForm.CONTROLLED
				uri = element["class"]
				instance = self.project._instance(uri)
				if lang not in instance or len(instance[lang]) == 0:
					lang = "en"
				voc = {}
				for rule in instance[lang]:
					voc[rule["name"]] = rule["value"]
				vocabulary[element["name"][lang]] = voc

			entry = {
				"name": element["name"],
				"path": element["path"],
				"field": element["name"][lang],
				"flags": flags,
				"order": element["order"],
				"datatype": element["datatype"],
				"type": element["type"]
			}
			entries.append(entry)

		# Sort the keys according to their application profile order
		entries = sorted(entries, key = lambda x: x["order"])

		form = MetadataForm(profile, self.client.lang, entries, vocabulary)
		if data:
			for key in data:
				form[key] = data[key]
		return form

###############################################################################

	def MetadataPresetForm(self) -> MetadataPresetForm:
		entries = []
		vocabulary = {}
		lang = self.client.lang
		applicationProfile = self.applicationProfile(parse = True)
		for element in applicationProfile["graph"]:
			flags = MetadataPresetForm.NONE
			if "minCount" in element and element["minCount"] > 0:
				flags |= MetadataPresetForm.REQUIRED
			if "maxCount" in element and element["maxCount"] > 1:
				flags |= MetadataPresetForm.LIST

			if "class" in element:
				flags |= MetadataPresetForm.CONTROLLED
				uri = element["class"]
				instance = self.project._instance(uri)
				if lang not in instance or len(instance[lang]) == 0:
					lang = "en"
				voc = {}
				for rule in instance[lang]:
					voc[rule["name"]] = rule["value"]
				vocabulary[element["name"][lang]] = voc
			
			entry = {
				"name": element["name"],
				"path": element["id"],
				"flags": flags,
				"field": element["name"][lang],
				"order": element["order"],
				"datatype": element["datatype"],
				"type": element["type"],
				"locked": False,
				"enabled": True
			}
			entries.append(entry)

		# Sort the keys according to their application profile order
		entries = sorted(entries, key = lambda x: x["order"])
		return MetadataPresetForm(applicationProfile, lang, entries, vocabulary)

###############################################################################

	def form(self) -> ResourceForm:
		form = self.project.ResourceForm()
		form.parse(self.data)
		return form

###############################################################################

	def update(self, form):
		if type(form) is ResourceForm:
			form = form.generate()
		uri = self.client.uri("Resources", "Resource", self.id)
		self.client.post(uri, data = form)

###############################################################################

	def update_preset(self, form):
		data = self.form().generate()
		data["fixedValues"] = form.generate()
		uri = self.client.uri("Resources", "Resource", self.id)
		self.client.post(uri, data = data)

###############################################################################