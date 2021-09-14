import logging
import os
import PIL
import re

from sample.exif_data_utility import get_location_and_datetime

regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([' \
        r'0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?.*'
match_iso8601 = re.compile(regex).match


def _validate_iso8601(string_to_validate):
	try:
		if match_iso8601(string_to_validate) is not None:
			return True
	except re.error:
		pass
	return False


def rename_photos(photos_folder: str):
	"""Rename all photos in a folder.
	If the photo in question contains gps data and datetime it will be renamed to 'datetime-location'.
	If the photo contains only datetime and has not already been renamed by the software
	it will be renamed to 'datetime-original name'.
	Otherwise it will not be renamed.

		:param: photos_folder: The folder that contains the photos
		:type: photos_folder: str
	"""
	for photo_name in os.listdir(photos_folder):
		photo_absolute_path = os.path.join(photos_folder, photo_name)
		if os.path.isfile(photo_absolute_path):
			try:
				location_datetime = get_location_and_datetime(photo_absolute_path=photo_absolute_path)
				if 'datetime' in location_datetime:
					photo_filename_and_extension = os.path.splitext(photo_name)
					photo_datetime = location_datetime['datetime']
					try:
						location = location_datetime['location']
						os.rename(photo_absolute_path,
						          f"{photos_folder}/{photo_datetime}-"
						          f"{location}"
						          f"{photo_filename_and_extension[1]}")
					except KeyError:
						original_file_name = photo_filename_and_extension[0]
						if not _validate_iso8601(original_file_name):
							os.rename(photo_absolute_path,
							          f"{photos_folder}/{photo_datetime}-"
							          f"{original_file_name}"
							          f"{photo_filename_and_extension[1]}")
			except PIL.UnidentifiedImageError:
				logging.error(f"file extension of {photo_absolute_path} not supported!")
