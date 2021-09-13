from geoformat.conversion.bytes_conversion import (
    int_to_4_bytes_integer,
    integer_4_bytes_to_int,
    float_to_double_8_bytes_array,
    double_8_bytes_to_float,
    coordinates_list_to_bytes
)

from tests.data.coordinates import (
    coordinates_with_tuple,
    coordinates_with_list,
    coordinates_with_duplicated_coordinates,
    point_coordinates,
    linestring_coordinates,
    polygon_coordinates,
    multipoint_coordinates,
    multilinestring_coordinates,
    multipolygon_coordinates,
    point_coordinates_3d,
    linestring_coordinates_3d,
    polygon_coordinates_3d,
    multipoint_coordinates_3d,
    multilinestring_coordinates_3d,
    multipolygon_coordinates_3d
)

from test_all import test_function

int_to_4_bytes_integer_parameters = {
    0: {
        "integer_value": 0,
        "integer_endian_big": True,
        "return_value": bytearray(b'\x00\x00\x00\x00')
    },
    1: {
        "integer_value": 0,
        "integer_endian_big": False,
        "return_value": bytearray(b'\x00\x00\x00\x00')
    },
    2: {
        "integer_value": 1,
        "integer_endian_big": True,
        "return_value": bytearray(b'\x00\x00\x00\x01')
    },
    3: {
        "integer_value": 1,
        "integer_endian_big": False,
        "return_value": bytearray(b'\x01\x00\x00\x00')
    },
    4: {
        "integer_value": -1,
        "integer_endian_big": True,
        "return_value": bytearray(b'\xff\xff\xff\xff')
    },
    5: {
        "integer_value": -1,
        "integer_endian_big": False,
        "return_value": bytearray(b'\xff\xff\xff\xff')
    },
    6: {
        "integer_value": 2147483647,
        "integer_endian_big": True,
        "return_value": bytearray(b'\x7f\xff\xff\xff')
    },
    7: {
        "integer_value": 2147483647,
        "integer_endian_big": False,
        "return_value": bytearray(b'\xff\xff\xff\x7f')
    },
    8: {
        "integer_value": -2147483648,
        "integer_endian_big": True,
        "return_value": bytearray(b'\x80\x00\x00\x00')
    },
    9: {
        "integer_value": -2147483648,
        "integer_endian_big": False,
        "return_value": bytearray(b'\x00\x00\x00\x80')
    }
}

integer_4_bytes_to_int_parameters = {
    0: {
        "integer_4_bytes": bytearray(b'\x00\x00\x00\x00'),
        "integer_endian_big": False,
        "return_value": 0
    },
    1: {
        "integer_4_bytes": bytearray(b'\x00\x00\x00\x00'),
        "integer_endian_big": False,
        "return_value": 0
    },
    2: {
        "integer_4_bytes": bytearray(b'\x00\x00\x00\x01'),
        "integer_endian_big": True,
        "return_value": 1
    },
    3: {
        "integer_4_bytes": bytearray(b'\x01\x00\x00\x00'),
        "integer_endian_big": False,
        "return_value": 1
    },
    4: {
        "integer_4_bytes": bytearray(b'\xff\xff\xff\xff'),
        "integer_endian_big": True,
        "return_value": -1
    },
    5: {
        "integer_4_bytes": bytearray(b'\xff\xff\xff\xff'),
        "integer_endian_big": False,
        "return_value": -1
    },
    6: {
        "integer_4_bytes": bytearray(b'\x7f\xff\xff\xff'),
        "integer_endian_big": True,
        "return_value": 2147483647
    },
    7: {
        "integer_4_bytes": bytearray(b'\xff\xff\xff\x7f'),
        "integer_endian_big": False,
        "return_value": 2147483647
    },
    8: {
        "integer_4_bytes": bytearray(b'\x80\x00\x00\x00'),
        "integer_endian_big": True,
        "return_value": -2147483648
    },
    9: {
        "integer_4_bytes": bytearray(b'\x00\x00\x00\x80'),
        "integer_endian_big": False,
        "return_value": -2147483648
    }
}

float_to_double_8_bytes_array_parameters = {
    0: {
        "float_value": 0.0,
        "float_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    },
    1: {
        "float_value": 0.0,
        "float_big_endian": False,
        "return_value": bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    },
    2: {
        "float_value": 1.0,
        "float_big_endian": True,
        "return_value": bytearray(b'?\xf0\x00\x00\x00\x00\x00\x00')
    },
    3: {
        "float_value": 1.0,
        "float_big_endian": False,
        "return_value": bytearray(b'\x00\x00\x00\x00\x00\x00\xf0?')
    },
    4: {
        "float_value": -1.0,
        "float_big_endian": True,
        "return_value": bytearray(b'\xbf\xf0\x00\x00\x00\x00\x00\x00')
    },
    5: {
        "float_value": -1.0,
        "float_big_endian": False,
        "return_value": bytearray(b'\x00\x00\x00\x00\x00\x00\xf0\xbf')
    },
    6: {
        "float_value": 987654321.9876543,
        "float_big_endian": True,
        "return_value": bytearray(b'A\xcdo4X\xfeku')
    },
    7: {
        "float_value": 987654321.9876543,
        "float_big_endian": False,
        "return_value": bytearray(b'uk\xfeX4o\xcdA')
    },
    8: {
        "float_value": 997654321.9876543,
        "float_big_endian": True,
        "return_value": bytearray(b'A\xcd\xbb\x7f\x98\xfeku')
    },
    9: {
        "float_value": 999999999.9876543,
        "float_big_endian": True,
        "return_value": bytearray(b'A\xcd\xcdd\xff\xfeku')
    },
    10: {
        "float_value": 9999999999.987654,
        "float_big_endian": True,
        "return_value": bytearray(b'B\x02\xa0_\x1f\xff\xe6\xb7')
    },
    11: {
        "float_value": 9999999999999999.,
        "float_big_endian": True,
        "return_value": bytearray(b'CA\xc3y7\xe0\x80\x00')
    },
    12: {
        "float_value": 999999999999999.9,
        "float_big_endian": True,
        "return_value": bytearray(b'C\x0ck\xf5&3\xff\xff')
    },
    13: {
        "float_value": 99999999999999.99,
        "float_big_endian": True,
        "return_value": bytearray(b'B\xd6\xbc\xc4\x1e\x8f\xff\xff')
    },
    14: {
        "float_value": 99999999999999.99,
        "float_big_endian": False,
        "return_value": bytearray(b'\xff\xff\x8f\x1e\xc4\xbc\xd6B')
    },
    15: {
        "float_value": -99999999999999.99,
        "float_big_endian": False,
        "return_value": bytearray(b'\xff\xff\x8f\x1e\xc4\xbc\xd6\xc2')
    },
    16: {
        "float_value": -987654321.9876543,
        "float_big_endian": True,
        "return_value": bytearray(b'\xc1\xcdo4X\xfeku')
    },
    17: {
        "float_value": -987654321.9876543,
        "float_big_endian": False,
        "return_value": bytearray(b'uk\xfeX4o\xcd\xc1')
    },
}

double_8_bytes_to_float_parameters = {
    0: {
       "double_8_bytes": bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'),
       "double_big_endian": True,
       "double_dimension": 1,
       "return_value": (0.0,)
    },
    1: {
        "double_8_bytes": bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'),
        "double_big_endian": False,
        "double_dimension": 1,
        "return_value": (0.0,)
    },
    2: {
        "double_8_bytes": bytearray(b'?\xf0\x00\x00\x00\x00\x00\x00'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (1.0,)
    },
    3: {
        "double_8_bytes": bytearray(b'\x00\x00\x00\x00\x00\x00\xf0?'),
        "double_big_endian": False,
        "double_dimension": 1,
        "return_value": (1.0,)
    },
    4: {
        "double_8_bytes": bytearray(b'\xbf\xf0\x00\x00\x00\x00\x00\x00'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (-1.0,)
    },
    5: {
        "double_8_bytes": bytearray(b'\x00\x00\x00\x00\x00\x00\xf0\xbf'),
        "double_big_endian": False,
        "double_dimension": 1,
        "return_value": (-1.0,)
    },
    6: {
        "double_8_bytes": bytearray(b'A\xcdo4X\xfeku'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (987654321.9876543,)
    },
    7: {
        "double_8_bytes": bytearray(b'uk\xfeX4o\xcdA'),
        "double_big_endian": False,
        "double_dimension": 1,
        "return_value": (987654321.9876543,)
    },
    8: {
        "double_8_bytes": bytearray(b'A\xcd\xbb\x7f\x98\xfeku'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (997654321.9876543,)
    },
    9: {
        "double_8_bytes": bytearray(b'A\xcd\xcdd\xff\xfeku'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (999999999.9876543,)
    },
    10: {
        "double_8_bytes": bytearray(b'B\x02\xa0_\x1f\xff\xe6\xb7'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (9999999999.987654,)
    },
    11: {
        "double_8_bytes": bytearray(b'CA\xc3y7\xe0\x80\x00'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (9999999999999999.,)
    },
    12: {
        "double_8_bytes": bytearray(b'C\x0ck\xf5&3\xff\xff'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (999999999999999.9,)
    },
    13: {
        "double_8_bytes": bytearray(b'B\xd6\xbc\xc4\x1e\x8f\xff\xff'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (99999999999999.99,)
    },
    14: {
        "double_8_bytes": bytearray(b'B\xd6\xbc\xc4\x1e\x8f\xff\xffB\xd6\xbc\xc4\x1e\x8f\xff\xff'),
        "double_big_endian": True,
        "double_dimension": 2,
        "return_value": (99999999999999.99, 99999999999999.99)
    },
    15: {
        "double_8_bytes": bytearray(b'\xff\xff\x8f\x1e\xc4\xbc\xd6B\xff\xff\x8f\x1e\xc4\xbc\xd6B'),
        "double_big_endian": False,
        "double_dimension": 2,
        "return_value": (99999999999999.99, 99999999999999.99)
    },
    16: {
        "double_8_bytes": bytearray(b'\xff\xff\x8f\x1e\xc4\xbc\xd6\xc2'),
        "double_big_endian": False,
        "double_dimension": 1,
        "return_value": (-99999999999999.99,)
    },
    17: {
        "double_8_bytes": bytearray(b'\xc1\xcdo4X\xfeku'),
        "double_big_endian": True,
        "double_dimension": 1,
        "return_value": (-987654321.9876543,)
    },
    18: {
        "double_8_bytes": bytearray(b'uk\xfeX4o\xcd\xc1'),
        "double_big_endian": False,
        "double_dimension": 1,
        "return_value": (-987654321.9876543,)
    },
}

coordinates_list_to_bytes_parameters = {
    0: {
        "coordinates_list": coordinates_with_tuple,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x03A#\xdd|fff\xabAZ(\xebs37)A#\xb1\x9a333\x7fAZ*\xe6\xcc\xcc\xd0\xbfA#\xa4x\x00\x00\x00NAZ.\xa39\x99\x9d\x7f\x00\x00\x00\x02A$r\xcf\x00\x00\x00*AZ\'\xc0\xc6fj_A$~\xe0\x99\x99\x99\xc3AZ"\xb4\xb337=')
    },
    1: {
        "coordinates_list": coordinates_with_list,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x03A#\xdd|fff\xabAZ(\xebs37)A#\xb1\x9a333\x7fAZ*\xe6\xcc\xcc\xd0\xbfA#\xa4x\x00\x00\x00NAZ.\xa39\x99\x9d\x7f\x00\x00\x00\x02A$r\xcf\x00\x00\x00*AZ\'\xc0\xc6fj_A$~\xe0\x99\x99\x99\xc3AZ"\xb4\xb337=')
    },
    2: {
        "coordinates_list": coordinates_with_duplicated_coordinates,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x04\x00\x00\x00\x04A#\xdd|fff\xabAZ(\xebs37)A#\xb1\x9a333\x7fAZ*\xe6\xcc\xcc\xd0\xbfA#\xb1\x9a333\x7fAZ*\xe6\xcc\xcc\xd0\xbfA#\xa4x\x00\x00\x00NAZ.\xa39\x99\x9d\x7f\x00\x00\x00\x03A$r\xcf\x00\x00\x00*AZ\'\xc0\xc6fj_A$~\xe0\x99\x99\x99\xc3AZ"\xb4\xb337=A$~\xe0\x99\x99\x99\xc3AZ"\xb4\xb337=\x00\x00\x00\x03A(f\xed\x99\x99\x98<AW\xe4S\xb33>(A(f\xed\x99\x99\x98<AW\xe4S\xb33>(A)4{ffd\xacAW\xe3Cs3>+\x00\x00\x00\nA*\x8c\x02\xcc\xcc\xcavAW\xdfdL\xcc\xd7\xd0A*\x8c\x02\xcc\xcc\xcavAW\xdfdL\xcc\xd7\xd0A*t\xa5\xcc\xcc\xca\x80AW\xdf\x97\xec\xcc\xd7\xd1A*t\xa5\xcc\xcc\xca\x80AW\xdf\x97\xec\xcc\xd7\xd1A*t\xa5\xcc\xcc\xca\x80AW\xdf\x97\xec\xcc\xd7\xd1A*np\x99\x99\x97TAW\xe6\x0b\x19\x99\xa4\x8bA*QK\x99\x99\x97`AW\xe6\x9c\xd33>&A*QK\x99\x99\x97`AW\xe6\x9c\xd33>&A*QK\x99\x99\x97`AW\xe6\x9c\xd33>&A*QK\x99\x99\x97`AW\xe6\x9c\xd33>&')
    },
    3: {
        "coordinates_list": point_coordinates,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\xc0\\\xf3\xd7\n=p\xa4@B\x9e\xb8Q\xeb\x85\x1f')
    },
    4: {
        "coordinates_list": linestring_coordinates,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02@!\xd6\x87+\x02\x0cJ@F4%\xae\xe61\xf9@!\xd8\x93t\xbcj\x7f@F4(\xf5\xc2\x8f\\')
    },
    5: {
        "coordinates_list": polygon_coordinates,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x04@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0@71\xa9\xfb\xe7l\x8b\xc04G\xae\x14z\xe1H\xc0^\x1b\x85\x1e\xb8Q\xec@3&fffff@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0\x00\x00\x00\x04\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3@.k\x85\x1e\xb8Q\xec\xc0%\x9e\xb8Q\xeb\x85\x1f\xc04\x82\x8f\\(\xf5\xc3?\xf8(\xf5\xc2\x8f\\)\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3')
    },
    6: {
        "coordinates_list": multipoint_coordinates,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x03\xc0cp\xa3\xd7\n=q@3\x9c(\xf5\xc2\x8f\\\xc0c\x87\n=p\xa3\xd7@4\xbdp\xa3\xd7\n=\xc0c\xbf\n=p\xa3\xd7@5u\xc2\x8f\\(\xf6')
    },
    7: {
        "coordinates_list": multilinestring_coordinates,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x02@\x0e\x00\x00\x00\x00\x00\x00@"\x80\x00\x00\x00\x00\x00\xc0`^fffff?\xf8Q\xeb\x85\x1e\xb8R\x00\x00\x00\x03@7&fffff\xc0A \x00\x00\x00\x00\x00\xbf\xf5\x99\x99\x99\x99\x99\x9a\xc0\x12\x99\x99\x99\x99\x99\x9a@\x0b\x99\x99\x99\x99\x99\x9a@S|\xcc\xcc\xcc\xcc\xcd')
    },
    8: {
        "coordinates_list": multipolygon_coordinates,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x04@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f\xc0`]\x1e\xb8Q\xeb\x85?\xf8Q\xeb\x85\x1e\xb8R@A\x8f\\(\xf5\xc2\x8f@R\x0e\xf9\xdb"\xd0\xe5@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f\x00\x00\x00\x01\x00\x00\x00\x04@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85\xbf\xf4\xf5\xc2\x8f\\(\xf6\xc0\x12p\xa3\xd7\n=q@\x0bG\xae\x14z\xe1H@Sz=p\xa3\xd7\n@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85')
    },
    9: {
        "coordinates_list": point_coordinates_3d,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\xc0\\\xf3\xd7\n=p\xa4@B\x9e\xb8Q\xeb\x85\x1f\xc0CS\xb6E\xa1\xca\xc1')
    },
    10: {
        "coordinates_list": linestring_coordinates_3d,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02@!\xd6\x87+\x02\x0cJ@F4%\xae\xe61\xf9@o\xd9\x99\x99\x99\x99\x9a@!\xd8\x93t\xbcj\x7f@F4(\xf5\xc2\x8f\\\xc0X\x80\x00\x00\x00\x00\x00')
    },
    11: {
        "coordinates_list": polygon_coordinates_3d,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x04@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0\xc0S)\x99\x99\x99\x99\x9a@71\xa9\xfb\xe7l\x8b\xc04G\xae\x14z\xe1H@b \x00\x00\x00\x00\x00\xc0^\x1b\x85\x1e\xb8Q\xec@3&fffff?\xc2\xb0 \xc4\x9b\xa5\xe3@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0@S\xb8\xf5\xc2\x8f\\)\x00\x00\x00\x04\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3@cL\xcc\xcc\xcc\xcc\xcd@.k\x85\x1e\xb8Q\xec\xc0%\x9e\xb8Q\xeb\x85\x1f\xc04\x82\x8f\\(\xf5\xc3?\xf8(\xf5\xc2\x8f\\)\xc0@L\xcc\xcc\xcc\xcc\xcd\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3@F\xcc\xcc\xcc\xcc\xcc\xcd')
    },
    12: {
        "coordinates_list": multipoint_coordinates_3d,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x03\xc0cp\xa3\xd7\n=q@3\x9c(\xf5\xc2\x8f\\@S\x9c\xcc\xcc\xcc\xcc\xcd\xc0c\x87\n=p\xa3\xd7@4\xbdp\xa3\xd7\n=@)L\xcc\xcc\xcc\xcc\xcd\xc0c\xbf\n=p\xa3\xd7@5u\xc2\x8f\\(\xf6\xc0R\xc9\x99\x99\x99\x99\x9a')
    },
    13: {
        "coordinates_list": multilinestring_coordinates_3d,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x02@\x0e\x00\x00\x00\x00\x00\x00@"\x80\x00\x00\x00\x00\x00\xc0P\\\xcc\xcc\xcc\xcc\xcd\xc0`^fffff?\xf8Q\xeb\x85\x1e\xb8R@F\xc5\x1e\xb8Q\xeb\x85\x00\x00\x00\x03@7&fffff\xc0A \x00\x00\x00\x00\x00@/+\x02\x0cI\xba^\xbf\xf5\x99\x99\x99\x99\x99\x9a\xc0\x12\x99\x99\x99\x99\x99\x9a\xc0X\x9c\xcc\xcc\xcc\xcc\xcd@\x0b\x99\x99\x99\x99\x99\x9a@S|\xcc\xcc\xcc\xcc\xcd@S\x88\xf5\xc2\x8f\\)')
    },
    14: {
        "coordinates_list": multipolygon_coordinates_3d,
        "coordinates_big_endian": True,
        "return_value": bytearray(b'\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x04@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f@^\xc0\x00\x00\x00\x00\x00\xc0`]\x1e\xb8Q\xeb\x85?\xf8Q\xeb\x85\x1e\xb8R@/\x14z\xe1G\xae\x14@A\x8f\\(\xf5\xc2\x8f@R\x0e\xf9\xdb"\xd0\xe5@S\xa6fffff@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f@U\xf81&\xe9x\xd5\x00\x00\x00\x01\x00\x00\x00\x04@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85\xc0F\x93dZ\x1c\xac\x08\xbf\xf4\xf5\xc2\x8f\\(\xf6\xc0\x12p\xa3\xd7\n=q\xc0\t\xf5\xc2\x8f\\(\xf6@\x0bG\xae\x14z\xe1H@Sz=p\xa3\xd7\n\xc0D\x80\x00\x00\x00\x00\x00@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85\xc0U\xf8\xf5\xc2\x8f\\)')
    }
}


def test_all():

    # int_to_4_bytes_integer
    print(test_function(int_to_4_bytes_integer, int_to_4_bytes_integer_parameters))

    # integer_4_bytes_to_int
    print(test_function(integer_4_bytes_to_int, integer_4_bytes_to_int_parameters))

    # float_to_double_8_bytes_array
    print(test_function(float_to_double_8_bytes_array, float_to_double_8_bytes_array_parameters))

    # double_8_bytes_to_float
    print(test_function(double_8_bytes_to_float, double_8_bytes_to_float_parameters))

    # coordinates_list_to_bytes
    print(test_function(coordinates_list_to_bytes, coordinates_list_to_bytes_parameters))


if __name__ == '__main__':
    test_all()
