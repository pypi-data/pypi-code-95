import struct

big_endian_wkb_geometry_type_to_geometry_type = {
    b'\x00\x00\x00\x01': 'Point',
    b'\x00\x00\x00\x02': 'LineString',
    b'\x00\x00\x00\x03': 'Polygon',
    b'\x00\x00\x00\x04': 'MultiPoint',
    b'\x00\x00\x00\x05': 'MultiLineString',
    b'\x00\x00\x00\x06': 'MultiPolygon',
    b'\x00\x00\x00\x07': 'GeometryCollection',
}

geometry_type_to_wkb_geometry_type = {
    'POINT': b'\x00\x00\x00\x01',
    'LINESTRING': b'\x00\x00\x00\x02',
    'POLYGON': b'\x00\x00\x00\x03',
    'MULTIPOINT': b'\x00\x00\x00\x04',
    'MULTILINESTRING': b'\x00\x00\x00\x05',
    'MULTIPOLYGON': b'\x00\x00\x00\x06',
    'GEOMETRYCOLLECTION': b'\x00\x00\x00\x07',
}


def int_to_4_bytes_integer(integer_value, integer_endian_big=True):
    """
    make translation between int type value to 4 bytes value.
    Optionally you can choose output bytes endian

    :param integer_value: integer value
    :param integer_endian_big: True if output big endian / False if output little endian
    :return: input value in 4 bytes
    """
    if integer_endian_big is True:
        struct_format = ">i"
    else:
        struct_format = "<i"

    return bytearray(struct.pack(struct_format, integer_value))


def float_to_double_8_bytes_array(float_value, float_big_endian=True):
    """
    Make translation between float type value to 8 bytes value.
    Optionally you can choose output bytes endian

    :param float_value: float value
    :param float_big_endian: True if output big endian / False if output little endian
    :return: input value in 8 bytes
    """
    if float_big_endian is True:
        struct_format = ">d"
    else:
        struct_format = "<d"

    return bytearray(struct.pack(struct_format, float_value))


def coordinates_list_to_bytes(coordinates_list, coordinates_big_endian=True):
    """
    Transform a list of coordinates to bytes value.
    Optionally you can choose the output endian.

    :param coordinates_list: list of coordinates.
    :param coordinates_big_endian: True if output big endian / False if output little endian.
    :return: coordinates in bytes value.
    """

    def coordinates_to_bytes(coordinates, float_big_endian=True):
        """
        Transform coordinates to bytes.
        Optionally you can choose the output endian.

        :param coordinates:
        :param float_big_endian:
        :return: coordinates in bytes value.
        """
        coordinates_bytes = bytearray()
        for coordinate in coordinates:
            coordinate_bytes = float_to_double_8_bytes_array(float_value=coordinate, float_big_endian=float_big_endian)
            coordinates_bytes += coordinate_bytes

        return coordinates_bytes

    first_coord = coordinates_list[0]
    if isinstance(first_coord, (list, tuple)):
        bytes_coordinates = int_to_4_bytes_integer(len(coordinates_list), integer_endian_big=coordinates_big_endian)
        for coord in coordinates_list:
            bytes_coordinates += coordinates_list_to_bytes(coordinates_list=coord,
                                                           coordinates_big_endian=coordinates_big_endian)
    elif isinstance(first_coord, (float, int)):
        bytes_coordinates = coordinates_to_bytes(coordinates=coordinates_list,
                                                 float_big_endian=coordinates_big_endian)
    else:
        raise ValueError

    return bytes_coordinates


def double_8_bytes_to_float(double_8_bytes, double_big_endian, double_dimension=2):
    """
    Make translation between dimension * 8 bytes value to float type value.
    You have to give the endian of data and dimension of coordinates.

    :param double_8_bytes: coordinates value in 8 bytes
    :param double_big_endian: the endian order of your bytes
    :param double_dimension: number of dimension (default 2) for your coordinates
    :return: float tuple of coordinates
    """
    if double_big_endian is True:
        struct_format = ">{dim}d".format(dim=double_dimension)
    elif double_big_endian is False:
        struct_format = "<{dim}d".format(dim=double_dimension)
    else:
        raise ValueError('endian_big must be a bool type')

    return struct.unpack(struct_format, double_8_bytes)


def integer_4_bytes_to_int(integer_4_bytes, integer_endian_big):
    """
    Make translation between integer 4 bytes value to integer type value.
    You have to give the endian of data and double_dimension of coordinates.

    :param integer_4_bytes: coordinates value in 8 bytes
    :param integer_endian_big: the endian of your bytes
    :return: float tuple of coordinates
    """
    if integer_endian_big is True:
        struct_format = ">i"
    elif integer_endian_big is False:
        struct_format = "<i"
    else:
        raise ValueError('endian_big must be a bool type')

    return struct.unpack(struct_format, integer_4_bytes)[0]
