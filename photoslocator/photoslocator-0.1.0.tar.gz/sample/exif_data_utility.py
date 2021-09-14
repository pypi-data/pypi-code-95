import logging

from PIL import Image
import re
import unidecode
import functools
from geopy.geocoders import Nominatim
from typing import Dict

DATETIME_DECIMAL_IFD_TAG = 36867
DATETIME_DECIMAL_TIFF_TAG = 306

GPS_DECIMAL_IFD_TAG = 34853

NOMINATIM_GEO_LOCATOR = Nominatim(user_agent='photoslocator')


def _none_not_allowed(original_function):
	@functools.wraps(original_function)
	def new_function(*args, **kwargs):
		if None in args:
			raise ValueError("None is not a valid parameter")
		return original_function(*args, **kwargs)

	return new_function


def _gps_degrees_minutes_seconds_to_decimal(d, m, s):
	return d + float(m) / 60 + float(s) / 3600


def _get_longitude(gps_info: dict):
	return _gps_degrees_minutes_seconds_to_decimal(gps_info[4][0], gps_info[4][1], gps_info[4][2])


def _get_latitude(gps_info: dict):
	return _gps_degrees_minutes_seconds_to_decimal(gps_info[2][0], gps_info[2][1], gps_info[2][2])


@_none_not_allowed
def _get_datetime_iso8601(date_time_info: str):
	date_time_split = date_time_info.split(' ')
	return f"{date_time_split[0].replace(':', '-')}T{date_time_split[1]}"


@_none_not_allowed
def _get_location(gps_exif_information):
	try:
		latitude = _get_latitude(gps_exif_information)
		longitude = _get_longitude(gps_exif_information)
		location = re.sub('[^A-Za-z0-9,]+', '',
		                  unidecode.unidecode(
			                  NOMINATIM_GEO_LOCATOR.reverse(f"{latitude}, {longitude}", zoom=14).address)).split(',')
		return f"{location[0]}_{location[1]}"
	except Exception:
		logging.error(f"Exception during coordinate parsing")
		raise ValueError


def get_location_and_datetime(photo_absolute_path: str) -> Dict[str, str]:
	"""Returns a dictionary that can contain the location, date and time the photo was taken

	:param: photo_absolute_path: The absolute path of the photo of which informations is needed
	:type: photo_absolute_path: str
	:return: a dictionary that can contain location and datetime (under location and datetime keys)
	:rtype: Dict
	:raises ValueError: the given file is not supported
	"""
	with Image.open(photo_absolute_path) as photo:
		exif_data = photo._getexif()
		location_datetime = {}
		if exif_data:
			gps_exif_information = exif_data.get(GPS_DECIMAL_IFD_TAG)
			date_time_exif_information = exif_data.get(
				DATETIME_DECIMAL_IFD_TAG) if DATETIME_DECIMAL_IFD_TAG in exif_data else exif_data.get(
				DATETIME_DECIMAL_TIFF_TAG)
			try:
				location = _get_location(gps_exif_information)
				location_datetime['location'] = location
			except ValueError:
				logging.warning("GPS exif data unavailable or not formatted correctly")
				pass
			try:
				date_time = _get_datetime_iso8601(date_time_exif_information)
				location_datetime['datetime'] = date_time
			except ValueError:
				logging.warning("Original date and time exif data unavailable")
				pass
		return location_datetime
