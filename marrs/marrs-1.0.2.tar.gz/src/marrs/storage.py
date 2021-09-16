import os
from os import path
from pathlib import Path

import appdirs

from .consts import PACKAGE_NAME, STORAGE_TMP_DIR_NAME
from .log import debug
from .utils import copy_file_with_dir_creation, get_filename, delete_folder, get_temp_name


class Storage:
	STORAGE_DIR_PATH = str(Path(appdirs.user_data_dir(appname=PACKAGE_NAME)))

	@staticmethod
	def get_folder_path():
		return Storage.STORAGE_DIR_PATH

	@staticmethod
	def set_folder_path(storage_dir_path):
		Storage.STORAGE_DIR_PATH = storage_dir_path

	@staticmethod
	def _get_path(filename):
		return path.join(Storage.STORAGE_DIR_PATH, filename)

	@staticmethod
	def contains(filename):
		return Storage.get(filename) is not None

	@staticmethod
	def get(filename):
		filepath = Storage._get_path(filename)
		if path.exists(filepath):
			return filepath

		return None

	@staticmethod
	def delete():
		delete_folder(Storage.STORAGE_DIR_PATH)

	@staticmethod
	def get_temp_dir_path():
		return path.join(Storage.STORAGE_DIR_PATH, STORAGE_TMP_DIR_NAME)

	@staticmethod
	def delete_temp_dir():
		delete_folder(Storage.get_temp_dir_path())

	@staticmethod
	def create_temp_dir():
		tmp_dir_path = path.join(Storage.get_temp_dir_path(), get_temp_name())
		os.makedirs(tmp_dir_path)
		return tmp_dir_path

	@staticmethod
	def save(src_file_path, filename=None):
		if not filename:
			filename = get_filename(src_file_path)

		dest_file_path = Storage._get_path(filename)

		debug("Saving file to local storage: {0}".format(dest_file_path))
		copy_file_with_dir_creation(src_file_path, dest_file_path)
