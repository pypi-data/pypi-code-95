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

from collections.abc import MutableMapping
from .exceptions import *

###############################################################################

class Form(MutableMapping):

	# Form flags
	NONE = 0
	REQUIRED = 1
	CONTROLLED = 2
	SET = 4
	FIXED = 8
	LIST = 16
	SPECIAL = 32

###############################################################################

	def __init__(self, name: str, lang: str, entries: list, vocabulary: dict):
		self._name = name
		self._lang = lang
		self._entries = entries
		self._keys = {}
		for entry in entries:
			self._keys[entry["name"][self._lang]] = entry
		self._vocabulary = vocabulary
		self.store = {}

###############################################################################

	def __getitem__(self, key: str) -> dict:
		if key not in self.keys():
			raise KeyError(key)
		elif key in self.store:
			return self.store[key]
		else:
			return None

###############################################################################

	def __setitem__(self, key: str, value: object):
		if key not in self._keys:
			raise KeyError(key)
		elif self.is_controlled(key):
			vocabulary = self.get_vocabulary(key)
			if type(value) is list:
				self.store[key] = []
				for val in value:
					if val in vocabulary:
						self.store[key].append(val)
					else:
						raise VocabularyError(val)
			else:
				if value in vocabulary:
					self.store[key] = value
				else:
					raise VocabularyError(value)
		else:
			self.store[key] = value

###############################################################################

	def __delitem__(self, key: str):
		del self.store[key]

###############################################################################

	def __iter__(self):
		return iter(self.store)

###############################################################################

	def __len__(self):
		return len(self.store)

###############################################################################

	def __str__(self) -> str:
		entries = []
		for key in self.keys():
			R = " "
			C = " "
			value = ""
			if self.is_required(key):
				R = "R"
			if self.is_controlled(key):
				C = "C"
			if key in self.store:
				value = " = %s" % self.store[key]
			entry = " [%s%s] %s%s" % (R, C, key, value)
			entries.append(entry)

		format = \
			"_______________________________\n\n" \
			"    %s\n" \
			"_______________________________\n\n" \
			" [R: Required] [C: Controlled]\n" \
			"-------------------------------\n" \
			"%s\n" \
			"_______________________________\n" \
			% (self._name, "\n".join(entries))

		return format

###############################################################################

	def is_required(self, key: str) -> bool:
		return self._keys[key]["flags"] & self.REQUIRED

###############################################################################

	def is_controlled(self, key: str) -> bool:
		return self._keys[key]["flags"] & self.CONTROLLED

###############################################################################

	def get_field(self, key: str) -> str:
		return self._keys[key]["field"]

###############################################################################

	def get_vocabulary(self, key: str) -> dict:
		if self.is_controlled(key):
			return self._vocabulary[self.get_field(key)]
		else:
			msg = "Key [%s] is not controlled by a vocabulary!" % key
			raise CoscineException(msg)

###############################################################################

	def keys(self) -> list[str]:
		return self._keys.keys()

###############################################################################

	def reset(self):

		"""
		Resets the input form to default
		"""

		self.store.clear()

###############################################################################

	def parse(self, data: dict):
		pass

###############################################################################

	def generate(self):
		pass

###############################################################################

	def entry(self, field: str) -> dict:
		for item in self._entries:
			if item["field"] == field:
				return item
		return None

###############################################################################