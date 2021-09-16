# -*- coding: utf-8 -*-
""" ai._conf """
import os
import json
import yaml
from configparser import ConfigParser


class AttrDict(dict):
	def __init__(self, *args, **kwargs):
		super(AttrDict, self).__init__(*args, **kwargs)
		self.__dict__ = self


def get_yaml(path):
	""" 使用 .yaml 文件配置
	"""
	return AttrDict(yaml.load(open(path, 'r', encoding="UTF-8"), Loader=yaml.FullLoader))


def get_conf(path):
	""" 使用 ._conf 文件配置
	"""
	_conf = ConfigParser()
	_conf.read(path, encoding="UTF-8")
	return _conf


def get_json(path):
	""" 使用 .json 文件配置
	"""
	return json.load(open(path, 'r', encoding="UTF-8"))


class Dict(dict):
	""" 重写 dict, 支持通过 “.” 调用带参数 key 的 __call__ 方法
		用于实例自身的调用, 达到 () 调用的效果
	"""
	def __init__(self, *args, **kwargs):
		super(Dict, self).__init__(*args, **kwargs)

	def __getattr__(self, key):
		try:
			value = self[key]
			if isinstance(value, dict):
				value = Dict(value)
			return value
		except KeyError as k:
			return None

	def __setattr__(self, key, value):
		if isinstance(value, dict):
			value = Dict(value)
		self[key] = value

	def __delattr__(self, key):
		try:
			del self[key]
		except KeyError as k:
			return None

	def __call__(self, key):
		try:
			return self[key]
		except KeyError as k:
			return None


class Config(object):
	""" 链式配置
	"""
	def __init__(self, filepath=None):
		if filepath:
			self.path = filepath
		else:
			cur_dir = os.path.split(os.path.realpath(__file__))[0]
			self.path = os.path.join(cur_dir, "self._conf")
		self._conf = get_conf(self.path)
		self._d = Dict()
		for s in self._conf.sections():
			value = Dict()
			for k in self._conf.options(s):
				value[k] = self._conf.get(s, k)
			self._d[s] = value

	def add(self, section):
		self._conf.add_section(section)
		self._d[section] = Dict()
		with open(self.path, 'w', encoding="UTF-8") as f:
			self._conf.write(f)

	def set(self, section, k, v):
		self._conf.set(section, k, v)
		self._d[section][k] = v
		with open(self.path, 'w', encoding="UTF-8") as f:
			self._conf.write(f)

	def get(self, section, key):
		return self._conf.get(section, key, default=None)

	def remove_section(self, section):
		self._conf.remove_section(section)
		del self._d[section]
		with open(self.path, 'w', encoding="UTF-8") as f:
			self._conf.write(f)

	def remove_option(self, section, key):
		self._conf.remove_option(section, key)
		del self._d[section][key]
		with open(self.path, 'w', encoding="UTF-8") as f:
			self._conf.write(f)

	def save(self):
		for s in self._d:
			if s not in self._conf.sections():
				self.add(s)
			for k in self._d[s]:
				try:
					v = self.get(s, k)
				except:
					v = None
				if self._d[s][k] != v:
					self.set(s, k, self._d[s][k])

	def __getattr__(self, name):
		if name not in self.__dict__:
			try:
				return self._d[name]
			except KeyError as k:
				self._d[name] = Dict()
				return self._d[name]
		return self.__dict__[name]