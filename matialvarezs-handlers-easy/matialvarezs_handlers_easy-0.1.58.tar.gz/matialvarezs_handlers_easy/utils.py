from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as matialvarezs_handlers_easy_models
from . import errors as matialvarezs_handlers_easy_errors
from . import settings
import os, time, random
from json_response import JsonResponse
import math
from datetime import datetime
import arrow, pytz
from dateutil import tz as dateutil_tz

random_string = "39gZ8WrsglwTzbIO4HiRfL9OwAhMDIuq"

"""
def parse_model_attributes(**kwargs):
	attributes = {}
	
	return attributes

def create_model(**kwargs):

	for key, value in parse_model_attributes(**kwargs).items():
		kwargs[key] = value
	return h_utils.db_create(matialvarezs_handlers_easy_models.Model, **kwargs)

def get_model(**kwargs):
	return h_utils.db_get(matialvarezs_handlers_easy_models.Model, **kwargs)

def get_or_none_model(**kwargs):
	return h_utils.db_get_or_none(matialvarezs_handlers_easy_models.Model, **kwargs)

def filter_model(**kwargs):
	return h_utils.db_filter(matialvarezs_handlers_easy_models.Model, **kwargs)

def q_model(q, **otions):
	return h_utils.db_q(matialvarezs_handlers_easy_models.Model, q)

def delete_model(entry, **options):
	return h_utils.db_delete(entry)

def update_model(entry, **kwargs):
	attributes = {}
	for key, value in parse_model_attributes(**kwargs).items():
		attributes[key] = value
	return h_utils.db_update(entry, **attributes)
"""


def delete_db_object(db_object, **options):
    # method_delete => return object if exists or none
    message_ok_delete = options.get('message_ok_delete', 'delete ok')
    message_error_on_delete = options.get('message_error_on_delete', 'error on delete')
    if db_object:
        db_object.delete()
        return JsonResponse({"results": message_ok_delete, "error": None})
    return JsonResponse({"results": None, "error": message_error_on_delete})


def electrical_conductivity_to_25C_method_ratio_model(ce_value, temperature_value, **options):
    contant_value = options.get('contant_value', 0.02)
    return ce_value / (1 + contant_value * (temperature_value - 25))


def electrical_conductivity_to_25C_method_exponencial_model(ce_value, temperature_value):
    return ce_value * (0.4470 + 1.4034 * pow(math.e, (-1 * temperature_value / 26.815)))


def time_string_to_utc_datetime(time, timezone):
    date = datetime.now().date()
    time_formated = datetime.strptime(time, '%H:%M')
    date_to_convert = datetime.combine(date, time_formated.time())
    # tz = pytz.timezone(timezone)
    tz = dateutil_tz.gettz(timezone)
    datetime_to_arrow = arrow.get(date_to_convert, tz)
    return datetime_to_arrow.to('utc').datetime


def datetime_utc_to_localtime(datetime_utc, timezone):
    tz = pytz.timezone('utc')
    datetime_utc_to_arrow = arrow.get(datetime_utc, tz)
    return datetime_utc_to_arrow.to(timezone).datetime


def shift_datetime(datetime, **kwargs):
    return arrow.get(datetime).shift(**kwargs).datetime


def list_pytz_timezones():
    data = list()
    for tz in pytz.all_timezones:
        data.append({
            'tz': tz
        })
    return data


def round_decimal_point_5(x):
    frac, whole = math.modf(x)
    if frac >= 0.5:
        return math.ceil(x)
    else:
        return math.trunc(whole)


def format_chilean_int_point_and_coma(number):
    return "{:,}".format(number).replace(',', 'x').replace('.', ',').replace('x', '.')
