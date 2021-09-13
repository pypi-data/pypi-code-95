from tests.data.coordinates import (
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
    multipolygon_coordinates_3d,
    paris_4326,
    paris_3857,
    tokyo_4326,
    tokyo_3857,
    loire_4326,
    loire_3857,
    katsuragawa_river_4326,
    katsuragawa_river_3857,
    france_4326,
    france_3857,
    japan_4326,
    japan_3857

)

# FORMAT : geojson like

POINT = {"type": "Point", "coordinates": point_coordinates}
POINT_EMPTY = {"type": "Point", "coordinates": []}
MULTIPOINT = {"type": "MultiPoint", "coordinates": multipoint_coordinates}
MULTIPOINT_EMPTY = {"type": "MultiPoint", "coordinates": []}
LINESTRING = {"type": "LineString", "coordinates": linestring_coordinates}
LINESTRING_EMPTY = {"type": "LineString", "coordinates": []}

LINESTRING_TEST_POINT_ON_LINESTRING = {
    "type": "LineString",
    "coordinates": [[-10, -10], [-10, 10], [10, 10]],
}
LINESTRING_TEST_POINT_ON_LINESTRING_REVERSE = {
    "type": "LineString",
    "coordinates": [[10, 10], [-10, 10], [-10, -10]],
}

MULTILINESTRING = {
    "type": "MultiLineString",
    "coordinates": multilinestring_coordinates,
}
MULTILINESTRING_EMPTY = {"type": "MultiLineString", "coordinates": []}
POLYGON = {"type": "Polygon", "coordinates": polygon_coordinates}
POLYGON_EMPTY = {"type": "Polygon", "coordinates": []}
MULTIPOLYGON = {"type": "MultiPolygon", "coordinates": multipolygon_coordinates}
MULTIPOLYGON_EMPTY = {"type": "MultiPolygon", "coordinates": []}
GEOMETRYCOLLECTION = {
    "type": "GeometryCollection",
    "geometries": [
        {"type": "Point", "coordinates": [-115.81, 37.24]},
        {"type": "LineString", "coordinates": [[8.919, 44.4074], [8.923, 44.4075]]},
        {
            "type": "Polygon",
            "coordinates": [
                [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
            ],
        },
        {
            "type": "MultiPoint",
            "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]],
        },
        {
            "type": "MultiLineString",
            "coordinates": [
                [[3.75, 9.25], [-130.95, 1.52]],
                [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
            ],
        },
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],
                [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]],
            ],
        },
    ],
}
GEOMETRYCOLLECTION_EMPTY = {"type": "GeometryCollection", "geometries": []}
GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES = {
    "type": "GeometryCollection",
    "geometries": [
        {"type": "Point", "coordinates": []},
        {"type": "LineString", "coordinates": [[8.919, 44.4074], [8.923, 44.4075]]},
        {
            "type": "Polygon",
            "coordinates": [
                [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
            ],
        },
        {"type": "MultiPoint", "coordinates": []},
        {
            "type": "MultiLineString",
            "coordinates": [
                [[3.75, 9.25], [-130.95, 1.52]],
                [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
            ],
        },
        {"type": "MultiPolygon", "coordinates": []},
    ],
}

# 3D
POINT_3D = {"type": "Point25D", "coordinates": point_coordinates_3d}
LINESTRING_3D = {"type": "LineString25D", "coordinates": linestring_coordinates_3d}
POLYGON_3D = {"type": "Polygon25D", "coordinates": polygon_coordinates_3d}
MULTIPOINT_3D = {"type": "MultiPoint25D", "coordinates": multipoint_coordinates_3d}
MULTILINESTRING_3D = {
    "type": "MultiLineString25D",
    "coordinates": multilinestring_coordinates_3d,
}
MULTIPOLYGON_3D = {
    "type": "MultiPolygon25D",
    "coordinates": multipolygon_coordinates_3d,
}
GEOMETRYCOLLECTION_3D = {
    "type": "GeometryCollection",
    "geometries": [
        POINT_3D,
        LINESTRING_3D,
        POLYGON_3D,
        MULTIPOINT_3D,
        MULTILINESTRING_3D,
        MULTIPOLYGON_3D,
    ],
}


# FORMAT : geoformat geojson like + bbox
POINT_WITH_BBOX = {
    "type": "Point",
    "coordinates": point_coordinates,
    "bbox": (-115.81, 37.24, -115.81, 37.24),
}
MULTIPOINT_WITH_BBOX = {
    "type": "MultiPoint",
    "coordinates": multipoint_coordinates,
    "bbox": (-157.97, 19.61, -155.52, 21.46),
}
LINESTRING_WITH_BBOX = {
    "type": "LineString",
    "coordinates": linestring_coordinates,
    "bbox": (8.919, 44.4074, 8.923, 44.4075),
}
MULTILINESTRING_WITH_BBOX = {
    "type": "MultiLineString",
    "coordinates": multilinestring_coordinates,
    "bbox": (-130.95, -34.25, 23.15, 77.95),
}
POLYGON_WITH_BBOX = {
    "type": "Polygon",
    "coordinates": polygon_coordinates,
    "bbox": (-120.43, -20.28, 23.194, 57.322),
}
MULTIPOLYGON_WITH_BBOX = {
    "type": "MultiPolygon",
    "coordinates": multipolygon_coordinates,
    "bbox": (-130.91, -34.29, 35.12, 77.91),
}
GEOMETRYCOLLECTION_WITH_BBOX = {
    "type": "GeometryCollection",
    "geometries": [
        {
            "type": "Point",
            "coordinates": [-115.81, 37.24],
            "bbox": (-115.81, 37.24, -115.81, 37.24),
        },
        {
            "type": "LineString",
            "coordinates": [[8.919, 44.4074], [8.923, 44.4075]],
            "bbox": (8.919, 44.4074, 8.923, 44.4075),
        },
        {
            "type": "Polygon",
            "coordinates": [
                [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
            ],
            "bbox": (-120.43, -20.28, 23.194, 57.322),
        },
        {
            "type": "MultiPoint",
            "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]],
            "bbox": (-157.97, 19.61, -155.52, 21.46),
        },
        {
            "type": "MultiLineString",
            "coordinates": [
                [[3.75, 9.25], [-130.95, 1.52]],
                [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
            ],
            "bbox": (-130.95, -34.25, 23.15, 77.95),
        },
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],
                [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]],
            ],
            "bbox": (-130.91, -34.29, 35.12, 77.91),
        },
    ],
    "bbox": (-157.97, -34.29, 35.12, 77.95),
}
GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WITH_BBOX = {
    "type": "GeometryCollection",
    "geometries": [
        {"type": "Point", "coordinates": []},
        {
            "type": "LineString",
            "coordinates": [[8.919, 44.4074], [8.923, 44.4075]],
            "bbox": (8.919, 44.4074, 8.923, 44.4075),
        },
        {
            "type": "Polygon",
            "coordinates": [
                [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]],
            ],
            "bbox": (-120.43, -20.28, 23.194, 57.322),
        },
        {"type": "MultiPoint", "coordinates": []},
        {
            "type": "MultiLineString",
            "coordinates": [
                [[3.75, 9.25], [-130.95, 1.52]],
                [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
            ],
            "bbox": (-130.95, -34.25, 23.15, 77.95),
        },
        {"type": "MultiPolygon", "coordinates": []},
    ],
    "bbox": (-130.95, -34.25, 23.194, 77.95),
}

# format : WKB with big endian
POINT_WKB_BIG_ENDIAN = (
    b"\x00\x00\x00\x00\x01\xc0\\\xf3\xd7\n=p\xa4@B\x9e\xb8Q\xeb\x85\x1f"
)
POINT_EMPTY_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x01\x7f\xf8\x00\x00\x00\x00\x00\x00\x7f\xf8\x00\x00\x00\x00\x00\x00"
LINESTRING_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x02\x00\x00\x00\x02@!\xd6\x87+\x02\x0cJ@F4%\xae\xe61\xf9@!\xd8\x93t\xbcj\x7f@F4(\xf5\xc2\x8f\\"
LINESTRING_EMPTY_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x02\x00\x00\x00\x00"
POLYGON_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x04@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0@71\xa9\xfb\xe7l\x8b\xc04G\xae\x14z\xe1H\xc0^\x1b\x85\x1e\xb8Q\xec@3&fffff@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0\x00\x00\x00\x04\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3@.k\x85\x1e\xb8Q\xec\xc0%\x9e\xb8Q\xeb\x85\x1f\xc04\x82\x8f\\(\xf5\xc3?\xf8(\xf5\xc2\x8f\\)\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3"
POLYGON_EMPTY_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x03\x00\x00\x00\x00"
MULTIPOINT_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\x01\xc0cp\xa3\xd7\n=q@3\x9c(\xf5\xc2\x8f\\\x00\x00\x00\x00\x01\xc0c\x87\n=p\xa3\xd7@4\xbdp\xa3\xd7\n=\x00\x00\x00\x00\x01\xc0c\xbf\n=p\xa3\xd7@5u\xc2\x8f\\(\xf6"
MULTIPOINT_EMPTY_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x04\x00\x00\x00\x00"
MULTILINESTRING_WKB_BIG_ENDIAN = b'\x00\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\x00\x02\x00\x00\x00\x02@\x0e\x00\x00\x00\x00\x00\x00@"\x80\x00\x00\x00\x00\x00\xc0`^fffff?\xf8Q\xeb\x85\x1e\xb8R\x00\x00\x00\x00\x02\x00\x00\x00\x03@7&fffff\xc0A \x00\x00\x00\x00\x00\xbf\xf5\x99\x99\x99\x99\x99\x9a\xc0\x12\x99\x99\x99\x99\x99\x9a@\x0b\x99\x99\x99\x99\x99\x9a@S|\xcc\xcc\xcc\xcc\xcd'
MULTILINESTRING_EMPTY_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x05\x00\x00\x00\x00"
MULTIPOLYGON_WKB_BIG_ENDIAN = b'\x00\x00\x00\x00\x06\x00\x00\x00\x02\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x04@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f\xc0`]\x1e\xb8Q\xeb\x85?\xf8Q\xeb\x85\x1e\xb8R@A\x8f\\(\xf5\xc2\x8f@R\x0e\xf9\xdb"\xd0\xe5@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x04@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85\xbf\xf4\xf5\xc2\x8f\\(\xf6\xc0\x12p\xa3\xd7\n=q@\x0bG\xae\x14z\xe1H@Sz=p\xa3\xd7\n@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85'
MULTIPOLYGON_EMPTY_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x06\x00\x00\x00\x00"
GEOMETRYCOLLECTION_WKB_BIG_ENDIAN = b'\x00\x00\x00\x00\x07\x00\x00\x00\x06\x00\x00\x00\x00\x01\xc0\\\xf3\xd7\n=p\xa4@B\x9e\xb8Q\xeb\x85\x1f\x00\x00\x00\x00\x02\x00\x00\x00\x02@!\xd6\x87+\x02\x0cJ@F4%\xae\xe61\xf9@!\xd8\x93t\xbcj\x7f@F4(\xf5\xc2\x8f\\\x00\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x04@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0@71\xa9\xfb\xe7l\x8b\xc04G\xae\x14z\xe1H\xc0^\x1b\x85\x1e\xb8Q\xec@3&fffff@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0\x00\x00\x00\x04\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3@.k\x85\x1e\xb8Q\xec\xc0%\x9e\xb8Q\xeb\x85\x1f\xc04\x82\x8f\\(\xf5\xc3?\xf8(\xf5\xc2\x8f\\)\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3\x00\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\x01\xc0cp\xa3\xd7\n=q@3\x9c(\xf5\xc2\x8f\\\x00\x00\x00\x00\x01\xc0c\x87\n=p\xa3\xd7@4\xbdp\xa3\xd7\n=\x00\x00\x00\x00\x01\xc0c\xbf\n=p\xa3\xd7@5u\xc2\x8f\\(\xf6\x00\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\x00\x02\x00\x00\x00\x02@\x0e\x00\x00\x00\x00\x00\x00@"\x80\x00\x00\x00\x00\x00\xc0`^fffff?\xf8Q\xeb\x85\x1e\xb8R\x00\x00\x00\x00\x02\x00\x00\x00\x03@7&fffff\xc0A \x00\x00\x00\x00\x00\xbf\xf5\x99\x99\x99\x99\x99\x9a\xc0\x12\x99\x99\x99\x99\x99\x9a@\x0b\x99\x99\x99\x99\x99\x9a@S|\xcc\xcc\xcc\xcc\xcd\x00\x00\x00\x00\x06\x00\x00\x00\x02\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x04@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f\xc0`]\x1e\xb8Q\xeb\x85?\xf8Q\xeb\x85\x1e\xb8R@A\x8f\\(\xf5\xc2\x8f@R\x0e\xf9\xdb"\xd0\xe5@\x0e=p\xa3\xd7\n=@"\x8f\\(\xf5\xc2\x8f\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x04@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85\xbf\xf4\xf5\xc2\x8f\\(\xf6\xc0\x12p\xa3\xd7\n=q@\x0bG\xae\x14z\xe1H@Sz=p\xa3\xd7\n@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85'
GEOMETRYCOLLECTION_EMPTY_WKB_BIG_ENDIAN = b"\x00\x00\x00\x00\x07\x00\x00\x00\x00"
GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_BIG_ENDIAN = b'\x00\x00\x00\x00\x07\x00\x00\x00\x06\x00\x00\x00\x00\x01\x7f\xf8\x00\x00\x00\x00\x00\x00\x7f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x02@!\xd6\x87+\x02\x0cJ@F4%\xae\xe61\xf9@!\xd8\x93t\xbcj\x7f@F4(\xf5\xc2\x8f\\\x00\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x04@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0@71\xa9\xfb\xe7l\x8b\xc04G\xae\x14z\xe1H\xc0^\x1b\x85\x1e\xb8Q\xec@3&fffff@\x03\n=p\xa3\xd7\n@L\xa97K\xc6\xa7\xf0\x00\x00\x00\x04\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3@.k\x85\x1e\xb8Q\xec\xc0%\x9e\xb8Q\xeb\x85\x1f\xc04\x82\x8f\\(\xf5\xc3?\xf8(\xf5\xc2\x8f\\)\xc0\x14\xd7\n=p\xa3\xd7@7\x82\x8f\\(\xf5\xc3\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\x00\x02\x00\x00\x00\x02@\x0e\x00\x00\x00\x00\x00\x00@"\x80\x00\x00\x00\x00\x00\xc0`^fffff?\xf8Q\xeb\x85\x1e\xb8R\x00\x00\x00\x00\x02\x00\x00\x00\x03@7&fffff\xc0A \x00\x00\x00\x00\x00\xbf\xf5\x99\x99\x99\x99\x99\x9a\xc0\x12\x99\x99\x99\x99\x99\x9a@\x0b\x99\x99\x99\x99\x99\x9a@S|\xcc\xcc\xcc\xcc\xcd\x00\x00\x00\x00\x06\x00\x00\x00\x00'

# format : WKB with little endian
POINT_WKB_LITTLE_ENDIAN = (
    b"\x01\x01\x00\x00\x00\xa4p=\n\xd7\xf3\\\xc0\x1f\x85\xebQ\xb8\x9eB@"
)
POINT_EMPTY_WKB_LITTLE_ENDIAN = b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f"
LINESTRING_WKB_LITTLE_ENDIAN = b"\x01\x02\x00\x00\x00\x02\x00\x00\x00J\x0c\x02+\x87\xd6!@\xf91\xe6\xae%4F@\x7fj\xbct\x93\xd8!@\\\x8f\xc2\xf5(4F@"
LINESTRING_EMPTY_WKB_LITTLE_ENDIAN = b"\x01\x02\x00\x00\x00\x00\x00\x00\x00"
POLYGON_WKB_LITTLE_ENDIAN = b"\x01\x03\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x8bl\xe7\xfb\xa917@H\xe1z\x14\xaeG4\xc0\xecQ\xb8\x1e\x85\x1b^\xc0fffff&3@\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x04\x00\x00\x00\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@\xecQ\xb8\x1e\x85k.@\x1f\x85\xebQ\xb8\x9e%\xc0\xc3\xf5(\\\x8f\x824\xc0)\\\x8f\xc2\xf5(\xf8?\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@"
POLYGON_EMPTY_WKB_LITTLE_ENDIAN = b"\x01\x03\x00\x00\x00\x00\x00\x00\x00"
MULTIPOINT_WKB_LITTLE_ENDIAN = b"\x01\x04\x00\x00\x00\x03\x00\x00\x00\x01\x01\x00\x00\x00q=\n\xd7\xa3pc\xc0\\\x8f\xc2\xf5(\x9c3@\x01\x01\x00\x00\x00\xd7\xa3p=\n\x87c\xc0=\n\xd7\xa3p\xbd4@\x01\x01\x00\x00\x00\xd7\xa3p=\n\xbfc\xc0\xf6(\\\x8f\xc2u5@"
MULTIPOINT_EMPTY_WKB_LITTLE_ENDIAN = b"\x01\x04\x00\x00\x00\x00\x00\x00\x00"
MULTILINESTRING_WKB_LITTLE_ENDIAN = b'\x01\x05\x00\x00\x00\x02\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e@\x00\x00\x00\x00\x00\x80"@fffff^`\xc0R\xb8\x1e\x85\xebQ\xf8?\x01\x02\x00\x00\x00\x03\x00\x00\x00fffff&7@\x00\x00\x00\x00\x00 A\xc0\x9a\x99\x99\x99\x99\x99\xf5\xbf\x9a\x99\x99\x99\x99\x99\x12\xc0\x9a\x99\x99\x99\x99\x99\x0b@\xcd\xcc\xcc\xcc\xcc|S@'
MULTILINESTRING_EMPTY_WKB_LITTLE_ENDIAN = b"\x01\x05\x00\x00\x00\x00\x00\x00\x00"
MULTIPOLYGON_WKB_LITTLE_ENDIAN = b'\x01\x06\x00\x00\x00\x02\x00\x00\x00\x01\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x85\xebQ\xb8\x1e]`\xc0R\xb8\x1e\x85\xebQ\xf8?\x8f\xc2\xf5(\\\x8fA@\xe5\xd0"\xdb\xf9\x0eR@=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x01\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\xaeG\xe1z\x14.7@\x85\xebQ\xb8\x1e%A\xc0\xf6(\\\x8f\xc2\xf5\xf4\xbfq=\n\xd7\xa3p\x12\xc0H\xe1z\x14\xaeG\x0b@\n\xd7\xa3p=zS@\xaeG\xe1z\x14.7@\x85\xebQ\xb8\x1e%A\xc0'
MULTIPOLYGON_EMPTY_WKB_LITTLE_ENDIAN = b"\x01\x06\x00\x00\x00\x00\x00\x00\x00"
GEOMETRYCOLLECTION_WKB_LITTLE_ENDIAN = b'\x01\x07\x00\x00\x00\x06\x00\x00\x00\x01\x01\x00\x00\x00\xa4p=\n\xd7\xf3\\\xc0\x1f\x85\xebQ\xb8\x9eB@\x01\x02\x00\x00\x00\x02\x00\x00\x00J\x0c\x02+\x87\xd6!@\xf91\xe6\xae%4F@\x7fj\xbct\x93\xd8!@\\\x8f\xc2\xf5(4F@\x01\x03\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x8bl\xe7\xfb\xa917@H\xe1z\x14\xaeG4\xc0\xecQ\xb8\x1e\x85\x1b^\xc0fffff&3@\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x04\x00\x00\x00\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@\xecQ\xb8\x1e\x85k.@\x1f\x85\xebQ\xb8\x9e%\xc0\xc3\xf5(\\\x8f\x824\xc0)\\\x8f\xc2\xf5(\xf8?\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@\x01\x04\x00\x00\x00\x03\x00\x00\x00\x01\x01\x00\x00\x00q=\n\xd7\xa3pc\xc0\\\x8f\xc2\xf5(\x9c3@\x01\x01\x00\x00\x00\xd7\xa3p=\n\x87c\xc0=\n\xd7\xa3p\xbd4@\x01\x01\x00\x00\x00\xd7\xa3p=\n\xbfc\xc0\xf6(\\\x8f\xc2u5@\x01\x05\x00\x00\x00\x02\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e@\x00\x00\x00\x00\x00\x80"@fffff^`\xc0R\xb8\x1e\x85\xebQ\xf8?\x01\x02\x00\x00\x00\x03\x00\x00\x00fffff&7@\x00\x00\x00\x00\x00 A\xc0\x9a\x99\x99\x99\x99\x99\xf5\xbf\x9a\x99\x99\x99\x99\x99\x12\xc0\x9a\x99\x99\x99\x99\x99\x0b@\xcd\xcc\xcc\xcc\xcc|S@\x01\x06\x00\x00\x00\x02\x00\x00\x00\x01\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x85\xebQ\xb8\x1e]`\xc0R\xb8\x1e\x85\xebQ\xf8?\x8f\xc2\xf5(\\\x8fA@\xe5\xd0"\xdb\xf9\x0eR@=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x01\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\xaeG\xe1z\x14.7@\x85\xebQ\xb8\x1e%A\xc0\xf6(\\\x8f\xc2\xf5\xf4\xbfq=\n\xd7\xa3p\x12\xc0H\xe1z\x14\xaeG\x0b@\n\xd7\xa3p=zS@\xaeG\xe1z\x14.7@\x85\xebQ\xb8\x1e%A\xc0'
GEOMETRYCOLLECTION_EMPTY_WKB_LITTLE_ENDIAN = b"\x01\x07\x00\x00\x00\x00\x00\x00\x00"
GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_LITTLE_ENDIAN = b'\x01\x07\x00\x00\x00\x06\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\x02\x00\x00\x00\x02\x00\x00\x00J\x0c\x02+\x87\xd6!@\xf91\xe6\xae%4F@\x7fj\xbct\x93\xd8!@\\\x8f\xc2\xf5(4F@\x01\x03\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x8bl\xe7\xfb\xa917@H\xe1z\x14\xaeG4\xc0\xecQ\xb8\x1e\x85\x1b^\xc0fffff&3@\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x04\x00\x00\x00\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@\xecQ\xb8\x1e\x85k.@\x1f\x85\xebQ\xb8\x9e%\xc0\xc3\xf5(\\\x8f\x824\xc0)\\\x8f\xc2\xf5(\xf8?\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@\x01\x04\x00\x00\x00\x00\x00\x00\x00\x01\x05\x00\x00\x00\x02\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e@\x00\x00\x00\x00\x00\x80"@fffff^`\xc0R\xb8\x1e\x85\xebQ\xf8?\x01\x02\x00\x00\x00\x03\x00\x00\x00fffff&7@\x00\x00\x00\x00\x00 A\xc0\x9a\x99\x99\x99\x99\x99\xf5\xbf\x9a\x99\x99\x99\x99\x99\x12\xc0\x9a\x99\x99\x99\x99\x99\x0b@\xcd\xcc\xcc\xcc\xcc|S@\x01\x06\x00\x00\x00\x00\x00\x00\x00'

# format : WKB with varying endian in geometry
MULTIPOINT_WKB_VARYING_ENDIAN = b"\x00\x00\x00\x00\x04\x00\x00\x00\x03\x01\x01\x00\x00\x00q=\n\xd7\xa3pc\xc0\\\x8f\xc2\xf5(\x9c3@\x01\x01\x00\x00\x00\xd7\xa3p=\n\x87c\xc0=\n\xd7\xa3p\xbd4@\x01\x01\x00\x00\x00\xd7\xa3p=\n\xbfc\xc0\xf6(\\\x8f\xc2u5@"
MULTILINESTRING_WKB_VARYING_ENDIAN = b'\x00\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\x00\x02\x00\x00\x00\x02@\x0e\x00\x00\x00\x00\x00\x00@"\x80\x00\x00\x00\x00\x00\xc0`^fffff?\xf8Q\xeb\x85\x1e\xb8R\x01\x02\x00\x00\x00\x03\x00\x00\x00fffff&7@\x00\x00\x00\x00\x00 A\xc0\x9a\x99\x99\x99\x99\x99\xf5\xbf\x9a\x99\x99\x99\x99\x99\x12\xc0\x9a\x99\x99\x99\x99\x99\x0b@\xcd\xcc\xcc\xcc\xcc|S@'
MULTIPOLYGON_WKB_VARYING_ENDIAN = b'\x00\x00\x00\x00\x06\x00\x00\x00\x02\x01\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x85\xebQ\xb8\x1e]`\xc0R\xb8\x1e\x85\xebQ\xf8?\x8f\xc2\xf5(\\\x8fA@\xe5\xd0"\xdb\xf9\x0eR@=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x01\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\xaeG\xe1z\x14.7@\x85\xebQ\xb8\x1e%A\xc0\xf6(\\\x8f\xc2\xf5\xf4\xbfq=\n\xd7\xa3p\x12\xc0H\xe1z\x14\xaeG\x0b@\n\xd7\xa3p=zS@\xaeG\xe1z\x14.7@\x85\xebQ\xb8\x1e%A\xc0'
GEOMETRYCOLLECTION_WKB_VARYING_ENDIAN = b'\x00\x00\x00\x00\x07\x00\x00\x00\x06\x01\x01\x00\x00\x00\xa4p=\n\xd7\xf3\\\xc0\x1f\x85\xebQ\xb8\x9eB@\x00\x00\x00\x00\x02\x00\x00\x00\x02@!\xd6\x87+\x02\x0cJ@F4%\xae\xe61\xf9@!\xd8\x93t\xbcj\x7f@F4(\xf5\xc2\x8f\\\x01\x03\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x8bl\xe7\xfb\xa917@H\xe1z\x14\xaeG4\xc0\xecQ\xb8\x1e\x85\x1b^\xc0fffff&3@\n\xd7\xa3p=\n\x03@\xf0\xa7\xc6K7\xa9L@\x04\x00\x00\x00\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@\xecQ\xb8\x1e\x85k.@\x1f\x85\xebQ\xb8\x9e%\xc0\xc3\xf5(\\\x8f\x824\xc0)\\\x8f\xc2\xf5(\xf8?\xd7\xa3p=\n\xd7\x14\xc0\xc3\xf5(\\\x8f\x827@\x00\x00\x00\x00\x04\x00\x00\x00\x03\x01\x01\x00\x00\x00q=\n\xd7\xa3pc\xc0\\\x8f\xc2\xf5(\x9c3@\x01\x01\x00\x00\x00\xd7\xa3p=\n\x87c\xc0=\n\xd7\xa3p\xbd4@\x01\x01\x00\x00\x00\xd7\xa3p=\n\xbfc\xc0\xf6(\\\x8f\xc2u5@\x00\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\x00\x02\x00\x00\x00\x02@\x0e\x00\x00\x00\x00\x00\x00@"\x80\x00\x00\x00\x00\x00\xc0`^fffff?\xf8Q\xeb\x85\x1e\xb8R\x01\x02\x00\x00\x00\x03\x00\x00\x00fffff&7@\x00\x00\x00\x00\x00 A\xc0\x9a\x99\x99\x99\x99\x99\xf5\xbf\x9a\x99\x99\x99\x99\x99\x12\xc0\x9a\x99\x99\x99\x99\x99\x0b@\xcd\xcc\xcc\xcc\xcc|S@\x00\x00\x00\x00\x06\x00\x00\x00\x02\x01\x03\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x85\xebQ\xb8\x1e]`\xc0R\xb8\x1e\x85\xebQ\xf8?\x8f\xc2\xf5(\\\x8fA@\xe5\xd0"\xdb\xf9\x0eR@=\n\xd7\xa3p=\x0e@\x8f\xc2\xf5(\\\x8f"@\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x04@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85\xbf\xf4\xf5\xc2\x8f\\(\xf6\xc0\x12p\xa3\xd7\n=q@\x0bG\xae\x14z\xe1H@Sz=p\xa3\xd7\n@7.\x14z\xe1G\xae\xc0A%\x1e\xb8Q\xeb\x85'

# format : WKB in hexa
POINT_WKB_HEX_BIG_ENDIAN = POINT_WKB_BIG_ENDIAN.hex()
POINT_EMPTY_WKB_HEX_BIG_ENDIAN = POINT_EMPTY_WKB_BIG_ENDIAN.hex()
LINESTRING_WKB_HEX_BIG_ENDIAN = LINESTRING_WKB_BIG_ENDIAN.hex()
LINESTRING_EMPTY_WKB_HEX_BIG_ENDIAN = LINESTRING_EMPTY_WKB_BIG_ENDIAN.hex()
POLYGON_WKB_HEX_BIG_ENDIAN = POLYGON_WKB_BIG_ENDIAN.hex()
POLYGON_EMPTY_WKB_HEX_BIG_ENDIAN = POLYGON_EMPTY_WKB_BIG_ENDIAN.hex()
MULTIPOINT_WKB_HEX_BIG_ENDIAN = MULTIPOINT_WKB_BIG_ENDIAN.hex()
MULTIPOINT_EMPTY_WKB_HEX_BIG_ENDIAN = MULTIPOINT_EMPTY_WKB_BIG_ENDIAN.hex()
MULTILINESTRING_WKB_HEX_BIG_ENDIAN = MULTILINESTRING_WKB_BIG_ENDIAN.hex()
MULTILINESTRING_EMPTY_WKB_HEX_BIG_ENDIAN = MULTILINESTRING_EMPTY_WKB_BIG_ENDIAN.hex()
MULTIPOLYGON_WKB_HEX_BIG_ENDIAN = MULTIPOLYGON_WKB_BIG_ENDIAN.hex()
MULTIPOLYGON_EMPTY_WKB_HEX_BIG_ENDIAN = MULTIPOLYGON_EMPTY_WKB_BIG_ENDIAN.hex()
GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN = GEOMETRYCOLLECTION_WKB_BIG_ENDIAN.hex()
GEOMETRYCOLLECTION_EMPTY_WKB_HEX_BIG_ENDIAN = (
    GEOMETRYCOLLECTION_EMPTY_WKB_BIG_ENDIAN.hex()
)
GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_HEX_BIG_ENDIAN = (
    GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_BIG_ENDIAN.hex()
)

# format : WKT
POINT_WKT = "POINT (-115.81 37.24)"
POINT_EMPTY_WKT = "POINT EMPTY"
LINESTRING_WKT = "LINESTRING (8.919 44.4074,8.923 44.4075)"
LINESTRING_EMPTY_WKT = "LINESTRING EMPTY"
POLYGON_WKT = "POLYGON ((2.38 57.322,23.194 -20.28,-120.43 19.15,2.38 57.322),(-5.21 23.51,15.21 -10.81,-20.51 1.51,-5.21 23.51))"
POLYGON_EMPTY_WKT = "POLYGON EMPTY"
MULTIPOINT_WKT = "MULTIPOINT (-155.52 19.61,-156.22 20.74,-157.97 21.46)"
MULTIPOINT_2_WKT = "MULTIPOINT ((-155.52 19.61),(-156.22 20.74),(-157.97 21.46))"
MULTIPOINT_EMPTY_WKT = "MULTIPOINT EMPTY"
MULTILINESTRING_WKT = (
    "MULTILINESTRING ((3.75 9.25,-130.95 1.52),(23.15 -34.25,-1.35 -4.65,3.45 77.95))"
)
MULTILINESTRING_EMPTY_WKT = "MULTILINESTRING EMPTY"
MULTIPOLYGON_WKT = "MULTIPOLYGON (((3.78 9.28,-130.91 1.52,35.12 72.234,3.78 9.28)),((23.18 -34.29,-1.31 -4.61,3.41 77.91,23.18 -34.29)))"
MULTIPOLYGON_EMPTY_WKT = "MULTIPOLYGON EMPTY"
GEOMETRYCOLLECTION_WKT = "GEOMETRYCOLLECTION (POINT (-115.81 37.24),LINESTRING (8.919 44.4074,8.923 44.4075),POLYGON ((2.38 57.322,23.194 -20.28,-120.43 19.15,2.38 57.322),(-5.21 23.51,15.21 -10.81,-20.51 1.51,-5.21 23.51)),MULTIPOINT (-155.52 19.61,-156.22 20.74,-157.97 21.46),MULTILINESTRING ((3.75 9.25,-130.95 1.52),(23.15 -34.25,-1.35 -4.65,3.45 77.95)),MULTIPOLYGON (((3.78 9.28,-130.91 1.52,35.12 72.234,3.78 9.28)),((23.18 -34.29,-1.31 -4.61,3.41 77.91,23.18 -34.29))))"
GEOMETRYCOLLECTION_EMPTY_WKT = "GEOMETRYCOLLECTION EMPTY"
GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT = "GEOMETRYCOLLECTION (POINT EMPTY,LINESTRING (8.919 44.4074,8.923 44.4075),POLYGON ((2.38 57.322,23.194 -20.28,-120.43 19.15,2.38 57.322),(-5.21 23.51,15.21 -10.81,-20.51 1.51,-5.21 23.51)),MULTIPOINT EMPTY,MULTILINESTRING ((3.75 9.25,-130.95 1.52),(23.15 -34.25,-1.35 -4.65,3.45 77.95)),MULTIPOLYGON EMPTY)"

# "true" geometries
POINT_paris = {"type": "Point", "coordinates": paris_4326}

# loire
LINESTRING_loire = {
    "type": "LineString",
    "coordinates": loire_4326
}

POLYGON_france = {
    "type": "Polygon",
    "coordinates": france_4326,
}


MULTIPOINT_paris_tokyo = {
    "type": "MultiPoint",
    "coordinates": [paris_4326, tokyo_4326]
}

MULTILINESTRING_loire_katsuragawa_river = {
    "type": "MultiLineString",
    "coordinates": [loire_4326, katsuragawa_river_4326]}


MULTIPOLYGON_france_japan = {
    "type": "MultiPolygon",
    "coordinates": [france_4326, japan_4326]
}

GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan = {
    "type": "GeometryCollection",
    "geometries": [
        MULTIPOINT_paris_tokyo,
        MULTILINESTRING_loire_katsuragawa_river,
        MULTIPOLYGON_france_japan
    ]
}

POINT_paris_3857 = {
    "type": "Point",
    "coordinates": paris_3857,
}
MULTIPOINT_paris_tokyo_3857 = {
    "type": "MultiPoint",
    "coordinates": [paris_3857, tokyo_3857]
}
LINESTRING_loire_3857 = {"type": "LineString", "coordinates": loire_3857}

MULTILINESTRING_loire_katsuragawa_river_3857 = {
    "type": "MultiLineString",
    "coordinates":  [loire_3857, katsuragawa_river_3857]
}
POLYGON_france_3857 = {
    "type": "Polygon",
    "coordinates": france_3857,
}
MULTIPOLYGON_france_japan_3857 = {
    "type": "MultiPolygon",
    "coordinates": [france_3857, japan_3857]
}
GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan_3857 = {
    "type": "GeometryCollection",
    "geometries": [
        MULTIPOINT_paris_tokyo_3857,
        MULTILINESTRING_loire_katsuragawa_river_3857,
        MULTIPOLYGON_france_japan
    ],
}

# testing geometry

test_polygon_a = {
    "type": "Polygon",
    "coordinates": [[[-2, -2], [-2, 2], [2, 2], [2, -2], [-2, -2]]],
}
test_polygon_b = {
    "type": "Polygon",
    "coordinates": [[[-1, -3], [-1, 1], [3, 1], [3, -3], [-1, -3]]],
}
test_polygon_c = {
    "type": "Polygon",
    "coordinates": [[[2, 2], [2, 4], [4, 4], [4, 2], [2, 2]]],
}



