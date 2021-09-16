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
# This file contains the main class of the coscine python package.
# The client class is the backbone and manager of everything contained
# within the coscine python module.
###############################################################################

import json
import urllib
import requests
from requests.exceptions import RequestException
import colorama
from requests.models import Response
from .banner import BANNER
from .about import __version__
from .exceptions import *
from .project import Project
from .static import StaticServer
from .ProjectForm import ProjectForm

###############################################################################

class Client:

#######################################
# Class member variable declaration
#######################################

	lang: str
	verbose: bool
	session: requests.Session
	loglevel: str
	version: str
	static: StaticServer

#######################################
# Class Constructor
###############################################################################

	def __init__(self, token: str, lang: str = "en", verbose: bool = True, \
					loglevel: list[str] = ["LOG", "INFO", "WARN", "REQUEST", "DATA"]):

		LANG = ("en", "de")
		if type(token) is not str:
			raise TypeError("Argument 'token' must be of type string!")
		if lang not in LANG:
			raise ValueError("Invalid value in argument 'lang'!")

		self.session = requests.Session()
		self.session.headers = {
			"Authorization": "Bearer " + token,
			"User-Agent": "Coscine Python Client %s" % __version__
		}
		self.lang = lang
		self.verbose = verbose
		self.loglevel = loglevel
		self.version = __version__
		self.static = StaticServer(self)
		if verbose:
			colorama.init(autoreset=True)
			print(BANNER)

###############################################################################

	def log(self, msg: str, level: str = "LOG"):
		LEVELS = {
			"LOG": colorama.Fore.MAGENTA,
			"INFO": colorama.Fore.GREEN,
			"WARN": colorama.Fore.YELLOW,
			"REQUEST": colorama.Fore.LIGHTGREEN_EX,
			"DATA": colorama.Fore.LIGHTBLUE_EX
		}

		if level not in LEVELS:
			raise ValueError(level)

		if not level in self.loglevel:
			return

		if self.verbose:
			print(LEVELS[level] + "[%s] " % level + msg)

###############################################################################

	def is_outdated(self) -> bool:
		uri = "https://pypi.org/pypi/coscine/json"
		data = requests.get(uri).json()
		version = data["info"]["version"]
		if version != __version__:
			msg = "Using Coscine Client version %s but latest version is %s.\n"\
					"Consider updating the package by running:\n" \
					"py -m pip install --user --upgrade coscine\n" \
					% (__version__, version)
			self.log(msg)
			return True
		else:
			return False

###############################################################################

	@staticmethod
	def uri(api: str, endpoint: str, *args) -> str:
		BASE = "https://coscine.rwth-aachen.de/coscine/api/Coscine.Api.%s/%s"
		ENDPOINTS = (
			"Blob",
			"Metadata",
			"Organization",
			"Project",
			"Resources",
			"Tree",
			"User",
			"ActivatedFeatures"
		)

		if api not in ENDPOINTS:
			raise ValueError("Argument 'api' does not specify a valid endpoint!")

		uri = BASE % (api, endpoint)
		for arg in args:
			if arg is None:
				continue
			uri += "/" + urllib.parse.quote(arg, safe="")
		return uri

###############################################################################

	def _request(self, method: str, uri: str, **kwargs) -> Response:
		if "data" in kwargs and type(kwargs["data"]) is dict:
			kwargs["headers"] = {"Content-Type": "application/json;charset=utf-8"}
			kwargs["data"] = json.dumps(kwargs["data"])

		try:
			self.log("%s %s" % (method, uri), "REQUEST")
			if "data" in kwargs:
				try:
					self.log(json.dumps(json.loads(kwargs["data"]), indent=4), "DATA")
				except :
					pass
			response = self.session.request(method, uri, **kwargs)
			response.raise_for_status()
			if response.content:
				try:
					self.log(json.dumps(response.json(), indent=4), "DATA")
				except:
					pass
			return response
		except requests.exceptions.ConnectionError:
			raise ConnectionError()
		except requests.exceptions.RequestException as e:
			if e.response.status_code == 401:
				raise UnauthorizedError("Invalid API token")
			else:
				raise RequestException()

###############################################################################

	def get(self, uri: str, **kwargs) -> requests.Response:
		return self._request("GET", uri, **kwargs)

###############################################################################

	def put(self, uri: str, **kwargs) -> requests.Response:
		return self._request("PUT", uri, **kwargs)

###############################################################################

	def post(self, uri: str, **kwargs) -> requests.Response:
		return self._request("POST", uri, **kwargs)

###############################################################################

	def delete(self, uri: str, **kwargs) -> requests.Response:
		return self._request("DELETE", uri, **kwargs)

###############################################################################

	def projects(self, toplevel: bool = True, **kwargs) -> list[Project]:
		ENDPOINTS = ("Project", "Project/-/topLevel")
		uri = self.uri("Project", ENDPOINTS[toplevel])
		projects = self.get(uri).json()
		filter = []
		for data in projects:
			match = True
			for key, value in kwargs.items():
				if data[key] != value:
					match = False
					break
			if match:
				filter.append(Project(self, data))
		return filter

###############################################################################

	def project(self, displayName: str = None, **kwargs) -> Project:
		if displayName:
			kwargs["displayName"] = displayName
		projects = self.projects(toplevel = True, **kwargs)
		if len(projects) == 1:
			return projects[0]
		elif len(projects) == 0:
			return None
		else:
			raise CoscineException("Undistinguishable projects!")

###############################################################################

	def ProjectForm(self, parent: Project = None) -> ProjectForm:
		vocabulary = {
			"Discipline": self.static.disciplines(),
			"Organization": self.static.organizations(),
			"Visibility": self.static.visibility(),
			"Features": self.static.features()
		}

		form = ProjectForm(self.lang, vocabulary, parent)
		return form

###############################################################################

	def create_project(self, form: ProjectForm) -> Project:
		if type(form) is ProjectForm:
			form = form.generate()

		uri = self.uri("Project", "Project")
		return Project(self, self.post(uri, data = form).json())

###############################################################################