###############################################################################
# Coscine Python3 Client
# Copyright (c) 2018-2021 RWTH Aachen University
# Contact: coscine@itc.rwth-aachen.de
# Git: https://git.rwth-aachen.de/coscine/docs/public/wiki/-/tree/master/
# Please direct bug reports, feature requests or questions at the URL above
# by opening an issue.
###############################################################################
# This python wrapper implements a client for the Coscine API.
# Coscine is an open source project at RWTH Aachen University for
# the management of research data.
# Visit https://coscine.rwth-aachen.de for more information.
###############################################################################

import os
import json
import urllib
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from requests_toolbelt.multipart.encoder import coerce_data
from tqdm import tqdm
import colorama
from .exceptions import *
from .MetadataForm import MetadataForm
from .ProjectForm import ProjectForm
from .ResourceForm import ResourceForm

###############################################################################

__version__ = "0.4.1"

###############################################################################
# Coscine Banner
###############################################################################

BANNER = colorama.Fore.BLUE + \
"""
                     _             
                    (_)            
   ___ ___  ___  ___ _ _ __   ___  
  / __/ _ \/ __|/ __| | '_ \ / _ \ 
 | (_| (_) \__ \ (__| | | | |  __/ 
  \___\___/|___/\___|_|_| |_|\___| 

""" + colorama.Fore.WHITE + \
"____________________________________\n" + \
"\n   Coscine API Client" + colorama.Fore.YELLOW + " " + __version__ + "\n" + \
colorama.Fore.WHITE + "____________________________________\n\n"

###############################################################################

class CoscineClient:

	"""
	Provides a python client for the Coscine REST API
	"""

###############################################################################

	def __init__(self, token, verbose=True, lang="en"):

		"""
		Constructor of the CoscineClient class

		Parameters
		----------
		token : str
			Your Coscine API token
		verbose : bool
			Enable/Disable command line output
		lang : str
			Set form and controlled vocabulary language
		"""

		if lang != "en" and lang != "de":
			raise ValueError("Expected \"en\" or \"de\" for parameter lang!")

		if type(token) is not str:
			raise ValueError("Expected Coscine API token as string!")

		self.session = requests.Session()
		self.session.headers = {
			"Authorization": "Bearer " + token,
			"User-Agent": "Coscine Python Client v0.3.2"
		}
		self.verbose = verbose
		self.lang = lang
		self.cache = {}
		if verbose:
			colorama.init(autoreset=True)
			self.log(BANNER)
			self.check_version()

###############################################################################

	def check_version(self):

		"""
		Checks for the latest version hosted at pypi and compares it with
		the current version.
		"""

		uri = "https://pypi.org/pypi/coscine/json"
		data = requests.get(uri).json()
		version = data["info"]["version"]
		if version != __version__:
			msg = "Using CoscineClient version %s but latest version is %s.\n"\
					"Consider updating the package by running:\n" \
					"py -m pip install --user --upgrade coscine\n" \
					"This version is OUTDATED and UNSUPPORTED!\n" \
					% (__version__, version)
			self.log(msg, level = "WARN")

###############################################################################

	def __del__(self):
		pass

###############################################################################

	@staticmethod
	def uri(api, endpoint, *args):

		"""
		Coscine API URL builder

		Parameters
		----------
		api : str
			Select the Coscine API (e.g. "Project" or "Metadata")
		endpoint : str
			Select the Coscine API endpoint
		args : vargs
			Include values and additional parameters
		"""

		BASE = "https://coscine.rwth-aachen.de/coscine/api/Coscine.Api.%s/%s"
		uri = BASE % (api, endpoint)
		if len(args) > 0:
			for arg in args:
				uri += "/" + urllib.parse.quote(arg, safe="")
		return uri

###############################################################################

	def log(self, msg, level = None):

		"""
		If logging is enabled you can use this method to print messages
		to the command line interface
		"""

		LEVELS = {
			"INFO": colorama.Fore.GREEN,
			"LOG": colorama.Fore.MAGENTA,
			"WARN": colorama.Fore.YELLOW
		}

		if self.verbose:
			if level and level in LEVELS:
				msg = LEVELS[level] + "[%s] " % level + msg
			print(msg)

###############################################################################

	def _req(self, method, uri, cache = False, **kwargs):

		"""
		HTTP Request handler with simple cache
		"""

		# Some rudimentary caching to speed things up
		if cache and uri in self.cache and method == "GET":
			return self.cache[uri]

		try:
			self.log("%s %s" % (method, uri), level = "LOG")
			response = self.session.request(method, uri, **kwargs)
			response.raise_for_status()
			if cache and method == "GET":
				self.cache[uri] = response
			return response
		except requests.exceptions.ConnectionError as e:
			raise ConnectionError()
		except requests.exceptions.RequestException as e:
			raise ServerError()

###############################################################################

	def get(self, uri, cache = False, **kwargs):
		return self._req("GET", uri, cache = cache, **kwargs)

###############################################################################

	def put(self, uri, **kwargs):
		return self._req("PUT", uri, **kwargs)

###############################################################################

	def post(self, uri, **kwargs):
		return self._req("POST", uri, **kwargs)

###############################################################################

	def delete(self, uri, **kwargs):
		return self._req("DELETE", uri, **kwargs)

###############################################################################

	def get_projects(self, **kwargs):

		"""
		Get a list of projects optionally matching certain criteria
		
		Parameters
		----------
		kwargs : unfolded dictionary containing filter criteria
			May contain any top-level key present in the project json
		
		Returns
		-------
		A list of projects as json dicts or an empty list
		"""

		uri = self.uri("Project", "Project")
		projects = self.get(uri, cache=True).json()
		if kwargs:
			projects = self._filter(projects, kwargs)
		return projects

###############################################################################

	def get_project(self, displayName):

		"""
		Get a specific project by its display name

		Parameters
		----------
		displayName : str
			The display name of the project
		"""

		projects = self.get_projects(displayName = displayName)
		if projects:
			if len(projects) > 1:
				self.log("Projects share common displayName!", level="WARN")
			return projects[0]
		else:
			raise NotFound(displayName)

###############################################################################

	def delete_project(self, project):

		"""
		Delete a project in Coscine
		
		Parameters
		----------
		project : JSON-object containing project information
		"""

		self.log("Deleting project [%s]" % project["projectName"], level="INFO")
		uri = self.uri("Project", "Project", project["id"])
		self.delete(uri)

###############################################################################

	def create_project(self, form):

		"""
		Create a Project in Coscine
		
		Parameters
		----------
		form : ProjectForm
		
		Returns
		-------
		A handle to the new project
		"""

		if type(form) is ProjectForm:
			form = form.generate()
		if type(form) is dict:
			form = json.dumps(form)
		uri = self.uri("Project", "Project")
		return self.post(uri, data=form).json()

###############################################################################

	def download_project(self, project, path="./"):

		"""
		Download a Coscine project including all of its resources to
		a directory on your harddrive
		
		Parameters
		----------
		project : Coscine Project Handle
		path : (optional) Path to the local save directory
		
		Returns
		-------
		Nothing
		"""

		self.log("Downloading project [%s]" % project["projectName"], level="INFO")
		path = os.path.join(path, project["displayName"])
		if not os.path.isdir(path):
			os.mkdir(path)
		for resource in self.get_resources(project):
			self.download_resource(resource, path=path)

###############################################################################

	def get_resources(self, project, **kwargs):

		"""
		Parameters
		----------
		
		Returns
		-------
		
		"""

		uri = self.uri("Project", "Project", project["id"], "resources")
		resources = self.get(uri, cache = True).json()
		if kwargs:
			resources = self._filter(resources, kwargs)
		return resources

###############################################################################

	def get_resource(self, project, displayName):
		resources = self.get_resources(project, displayName = displayName)
		if resources and len(resources) == 1:
			return resources[0]
		else:
			raise NotFound(displayName)

###############################################################################

	def delete_resource(self, resource):

		"""
		Deletes a Resource

		Parameters
		----------
		resource : Coscine Resource Handle

		Returns
		-------
		Nothing
		"""

		self.log("Deleting resource [%s]." % resource["resourceName"], level="INFO")
		uri = self.uri("Resources", "Resource", resource["id"])
		self.delete(uri)

###############################################################################

	def create_resource(self, project, form):

		"""
		Parameters
		----------
		
		Returns
		-------
	
		"""

		if type(form) is ResourceForm:
			form = form.generate()
		if type(form) is dict:
			form = json.dumps(form)
		uri = self.uri("Resources", "Resource", "Project", project["id"])
		headers = {
			"Content-Type": "application/json;charset=utf-8"
		}
		self.post(uri, data=form, headers=headers)

###############################################################################

	def download_resource(self, resource, path="./"):

		"""
		Downloads a resource and all of its files

		Parameters
		----------
		resource : Coscine Resource Handle
			The Resource you want to download

		path : str
			The path to the save directory

		Returns
		-------
		Nothing
		
		"""

		self.log("Downloading resource [%s]" % resource["resourceName"], level="INFO")
		dirpath = os.path.join(path, resource["displayName"])
		if not os.path.isdir(dirpath):
			os.mkdir(dirpath)
		files = self.get_files(resource)
		for file in files:
			filepath = os.path.join(dirpath, file["Path"].strip("/"))
			self.download_file(resource, file["Name"], path=filepath)

###############################################################################

	def get_quota(self, resource):

		"""
		Get the quota used by a Coscine resource in bytes

		Parameters
		----------
		resource : Coscine resource handle

		Returns
		-------
		The used quota of the resource as int
		"""

		uri = self.uri("Blob", "Blob", resource["id"], "quota")
		data = self.get(uri).json()
		quota = int(data["data"]["usedSizeByte"])
		return quota

###############################################################################

	def get_files(self, resource, **kwargs):

		"""
		Get a list of files and their metadata

		Parameters
		----------
		resource : Coscine Resource handle
		kwargs : Optional keyword arguments

		Returns
		-------
		A list of files and their metadata
		"""

		uri = self.uri("Tree", "Tree", resource["id"])
		data = self.get(uri, cache=True).json()
		files = []
		for entry in data["data"]["fileStorage"]:
			info = {
				"Name": entry["Name"],
				"Path": entry["Path"],
				"Size": entry["Size"],
				"Type": entry["Kind"],
				"Provider": entry["Provider"]
			}
			files.append(info)

		if kwargs:
			files = self._filter(files, kwargs)

		return files

###############################################################################

	def get_metadata(self, resource, filename):

		"""
		Get the metadata of a file

		Parameters
		----------
		resource : Coscine Resource Handle
		filename : str

		Returns
		-------
		Metadata of file referenced by filename
		"""

		uri = self.uri("Tree", "Tree", resource["id"], filename)
		data = self.get(uri).json()
		metadata = data["data"]["metadataStorage"][0]
		for key in metadata:
			return metadata[key]

###############################################################################

	def put_metadata(self, resource, filename, metadata):

		"""
		Upload or update metadata for a file

		Parameters
		----------
		resource : Coscine Resource Handle
		filename : str
		metadata : MetadataForm or dict or str

		Returns
		-------
		"""

		if type(metadata) is MetadataForm:
			metadata = metadata.generate()
		if type(metadata) is dict:
			metadata = json.dumps(metadata)
		uri = self.uri("Tree", "Tree", resource["id"], filename)
		self.put(uri, data = metadata)

###############################################################################

	def download_file(self, resource, filename, path):

		"""
		Downloads a file from a resource

		Parameters
		----------
		resource : Coscine Resource Handle
		filename : str
		path : str

		Returns
		-------

		"""

		uri = self.uri("Blob", "Blob", resource["id"], filename)
		response = self.get(uri, stream = True)
		fd = open(path, "wb")
		CHUNK_SIZE = 4096
		if self.verbose:
			filesize = self.get_files(resource, Name = filename)[0]["Size"]
			bar = tqdm(total = filesize, unit = "B", unit_scale = True, \
											desc = "↓ %s" % filename)
		for chunk in response.iter_content(chunk_size = CHUNK_SIZE):
			fd.write(chunk)
			if self.verbose:
				bar.update(len(chunk))
		if self.verbose:
			bar.close()
		fd.close()

###############################################################################

	def upload_file(self, resource, filename, path, metadata):

		"""
		Uploads a file to a resource
		"""

		fd = open(path, "rb")
		self.upload_data(resource, filename, fd, metadata)
		fd.close()

###############################################################################

	def _progress_callback(self, monitor, bar):
		if self.verbose:
			bar.update(monitor.bytes_read - bar.n)

	def upload_data(self, resource, filename, data, metadata):

		"""
		Uploads data to a resource

		Parameters
		----------
		"""

		uri = self.uri("Blob", "Blob", resource["id"], filename)
		self.put_metadata(resource, filename, metadata)
		fields = {
			"files": (filename, data, "application/octet-stream")
		}
		encoder = MultipartEncoder(fields = fields)
		filesize = encoder.len
		if self.verbose:
			bar = tqdm(total = filesize, unit = "B", unit_scale = True, \
				desc = "↑ %s" % filename)
		else:
			bar = None
		monitor = MultipartEncoderMonitor(encoder, \
			lambda callback: self._progress_callback(callback, bar))
		headers = {
			"Content-Type": monitor.content_type
		}
		self.put(uri, data = monitor, headers = headers)
		if self.verbose:
			bar.close()

###############################################################################

	def delete_file(self, resource, filename):

		"""
		Deletes a file from a resource

		Parameters
		----------
		resource : Coscine Resource Handle
		filename : str
		"""

		self.log("Deleting file [%s/%s]" % (resource["resourceName"], filename), level="INFO")
		uri = self.uri("Blob", "Blob", resource["id"], filename)
		try:
			self.delete(uri)
		except ServerError:
			raise CoscineException("File [%s] does not exist" % filename)

###############################################################################

	@staticmethod
	def _get_lang(entry, lang):
		for it in entry:
			if it["@language"] == lang:
				return it
		return None

	@staticmethod
	def _parse_application_profile(profile):
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
				"de": CoscineClient._get_lang(entry[W3PREFIX % "name"], "de")["@value"],
				"en": CoscineClient._get_lang(entry[W3PREFIX % "name"], "en")["@value"]
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

	def get_application_profile(self, resource, parse=False):

		"""
		Returns the application profile used by a resource

		Parameters
		----------
		resource : Coscine Resource Handle
		parse : bool
			If set to true, converts the application profile to a simplified
			representation
		"""

		uri = self.uri("Metadata", "Metadata", "profiles", \
			resource["applicationProfile"], resource["id"])
		profile = self.get(uri).json()
		if parse:
			profile = CoscineClient._parse_application_profile(profile)
		return profile

###############################################################################

	def MetadataForm(self, project, resource, data=None):

		"""
		Generate a Coscine Metadata Input Form

		Parameters
		----------
		
		Returns
		-------
		A Metadata Input Form
		"""

		form = MetadataForm(self, project, resource)
		if data:
			for key in data:
				form[key] = data[key]
		return form

###############################################################################

	def ProjectForm(self, parent=None, data=None):

		"""
		Parameters
		----------
		
		Returns
		-------
		
		"""

		form = ProjectForm(self, parent=parent)
		if data:
			for key in data:
				form[key] = data[key]
		return form

###############################################################################

	def ResourceForm(self, data=None):

		"""
		Parameters
		----------
		
		Returns
		-------
		
		"""

		form = ResourceForm(self)
		if data:
			for key in data:
				form[key] = data[key]
		return form

###############################################################################

	def get_disciplines(self):

		"""
		"""

		LMAP = {
			"de": "displayNameDe",
			"en": "displayNameEn"
		}
		lang = LMAP[self.lang]
		disciplines = {}
		uri = self.uri("Project", "Discipline")
		data = self.get(uri, cache=True).json()
		for entry in data:
			disciplines[entry[lang]] = entry
		return disciplines

###############################################################################

	def get_organizations(self, filter=None):

		"""
		Parameters
		----------
		
		Returns
		-------
		
		"""

		organizations = {}
		uri = self.uri("Organization", "Organization")
		data = self.get(uri, cache=True).json()
		for entry in data["data"]:
			organizations[entry["displayName"]] = entry
		return organizations

###############################################################################

	def get_visibility(self):
		visibility = {}
		uri = self.uri("Project", "Visibility")
		data = self.get(uri, cache=True).json()
		for entry in data:
			visibility[entry["displayName"]] = entry
		return visibility

###############################################################################

	def get_features(self):
		features = {}
		uri = self.uri("ActivatedFeatures", "ActivatedFeatures")
		data = self.get(uri, cache=True).json()
		for entry in data:
			features[entry[self.lang]] = entry
		return features

###############################################################################

	def get_instance(self, project, link):
		uri = self.uri("Metadata", "Metadata", "instances", \
										project["id"], link)
		instance = self.get(uri, cache=True).json()
		return instance

###############################################################################

	def get_resource_types(self):
		uri = self.uri("Resources", "ResourceType", "types")
		data = self.get(uri, cache=True).json()
		types = {}
		for it in data:
			if it["isEnabled"]:
				types[it["displayName"]] = it
		return types

###############################################################################

	def get_profiles(self):
		profiles = {}
		uri = self.uri("Metadata", "Metadata", "profiles")
		data = self.get(uri, cache=True).json()
		for entry in data:
			name = urllib.parse.urlparse(entry)[2]
			name = os.path.relpath(name, "/coscine/ap/")
			name = name.upper()
			profiles[name] = entry
		return profiles

###############################################################################

	def get_licenses(self):
		licenses = {}
		uri = self.uri("Project", "License")
		data = self.get(uri, cache=True).json()
		for entry in data:
			licenses[entry["displayName"]] = entry
		return licenses

###############################################################################

	def activate_feature(self, project, feature, flag):
		FLAGS = {
			True: "activateFeature",
			False: "deactivateFeature"
		}
		uri = self.uri("ActivatedFeatures", "ActivatedFeatures", \
			project["id"], FLAGS[flag], feature["id"])
		self.get(uri)

###############################################################################

	@staticmethod
	def _filter(data, kwargs):

		"""
		Filters an array of dictionaries according to kwargs
		"""

		filtered = []
		for entry in data:
			for kw in kwargs:
				if kw in entry and entry[kw] == kwargs[kw]:
					filtered.append(entry)
		return filtered
