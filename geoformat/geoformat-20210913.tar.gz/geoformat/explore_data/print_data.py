
def _get_line(fields_value_list, max_width_value_list, separator='|'):
    """
    Return a string with values contains in fields_value_list separate by seperator and with for column width the
    informations contained in max_width_value_list

    :param fields_value_list: list of values that we want print
    :param max_width_value_list: list of width column for each values that we want print
    :param separator: separator character between each column
    :return: the formated values contain in fields_value_list
    """

    width_field = [(' ' * (width_value + 2))[:1] + str(fields_value_list[i_field]) + (' ' * (
            width_value + 2))[len(str(fields_value_list[i_field])) + 1:] for i_field, width_value in
     enumerate(max_width_value_list)]

    line = separator + separator.join(width_field) + separator

    return line


def _get_header_separator(width_column_list, table_type='RST'):
    """
    Return a string header of data table

    :param width_column_list: the width for each column
    :param table_type: type of output (value : 'RST' or 'MD' only)
    :return: header separator
    """
    if table_type == 'RST':
        separator = '+'
        header = '='

    elif table_type == 'MD':
        separator = '|'
        header = '-'
    else:
        raise ValueError('error table type value {} not valid'.format(table_type))

    combi = header + separator + header

    return separator + header + combi.join(
        [header * width_value for width_value in width_column_list]) + header + separator


def _get_line_separator(width_column_list):
    """
    Return a string separator between line of data table
    :param width_column_list:
    :return:
    """
    return '+-' + '-+-'.join(['-' * width_value for width_value in width_column_list]) + '-+'


# TODO add header
def _get_features_data_table_line(
    geolayer,
    field_name_list=None,
    print_i_feat=True,
    table_type='RST',
    light=True,
    display_geo_data=True,
    max_width_coordinates_printing=30,
    limit=None,
    header=True
):
    """
    Returns a generator to display the attribute data of a geolayer
    
    :param geolayer: geolayer that we want print
    :param field_name_list: if filled out we restrain printing on only indicate fields
    :param print_i_feat: choose if you want to see appears i_feat or not (default : NOT)
    :param table_type: choose type of printing ( 2 format allowed Markdown ('MD') or reStructuredText (RST))
    :param light: choose if you want a separator between line or not (default: NOT)
    :param display_geo_data: print geometry information (Geometry Type and Coordinates extract) ? (default: NOT)
    :param max_width_coordinates_printing: if display_geometry is True you can choose the max width of coordinates
           column. (if None all coordinates are print).
    :param header: print table header

    :return: line that compose table
    """
    # init attributes_values and geometry_values
    if 'fields' in geolayer['metadata']:
        attributes_values = True
    else:
        attributes_values = False

    if 'geometry_ref' in geolayer['metadata']:
        geometry_values = True
    else:
        geometry_values = False

    if not field_name_list:
        # create field name
        if 'fields' in geolayer['metadata']:
            attributes_values = True
            field_name_list = [None] * len(geolayer['metadata']['fields'])
            for i_field, field_name in enumerate(geolayer['metadata']['fields']):
                if 'index' in geolayer['metadata']['fields'][field_name]:
                    idx_field = geolayer['metadata']['fields'][field_name]['index']
                else:
                    idx_field = i_field
                field_name_list[idx_field] = field_name
        else:
            field_name_list = []

    if attributes_values:
        max_width_value_list = [len(field_name) for field_name in field_name_list]
    else:
        max_width_value_list = []

    if print_i_feat is True:
        key_max_width = len('i_feat')

    if display_geo_data:
        if "geometry_ref" in geolayer['metadata']:
            geometry_values = True
            max_width_value_list += [len('type'), len('coordinates')]

    # scan geolayer data for determine output width table
    for i_limit, (i_feat, feature) in enumerate(geolayer['features'].items()):
        # if limit we stop loop
        if limit and i_limit == limit:
            break
        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize'] is True:
                feature = eval(feature)

        #  DATA
        # get attributes data
        if attributes_values:
            if 'attributes' in feature:
                width_value_list = [len(str(feature['attributes'][field_name])) if field_name in feature['attributes'] else 0 for field_name in field_name_list]
            else:
                width_value_list = [0] * len(field_name_list)
        else:
            width_value_list = []

        # GEOMETRY
        # get geometry data
        if geometry_values:
            if display_geo_data:
                if 'geometry' in feature:
                    if 'coordinates' in feature['geometry']:
                        coordinates_geometries_key = 'coordinates'
                    elif 'geometries' in feature['geometry']:
                        coordinates_geometries_key = 'geometries'
                    else:
                        raise Exception('unreadable geometry')
                    coordinates = feature['geometry'][coordinates_geometries_key]
                    width_coordinates = len(str(coordinates))

                    if max_width_coordinates_printing:
                        if width_coordinates > max_width_coordinates_printing:
                            width_coordinates = max_width_coordinates_printing

                    width_value_list += [len(str(feature['geometry']['type'])), width_coordinates]
                else:
                    width_value_list += [0, 0]

        # resize width of column if feature's data are larger than other one
        for i_width_value, width_value in enumerate(width_value_list):
            if width_value > max_width_value_list[i_width_value]:
                max_width_value_list[i_width_value] = width_value

            # compute key width
            if print_i_feat is True:
                if len(str(i_feat)) > key_max_width:
                    key_max_width = len(str(i_feat))
    # OPTIONS
    # i_feat
    if print_i_feat is True:
        # add i_feat max wisth to field_name_list
        max_width_value_list = [key_max_width] + max_width_value_list
        # add 'i_feat' value to complete_field_name_list
        complete_field_name_list = ['i_feat'] + field_name_list
    else:
        complete_field_name_list = field_name_list

    # add field type and coordinates at the end
    if display_geo_data:
        if 'geometry_ref' in geolayer["metadata"]:
            complete_field_name_list = complete_field_name_list + ['type', 'coordinates']

    # RETURN LINE TABLE
    # generate header top
    if table_type == 'RST':
        yield _get_line_separator(max_width_value_list)

    # generate header
    yield _get_line(fields_value_list=complete_field_name_list, max_width_value_list=max_width_value_list)
    # generate header seprator
    yield _get_header_separator(max_width_value_list, table_type=table_type)

    # generate line for each value in geolayer
    for i_limit, (i_feat, feature) in enumerate(geolayer['features'].items()):
        # if limit we stop loop
        if limit and i_limit == limit:
            break
        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize'] is True:
                feature = eval(feature)

        # get attributes value
        if attributes_values:
            if 'attributes' in feature:
                field_value_list = [feature['attributes'][field_name] if field_name in feature['attributes'] else None for field_name in field_name_list]
            else:
                field_value_list = [None] * len(geolayer['metadata']['fields'])
        else:
            field_value_list = []
        
        # adding i_feat if option is True
        if print_i_feat is True:
            field_value_list = [i_feat] + field_value_list

        if display_geo_data:
            if "geometry" in feature:
                geometry_type = feature['geometry']['type']
                field_value_list += [geometry_type]

                if geometry_type == 'GeometryCollection':
                    coordinates_value = str(feature['geometry']['geometries'])
                else:
                    coordinates_value = str(feature['geometry']['coordinates'])

                if max_width_coordinates_printing:
                    coordinates_value = coordinates_value[:max_width_coordinates_printing]

                    if len(coordinates_value) == max_width_coordinates_printing:
                        if geometry_type.upper() in ['POINT', 'GEOMETRYCOLLECTION']:  # ['Point', 'GeometryCollection']
                            coordinates_value = coordinates_value[:-5] + ' ...]'
                        elif geometry_type.upper() in ['LINESTRING', 'MULTIPOINT']:  # ['LineString', 'MultiPoint']
                            coordinates_value = coordinates_value[:-6] + ' ...]]'
                        elif geometry_type.upper() in ['POLYGON', 'MULTILINESTRING']:  # ['Polygon', 'MultiLineString']
                            coordinates_value = coordinates_value[:-7] + ' ...]]]'
                        elif geometry_type.upper() in ['MULTIPOLYGON']:  # ['MultiPolygon']
                            coordinates_value = coordinates_value[:-8] + ' ...]]]]'

                field_value_list += [coordinates_value]
            else:
                field_value_list += [None, None]

        # generate feature value
        yield _get_line(field_value_list, max_width_value_list)

        # generate line separator if output format is RST
        if table_type == 'RST':
            if light is False:
                yield _get_line_separator(max_width_value_list)

    # generate line separator if output format is RST
    if table_type == 'RST':
        yield _get_line_separator(max_width_value_list)


def print_features_data_table(
    geolayer,
    field_name_list=None,
    print_i_feat=True,
    table_type='RST',
    light=True,
    display_geometry=True,
    max_width_coordinates_printing=30,
    header=True,
    limit=None
):
    """
    Print geolayer features attributes and/or geometry when exists.

    :param geolayer: geolayer that we want print
    :param field_name_list: if filled out we restrain printing on only indicate fields
    :param print_i_feat: choose if you want to see appears i_feat or not (default : NOT)
    :param table_type: choose type of printing ( 2 format allowed Markdown ('MD') or reStructuredText (RST))
    :param light: choose if you want a separator between line or not (default: NOT)
    :param display_geometry: print geometry information (Geometry Type and Coordinates extract) ? (default: NOT)
    :param max_width_coordinates_printing: if display_geo_data is True you can choose the max width of coordinates
    column. (if None all coordinates are print).
    :param header: print table header
    :param limit: if you want just print x features.

    :return: line that compose table
    """
    return_value = ''
    for i_line, line in enumerate(_get_features_data_table_line(
        geolayer=geolayer,
        field_name_list=field_name_list,
        print_i_feat=print_i_feat,
        table_type=table_type,
        light=light,
        display_geo_data=display_geometry,
        max_width_coordinates_printing=max_width_coordinates_printing,
        header=True,
        limit=limit
    )):
        return_value += line + '\n'

    return return_value


# TODO add header
def _get_fields_metadata_table_line(
    geolayer,
    field_name_list=None,
    key_field_name='field name',
    order_value=False,
    table_type='RST',
    light=True,
    header=True
):
    """
    Returns a generator to display the metadata data of a geolayer

    :param geolayer:
    :param field_name_list: if filled out we restrain printing on only indicate fields
    :param key_field_name: name of column that contains field_name
    :param order_value: respect the order apparition of field_name ('index' key must be filled out in field metadata).
           (default: NOT)
    :param table_type: choose type of printing ( 2 format allowed Markdown ('MD') or reStructuredText (RST))
    :param light: choose if you want a separator between line or not (default: NOT)
    :param header: print table header

    :return: line that compose table
    """

    dict_data = geolayer['metadata'].get('fields')
    if dict_data:
        if not field_name_list:
            field_name_list = ['type', 'width', 'precision', 'index']

        max_width_value_list = [len(str(field_name)) for field_name in field_name_list]

        # create a calling list who is
        call_feature_order = list(dict_data.keys())

        # compute max width for data_value
        key_max_width = 0
        for i_field, key in enumerate(dict_data):
            width_value_list = [len(str(dict_data[key][field_name])) if field_name in dict_data[key] else len('None') for field_name in field_name_list]
            # compute width data_value
            for i_width_value, width_value in enumerate(width_value_list):
                if width_value > max_width_value_list[i_width_value]:
                    max_width_value_list[i_width_value] = width_value
            # compute key width
            if len(str(key)) > key_max_width:
                key_max_width = len(str(key))

            if order_value:
                idx = dict_data[key]['index']
                call_feature_order[idx] = key

        # add max key width to key width value list
        if len(key_field_name) > key_max_width:
            key_max_width  = len(key_field_name)
        max_width_value_list = [key_max_width] + max_width_value_list

        # add key_field_name to field_name_list
        complete_field_name_list = [key_field_name] + field_name_list

        # create line separator
        line_separator = _get_line_separator(max_width_value_list)

        # create fields name line
        line_field_name = _get_line(complete_field_name_list, max_width_value_list)

        # generate table to print
        if table_type == 'RST':
            yield line_separator
        yield line_field_name
        yield _get_header_separator(max_width_value_list, table_type=table_type)

        # for i_field, key in enumerate(dict_data):
        for i_feat in call_feature_order:
            field_value_list = [i_feat] + [dict_data[i_feat][field_name] if field_name in dict_data[i_feat] else None for field_name in field_name_list]
            yield _get_line(field_value_list, max_width_value_list)
            if not light:
                yield line_separator

        if table_type == 'RST':
            yield _get_line_separator(max_width_value_list)


def print_metadata_field_table(
    geolayer,
    field_name_list=None,
    key_field_name='field name',
    order_value=False,
    table_type='RST',
    light=True,
    header=True
):
    """
    Return a string metadata abstract.

    :param geolayer:
    :param field_name_list: if filled out we restrain printing on only indicate fields
    :param key_field_name: name of column that contains field_name
    :param order_value: respect the order apparition of field_name ('index' key must be filled out in field metadata).
    (default: NOT)
    :param table_type: choose type of printing ( 2 format allowed Markdown ('MD') or reStructuredText (RST))
    :param light: choose if you want a separator between line or not (default: NOT)
    :param header: print table header

    :return: line that compose table
    """
    return_value = ''
    for line in _get_fields_metadata_table_line(geolayer,
                                                field_name_list=field_name_list,
                                                key_field_name=key_field_name,
                                                order_value=order_value,
                                                table_type=table_type,
                                                light=light,
                                                header=header):
        return_value += line + '\n'

    return return_value
