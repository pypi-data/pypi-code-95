from geoformat.conf.format_data import value_to_iterable_value
from geoformat.conf.fields_variable import python_type_to_field_type


def geometries_scan_to_geometries_metadata(
    geometry_scan,
    crs=None,
    extent=True
):
    """
    Crete geometry metadata dict from geometry scan get from features_geometry_ref_scan.

    :param geometry_scan: result from features_geometry_ref_scan function
    :param crs: coordinates reference system of features contains in geolayer
    :param extent: if True add extent geolyer to geometry metadata
    :return: geometry metadata
    """
    if geometry_scan['type']:
        geometry_metadata = {'type': geometry_scan['type']}
        if extent and 'extent' in geometry_scan:
            if geometry_scan['extent']:
                geometry_metadata['extent'] = geometry_scan['extent']
        if crs:
            geometry_metadata['crs'] = crs
    else:
        geometry_metadata = None

    return geometry_metadata


def fields_scan_to_fields_metadata(fields_scan):
    """
    Deduce fields metadata from fields scan result.

    List of field's type and necessary keys :

        | type          | width    | precision | index    |
        |---------------|----------|-----------|----------|
        | 'Integer'     | None     | None      | Optional |
        | 'IntegerList' | None     | None      | Optional |
        | 'Real'        | Required | Required  | Optional |
        | 'RealList'    | Required | Required  | Optional |
        | 'String'      | Required | None      | Optional |
        | 'StringList'  | Required | None      | Optional |
        | 'Binary'      | None     | None      | Optional |
        | 'Date'        | None     | None      | Optional |
        | 'Time'        | None     | None      | Optional |
        | 'DateTime'    | None     | None      | Optional |
        | 'Boolean'     | None     | None      | Optional |

        example :
            field_metadata  = {
                'field_a': {'type': 'Integer', 'index': 0},
                'field_b': {'type': 'Real', 'width': 4, 'precision': 2, 'index': 1}
            }


    :param fields_scan: result of geolayer_fields_type_scan
    :return: geolayer fields metadata
    """
    # create fields metadata dict
    fields_metadata = {}

    # create field_name list ordered by 'field_index' in field_name data
    field_name_list = [None] * len(fields_scan)
    for i_field, (field_name, field_data) in enumerate(fields_scan.items()):
        # if "field_index" key in field_data we store field_name in field_name_list in 'field_index' order
        if 'field_index' in field_data:
            field_idx = field_data['field_index']
        else:
            field_idx = i_field
        field_name_list[field_idx] = field_name

    # loop on fields and create field metadata dict
    reorder_field_index = []
    for field_name in field_name_list:
        field_dict = fields_scan[field_name]
        if field_dict['field_delete'] is False:
            field_metadata_dict = {}
            # determine field type
            field_type = field_dict['field_type']
            field_type_key = field_type
            if field_dict['field_list'] is True:
                field_type_key = (field_type_key, list)
            # add data in field_metadata_dict
            # get type
            field_metadata_dict['type'] = python_type_to_field_type[field_type_key]
            # get width for str
            if field_type == str:
                field_metadata_dict['width'] = field_dict['field_width_str']
                # if we transform an list original to str (does not work with StringList type)
                if field_type is str and field_dict['field_list'] is False:
                    if field_dict['field_width_list'] and field_dict['field_width_list'] > field_dict['field_width_str']:
                        field_metadata_dict['width'] = field_dict['field_width_list']
            # get with and precision for float
            if field_type == float:
                field_metadata_dict['width'] = field_dict['field_width_float']
                field_metadata_dict['precision'] = field_dict['field_precision']
            # get field_index (if require)
            if 'field_index' in field_dict:
                field_metadata_dict['index'] = field_dict['field_index']

            # write field metadata in fields metadata
            fields_metadata[field_name] = field_metadata_dict

        else:
            # if field must be deleted and fields have an index (we have to reorder it)
            if 'field_index' in field_dict:
                reorder_field_index.append(field_dict['field_index'])

    # if we need to reorder field index
    if reorder_field_index:
        fields_metadata = reorder_metadata_field_index_after_field_drop(fields_metadata=fields_metadata,
                                                                        reorder_field_index=reorder_field_index)

    return fields_metadata


def reorder_metadata_field_index_after_field_drop(fields_metadata, reorder_field_index):
    """
    This function is used when a field is deleted in a geolayer.

    Reorder "index" key in fields_metadata for step(s) specified in reorder_field_index.

    :param fields_metadata: field metadata from geolayer
    :param reorder_field_index: list that contains original index to delete field.
    :return: fields_metadata with field index reordered after field delete
    """

    # init reorder field index
    reorder_field_index = value_to_iterable_value(reorder_field_index, list)

    # sort index
    reorder_field_index.sort()
    # loop on each index
    for idx in reversed(reorder_field_index):
        for field_name, field_metadata in fields_metadata.items():
            if field_metadata['index'] > idx:
                field_metadata['index'] = field_metadata['index'] - 1

    return fields_metadata