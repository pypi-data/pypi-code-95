import copy
import datetime
import sys

from geoformat.conf.format_data import value_to_iterable_value, is_hexadecimal

from geoformat.conversion.fields_conversion import (
    drop_field,
    recast_field
)
from geoformat.conversion.metadata_conversion import (
    geometries_scan_to_geometries_metadata,
    fields_scan_to_fields_metadata
)
from geoformat.conversion.geometry_conversion import (
    geometry_to_wkb,
    wkb_to_geometry,
    geometry_to_bbox,
    geometry_to_geometry_collection
)
from geoformat.geoprocessing.connectors.predicates import bbox_intersects_bbox
from geoformat.geoprocessing.geoparameters.bbox import bbox_union


def feature_serialize(feature):
    """
    Serialize feature.
        "attributes" are converted to string. TODO serialize in bytes.
        "geometry' are converted to WKB.

    :param feature: feature that we want to convert
    :return: feature serialized
    """
    serialized_feature = {}
    if 'attributes' in feature:
        serialized_feature["attributes"] = str(feature['attributes'])

    if 'geometry' in feature:
        serialized_feature["geometry"] = geometry_to_wkb(feature['geometry'])

    return serialized_feature


def feature_deserialize(serialized_feature, bbox=True):
    """
    Convert serialized feature to non serialized feature

    :param serialized_feature: feature serialized
    :param bbox: True if you want to add bbox information geometry key
    :return: non serialized geometry
    """
    feature = {}
    if "attributes" in serialized_feature:
        attributes = eval(serialized_feature["attributes"])
        feature["attributes"] = attributes
    if "geometry" in serialized_feature:
        geometry = wkb_to_geometry(serialized_feature["geometry"], bbox=bbox)
        feature["geometry"] = geometry

    return feature


def features_geometry_ref_scan(
        geolayer_or_feature_list,
        geometry_type_filter=None,
        bbox_filter=None,
        extent=True
):
    """
    Loop on each features on a geolayer or a list and deduce geometries metadata from it.

    :param geolayer_or_feature_list: geolayer or features list to scan
    :param geometry_type_filter: filter on geolayer_or_feature_list only geometry type sepcified on this variable
           (can be a list)
    :param bbox_filter: filter on features geometry that intersects bbox (can be a list)
    :param extent: if True add geolayer extent to geometry metadata
    :return: geometry scan result
    """
    # init
    geometry_type_filter = value_to_iterable_value(geometry_type_filter, set)
    if isinstance(bbox_filter, (list, tuple)):
        if isinstance(bbox_filter[0], (int, float)):
            bbox_filter = [bbox_filter]
    bbox_filter = value_to_iterable_value(bbox_filter, set)
    geometry_type_set = set([])

    # check if input data is geolayer or feature
    if isinstance(geolayer_or_feature_list, list):
        is_geolayer = False
        feature_list = geolayer_or_feature_list
    elif isinstance(geolayer_or_feature_list, dict):
        is_geolayer = True
        feature_list = geolayer_or_feature_list["features"]
    else:
        raise Exception('geolayer_or_feature_list must be a list of features or')

    extent_value = None
    for i, feature in enumerate(feature_list):
        if is_geolayer:
            feature = geolayer_or_feature_list["features"][feature]

        # check if geometry
        if "geometry" in feature:
            geometry = feature["geometry"]
            # get geometry type
            geometry_type = geometry['type']

            # check geometry type
            if geometry_type_filter:
                # if geometry not in geometry_type_filter we loop on next feature
                if geometry_type not in geometry_type_filter:
                    continue

            # check bbox
            if bbox_filter:
                if "bbox" in geometry:
                    feature_bbox = geometry['bbox']
                else:
                    feature_bbox = geometry_to_bbox(geometry)

                geometry_in_bbox = False
                # loop on each bbox from bbox_filter
                for bbox in bbox_filter:
                    if bbox_intersects_bbox(bbox, feature_bbox):
                        geometry_in_bbox = True
                        break

                # if geometry not in bbox we loop on next feature
                if geometry_in_bbox is False:
                    continue

            # add geometry type in geometry_type_set
            geometry_type_set.update([geometry_type])

            # if extent option in True
            if extent:
                if 'bbox' in feature:
                    bbox = feature['bbox']
                else:
                    bbox = geometry_to_bbox(geometry)
                # compute extent
                if extent_value:
                    extent_value = bbox_union(bbox, extent_value)
                else:
                    extent_value = bbox

    # create geometry ref metadata dict
    if not geometry_type_set:
        geometry_type_set = None

    geometry_return = {'type': geometry_type_set, 'extent': extent_value}

    return geometry_return


def check_if_value_is_from_datetime_lib(datetime_type, value, try_to_force):
    """
    Return True if value is instance of indicated datetime_type

    :param datetime_type: datetime type that we want test
    :param value: value to test
    :param try_to_force: True if you want force input value
    :return: True / False
    """

    if isinstance(value, datetime_type):
        return_value = True
    else:
        return_value = False

    if try_to_force is True and return_value is False:
        if sys.version_info >= (3, 7):
            try:
                value_from_isoformat = datetime_type.fromisoformat(value)
                if value_from_isoformat:
                    return_value = True

            except (ValueError, TypeError):
                return_value = False
        else:
            return_value = False

    return return_value


def check_if_value_is_date(value, try_to_force):
    """
    check if value is date type

    :param value: value to test
    :param try_to_force: True if you want to force value to datetime type date
    :return:
    """
    return check_if_value_is_from_datetime_lib(datetime_type=datetime.date, value=value, try_to_force=try_to_force)


def check_if_value_is_datetime(value, try_to_force):
    """
    check if value is datetime type

    :param value: value to test
    :param try_to_force: True if you want to force value to datetime type datetime
    :return:
    """
    return check_if_value_is_from_datetime_lib(datetime_type=datetime.datetime, value=value, try_to_force=try_to_force)


def check_if_value_is_time(value, try_to_force):
    """
    check if value is datetime time

    :param value: value to test
    :param try_to_force: True if you want to force value to datetime type time
    :return:
    """
    return check_if_value_is_from_datetime_lib(datetime_type=datetime.time, value=value, try_to_force=try_to_force)


def return_if_value_is_time_date_or_datetime(value, try_to_force):
    """
    Determine if value is date / time or datetime returns None if none of the this cases.

    :param value: value to test
    :param try_to_force: True if you want to force value to datetime type
    :return: datetime type (date / time or datetime).
    """

    if isinstance(value, (datetime.date, datetime.time, datetime.datetime)):
        return_value = type(value)
    else:
        is_date = check_if_value_is_date(value=value, try_to_force=try_to_force)
        is_time = check_if_value_is_time(value=value, try_to_force=try_to_force)
        is_datetime = check_if_value_is_datetime(value=value, try_to_force=try_to_force)

        if is_date is False and is_time is False and is_datetime is True:
            # datetime is compatible with date (that why we don't test it).
            return_value = datetime.datetime
        elif is_date is True and is_time is False and is_datetime is True:
            return_value = datetime.date
        elif is_date is False and is_time is True and is_datetime is False:
            return_value = datetime.time
        elif is_date is True and is_time is False and is_datetime is False:
            return_value = datetime.date
        else:
            return_value = None

    return return_value


def features_fields_type_scan(
        geolayer_or_feature_list,
        field_name_filter=None,
        try_to_force_type=False,
        fields_index=True
):
    """
    Loop on each features on a geolayer or a list and deduce fields metadata from it.

    :param geolayer_or_feature_list: geolayer_or_feature_list: geolayer or features list to scan
    :param field_name_filter: filter only on sprecified field_name (can be a list)
    :param try_to_force_type: option that can force the Type of value on geolayer or features list
    :param fields_index: if True add field index position on field_name contians in geolayer or features list
    :return: fields scan result
    """

    def define_field_type(field_dict, field_value, field_try_to_force_type=False):
        """
        Return from a given list deduce type of data's in it.
        To work this function need field dict that is the summary of all data type for the field

        TODO : big refacto to do here :
                - work with sub-functions by field type (which takes try_to_force as parameter)

        :param field_dict: field's dictionary that type you want to know
        :param field_value: value_to_force in field
        :param field_try_to_force_type:
        :return: return edited field_dict with parameters that we deduce from field_value
        """

        def force_value(value_to_force, force_type):
            """
            This function force a given value to an other type.
            If type is incompatible function return None

            :param value_to_force: value to recast
            :param force_type:  type that we want to recast value
            :return: new value
            """

            try:
                forced_value = force_type(value_to_force)
                return forced_value
            except ValueError:
                return None
            except TypeError:
                return None

        # init variable
        values_in_list = False
        values_out_list = False

        if isinstance(field_value, (list, tuple, set)):
            values_in_list = True
            values_list = field_value
            if field_dict['field_width_list']:
                if len(str(field_value)) > field_dict['field_width_list']:
                    field_dict['field_width_list'] = len(str(field_value))
            else:
                field_dict['field_width_list'] = len(str(field_value))
        else:
            values_out_list = True
            values_list = [field_value]

        # loop on each value_to_force in list
        for value in values_list:
            # test if is None if try to force is True
            if field_try_to_force_type is True:
                if isinstance(value, str):
                    if value == '' or value.upper() == 'NULL' or value.upper() == 'NONE':
                        value = None
            # check if value is None
            if value is None:
                field_dict["none_value"] = True
            # if value is not None
            else:
                field_dict["not_none_value"] = True
                # determine value_to_force type
                value_type = type(value)
                field_dict['native_type'].update({value_type})
                test_hexadecimal = True
                # if try to force activate
                if field_try_to_force_type is True:
                    # we try to deduce if value_to_force is a list
                    iterable_value = False
                    if isinstance(value, str):
                        try:
                            eval_value = eval(value)
                            if isinstance(eval_value, (list, tuple, set)):
                                values_in_list = True
                                values_out_list = False
                                saving_native_type = set(field_dict['native_type'])
                                field_dict = define_field_type(field_dict=field_dict,
                                                               field_value=eval_value,
                                                               field_try_to_force_type=field_try_to_force_type)
                                # restore native type
                                field_dict['native_type'] = saving_native_type
                                iterable_value = True

                            if isinstance(eval_value, bytes):
                                field_dict['tmp_field_type'].update({bytes})
                                # we do not need to test hexadecimal for this value
                                test_hexadecimal = False

                            # for this two new value_to_force recast is necessary
                            field_dict['field_recast'] = True
                            float_value = None

                        except SyntaxError:
                            pass
                        except ValueError:
                            pass
                        except NameError:
                            pass

                    # if not iterable we can deduce type
                    if not iterable_value:
                        if isinstance(value, bool):
                            field_dict["tmp_field_type"].update({bool})
                            float_value = None
                        else:
                            # if not float try to force in float
                            if value_type != float:
                                float_value = force_value(value, float)
                                if float_value is None:
                                    field_dict["tmp_field_type"].update({float})
                            else:
                                float_value = value
                            # try to int
                            int_value = force_value(value, int)
                            if int_value is None:
                                field_dict["tmp_field_type"].update({int})
                            # if there is a difference between float and int value_to_force then value_to_force cannot
                            # be int
                            elif abs(float_value - int_value) != 0:
                                field_dict["tmp_field_type"].update({int})

                            # for bytes value
                            if value_type is bytes:
                                field_dict["tmp_field_type"].update({bytes})

                # if not try to force
                else:
                    # str
                    if isinstance(value, str):
                        field_dict["tmp_field_type"].update({str})
                    # float
                    elif isinstance(value, float):
                        field_dict["tmp_field_type"].update({float})
                    # int
                    elif isinstance(value, int):
                        # if bool
                        if isinstance(value, bool):
                            field_dict["tmp_field_type"].update({bool})
                        else:
                            field_dict["tmp_field_type"].update({int})

                    # bytes
                    elif isinstance(value, bytes):
                        field_dict["tmp_field_type"].update({bytes})
                    # iterable for iterable values in iterable values
                    if isinstance(value, (list, tuple, set)):
                        values_in_list = True
                        values_out_list = False
                        field_dict = define_field_type(field_dict=field_dict,
                                                       field_value=value,
                                                       field_try_to_force_type=field_try_to_force_type)

                # test if value is Date / Time or DateTime
                date_type = return_if_value_is_time_date_or_datetime(value=value, try_to_force=try_to_force_type)
                if date_type:
                    field_dict["tmp_field_type"].update({date_type})

                # define if str is always hexadecimal
                if isinstance(value, str) and not date_type:
                    if (field_dict['str_is_always_hexadecimal'] is None or field_dict[
                        'str_is_always_hexadecimal'] is True) and test_hexadecimal is True:
                        field_dict['str_is_always_hexadecimal'] = is_hexadecimal(value)
                    field_dict["tmp_field_type"].update({str})

                # Define width
                width_value = len(str(value))
                if width_value > field_dict["field_width_str"]:
                    field_dict["field_width_str"] = width_value

                # Define precision and modify with if necessary
                if field_try_to_force_type is False:
                    float_value = value
                if isinstance(float_value, float):
                    value_split = str(value).split(".")
                    if len(value_split) == 2:
                        before_comma_value, after_comma_values = value_split
                    else:
                        before_comma_value = value_split[-1]
                        after_comma_values = '0'

                    if after_comma_values == '0':
                        width_after_comma = 0
                    else:
                        width_after_comma = len(after_comma_values)

                    if before_comma_value == '0':
                        width_before_comma = 0
                    else:
                        width_before_comma = len(before_comma_value)

                    if width_after_comma > field_dict["field_precision"]:
                        field_dict["field_precision"] = width_after_comma
                        field_dict["width_after_comma"] = width_after_comma

                    if width_before_comma > field_dict["width_before_comma"]:
                        field_dict["width_before_comma"] = width_before_comma

                    # update width
                    if field_dict["width_before_comma"] + field_dict["width_after_comma"] > field_dict["field_width_float"]:
                        field_dict["field_width_float"] = field_dict["width_before_comma"] + field_dict["width_after_comma"]

            # if list or not
            if values_in_list is True and field_dict["values_in_list"] is False:
                field_dict["values_in_list"] = True

            if values_out_list is True and field_dict["values_out_list"] is False:
                field_dict["values_out_list"] = True

        return field_dict

    def loop_on_each_features(
        _geolayer_or_feature_list,
        _is_geolayer,
        _scan_field_name_for_each_feature,
        _field_name_list,
        _try_to_force_type
    ):
        """
        Loop on each feature (in feature_list or geolayer).

        :param _geolayer_or_feature_list: list of all features or geolayer
        :param _is_geolayer: True if _feature_list is geolayer / False if feature_list.
        :param _scan_field_name_for_each_feature: is True all field name in features will be scan.
        :param _field_name_list: field name list that we want to scan on geolayer or feature list.
        :param _try_to_force_type: option that can force the Type of value on geolayer or features list.
        :return: result from fields scan of each features
        """

        # init output values
        fields_scan = {}
        field_index = 0
        fields_name_set = set()

        # loop on each features
        for i, feature in enumerate(_geolayer_or_feature_list):
            if _is_geolayer:
                feature = geolayer_or_feature_list["features"][feature]
            if "attributes" in feature:
                # if we loop on each field in feature, we get all fields in feature
                if _scan_field_name_for_each_feature:
                    _field_name_list = feature["attributes"].keys()

                # we loop on feature's fields
                # if field does not exists in fields_name_set we create it enter in fields_scan
                for i_field, field_name_filter in enumerate(_field_name_list):
                    # first apparition initialise dico
                    if field_name_filter not in fields_name_set:
                        fields_name_set.update({field_name_filter})
                        fields_scan[field_name_filter] = {
                            "values_in_list": False,
                            "values_out_list": False,
                            "field_list": False,
                            "tmp_field_type": set(),
                            "field_type": None,
                            "field_width_str": 0,
                            "field_width_list": None,
                            "field_precision": 0,
                            "none_value": False,
                            "not_none_value": False,
                            "field_index": field_index,
                            "field_recast": False,
                            "native_type": set(),
                            "force_type": False,
                            "str_is_always_hexadecimal": None,
                            "field_width_float": 0,
                            "width_before_comma": 0,
                            "width_after_comma": 0,
                        }
                        # if we create a new field_name in dict not at first feature that means
                        # that for the previous entities the value of the field was None.
                        if i != 0:
                            fields_scan[field_name_filter]['none_value'] = True
                        if _try_to_force_type is True:
                            fields_scan[field_name_filter]['force_type'] = True
                        # save field field_index
                        field_index += 1

                    # if field_name is in feature we deduce type of field value
                    if field_name_filter in feature["attributes"]:
                        feature_field_value = feature["attributes"][field_name_filter]
                        fields_scan[field_name_filter] = define_field_type(field_dict=fields_scan[field_name_filter],
                                                                           field_value=feature_field_value,
                                                                           field_try_to_force_type=_try_to_force_type)
                    else:
                        fields_scan[field_name_filter]['none_value'] = True

                # test if missing field name
                if _scan_field_name_for_each_feature:
                    missing_field_name_set = (fields_name_set.difference(_field_name_list))
                    if missing_field_name_set:
                        for missing_field_name in missing_field_name_set:
                            fields_scan[missing_field_name]['none_value'] = True

        return fields_scan

    def deduce_fields_type_from_raw_metadata(_feature_list_fields_scan, _try_to_force_type):
        """
        From raw metadata result deduce field type.

        :param _feature_list_fields_scan: raw metadata dict
        :param _try_to_force_type: True if you want force type value
        :return: raw metadata dict with feature type in it.
        """
        # deduce output field type
        for _field_name_filter in _feature_list_fields_scan:
            feature_tmp_field_type = _feature_list_fields_scan[_field_name_filter].get('tmp_field_type', None)
            if _try_to_force_type is True:
                # WARNING
                # When _try_to_force_type is TRUE
                # types stored in 'tmp_field_type' can contains types that are NOT compatible with data thus we
                # can DEDUCE the type.
                if feature_tmp_field_type:
                    str_force = True
                    field_type_set = {}
                    # numeric fields (float and int)
                    if float not in feature_tmp_field_type and int in \
                            feature_tmp_field_type:
                        field_type_set = {float}
                        str_force = False

                    if int not in feature_tmp_field_type:
                        field_type_set = {int}
                        _feature_list_fields_scan[_field_name_filter]['field_precision'] = 0
                        str_force = False

                    # bytes
                    if bytes in feature_tmp_field_type and float in \
                            _feature_list_fields_scan[_field_name_filter][
                                'tmp_field_type'] and int in _feature_list_fields_scan[_field_name_filter][
                        'tmp_field_type']:
                        # if there is other type in 'tmp_field_type' it must be str else we force to str
                        if feature_tmp_field_type - {int, float, bytes} == {
                            str} or feature_tmp_field_type - {int, float,
                                                                                                       bytes} == set():
                            # if str is always hexadecimal then it's a bytes valid
                            if str in feature_tmp_field_type and \
                                    _feature_list_fields_scan[_field_name_filter]['str_is_always_hexadecimal'] is False:
                                str_force = True
                            else:
                                field_type_set = {bytes}
                                str_force = False
                        else:
                            str_force = True
                    # bytes 2 (if data is only hexadecimal but not integer only)
                    if feature_tmp_field_type - {float, str, int} == set() and \
                            _feature_list_fields_scan[_field_name_filter][
                                'str_is_always_hexadecimal'] is True and int not in field_type_set:
                        field_type_set = {bytes}
                        str_force = False

                    # datetime / date and time and bool
                    # create temp_field_type variable
                    if {bool, datetime.date, datetime.time, datetime.datetime}.intersection(feature_tmp_field_type):
                        date_time_datetime_and_bool = feature_tmp_field_type - {int, float}
                        temp_field_type_for_date_time_datetime_and_bool = date_time_datetime_and_bool.difference({bool, datetime.date, datetime.time, datetime.datetime})
                        if len(temp_field_type_for_date_time_datetime_and_bool) == 0:
                            # if one type
                            if len(date_time_datetime_and_bool) == 1:
                                field_type_set = date_time_datetime_and_bool
                                str_force = False
                            else:
                                # if bool we must recast field to str
                                if bool in date_time_datetime_and_bool:
                                    field_type_set = date_time_datetime_and_bool
                                    str_force = True
                                else:
                                    # if time / date and datetime (no compatibility we force to str)
                                    if len(date_time_datetime_and_bool) == 3:
                                        field_type_set = date_time_datetime_and_bool
                                        str_force = True
                                    else:
                                        if date_time_datetime_and_bool == {datetime.datetime, datetime.date}:
                                            field_type_set = {datetime.datetime}
                                            str_force = False
                                        else:
                                            field_type_set = date_time_datetime_and_bool
                                            str_force = True

                    # define if value in list must be forced to str
                    if _feature_list_fields_scan[_field_name_filter]['values_in_list'] is True and \
                            _feature_list_fields_scan[_field_name_filter]['values_out_list'] is True:
                        str_force = True

                    # force in str
                    if str_force is True:
                        field_type_set = {str}

                    feature_tmp_field_type = field_type_set

                else:
                    # for  integer value
                    if _feature_list_fields_scan[_field_name_filter]['not_none_value'] is True:
                        feature_tmp_field_type = {int}
                        _feature_list_fields_scan[_field_name_filter]['field_precision'] = 0

            # if try_to_force is False
            else:
                if len(feature_tmp_field_type) > 1:
                    _feature_list_fields_scan[_field_name_filter]['field_recast'] = True

                    if str in feature_tmp_field_type:
                        feature_tmp_field_type = {str}
                    else:
                        datetime_set = {datetime.date, datetime.time, datetime.datetime}
                        # boolean or integer
                        if bool in feature_tmp_field_type and int in feature_tmp_field_type:
                            feature_tmp_field_type = {str}
                        # float
                        elif float in feature_tmp_field_type and int in feature_tmp_field_type and len(feature_tmp_field_type) == 2:
                            feature_tmp_field_type = {float}

                        # date / time / datetime
                        elif len(feature_tmp_field_type.difference(datetime_set)) == 0:
                            date_time_datetime_and_bool = feature_tmp_field_type.intersection(datetime_set)
                            # if time / date and datetime (no compatibility we force to str)
                            if len(date_time_datetime_and_bool) == 3:
                                datetime_field_type = {str}
                            else:
                                if date_time_datetime_and_bool == {datetime.datetime, datetime.date}:
                                    datetime_field_type = {datetime.datetime}
                                else:
                                    datetime_field_type = {str}
                            feature_tmp_field_type = datetime_field_type
                        else:
                            feature_tmp_field_type = {str}

            _feature_list_fields_scan[_field_name_filter]['tmp_field_type'] = feature_tmp_field_type

        # Rescan all fields data and determine :
        # - deduce final type of data in field and delete field with only None value
        # - are on a list (only for str / int / float data)

        # write final type field and delete field with only None value ('reindex other field is necessary')
        for _field_name_filter, field_name_dict in _feature_list_fields_scan.items():
            # determine field type
            if field_name_dict['tmp_field_type']:
                field_type = list(field_name_dict['tmp_field_type'])[0]
                field_name_dict['field_type'] = field_type
            else:
                # for none type field
                field_name_dict['field_delete'] = True

        # list
        for _field_name_filter, field_name_dict in _feature_list_fields_scan.items():
            type_list = False
            if field_name_dict['field_type'] in {str, int, float}:
                if field_name_dict['values_in_list'] is True and field_name_dict['values_out_list'] is False:
                    type_list = True

            field_name_dict['field_list'] = type_list

        return _feature_list_fields_scan

    def check_field_to_delete(_feature_list_fields_scan):
        """
        Scan field scan result : add key 'field_delete' and deduce if field must be deleted or not

        :param _feature_list_fields_scan: fields scan dict
        :return: _feature_list_fields_scan with 'field_delete' key
        """
        for _field_name_filter, _field_name_dict in _feature_list_fields_scan.items():
            _field_name_dict['field_delete'] = False
            if _field_name_dict['none_value'] is True and _field_name_dict['not_none_value'] is False:
                _field_name_dict['field_delete'] = True

        return _feature_list_fields_scan

    def check_field_to_recast(_feature_list_fields_scan):
        """
        Scan field scan result : update key 'field_recast' and deduce if field must be recast or not

        :param _feature_list_fields_scan: fields scan dict
        :return:  _feature_list_fields_scan with 'field_recast' updated
        """

        # determine if field must be recast
        for _field_name_filter, _field_name_dict in _feature_list_fields_scan.items():
            if len(_field_name_dict['native_type']) > 1 or \
                    _field_name_dict['native_type'] != _field_name_dict['tmp_field_type']:
                _field_name_dict['field_recast'] = True
            if _field_name_dict['field_type'] in {str, int, float}:
                if _field_name_dict['values_in_list'] is True and _field_name_dict['values_out_list'] is True:
                    _field_name_dict['field_recast'] = True
            else:
                if _field_name_dict['values_in_list'] is True:
                    raise Exception("field {field_name} : field_type must be change to str".format(
                        field_name=_field_name_filter))

        return _feature_list_fields_scan

    # init input values
    # check if input data is geolayer or feature
    if isinstance(geolayer_or_feature_list, list):
        is_geolayer = False
        feature_list = geolayer_or_feature_list
    elif isinstance(geolayer_or_feature_list, dict):
        is_geolayer = True
        feature_list = geolayer_or_feature_list["features"]
    else:
        raise Exception('geolayer_or_feature_list must be a list of features or a Geolayer')

    scan_field_name_for_each_feature = True
    if field_name_filter:
        scan_field_name_for_each_feature = False
        field_name_list = value_to_iterable_value(field_name_filter, list)
    else:
        field_name_list = None

    # loop on each features and get raw metadata
    feature_list_fields_scan = loop_on_each_features(
        _geolayer_or_feature_list=feature_list,
        _is_geolayer=is_geolayer,
        _scan_field_name_for_each_feature=scan_field_name_for_each_feature,
        _field_name_list=field_name_list,
        _try_to_force_type=try_to_force_type
    )

    # from raw metadata deduce field type
    feature_list_fields_scan = deduce_fields_type_from_raw_metadata(
        _feature_list_fields_scan=feature_list_fields_scan,
        _try_to_force_type=try_to_force_type
    )

    # check if field(s) must be delete
    feature_list_fields_scan = check_field_to_delete(_feature_list_fields_scan=feature_list_fields_scan)
    # check if field(s) must be recast or not
    feature_list_fields_scan = check_field_to_recast(_feature_list_fields_scan=feature_list_fields_scan)

    # clean output
    for field_name_filter, field_name_dict in feature_list_fields_scan.items():
        del field_name_dict['tmp_field_type']
        if fields_index is False:
            del field_name_dict['field_index']

    return feature_list_fields_scan


def feature_list_to_geolayer(
    feature_list,
    geolayer_name,
    field_name_filter=None,
    force_field_conversion=False,
    geometry_type_filter=None,
    bbox_filter=None,
    bbox_extent=True,
    crs=None,
    serialize=False
):
    """
    Create a geolayer with an input feature list.

    :param feature_list: features list that we want to transform to geolayer.
    :param geolayer_name: name for geolayer.
    :param field_name_filter: field_name that we want to keep in geolayer (can be a list).
    :param force_field_conversion: True if you want to force value in field (can change field type) / False if you want
           to deduce field type without forcing field type.
    :param geometry_type_filter: keep only features with geometry type in this variable (can be a list).
    :param bbox_filter: keep only feature that intersects bbox (can be a list of bbox).
    :param bbox_extent: add "bbox" key in each features and "extent" key in geometry metadata.
    :param crs: coordinates spatial reference for geolayer.
    :param serialize: True if features in geolayer are serialized (can reduce performance) / False if not.
    :return: Return geolayer that contains features in feature_list depending on the options specified at the start
    of this function.
    """
    # initialize input variable
    feature_list = value_to_iterable_value(feature_list, list)
    field_name_filter = value_to_iterable_value(field_name_filter, list)
    geometry_type_filter = value_to_iterable_value(geometry_type_filter, list)
    if isinstance(bbox_filter, (list, tuple)):  # TODO remove when bbox will be an object
        if isinstance(bbox_filter[0], (int, float)):  # TODO remove when bbox will be an object
            bbox_filter = [bbox_filter]
    bbox_filter = value_to_iterable_value(bbox_filter, set)

    # initialize output variable
    # create empty _geolayer
    _geolayer = {
        "metadata": {
            "name": geolayer_name
        },
        "features": {

        }
    }

    # metadata
    # get fields metadata
    features_fields_scan = features_fields_type_scan(
        geolayer_or_feature_list=feature_list,
        field_name_filter=field_name_filter,
        try_to_force_type=force_field_conversion,
        fields_index=True
    )
    geolayer_fields_metadata = fields_scan_to_fields_metadata(
        fields_scan=features_fields_scan
    )

    # get geometry metadata
    features_geometries_scan = features_geometry_ref_scan(
        geolayer_or_feature_list=feature_list,
        geometry_type_filter=geometry_type_filter,
        bbox_filter=bbox_filter,
        extent=bbox_extent
    )
    geolayer_geometry_metadata = geometries_scan_to_geometries_metadata(
        geometry_scan=features_geometries_scan,
        crs=crs,
        extent=bbox_extent
    )

    # add metadata to _geolayer
    if geolayer_fields_metadata:
        _geolayer['metadata']['fields'] = geolayer_fields_metadata
    if geolayer_geometry_metadata:
        _geolayer['metadata']['geometry_ref'] = geolayer_geometry_metadata
    if serialize is True:
        _geolayer['metadata']['feature_serialize'] = True

    # add feature to _geolayer
    i_feat = 0

    for feature in feature_list:
        feature = feature_filter(
            feature=feature,
            field_name_filter=field_name_filter,
            geometry_type_filter=geometry_type_filter,
            bbox_filter=bbox_filter,
            bbox=bbox_extent
        )
        # if feature
        if feature:
            # if feature must be serialized
            if serialize:
                feature = feature_serialize(feature)
            _geolayer['features'][i_feat] = feature
            i_feat += 1

    # drop field if necessary
    if geolayer_fields_metadata:
        for field_name, field_dict in features_fields_scan.items():
            if field_dict['field_delete'] is True:
                _geolayer = drop_field(geolayer=_geolayer, field_name_to_drop=field_name)

    # recast field if necessary
    if geolayer_fields_metadata:
        for field_name, field_dict in features_fields_scan.items():
            if field_dict['field_recast'] is True:
                # define type to recast
                recast_to_type = _geolayer['metadata']['fields'][field_name]['type']
                # resize width to recast
                resize_width = None
                if 'width' in _geolayer['metadata']['fields'][field_name]:
                    resize_width = _geolayer['metadata']['fields'][field_name]['width']
                # resize precision to recast
                resize_precision = None
                if 'precision' in _geolayer['metadata']['fields'][field_name]:
                    resize_precision = _geolayer['metadata']['fields'][field_name]['precision']
                # recast field in _geolayer
                _geolayer = recast_field(
                    geolayer_to_recast=_geolayer,
                    field_name_to_recast=field_name,
                    recast_to_geoformat_type=recast_to_type,
                    resize_width=resize_width,
                    resize_precision=resize_precision
                )

    return _geolayer


def feature_filter_geometry(
    feature,
    geometry_type_filter=None,
    bbox_filter=None,
    bbox=True
):
    """
    return a geometry :
        - a certain type of geometries when geometry_type_filter is filled
        - a geometry that intersect a given bbox if bbox_filter is filled

    :param feature: feature that will be filtered
    :param geometry_type_filter: Geometry(ies) type(s) that we want to keep in feature.
        If type not existing the feature is None.
    :param bbox_filter: if bbox(s) intersects features return feature. If feature not intersecting bbox function return
        None
    :param bbox:
    :return: geometry part of feature (beware this is not a feature on output but only geometry part)
    """
    if feature:
        feature = copy.deepcopy(feature)
        # TODO remove when bbox will be an object
        if isinstance(bbox_filter, (list, tuple)):
            if isinstance(bbox_filter[0], (int, float)):
                bbox_filter = [bbox_filter]
        bbox_filter = value_to_iterable_value(bbox_filter, tuple)

        geometry = {}
        if 'geometry' in feature:
            if geometry_type_filter:
                # convert geometry to geometry collection (we use geometry_type_filter to filter geometries)
                geometry_in_collection = geometry_to_geometry_collection(
                    geometry=feature['geometry'],
                    geometry_type_filter=geometry_type_filter,
                    bbox=False
                )

                if geometry_in_collection['geometries']:
                    # if we get only one geometry in geometryCollection we return the only geometry in it
                    if len(geometry_in_collection['geometries']) == 1:
                        geometry = geometry_in_collection['geometries'][0]
                    else:
                        geometry = geometry_in_collection
                else:
                    geometry = {}
            else:
                geometry = feature['geometry']

            if bbox_filter and geometry:
                geometry_in_bbox = False
                geometry_bbox = geometry_to_bbox(geometry)
                if geometry_bbox:
                    for bbox_in_filter in bbox_filter:
                        if bbox_intersects_bbox(geometry_bbox, bbox_in_filter):
                            geometry_in_bbox = True
                            break

                if geometry_in_bbox is False:
                    geometry = {}


            # if bbox option is activate we compute it
            if bbox is True and geometry:
                if 'bbox' not in feature['geometry']:
                    if geometry['type'] == 'GeometryCollection':
                        for geometry_in_collection in geometry['geometries']:
                            geometry_in_collection_bbox = geometry_to_bbox(geometry_in_collection)
                            if geometry_in_collection_bbox:
                                geometry_in_collection['bbox'] = geometry_in_collection_bbox

                    geometry_bbox = geometry_to_bbox(geometry)
                    if geometry_bbox:
                        geometry['bbox'] = geometry_bbox

        return geometry


def feature_filter_attributes(feature, field_name_filter=None):
    """
    Keeps (filter) only the fields specified in the variable field_name_filter

    :param feature: feature that will be filtered
    :param field_name_filter: field name that we want to keep in feature (if present in feature).
    :return: attributes part of feature (beware this is not a feature on output but only attributes part)
    """
    # initialize input
    field_name_filter = value_to_iterable_value(field_name_filter, list)

    if feature:
        # initialize output
        new_feature_attributes = {}

        if field_name_filter:

            # format field_name_filter
            field_name_filter = value_to_iterable_value(field_name_filter)

            if 'attributes' in feature:
                if field_name_filter:
                    for field_name in field_name_filter:
                        if field_name in feature["attributes"]:
                            if new_feature_attributes:
                                new_feature_attributes[field_name] = feature['attributes'][field_name]
                            else:
                                new_feature_attributes = {field_name: feature['attributes'][field_name]}
        else:
            if 'attributes' in feature:
                new_feature_attributes = feature['attributes']

        return new_feature_attributes


def feature_filter(
    feature,
    serialize=None,
    field_name_filter=None,
    geometry_type_filter=None,
    bbox_filter=None,
    bbox=True
):
    """
    This function apply filter on "attributes" and/or "geometry"
        Attributes filter
            - field name filter

        Geometry filter
            - geometry type filter
            - bbox filter if feature geometry


    :param serialize: if you want serialize your data
    :param feature: feature that we want filter
    :param field_name_filter: field name that we want to keep in feature (if present in feature).
    :param geometry_type_filter: Geometry(ies) type(s) that we want to keep in feature.
        If type not existing the feature is None.
    :param bbox_filter: if bbox(s) intersects features return feature. If feature not intersecting bbox function return
        None
    :param bbox: if you want compute feature geometry bbox
    :return: filtered feature
    """
    # check value to deduce if we must filter feature or not
    if serialize or field_name_filter or geometry_type_filter or bbox_filter or bbox:
        # initialize input variable
        # attributes
        attributes_filter = False
        if field_name_filter:
            attributes_filter = True
        # geometry
        geometry_filter = False
        if geometry_type_filter or bbox_filter:
            geometry_filter = True

        # initialize output variable
        new_feature = {}
        # attributes filter
        feature_attributes = feature_filter_attributes(
            feature,
            field_name_filter=field_name_filter
        )
        if feature_attributes:
            new_feature['attributes'] = feature_attributes

        # geometry filter
        feature_geometry = feature_filter_geometry(
            feature,
            geometry_type_filter=geometry_type_filter,
            bbox_filter=bbox_filter,
            bbox=bbox
        )
        if feature_geometry:
            new_feature['geometry'] = feature_geometry

        # check if feature is valid
        if attributes_filter and 'attributes' not in new_feature and 'geometry' not in new_feature:
            new_feature = None

        if geometry_filter and new_feature and 'geometry' not in new_feature:
            new_feature = None

        if new_feature:
            if serialize:
                new_feature = feature_serialize(new_feature)

            return new_feature

    else:
        return feature


def features_filter(
    geolayer_feature_list_or_generator,
    field_name_filter=None,
    geometry_type_filter=None,
    bbox_filter=None,
    serialize=None,
    bbox_extent=True,
    feature_limit=None,
    feature_offset=None
):
    # if input is a geolayer
    if isinstance(geolayer_feature_list_or_generator, dict):
        feature_i_feat_list, geolayer_feature_list_or_generator = zip(*geolayer_feature_list_or_generator['features'])

    yield_count = 0
    for i_feat, feature in enumerate(geolayer_feature_list_or_generator):
        if feature_offset:
            if i_feat < feature_offset:
                continue

        output_feature = feature_filter(
            feature=feature,
            serialize=serialize,
            field_name_filter=field_name_filter,
            geometry_type_filter=geometry_type_filter,
            bbox_filter=bbox_filter,
            bbox=bbox_extent,
        )
        if output_feature:
            yield output_feature
            yield_count += 1

            if feature_limit:
                if yield_count == feature_limit:
                    break
