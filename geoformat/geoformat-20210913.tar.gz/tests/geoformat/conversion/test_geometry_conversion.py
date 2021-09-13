from geoformat.conversion.geometry_conversion import (
    geometry_type_to_2d_geometry_type,
    geometry_to_2d_geometry,
    geometry_to_geometry_collection,
    single_geometry_to_multi_geometry,
    multi_geometry_to_single_geometry,
    geometry_to_multi_geometry,
    wkb_to_geometry,
    geometry_to_wkb,
    wkt_to_geometry,
    geometry_to_wkt,
    force_rhr,
    geometry_to_bbox,
    reproject_geometry,
    geometry_to_ogr_geometry,
    ogr_geometry_to_geometry
)

from tests.data.geometries import (
    POINT,
    POINT_EMPTY,
    MULTIPOINT,
    MULTIPOINT_EMPTY,
    LINESTRING,
    LINESTRING_EMPTY,
    MULTILINESTRING,
    MULTILINESTRING_EMPTY,
    POLYGON,
    POLYGON_EMPTY,
    MULTIPOLYGON,
    MULTIPOLYGON_EMPTY,
    GEOMETRYCOLLECTION,
    GEOMETRYCOLLECTION_EMPTY,
    GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
    POINT_WITH_BBOX,
    MULTIPOINT_WITH_BBOX,
    LINESTRING_WITH_BBOX,
    MULTILINESTRING_WITH_BBOX,
    POLYGON_WITH_BBOX,
    MULTIPOLYGON_WITH_BBOX,
    GEOMETRYCOLLECTION_WITH_BBOX,
    GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WITH_BBOX,
    POINT_WKB_BIG_ENDIAN,
    LINESTRING_WKB_BIG_ENDIAN,
    POLYGON_WKB_BIG_ENDIAN,
    MULTIPOINT_WKB_BIG_ENDIAN,
    MULTILINESTRING_WKB_BIG_ENDIAN,
    MULTIPOLYGON_WKB_BIG_ENDIAN,
    GEOMETRYCOLLECTION_WKB_BIG_ENDIAN,
    POINT_WKB_LITTLE_ENDIAN,
    LINESTRING_WKB_LITTLE_ENDIAN,
    POLYGON_WKB_LITTLE_ENDIAN,
    MULTIPOINT_WKB_LITTLE_ENDIAN,
    MULTILINESTRING_WKB_LITTLE_ENDIAN,
    MULTIPOLYGON_WKB_LITTLE_ENDIAN,
    GEOMETRYCOLLECTION_WKB_LITTLE_ENDIAN,
    MULTIPOINT_WKB_VARYING_ENDIAN,
    MULTILINESTRING_WKB_VARYING_ENDIAN,
    MULTIPOLYGON_WKB_VARYING_ENDIAN,
    GEOMETRYCOLLECTION_WKB_VARYING_ENDIAN,
    POINT_EMPTY_WKB_BIG_ENDIAN,
    POINT_EMPTY_WKB_LITTLE_ENDIAN,
    LINESTRING_EMPTY_WKB_BIG_ENDIAN,
    LINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
    POLYGON_EMPTY_WKB_BIG_ENDIAN,
    POLYGON_EMPTY_WKB_LITTLE_ENDIAN,
    MULTIPOINT_EMPTY_WKB_BIG_ENDIAN,
    MULTIPOINT_EMPTY_WKB_LITTLE_ENDIAN,
    MULTILINESTRING_EMPTY_WKB_BIG_ENDIAN,
    MULTILINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
    MULTIPOLYGON_EMPTY_WKB_BIG_ENDIAN,
    MULTIPOLYGON_EMPTY_WKB_LITTLE_ENDIAN,
    GEOMETRYCOLLECTION_EMPTY_WKB_BIG_ENDIAN,
    GEOMETRYCOLLECTION_EMPTY_WKB_LITTLE_ENDIAN,
    GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_BIG_ENDIAN,
    GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_LITTLE_ENDIAN,
    POINT_WKT,
    POINT_EMPTY_WKT,
    LINESTRING_WKT,
    LINESTRING_EMPTY_WKT,
    POLYGON_WKT,
    POLYGON_EMPTY_WKT,
    MULTIPOINT_WKT,
    MULTIPOINT_EMPTY_WKT,
    MULTILINESTRING_WKT,
    MULTILINESTRING_EMPTY_WKT,
    MULTIPOLYGON_WKT,
    MULTIPOLYGON_EMPTY_WKT,
    GEOMETRYCOLLECTION_WKT,
    GEOMETRYCOLLECTION_EMPTY_WKT,
    GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT,
    POINT_3D,
    LINESTRING_3D,
    POLYGON_3D,
    MULTIPOINT_3D,
    MULTILINESTRING_3D,
    MULTIPOLYGON_3D,
    GEOMETRYCOLLECTION_3D,
    POINT_paris,
    LINESTRING_loire,
    POLYGON_france,
    MULTIPOINT_paris_tokyo,
    MULTILINESTRING_loire_katsuragawa_river,
    MULTIPOLYGON_france_japan,
    GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan,
    POINT_paris_3857,
    MULTIPOINT_paris_tokyo_3857,
    LINESTRING_loire_3857,
    MULTILINESTRING_loire_katsuragawa_river_3857,
    POLYGON_france_3857,
    MULTIPOLYGON_france_japan_3857,
    GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan_3857,
)

from test_all import (
    test_function,
    test_dependencies
)

try:
    from osgeo import ogr
except ImportError:
    pass


geometry_type_to_2d_geometry_type_parameters = {
    0: {
        "geometry_type": "POINT",
        "return_value": "Point"
    },
    1: {
        "geometry_type": "Linestring",
        "return_value": "LineString"
    },
    2: {
        "geometry_type": "Polygon",
        "return_value": "Polygon"
    },
    3: {
        "geometry_type": "multipoint",
        "return_value": "MultiPoint"
    },
    4: {
        "geometry_type": "MultiLInestring",
        "return_value": "MultiLineString"
    },
    5: {
        "geometry_type": "MultiPolygon",
        "return_value": "MultiPolygon"
    },
    6: {
        "geometry_type": "MultiPolygon",
        "return_value": "MultiPolygon"
    },
    7: {
        "geometry_type": "GEOMETRYCOLLECTION",
        "return_value": "GeometryCollection"
    },
    8: {
        "geometry_type": "Point25D",
        "return_value": "Point"
    },
    9: {
        "geometry_type": "LineString25D",
        "return_value": "LineString"
    },
    10: {
        "geometry_type": "Polygon25D",
        "return_value": "Polygon"
    },
    11: {
        "geometry_type": "MultiPoint25D",
        "return_value": "MultiPoint"
    },
    12: {
        "geometry_type": "MultiLineString25D",
        "return_value": "MultiLineString"
    },
    13: {
        "geometry_type": "MultiPolygon25D",
        "return_value": "MultiPolygon"
    },
}

geometry_to_2d_geometry_parameters = {
    0: {
        "geometry": POINT_3D,
        "bbox": False,
        "return_value": POINT
    },
    1: {
        "geometry": LINESTRING_3D,
        "bbox": False,
        "return_value": LINESTRING
    },
    2: {
        "geometry": POLYGON_3D,
        "bbox": False,
        "return_value": POLYGON
    },
    3: {
        "geometry": MULTIPOINT_3D,
        "bbox": False,
        "return_value": MULTIPOINT
    },
    4: {
        "geometry": MULTILINESTRING_3D,
        "bbox": False,
        "return_value": MULTILINESTRING
    },
    5: {
        "geometry": MULTIPOLYGON_3D,
        "bbox": False,
        "return_value": MULTIPOLYGON
    },
    6: {
        "geometry": GEOMETRYCOLLECTION_3D,
        "bbox": False,
        "return_value": GEOMETRYCOLLECTION
    }
}

geometry_to_geometry_collection_parameters = {
    0: {
        "geometry": POINT,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [POINT_WITH_BBOX], "bbox": POINT_WITH_BBOX['bbox']}
    },
    1: {
        "geometry": LINESTRING,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [LINESTRING_WITH_BBOX], "bbox": LINESTRING_WITH_BBOX['bbox']}
    },
    2: {
        "geometry": POLYGON,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [POLYGON_WITH_BBOX], "bbox": POLYGON_WITH_BBOX['bbox']}
    },
    3: {
        "geometry": MULTIPOINT,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [MULTIPOINT_WITH_BBOX], "bbox": MULTIPOINT_WITH_BBOX['bbox']}
    },
    4: {
        "geometry": MULTILINESTRING,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [MULTILINESTRING_WITH_BBOX], "bbox": MULTILINESTRING_WITH_BBOX['bbox']}
    },
    5: {
        "geometry": MULTIPOLYGON,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [MULTIPOLYGON_WITH_BBOX], "bbox": MULTIPOLYGON_WITH_BBOX['bbox']}
    },
    6: {
        "geometry": GEOMETRYCOLLECTION,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": GEOMETRYCOLLECTION_WITH_BBOX
    },
    7: {
        "geometry": POINT_EMPTY,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [POINT_EMPTY]}
    },
    8: {
        "geometry": LINESTRING_EMPTY,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [LINESTRING_EMPTY]}
    },
    9: {
        "geometry": POLYGON_EMPTY,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [POLYGON_EMPTY]}
    },
    10: {
        "geometry": MULTIPOINT_EMPTY,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [MULTIPOINT_EMPTY]}
    },
    11: {
        "geometry": MULTILINESTRING_EMPTY,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [MULTILINESTRING_EMPTY]}
    },
    12: {
        "geometry": MULTIPOLYGON_EMPTY,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {"type": "GeometryCollection", "geometries": [MULTIPOLYGON_EMPTY]}
    },
    13: {
        "geometry": GEOMETRYCOLLECTION_EMPTY,
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": GEOMETRYCOLLECTION_EMPTY
    },
    14: {
        "geometry": {'type': 'GeometryCollection', 'geometries': [{'type': 'Polygon', 'coordinates': []}]},
        "geometry_type_filter": None,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'Polygon', 'coordinates': []}]}
    },
    15: {
        "geometry": GEOMETRYCOLLECTION,
        "geometry_type_filter": None,
        "bbox": False,
        "return_value": GEOMETRYCOLLECTION
    }
}

geometry_to_multi_geometry_parameters = {
    0: {"geometry": POINT,
        "bbox": False,
        "return_value": {'type': "MultiPoint", "coordinates": [POINT['coordinates']]}
    },
    1: {"geometry": LINESTRING,
        "bbox": False,
        "return_value": {"type": "MultiLineString", "coordinates": [LINESTRING['coordinates']]}
    },
    2: {"geometry": POLYGON,
        "bbox": False,
        "return_value":  {"type": "MultiPolygon", "coordinates": [POLYGON['coordinates']]}
    },
    3: {
        "geometry": MULTIPOINT,
        "bbox": False,
        "return_value": MULTIPOINT
    },
    4: {
        "geometry": MULTILINESTRING,
        "bbox": False,
        "return_value": MULTILINESTRING
    },
    5: {
        "geometry": MULTIPOLYGON,
        "bbox": False,
        "return_value": MULTIPOLYGON
    },
    6: {
        "geometry": GEOMETRYCOLLECTION,
        "bbox": False,
        "return_value": {"type": "GeometryCollection", "geometries": [
            {"type": "MultiPoint", "coordinates": [[-115.81, 37.24]]},
            {"type": "MultiLineString", "coordinates": [[[8.919, 44.4074], [8.923, 44.4075]]]},
            {"type": "MultiPolygon", "coordinates": [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]]},
            {"type": "MultiPoint", "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]},
            {"type": "MultiLineString", "coordinates": [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]},
            {"type": "MultiPolygon", "coordinates": [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]}
        ]
        }
    },
    7: {"geometry": POINT,
        "bbox": True,
        "return_value": {'type': "MultiPoint", "coordinates": [POINT_WITH_BBOX['coordinates']], "bbox": POINT_WITH_BBOX["bbox"]}
        },
    8: {"geometry": LINESTRING,
        "bbox": True,
        "return_value": {"type": "MultiLineString", "coordinates": [LINESTRING_WITH_BBOX['coordinates']], "bbox": LINESTRING_WITH_BBOX["bbox"]}
        },
    9: {"geometry": POLYGON,
        "bbox": True,
        "return_value": {"type": "MultiPolygon", "coordinates": [POLYGON_WITH_BBOX['coordinates']], "bbox": POLYGON_WITH_BBOX["bbox"]}
        },
    10: {
        "geometry": MULTIPOINT,
        "bbox": True,
        "return_value": MULTIPOINT_WITH_BBOX
    },
    11: {
        "geometry": MULTILINESTRING,
        "bbox": True,
        "return_value": MULTILINESTRING_WITH_BBOX
    },
    12: {
        "geometry": MULTIPOLYGON,
        "bbox": True,
        "return_value": MULTIPOLYGON_WITH_BBOX
    },
    13: {
        "geometry": GEOMETRYCOLLECTION,
        "bbox": True,
        "return_value": {'type': 'GeometryCollection',
                         'geometries': [
                            {'type': 'MultiPoint', 'coordinates': [[-115.81, 37.24]], 'bbox': (-115.81, 37.24, -115.81, 37.24)},
                            {'type': 'MultiLineString', 'coordinates': [[[8.919, 44.4074], [8.923, 44.4075]]], 'bbox': (8.919, 44.4074, 8.923, 44.4075)},
                            {'type': 'MultiPolygon', 'coordinates': [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]], 'bbox': (-120.43, -20.28, 23.194, 57.322)},
                            {'type': 'MultiPoint', 'coordinates': [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]], 'bbox': (-157.97, 19.61, -155.52, 21.46)},
                            {'type': 'MultiLineString', 'coordinates': [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]], 'bbox': (-130.95, -34.25, 23.15, 77.95)},
                            {'type': 'MultiPolygon', 'coordinates': [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]], 'bbox': (-130.91, -34.29, 35.12, 77.91)}
                        ],
                        'bbox': (-157.97, -34.29, 35.12, 77.95)}
    },
}

single_geometry_to_multi_geometry_parameters = {
    0: {
        "geometry": POINT,
        "bbox": False,
        "return_value": {"type": "MultiPoint", "coordinates": [POINT["coordinates"]]}
    },
    1: {
        "geometry": LINESTRING,
        "bbox": False,
        "return_value": {"type": "MultiLineString", "coordinates": [LINESTRING["coordinates"]]}
    },
    2: {
        "geometry": POLYGON,
        "bbox": False,
        "return_value": {"type": "MultiPolygon", "coordinates": [POLYGON["coordinates"]]}
    },
    3: {
        "geometry": GEOMETRYCOLLECTION,
        "bbox": False,
        "return_value": {"type": "GeometryCollection", "geometries": [{"type": "MultiPoint", "coordinates": [[-115.81, 37.24]]}, {"type": "MultiLineString", "coordinates": [[[8.919, 44.4074], [8.923, 44.4075]]]}, {"type": "MultiPolygon", "coordinates": [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]]}, {"type": "MultiPoint", "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]}, {"type": "MultiLineString", "coordinates": [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]}, {"type": "MultiPolygon", "coordinates": [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]}]}
    },
    4: {
        "geometry": POINT,
        "bbox": True,
        "return_value": {"type": "MultiPoint", "coordinates": [POINT["coordinates"]], "bbox": POINT_WITH_BBOX['bbox']}
    },
    5: {
        "geometry": LINESTRING,
        "bbox": True,
        "return_value": {"type": "MultiLineString", "coordinates": [LINESTRING["coordinates"]], "bbox": LINESTRING_WITH_BBOX['bbox']}
    },
    6: {
        "geometry": POLYGON,
        "bbox": True,
        "return_value": {"type": "MultiPolygon", "coordinates": [POLYGON["coordinates"]], "bbox": POLYGON_WITH_BBOX['bbox']}
    },
    7: {
        "geometry": GEOMETRYCOLLECTION,
        "bbox": True,
        "return_value": {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "MultiPoint",
                    "coordinates": [[-115.81, 37.24]],
                    "bbox": GEOMETRYCOLLECTION_WITH_BBOX['geometries'][0]['bbox']
                },
                {
                    "type": "MultiLineString",
                    "coordinates": [[[8.919, 44.4074], [8.923, 44.4075]]],
                    "bbox": GEOMETRYCOLLECTION_WITH_BBOX['geometries'][1]['bbox']
                },
                {
                    "type": "MultiPolygon",
                    "coordinates": [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]],
                    "bbox": GEOMETRYCOLLECTION_WITH_BBOX['geometries'][2]['bbox']
                },
                {
                    "type": "MultiPoint",
                    "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]],
                    "bbox": GEOMETRYCOLLECTION_WITH_BBOX['geometries'][3]['bbox']
                },
                {
                    "type": "MultiLineString",
                    "coordinates": [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]],
                    "bbox": GEOMETRYCOLLECTION_WITH_BBOX['geometries'][4]['bbox']
                },
                {
                    "type": "MultiPolygon",
                    "coordinates": [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]],
                    "bbox": GEOMETRYCOLLECTION_WITH_BBOX['geometries'][5]['bbox']
                }
            ],
        "bbox": GEOMETRYCOLLECTION_WITH_BBOX['bbox']
        }
    },
}

multi_geometry_to_single_geometry_parameters = {
    0: {"geometry": POINT,
        "bbox": False,
        "return_value": (POINT,)},
    1: {"geometry": LINESTRING,
        "bbox": False,
        "return_value": (LINESTRING,)},
    2: {"geometry": POLYGON,
        "bbox": False,
        "return_value": (POLYGON,)},
    3: {
        "geometry": MULTIPOINT,
        "bbox": False,
        "return_value": (
            {"type": "Point", "coordinates": [-155.52, 19.61]},
            {"type": "Point", "coordinates": [-156.22, 20.74]},
            {"type": "Point", "coordinates": [-157.97, 21.46]},
        ),
    },
    4: {
        "geometry": MULTILINESTRING,
        "bbox": False,
        "return_value": (
            {"type": "LineString", "coordinates": [[3.75, 9.25], [-130.95, 1.52]]},
            {
                "type": "LineString",
                "coordinates": [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]],
            },
        ),
    },
    5: {
        "geometry": MULTIPOLYGON,
        "bbox": False,
        "return_value": (
            {
                "type": "Polygon",
                "coordinates": [
                    [[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]
                ],
            },
            {
                "type": "Polygon",
                "coordinates": [
                    [[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]
                ],
            },
        ),
    },
    6: {
        "geometry": GEOMETRYCOLLECTION,
        "bbox": False,
        "return_value": (
            {"type": "Point", "coordinates": [-115.81, 37.24]},
            {"type": "LineString", "coordinates": [[8.919, 44.4074], [8.923, 44.4075]]},
            {"type": "Polygon", "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]},
            {"type": "Point", "coordinates": [-155.52, 19.61]},
            {"type": "Point", "coordinates": [-156.22, 20.74]},
            {"type": "Point", "coordinates": [-157.97, 21.46]},
            {"type": "LineString", "coordinates": [[3.75, 9.25], [-130.95, 1.52]]},
            {"type": "LineString", "coordinates": [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]},
            {"type": "Polygon", "coordinates": [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]]},
            {"type": "Polygon", "coordinates": [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]}
        )
    },
    7: {"geometry": POINT,
        "bbox": True,
        "return_value": (POINT_WITH_BBOX,)},
    8: {"geometry": LINESTRING,
        "bbox": True,
        "return_value": (LINESTRING_WITH_BBOX,)},
    9: {"geometry": POLYGON,
        "bbox": True,
        "return_value": (POLYGON_WITH_BBOX,)},
    10: {
        "geometry": MULTIPOINT,
        "bbox": True,
        "return_value": (
            {"type": "Point", "coordinates": [-155.52, 19.61], "bbox": (-155.52, 19.61, -155.52, 19.61)},
            {"type": "Point", "coordinates": [-156.22, 20.74], "bbox": (-156.22, 20.74, -156.22, 20.74)},
            {"type": "Point", "coordinates": [-157.97, 21.46], "bbox": (-157.97, 21.46, -157.97, 21.46)},
        ),
    },
    11: {
        "geometry": MULTILINESTRING,
        "bbox": True,
        "return_value": (
            {"type": "LineString", "coordinates": [[3.75, 9.25], [-130.95, 1.52]], "bbox": (-130.95, 1.52, 3.75, 9.25)},
            {"type": "LineString", "coordinates": [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]], "bbox": (-1.35, -34.25, 23.15, 77.95)},
        ),
    },
    12: {
        "geometry": MULTIPOLYGON,
        "bbox": True,
        "return_value": (
            {"type": "Polygon", "coordinates": [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], "bbox": (-130.91, 1.52, 35.12, 72.234)},
            {"type": "Polygon", "coordinates": [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]], "bbox": (-1.31, -34.29, 23.18, 77.91)},
        ),
    },
    13: {
        "geometry": GEOMETRYCOLLECTION,
        "bbox": True,
        "return_value": (
            {"type": "Point", "coordinates": [-115.81, 37.24], "bbox": (-115.81, 37.24, -115.81, 37.24)},
            {"type": "LineString", "coordinates": [[8.919, 44.4074], [8.923, 44.4075]], "bbox": (8.919, 44.4074, 8.923, 44.4075)},
            {"type": "Polygon", "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                                                [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]],
                "bbox": (-120.43, -20.28, 23.194, 57.322)},
            {"type": "Point", "coordinates": [-155.52, 19.61], "bbox": (-155.52, 19.61, -155.52, 19.61)},
            {"type": "Point", "coordinates": [-156.22, 20.74], "bbox": (-156.22, 20.74, -156.22, 20.74)},
            {"type": "Point", "coordinates": [-157.97, 21.46], "bbox": (-157.97, 21.46, -157.97, 21.46)},
            {"type": "LineString", "coordinates": [[3.75, 9.25], [-130.95, 1.52]], "bbox": (-130.95, 1.52, 3.75, 9.25)},
            {"type": "LineString", "coordinates": [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]], "bbox": (-1.35, -34.25, 23.15, 77.95)},
            {"type": "Polygon", "coordinates": [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], "bbox": (-130.91, 1.52, 35.12, 72.234)},
            {"type": "Polygon", "coordinates": [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]], "bbox": (-1.31, -34.29, 23.18, 77.91)}
        ),
    },
}

geometry_to_wkb_parameters = {
    0: {
        "geometry": POINT,
        "endian_big": True,
        "return_value": POINT_WKB_BIG_ENDIAN
    },
    1: {
        "geometry": LINESTRING,
        "endian_big": True,
        "return_value": LINESTRING_WKB_BIG_ENDIAN,
    },
    2: {
        "geometry": POLYGON,
        "endian_big": True,
        "return_value": POLYGON_WKB_BIG_ENDIAN,
    },
    3: {
        "geometry": MULTIPOINT,
        "endian_big": True,
        "return_value": MULTIPOINT_WKB_BIG_ENDIAN,
    },
    4: {
        "geometry": MULTILINESTRING,
        "endian_big": True,
        "return_value": MULTILINESTRING_WKB_BIG_ENDIAN,
    },
    5: {
        "geometry": MULTIPOLYGON,
        "endian_big": True,
        "return_value": MULTIPOLYGON_WKB_BIG_ENDIAN,
    },
    6: {
        "geometry": GEOMETRYCOLLECTION,
        "endian_big": True,
        "return_value": GEOMETRYCOLLECTION_WKB_BIG_ENDIAN,
    },
    7: {
        "geometry": POINT,
        "endian_big": False,
        "return_value": POINT_WKB_LITTLE_ENDIAN,
    },
    8: {
        "geometry": LINESTRING,
        "endian_big": False,
        "return_value": LINESTRING_WKB_LITTLE_ENDIAN,
    },
    9: {
        "geometry": POLYGON,
        "endian_big": False,
        "return_value": POLYGON_WKB_LITTLE_ENDIAN,
    },
    10: {
        "geometry": MULTIPOINT,
        "endian_big": False,
        "return_value": MULTIPOINT_WKB_LITTLE_ENDIAN,
    },
    11: {
        "geometry": MULTILINESTRING,
        "endian_big": False,
        "return_value": MULTILINESTRING_WKB_LITTLE_ENDIAN,
    },
    12: {
        "geometry": MULTIPOLYGON,
        "endian_big": False,
        "return_value": MULTIPOLYGON_WKB_LITTLE_ENDIAN,
    },
    13: {
        "geometry": GEOMETRYCOLLECTION,
        "endian_big": False,
        "return_value": GEOMETRYCOLLECTION_WKB_LITTLE_ENDIAN,
    },
    14: {
        "geometry": POINT_EMPTY,
        "endian_big": True,
        "return_value": POINT_EMPTY_WKB_BIG_ENDIAN,
    },
    15: {
        "geometry": LINESTRING_EMPTY,
        "endian_big": True,
        "return_value": LINESTRING_EMPTY_WKB_BIG_ENDIAN,
    },
    16: {
        "geometry": POLYGON_EMPTY,
        "endian_big": True,
        "return_value": POLYGON_EMPTY_WKB_BIG_ENDIAN,
    },
    17: {
        "geometry": MULTIPOINT_EMPTY,
        "endian_big": True,
        "return_value": MULTIPOINT_EMPTY_WKB_BIG_ENDIAN,
    },
    18: {
        "geometry": MULTILINESTRING_EMPTY,
        "endian_big": True,
        "return_value": MULTILINESTRING_EMPTY_WKB_BIG_ENDIAN,
    },
    19: {
        "geometry": MULTIPOLYGON_EMPTY,
        "endian_big": True,
        "return_value": MULTIPOLYGON_EMPTY_WKB_BIG_ENDIAN,
    },
    20: {
        "geometry": GEOMETRYCOLLECTION_EMPTY,
        "endian_big": True,
        "return_value": GEOMETRYCOLLECTION_EMPTY_WKB_BIG_ENDIAN,
    },
    21: {
        "geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
        "endian_big": True,
        "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_BIG_ENDIAN,
    },
    22: {
        "geometry": POINT_EMPTY,
        "endian_big": False,
        "return_value": POINT_EMPTY_WKB_LITTLE_ENDIAN,
    },
    23: {
        "geometry": LINESTRING_EMPTY,
        "endian_big": False,
        "return_value": LINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
    },
    24: {
        "geometry": POLYGON_EMPTY,
        "endian_big": False,
        "return_value": POLYGON_EMPTY_WKB_LITTLE_ENDIAN,
    },
    25: {
        "geometry": MULTIPOINT_EMPTY,
        "endian_big": False,
        "return_value": MULTIPOINT_EMPTY_WKB_LITTLE_ENDIAN,
    },
    26: {
        "geometry": MULTILINESTRING_EMPTY,
        "endian_big": False,
        "return_value": MULTILINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
    },
    27: {
        "geometry": MULTIPOLYGON_EMPTY,
        "endian_big": False,
        "return_value": MULTIPOLYGON_EMPTY_WKB_LITTLE_ENDIAN,
    },
    28: {
        "geometry": GEOMETRYCOLLECTION_EMPTY,
        "endian_big": False,
        "return_value": GEOMETRYCOLLECTION_EMPTY_WKB_LITTLE_ENDIAN,
    },
    29: {
        "geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
        "endian_big": False,
        "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_LITTLE_ENDIAN,
    },
}

wkb_to_geometry_parameters = {
    0: {
        "wkb_geometry": POINT_WKB_BIG_ENDIAN,
        "return_value": POINT,
        "bbox": False
    },
    1: {
        "wkb_geometry": LINESTRING_WKB_BIG_ENDIAN,
        "return_value": LINESTRING,
        "bbox": False
    },
    2: {
        "wkb_geometry": POLYGON_WKB_BIG_ENDIAN,
        "return_value": POLYGON,
        "bbox": False
    },
    3: {
        "wkb_geometry": MULTIPOINT_WKB_BIG_ENDIAN,
        "return_value": MULTIPOINT,
        "bbox": False
    },
    4: {
        "wkb_geometry": MULTILINESTRING_WKB_BIG_ENDIAN,
        "return_value": MULTILINESTRING,
        "bbox": False
    },
    5: {
        "wkb_geometry": MULTIPOLYGON_WKB_BIG_ENDIAN,
        "return_value": MULTIPOLYGON,
        "bbox": False
    },
    6: {
        "wkb_geometry": GEOMETRYCOLLECTION_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRYCOLLECTION,
        "bbox": False
    },
    7: {
        "wkb_geometry": POINT_WKB_LITTLE_ENDIAN,
        "return_value": POINT,
        "bbox": False
    },
    8: {
        "wkb_geometry": LINESTRING_WKB_LITTLE_ENDIAN,
        "return_value": LINESTRING,
        "bbox": False
    },
    9: {
        "wkb_geometry": POLYGON_WKB_LITTLE_ENDIAN,
        "return_value": POLYGON,
        "bbox": False
    },
    10: {
        "wkb_geometry": MULTIPOINT_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOINT,
        "bbox": False
    },
    11: {
        "wkb_geometry": MULTILINESTRING_WKB_LITTLE_ENDIAN,
        "return_value": MULTILINESTRING,
        "bbox": False
    },
    12: {
        "wkb_geometry": MULTIPOLYGON_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOLYGON,
        "bbox": False
    },
    13: {
        "wkb_geometry": GEOMETRYCOLLECTION_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRYCOLLECTION,
        "bbox": False
    },
    14: {
        "wkb_geometry": MULTIPOINT_WKB_VARYING_ENDIAN,
        "return_value": MULTIPOINT,
        "bbox": False
    },
    15: {
        "wkb_geometry": MULTILINESTRING_WKB_VARYING_ENDIAN,
        "return_value": MULTILINESTRING,
        "bbox": False
    },
    16: {
        "wkb_geometry": MULTIPOLYGON_WKB_VARYING_ENDIAN,
        "return_value": MULTIPOLYGON,
        "bbox": False
    },
    17: {
        "wkb_geometry": GEOMETRYCOLLECTION_WKB_VARYING_ENDIAN,
        "return_value": GEOMETRYCOLLECTION,
        "bbox": False
    },
    18: {
        "wkb_geometry": POINT_WKB_BIG_ENDIAN,
        "return_value": POINT_WITH_BBOX,
        "bbox": True
    },
    19: {
        "wkb_geometry": LINESTRING_WKB_BIG_ENDIAN,
        "return_value": LINESTRING_WITH_BBOX,
        "bbox": True
    },
    20: {
        "wkb_geometry": POLYGON_WKB_BIG_ENDIAN,
        "return_value": POLYGON_WITH_BBOX,
        "bbox": True
    },
    21: {
        "wkb_geometry": MULTIPOINT_WKB_BIG_ENDIAN,
        "return_value": MULTIPOINT_WITH_BBOX,
        "bbox": True
    },
    22: {
        "wkb_geometry": MULTILINESTRING_WKB_BIG_ENDIAN,
        "return_value": MULTILINESTRING_WITH_BBOX,
        "bbox": True
    },
    23: {
        "wkb_geometry": MULTIPOLYGON_WKB_BIG_ENDIAN,
        "return_value": MULTIPOLYGON_WITH_BBOX,
        "bbox": True
    },
    24: {
        "wkb_geometry": GEOMETRYCOLLECTION_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRYCOLLECTION_WITH_BBOX,
        "bbox": True
    },
    25: {
        "wkb_geometry": POINT_WKB_LITTLE_ENDIAN,
        "return_value": POINT_WITH_BBOX,
        "bbox": True
    },
    26: {
        "wkb_geometry": LINESTRING_WKB_LITTLE_ENDIAN,
        "return_value": LINESTRING_WITH_BBOX,
        "bbox": True
    },
    27: {
        "wkb_geometry": POLYGON_WKB_LITTLE_ENDIAN,
        "return_value": POLYGON_WITH_BBOX,
        "bbox": True
    },
    28: {
        "wkb_geometry": MULTIPOINT_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOINT_WITH_BBOX,
        "bbox": True
    },
    29: {
        "wkb_geometry": MULTILINESTRING_WKB_LITTLE_ENDIAN,
        "return_value": MULTILINESTRING_WITH_BBOX,
        "bbox": True
    },
    30: {
        "wkb_geometry": MULTIPOLYGON_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOLYGON_WITH_BBOX,
        "bbox": True
    },
    31: {
        "wkb_geometry": GEOMETRYCOLLECTION_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRYCOLLECTION_WITH_BBOX,
        "bbox": True
    },
    32: {
        "wkb_geometry": MULTIPOINT_WKB_VARYING_ENDIAN,
        "return_value": MULTIPOINT_WITH_BBOX,
        "bbox": True
    },
    33: {
        "wkb_geometry": MULTILINESTRING_WKB_VARYING_ENDIAN,
        "return_value": MULTILINESTRING_WITH_BBOX,
        "bbox": True
    },
    34: {
        "wkb_geometry": MULTIPOLYGON_WKB_VARYING_ENDIAN,
        "return_value": MULTIPOLYGON_WITH_BBOX,
        "bbox": True
    },
    35: {
        "wkb_geometry": GEOMETRYCOLLECTION_WKB_VARYING_ENDIAN,
        "return_value": GEOMETRYCOLLECTION_WITH_BBOX,
        "bbox": True
    },
    36: {
        "wkb_geometry": POINT_EMPTY_WKB_BIG_ENDIAN,
        "return_value": POINT_EMPTY,
        "bbox": True
    },
    37: {
        "wkb_geometry": POINT_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": POINT_EMPTY,
        "bbox": True
    },
    38: {
        "wkb_geometry": LINESTRING_EMPTY_WKB_BIG_ENDIAN,
        "return_value": LINESTRING_EMPTY,
        "bbox": True
    },
    39: {
        "wkb_geometry": LINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": LINESTRING_EMPTY,
        "bbox": True
    },
    40: {
        "wkb_geometry": POLYGON_EMPTY_WKB_BIG_ENDIAN,
        "return_value": POLYGON_EMPTY,
        "bbox": True
    },
    41: {
        "wkb_geometry": POLYGON_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": POLYGON_EMPTY,
        "bbox": True
    },
    42: {
        "wkb_geometry": MULTIPOINT_EMPTY_WKB_BIG_ENDIAN ,
        "return_value": MULTIPOINT_EMPTY,
        "bbox": True
    },
    43: {
        "wkb_geometry": MULTIPOINT_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOINT_EMPTY,
        "bbox": True
    },
    44: {
        "wkb_geometry": MULTILINESTRING_EMPTY_WKB_BIG_ENDIAN,
        "return_value": MULTILINESTRING_EMPTY,
        "bbox": True
    },
    45: {
        "wkb_geometry": MULTILINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": MULTILINESTRING_EMPTY,
        "bbox": True
    },
    46: {
        "wkb_geometry": MULTIPOLYGON_EMPTY_WKB_BIG_ENDIAN,
        "return_value": MULTIPOLYGON_EMPTY,
        "bbox": True
    },
    47: {
        "wkb_geometry": MULTIPOLYGON_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOLYGON_EMPTY,
        "bbox": True
    },
    48: {
        "wkb_geometry": GEOMETRYCOLLECTION_EMPTY_WKB_BIG_ENDIAN,
        "return_value": GEOMETRYCOLLECTION_EMPTY,
        "bbox": True
    },
    49: {
        "wkb_geometry": GEOMETRYCOLLECTION_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRYCOLLECTION_EMPTY,
        "bbox": True
    },
    50: {
        "wkb_geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_BIG_ENDIAN,
        "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WITH_BBOX,
        "bbox": True
    },
    51: {
        "wkb_geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WITH_BBOX,
        "bbox": True
    },
    52: {
        "wkb_geometry": POINT_EMPTY_WKB_BIG_ENDIAN,
        "return_value": POINT_EMPTY,
        "bbox": False
    },
    53: {
        "wkb_geometry": POINT_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": POINT_EMPTY,
        "bbox": False
    },
    54: {
        "wkb_geometry": LINESTRING_EMPTY_WKB_BIG_ENDIAN,
        "return_value": LINESTRING_EMPTY,
        "bbox": False
    },
    55: {
        "wkb_geometry": LINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": LINESTRING_EMPTY,
        "bbox": False
    },
    56: {
        "wkb_geometry": POLYGON_EMPTY_WKB_BIG_ENDIAN,
        "return_value": POLYGON_EMPTY,
        "bbox": False
    },
    57: {
        "wkb_geometry": POLYGON_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": POLYGON_EMPTY,
        "bbox": False
    },
    58: {
        "wkb_geometry": MULTIPOINT_EMPTY_WKB_BIG_ENDIAN ,
        "return_value": MULTIPOINT_EMPTY,
        "bbox": False
    },
    59: {
        "wkb_geometry": MULTIPOINT_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOINT_EMPTY,
        "bbox": False
    },
    60: {
        "wkb_geometry": MULTILINESTRING_EMPTY_WKB_BIG_ENDIAN,
        "return_value": MULTILINESTRING_EMPTY,
        "bbox": False
    },
    61: {
        "wkb_geometry": MULTILINESTRING_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": MULTILINESTRING_EMPTY,
        "bbox": False
    },
    62: {
        "wkb_geometry": MULTIPOLYGON_EMPTY_WKB_BIG_ENDIAN,
        "return_value": MULTIPOLYGON_EMPTY,
        "bbox": False
    },
    63: {
        "wkb_geometry": MULTIPOLYGON_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": MULTIPOLYGON_EMPTY,
        "bbox": False
    },
    64: {
        "wkb_geometry": GEOMETRYCOLLECTION_EMPTY_WKB_BIG_ENDIAN,
        "return_value": GEOMETRYCOLLECTION_EMPTY,
        "bbox": False
    },
    65: {
        "wkb_geometry": GEOMETRYCOLLECTION_EMPTY_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRYCOLLECTION_EMPTY,
        "bbox": False
    },
    66: {
        "wkb_geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_BIG_ENDIAN,
        "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
        "bbox": False
    },
    67: {
        "wkb_geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKB_LITTLE_ENDIAN,
        "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
        "bbox": False
    },
}

geometry_to_wkt_parameters = {
    0: {
        "geometry": POINT,
        "return_value": POINT_WKT
    },
    1: {
        "geometry": LINESTRING,
        "return_value": LINESTRING_WKT
    },
    2: {
        "geometry": POLYGON,
        "return_value": POLYGON_WKT
    },
    3: {
        "geometry": MULTIPOINT,
        "return_value": MULTIPOINT_WKT
    },
    4: {
        "geometry": MULTILINESTRING,
        "return_value": MULTILINESTRING_WKT
    },
    5: {
        "geometry": MULTIPOLYGON,
        "return_value": MULTIPOLYGON_WKT
    },
    6: {
        "geometry": GEOMETRYCOLLECTION,
        "return_value": GEOMETRYCOLLECTION_WKT
    },
    7: {
        "geometry": POINT_EMPTY,
        "return_value": POINT_EMPTY_WKT
    },
    8: {
        "geometry": LINESTRING_EMPTY,
        "return_value": LINESTRING_EMPTY_WKT
    },
    9: {
        "geometry": POLYGON_EMPTY,
        "return_value": POLYGON_EMPTY_WKT
    },
    10: {
        "geometry": MULTIPOINT_EMPTY,
        "return_value": MULTIPOINT_EMPTY_WKT
    },
    11: {
        "geometry": MULTILINESTRING_EMPTY,
        "return_value": MULTILINESTRING_EMPTY_WKT
    },
    12: {
        "geometry": MULTIPOLYGON_EMPTY,
        "return_value": MULTIPOLYGON_EMPTY_WKT
    },
    13: {
        "geometry": GEOMETRYCOLLECTION_EMPTY,
        "return_value": GEOMETRYCOLLECTION_EMPTY_WKT
    },
    14: {
        "geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
        "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT
    }
}

wkt_to_geometry_parameters = {
    0: {
        "wkt_geometry": POINT_WKT,
        "bbox": False,
        "return_value": POINT
    },
    1: {
        "wkt_geometry": LINESTRING_WKT,
        "bbox": False,
        "return_value": LINESTRING
    },
    2: {
        "wkt_geometry": POLYGON_WKT,
        "bbox": False,
        "return_value": POLYGON
    },
    3: {
        "wkt_geometry": MULTIPOINT_WKT,
        "bbox": False,
        "return_value": MULTIPOINT
     },
    4: {
        "wkt_geometry": MULTILINESTRING_WKT,
        "bbox": False,
        "return_value": MULTILINESTRING
    },
    5: {
        "wkt_geometry": MULTIPOLYGON_WKT,
        "bbox": False,
        "return_value": MULTIPOLYGON
    },
    6: {
        "wkt_geometry": GEOMETRYCOLLECTION_WKT,
        "bbox": False,
        "return_value": GEOMETRYCOLLECTION
    },
    7: {
        "wkt_geometry": POINT_WKT,
        "bbox": True,
        "return_value": POINT_WITH_BBOX
    },
    8: {
        "wkt_geometry": LINESTRING_WKT,
        "bbox": True,
        "return_value": LINESTRING_WITH_BBOX
    },
    9: {
        "wkt_geometry": POLYGON_WKT,
        "bbox": True,
        "return_value": POLYGON_WITH_BBOX
    },
    10: {
        "wkt_geometry": MULTIPOINT_WKT,
        "bbox": True,
        "return_value": MULTIPOINT_WITH_BBOX
    },
    11: {
        "wkt_geometry": MULTILINESTRING_WKT,
        "bbox": True,
        "return_value": MULTILINESTRING_WITH_BBOX
    },
    12: {
        "wkt_geometry": MULTIPOLYGON_WKT,
        "bbox": True,
        "return_value": MULTIPOLYGON_WITH_BBOX
    },
    13: {
        "wkt_geometry": GEOMETRYCOLLECTION_WKT,
        "bbox": True,
        "return_value": GEOMETRYCOLLECTION_WITH_BBOX
    },
    14: {
        "wkt_geometry": POINT_EMPTY_WKT,
        "bbox": False,
        "return_value": POINT_EMPTY
    },
    15: {
        "wkt_geometry": LINESTRING_EMPTY_WKT,
        "bbox": False,
        "return_value": LINESTRING_EMPTY
    },
    16: {
        "wkt_geometry": POLYGON_EMPTY_WKT,
        "bbox": False,
        "return_value": POLYGON_EMPTY
    },
    17: {
        "wkt_geometry": MULTIPOINT_EMPTY_WKT,
        "bbox": False,
        "return_value": MULTIPOINT_EMPTY
    },
    18: {
        "wkt_geometry": MULTILINESTRING_EMPTY_WKT,
        "bbox": False,
        "return_value": MULTILINESTRING_EMPTY
    },
    19: {
        "wkt_geometry": MULTIPOLYGON_EMPTY_WKT,
        "bbox": False,
        "return_value": MULTIPOLYGON_EMPTY
    },
    20: {
        "wkt_geometry": GEOMETRYCOLLECTION_EMPTY_WKT,
        "bbox": False,
        "return_value": GEOMETRYCOLLECTION_EMPTY
    },
    21: {
        "wkt_geometry": POINT_EMPTY_WKT,
        "bbox": True,
        "return_value": POINT_EMPTY
    },
    22: {
        "wkt_geometry": LINESTRING_EMPTY_WKT,
        "bbox": True,
        "return_value": LINESTRING_EMPTY
    },
    23: {
        "wkt_geometry": POLYGON_EMPTY_WKT,
        "bbox": True,
        "return_value": POLYGON_EMPTY
    },
    24: {
        "wkt_geometry": MULTIPOINT_EMPTY_WKT,
        "bbox": True,
        "return_value": MULTIPOINT_EMPTY
    },
    25: {
        "wkt_geometry": MULTILINESTRING_EMPTY_WKT,
        "bbox": True,
        "return_value": MULTILINESTRING_EMPTY
    },
    26: {
        "wkt_geometry": MULTIPOLYGON_EMPTY_WKT,
        "bbox": True,
        "return_value": MULTIPOLYGON_EMPTY
    },
    27: {
        "wkt_geometry": GEOMETRYCOLLECTION_EMPTY_WKT,
        "bbox": True,
        "return_value": GEOMETRYCOLLECTION_EMPTY
    },
    28: {
        "wkt_geometry": "GEOMETRYCOLLECTION (POINT EMPTY,LINESTRING (8.919 44.4074,8.923 44.4075),POLYGON ((2.38 57.322,23.194 -20.28,-120.43 19.15,2.38 57.322),(-5.21 23.51,15.21 -10.81,-20.51 1.51,-5.21 23.51)),MULTIPOINT (-155.52 19.61,-156.22 20.74,-157.97 21.46),MULTILINESTRING ((3.75 9.25,-130.95 1.52),(23.15 -34.25,-1.35 -4.65,3.45 77.95)),MULTIPOLYGON (((3.78 9.28,-130.91 1.52,35.12 72.234,3.78 9.28)),((23.18 -34.29,-1.31 -4.61,3.41 77.91,23.18 -34.29))))",
        "bbox": False,
        "return_value":  {"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": []}, {"type": "LineString", "coordinates": [[8.919, 44.4074], [8.923, 44.4075]]}, {"type": "Polygon", "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]}, {"type": "MultiPoint", "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]}, {"type": "MultiLineString", "coordinates": [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]}, {"type": "MultiPolygon", "coordinates": [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]}]}
    },
    29: {
        "wkt_geometry": "GEOMETRYCOLLECTION (POINT EMPTY,LINESTRING (8.919 44.4074,8.923 44.4075),POLYGON ((2.38 57.322,23.194 -20.28,-120.43 19.15,2.38 57.322),(-5.21 23.51,15.21 -10.81,-20.51 1.51,-5.21 23.51)),MULTIPOINT (-155.52 19.61,-156.22 20.74,-157.97 21.46),MULTILINESTRING ((3.75 9.25,-130.95 1.52),(23.15 -34.25,-1.35 -4.65,3.45 77.95)),MULTIPOLYGON EMPTY)",
        "bbox": False,
        "return_value":  {"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": []}, {"type": "LineString", "coordinates": [[8.919, 44.4074], [8.923, 44.4075]]}, {"type": "Polygon", "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]}, {"type": "MultiPoint", "coordinates": [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]}, {"type": "MultiLineString", "coordinates": [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]}, {"type": "MultiPolygon", "coordinates": []}]}
    },
    30: {
        "wkt_geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT,
        "bbox": False,
        "return_value":  GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES
    },
    31: {
        "wkt_geometry": "GEOMETRYCOLLECTION (POINT EMPTY,LINESTRING (8.919 44.4074,8.923 44.4075),POLYGON ((2.38 57.322,23.194 -20.28,-120.43 19.15,2.38 57.322),(-5.21 23.51,15.21 -10.81,-20.51 1.51,-5.21 23.51)),MULTIPOINT (-155.52 19.61,-156.22 20.74,-157.97 21.46),MULTILINESTRING ((3.75 9.25,-130.95 1.52),(23.15 -34.25,-1.35 -4.65,3.45 77.95)),MULTIPOLYGON (((3.78 9.28,-130.91 1.52,35.12 72.234,3.78 9.28)),((23.18 -34.29,-1.31 -4.61,3.41 77.91,23.18 -34.29))))",
        "bbox": True,
        "return_value":  {'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': []}, {'type': 'LineString', 'coordinates': [[8.919, 44.4074], [8.923, 44.4075]], 'bbox': (8.919, 44.4074, 8.923, 44.4075)}, {'type': 'Polygon', 'coordinates': [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]], 'bbox': (-120.43, -20.28, 23.194, 57.322)}, {'type': 'MultiPoint', 'coordinates': [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]], 'bbox': (-157.97, 19.61, -155.52, 21.46)}, {'type': 'MultiLineString', 'coordinates': [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]], 'bbox': (-130.95, -34.25, 23.15, 77.95)}, {'type': 'MultiPolygon', 'coordinates': [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]], 'bbox': (-130.91, -34.29, 35.12, 77.91)}], 'bbox': (-157.97, -34.29, 35.12, 77.95)}
    },
    32: {
        "wkt_geometry": "GEOMETRYCOLLECTION (POINT EMPTY,LINESTRING (8.919 44.4074,8.923 44.4075),POLYGON ((2.38 57.322,23.194 -20.28,-120.43 19.15,2.38 57.322),(-5.21 23.51,15.21 -10.81,-20.51 1.51,-5.21 23.51)),MULTIPOINT (-155.52 19.61,-156.22 20.74,-157.97 21.46),MULTILINESTRING ((3.75 9.25,-130.95 1.52),(23.15 -34.25,-1.35 -4.65,3.45 77.95)),MULTIPOLYGON EMPTY)",
        "bbox": True,
        "return_value":  {'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': []}, {'type': 'LineString', 'coordinates': [[8.919, 44.4074], [8.923, 44.4075]], 'bbox': (8.919, 44.4074, 8.923, 44.4075)}, {'type': 'Polygon', 'coordinates': [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]], 'bbox': (-120.43, -20.28, 23.194, 57.322)}, {'type': 'MultiPoint', 'coordinates': [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]], 'bbox': (-157.97, 19.61, -155.52, 21.46)}, {'type': 'MultiLineString', 'coordinates': [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]], 'bbox': (-130.95, -34.25, 23.15, 77.95)}, {'type': 'MultiPolygon', 'coordinates': []}], 'bbox': (-157.97, -34.25, 23.194, 77.95)}
    },
    33: {
        "wkt_geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT,
        "bbox": True,
        "return_value":  GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WITH_BBOX
    },

}

force_rhr_parameters = {
    0: {
        "polygon_geometry": {'type': 'Polygon',
                             'coordinates': [[[0, 0], [5, 0], [0, 5], [0, 0]],
                                             [[1, 1], [1, 3], [3, 1], [1, 1]]]},
        "return_value": {'type': 'Polygon',
                         'coordinates': [[[0, 0], [0, 5], [5, 0], [0, 0]],
                                         [[1, 1], [3, 1], [1, 3], [1, 1]]]}
    },
    1: {
        "polygon_geometry": POLYGON,
        "return_value": {"type": "Polygon",
                         "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                                         [[-5.21, 23.51], [-20.51, 1.51], [15.21, -10.81], [-5.21, 23.51]]]}
    },
    2: {
        "polygon_geometry": MULTIPOLYGON,
        "return_value": {"type": "MultiPolygon",
                         "coordinates": [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],
                                         [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]}
    },
    3: {
        "polygon_geometry": POLYGON_WITH_BBOX,
        "return_value": {"type": "Polygon",
                         "coordinates": [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
                                         [[-5.21, 23.51], [-20.51, 1.51], [15.21, -10.81], [-5.21, 23.51]]],
                         'bbox': (-120.43, -20.28, 23.194, 57.322)}
    },
    4: {
        "polygon_geometry": MULTIPOLYGON_WITH_BBOX,
        "return_value": {"type": "MultiPolygon",
                         "coordinates": [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],
                                         [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]],
                         'bbox': (-130.91, -34.29, 35.12, 77.91)}
    }
}

geometry_to_bbox_parameters = {
    0: {
        "geometry": POINT,
        "return_value": (-115.81, 37.24, -115.81, 37.24)
    },
    1: {
        "geometry": POINT_EMPTY,
        "return_value": ()
    },
    2: {
        "geometry": LINESTRING,
        "return_value": (8.919, 44.4074, 8.923, 44.4075)
    },
    3: {
        "geometry": LINESTRING_EMPTY,
        "return_value": ()
    },
    4: {
        "geometry": POLYGON,
        "return_value": (-120.43, -20.28, 23.194, 57.322)
    },
    5: {
        "geometry": POLYGON_EMPTY,
        "return_value": ()
    },
    6: {
        "geometry": MULTIPOINT,
        "return_value": (-157.97, 19.61, -155.52, 21.46)
    },
    7: {
        "geometry": MULTIPOINT_EMPTY,
        "return_value": ()
    },
    8: {
        "geometry": MULTILINESTRING,
        "return_value": (-130.95, -34.25, 23.15, 77.95)
    },
    9: {
        "geometry": MULTILINESTRING_EMPTY,
        "return_value": ()
    },
    10: {
        "geometry": MULTIPOLYGON,
        "return_value": (-130.91, -34.29, 35.12, 77.91)
    },
    11: {
        "geometry": MULTIPOLYGON_EMPTY,
        "return_value": ()
    },
    12: {
        "geometry": GEOMETRYCOLLECTION,
        "return_value": (-157.97, -34.29, 35.12, 77.95)
    },
    13: {
        "geometry": GEOMETRYCOLLECTION_EMPTY,
        "return_value": ()
    },
    14: {
        "geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
        "return_value": (-130.95, -34.25, 23.194, 77.95)
    },
}

reproject_geometry_parameters = {
    0: {
        "geometry": POINT_paris,
        "in_crs": 4326,
        "out_crs": 3857,
        "precision": 2,
        "return_value": POINT_paris_3857
    },
    1: {
        "geometry": LINESTRING_loire,
        "in_crs": 4326,
        "out_crs": 3857,
        "precision": 2,
        "return_value": {'type': 'LineString', 'coordinates': [[-237872.03, 5988382.54], [-209743.21, 5987159.55], [-198124.78, 5976152.62], [-174276.42, 5974318.13], [-154097.05, 5986548.06], [-145536.1, 5998777.98], [-119241.76, 6002446.96], [-104565.85, 6003669.95], [-88055.46, 6004281.45], [-78271.52, 6004281.45], [-66653.09, 6009173.42], [-52588.68, 6009173.42], [-37301.27, 6009173.42], [-32409.3, 6008561.92], [-23236.86, 5996332.0], [-4891.97, 5983490.57], [9172.44, 5977987.11], [18344.89, 5980433.09], [48919.7, 5996943.49], [67264.59, 6001223.97], [91724.43, 6009784.91], [116184.28, 6010396.41], [149205.08, 6032410.27], [155320.04, 6045863.19], [181002.88, 6060539.1], [182225.88, 6071546.03], [194455.8, 6079495.48], [204851.24, 6083775.96], [218915.65, 6089890.92], [245209.99, 6084387.45], [257439.91, 6077049.5], [295352.68, 6051978.15], [307582.6, 6038525.23], [328984.97, 6018957.36], [317366.54, 5998166.48], [342437.89, 5969426.16], [344883.87, 5941297.34], [389523.1, 5912557.01], [409702.47, 5892377.64], [412759.95, 5881982.2], [426824.37, 5861802.83], [447615.24, 5848961.4], [451284.22, 5812271.63], [452507.21, 5782919.81], [448838.23, 5766409.41], [457399.18, 5755402.48], [469017.61, 5738280.59], [465348.63, 5710151.76], [473298.08, 5695475.85], [468406.11, 5678965.45], [461068.15, 5656951.59], [448838.23, 5654811.35], [437066.93, 5651753.87], [436608.31, 5643498.67], [435385.31, 5636772.21], [440583.03, 5624695.16], [434468.07, 5621943.43], [435538.19, 5617815.83], [437831.3, 5613229.61], [435232.44, 5604821.54]]}
    },
    2: {
        "geometry": POLYGON_france,
        "in_crs": 4326,
        "out_crs": 3857,
        "precision": 2,
        "return_value": {'type': 'Polygon', 'coordinates': [[[273950.31, 6643295.0], [190786.82, 6599267.27], [190786.82, 6467184.09], [44027.73, 6408480.45], [4891.97, 6364452.72], [39135.76, 6335100.9], [-122299.24, 6315533.02], [-141867.12, 6388912.57], [-200570.76, 6388912.57], [-176110.91, 6315533.02], [-151651.06, 6207909.69], [-288626.22, 6183449.84], [-337545.92, 6237261.51], [-513656.83, 6217693.63], [-528332.74, 6163881.96], [-489196.98, 6168773.93], [-469629.1, 6134530.14], [-513656.83, 6119854.23], [-484305.01, 6061150.6], [-450061.22, 6105178.32], [-313086.07, 6056258.62], [-225030.61, 5953527.26], [-249490.46, 5929067.41], [-136975.15, 5826336.04], [-112515.31, 5743172.56], [-73379.55, 5640441.19], [-127191.21, 5699144.83], [-127191.21, 5523033.92], [-195678.79, 5356706.94], [63595.61, 5258867.55], [73379.55, 5293111.33], [210354.7, 5229515.73], [362005.77, 5214839.82], [327761.98, 5307787.24], [464737.13, 5390950.73], [547900.62, 5386058.76], [665307.89, 5327355.12], [719119.56, 5342031.03], [841418.81, 5420302.55], [846310.78, 5479006.19], [782715.17, 5488790.13], [748471.38, 5625765.28], [777823.2, 5718712.71], [768039.26, 5836119.98], [684875.77, 5782308.32], [679983.8, 5860579.83], [758255.32, 5938851.35], [841418.81, 6031798.78], [851202.75, 6114962.26], [914798.35, 6271505.3], [748471.38, 6291073.18], [714227.59, 6354668.78], [635956.07, 6344884.84], [513656.83, 6447616.21], [322870.01, 6555239.55], [273950.31, 6643295.0]]]}
    },
    3: {
        "geometry": MULTIPOINT_paris_tokyo,
        "in_crs": 4326,
        "out_crs": 3857,
        "precision": 2,
        "return_value": MULTIPOINT_paris_tokyo_3857
    },
    4: {
        "geometry": MULTILINESTRING_loire_katsuragawa_river,
        "in_crs": 4326,
        "out_crs": 3857,
        "precision": 2,
        "return_value":  {'type': 'MultiLineString', 'coordinates': [[[-237872.03, 5988382.54], [-209743.21, 5987159.55], [-198124.78, 5976152.62], [-174276.42, 5974318.13], [-154097.05, 5986548.06], [-145536.1, 5998777.98], [-119241.76, 6002446.96], [-104565.85, 6003669.95], [-88055.46, 6004281.45], [-78271.52, 6004281.45], [-66653.09, 6009173.42], [-52588.68, 6009173.42], [-37301.27, 6009173.42], [-32409.3, 6008561.92], [-23236.86, 5996332.0], [-4891.97, 5983490.57], [9172.44, 5977987.11], [18344.89, 5980433.09], [48919.7, 5996943.49], [67264.59, 6001223.97], [91724.43, 6009784.91], [116184.28, 6010396.41], [149205.08, 6032410.27], [155320.04, 6045863.19], [181002.88, 6060539.1], [182225.88, 6071546.03], [194455.8, 6079495.48], [204851.24, 6083775.96], [218915.65, 6089890.92], [245209.99, 6084387.45], [257439.91, 6077049.5], [295352.68, 6051978.15], [307582.6, 6038525.23], [328984.97, 6018957.36], [317366.54, 5998166.48], [342437.89, 5969426.16], [344883.87, 5941297.34], [389523.1, 5912557.01], [409702.47, 5892377.64], [412759.95, 5881982.2], [426824.37, 5861802.83], [447615.24, 5848961.4], [451284.22, 5812271.63], [452507.21, 5782919.81], [448838.23, 5766409.41], [457399.18, 5755402.48], [469017.61, 5738280.59], [465348.63, 5710151.76], [473298.08, 5695475.85], [468406.11, 5678965.45], [461068.15, 5656951.59], [448838.23, 5654811.35], [437066.93, 5651753.87], [436608.31, 5643498.67], [435385.31, 5636772.21], [440583.03, 5624695.16], [434468.07, 5621943.43], [435538.19, 5617815.83], [437831.3, 5613229.61], [435232.44, 5604821.54]], [[15075140.03, 4120873.07], [15084083.16, 4126223.66], [15096313.09, 4135243.23], [15104262.54, 4148543.27], [15109918.88, 4153588.12], [15110262.84, 4155919.45], [15106899.62, 4163639.59], [15105065.13, 4163639.59], [15100937.53, 4167958.28], [15092644.11, 4166888.16], [15089252.22, 4171034.87], [15085115.06, 4176481.01], [15085678.79, 4179729.58], [15082974.82, 4181449.41], [15084637.33, 4184449.57], [15085621.46, 4184755.31], [15085726.56, 4183828.52], [15087914.57, 4183508.44], [15088588.17, 4181855.49], [15091387.67, 4181329.98], [15092431.52, 4182767.95], [15091777.03, 4183682.81], [15093140.95, 4183494.1], [15095223.86, 4182710.63], [15095988.23, 4181850.71], [15099141.26, 4182901.72], [15098567.98, 4184841.31], [15100469.35, 4187115.31], [15103259.3, 4189274.65], [15104014.12, 4190640.97], [15106297.67, 4190870.28], [15107119.37, 4190144.13], [15107377.35, 4191443.55], [15107931.51, 4192676.1], [15108867.87, 4191271.57], [15110071.75, 4192504.12], [15111356.85, 4191615.54], [15112087.78, 4192284.36], [15112637.17, 4191343.23], [15112938.14, 4191711.09], [15114299.67, 4191854.4], [15114925.5, 4194090.19], [15114743.96, 4195962.89]]]}
    },
    5: {
        "geometry": MULTIPOLYGON_france_japan,
        "in_crs": 4326,
        "out_crs": 3857,
        "precision": 2,
        "return_value": {'type': 'MultiPolygon', 'coordinates': [[[[273950.31, 6643295.0], [190786.82, 6599267.27], [190786.82, 6467184.09], [44027.73, 6408480.45], [4891.97, 6364452.72], [39135.76, 6335100.9], [-122299.24, 6315533.02], [-141867.12, 6388912.57], [-200570.76, 6388912.57], [-176110.91, 6315533.02], [-151651.06, 6207909.69], [-288626.22, 6183449.84], [-337545.92, 6237261.51], [-513656.83, 6217693.63], [-528332.74, 6163881.96], [-489196.98, 6168773.93], [-469629.1, 6134530.14], [-513656.83, 6119854.23], [-484305.01, 6061150.6], [-450061.22, 6105178.32], [-313086.07, 6056258.62], [-225030.61, 5953527.26], [-249490.46, 5929067.41], [-136975.15, 5826336.04], [-112515.31, 5743172.56], [-73379.55, 5640441.19], [-127191.21, 5699144.83], [-127191.21, 5523033.92], [-195678.79, 5356706.94], [63595.61, 5258867.55], [73379.55, 5293111.33], [210354.7, 5229515.73], [362005.77, 5214839.82], [327761.98, 5307787.24], [464737.13, 5390950.73], [547900.62, 5386058.76], [665307.89, 5327355.12], [719119.56, 5342031.03], [841418.81, 5420302.55], [846310.78, 5479006.19], [782715.17, 5488790.13], [748471.38, 5625765.28], [777823.2, 5718712.71], [768039.26, 5836119.98], [684875.77, 5782308.32], [679983.8, 5860579.83], [758255.32, 5938851.35], [841418.81, 6031798.78], [851202.75, 6114962.26], [914798.35, 6271505.3], [748471.38, 6291073.18], [714227.59, 6354668.78], [635956.07, 6344884.84], [513656.83, 6447616.21], [322870.01, 6555239.55], [273950.31, 6643295.0]]], [[[15683655.21, 5090094.59], [15574808.88, 4961680.38], [15589484.79, 4786792.46], [15546680.06, 4662047.23], [15451286.65, 4551977.91], [15280067.7, 4402772.83], [15240931.94, 4446800.56], [15294743.61, 4505504.19], [15214026.11, 4493274.27], [15226256.03, 4407664.8], [15128416.64, 4297595.48], [15143092.55, 4251121.77], [15079496.94, 4226661.92], [15052591.11, 4278027.6], [14856912.31, 4229107.9], [14827560.5, 4243783.81], [14763964.89, 4229107.9], [14773748.83, 4194864.11], [14626989.73, 4087240.78], [14568286.09, 4075010.85], [14585407.99, 4023645.17], [14661233.52, 4035875.09], [14732167.08, 4004077.29], [14732167.08, 4084794.79], [14773748.83, 4067672.9], [14847128.37, 4087240.78], [14900940.04, 4077456.84], [14969427.62, 4131268.5], [15028131.26, 4119038.58], [15072158.99, 4131268.5], [15055037.09, 4075010.85], [15099064.82, 3955157.59], [15182228.31, 4052996.99], [15236039.97, 4092132.75], [15216472.09, 4182634.19], [15304527.55, 4119038.58], [15377907.1, 4121484.57], [15461070.59, 4194864.11], [15441502.71, 4116592.6], [15495314.37, 4163066.31], [15527112.18, 4211986.01], [15573585.89, 4258459.72], [15605383.69, 4241337.83], [15571139.91, 4192418.13], [15568693.92, 4155728.35], [15634735.51, 4194864.11], [15644519.45, 4253567.75], [15678763.24, 4265797.67], [15634735.51, 4329393.28], [15673871.27, 4432124.65], [15688547.18, 4593559.65], [15715453.02, 4647371.32], [15761926.73, 4630249.43], [15761926.73, 4715858.9], [15810846.43, 4806360.34], [15776602.64, 4933551.55], [15744804.83, 4967795.34], [15747250.82, 5080310.65], [15720344.99, 5055850.8], [15683655.21, 5090094.59]]]]}
    },
    6: {
        "geometry": GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan,
        "in_crs": 4326,
        "out_crs": 3857,
        "precision": 2,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'MultiPoint', 'coordinates': [[261473.94, 6250010.11], [15557242.85, 4257415.09]]}, {'type': 'MultiLineString', 'coordinates': [[[-237872.03, 5988382.54], [-209743.21, 5987159.55], [-198124.78, 5976152.62], [-174276.42, 5974318.13], [-154097.05, 5986548.06], [-145536.1, 5998777.98], [-119241.76, 6002446.96], [-104565.85, 6003669.95], [-88055.46, 6004281.45], [-78271.52, 6004281.45], [-66653.09, 6009173.42], [-52588.68, 6009173.42], [-37301.27, 6009173.42], [-32409.3, 6008561.92], [-23236.86, 5996332.0], [-4891.97, 5983490.57], [9172.44, 5977987.11], [18344.89, 5980433.09], [48919.7, 5996943.49], [67264.59, 6001223.97], [91724.43, 6009784.91], [116184.28, 6010396.41], [149205.08, 6032410.27], [155320.04, 6045863.19], [181002.88, 6060539.1], [182225.88, 6071546.03], [194455.8, 6079495.48], [204851.24, 6083775.96], [218915.65, 6089890.92], [245209.99, 6084387.45], [257439.91, 6077049.5], [295352.68, 6051978.15], [307582.6, 6038525.23], [328984.97, 6018957.36], [317366.54, 5998166.48], [342437.89, 5969426.16], [344883.87, 5941297.34], [389523.1, 5912557.01], [409702.47, 5892377.64], [412759.95, 5881982.2], [426824.37, 5861802.83], [447615.24, 5848961.4], [451284.22, 5812271.63], [452507.21, 5782919.81], [448838.23, 5766409.41], [457399.18, 5755402.48], [469017.61, 5738280.59], [465348.63, 5710151.76], [473298.08, 5695475.85], [468406.11, 5678965.45], [461068.15, 5656951.59], [448838.23, 5654811.35], [437066.93, 5651753.87], [436608.31, 5643498.67], [435385.31, 5636772.21], [440583.03, 5624695.16], [434468.07, 5621943.43], [435538.19, 5617815.83], [437831.3, 5613229.61], [435232.44, 5604821.54]], [[15075140.03, 4120873.07], [15084083.16, 4126223.66], [15096313.09, 4135243.23], [15104262.54, 4148543.27], [15109918.88, 4153588.12], [15110262.84, 4155919.45], [15106899.62, 4163639.59], [15105065.13, 4163639.59], [15100937.53, 4167958.28], [15092644.11, 4166888.16], [15089252.22, 4171034.87], [15085115.06, 4176481.01], [15085678.79, 4179729.58], [15082974.82, 4181449.41], [15084637.33, 4184449.57], [15085621.46, 4184755.31], [15085726.56, 4183828.52], [15087914.57, 4183508.44], [15088588.17, 4181855.49], [15091387.67, 4181329.98], [15092431.52, 4182767.95], [15091777.03, 4183682.81], [15093140.95, 4183494.1], [15095223.86, 4182710.63], [15095988.23, 4181850.71], [15099141.26, 4182901.72], [15098567.98, 4184841.31], [15100469.35, 4187115.31], [15103259.3, 4189274.65], [15104014.12, 4190640.97], [15106297.67, 4190870.28], [15107119.37, 4190144.13], [15107377.35, 4191443.55], [15107931.51, 4192676.1], [15108867.87, 4191271.57], [15110071.75, 4192504.12], [15111356.85, 4191615.54], [15112087.78, 4192284.36], [15112637.17, 4191343.23], [15112938.14, 4191711.09], [15114299.67, 4191854.4], [15114925.5, 4194090.19], [15114743.96, 4195962.89]]]}, {'type': 'MultiPolygon', 'coordinates': [[[[273950.31, 6643295.0], [190786.82, 6599267.27], [190786.82, 6467184.09], [44027.73, 6408480.45], [4891.97, 6364452.72], [39135.76, 6335100.9], [-122299.24, 6315533.02], [-141867.12, 6388912.57], [-200570.76, 6388912.57], [-176110.91, 6315533.02], [-151651.06, 6207909.69], [-288626.22, 6183449.84], [-337545.92, 6237261.51], [-513656.83, 6217693.63], [-528332.74, 6163881.96], [-489196.98, 6168773.93], [-469629.1, 6134530.14], [-513656.83, 6119854.23], [-484305.01, 6061150.6], [-450061.22, 6105178.32], [-313086.07, 6056258.62], [-225030.61, 5953527.26], [-249490.46, 5929067.41], [-136975.15, 5826336.04], [-112515.31, 5743172.56], [-73379.55, 5640441.19], [-127191.21, 5699144.83], [-127191.21, 5523033.92], [-195678.79, 5356706.94], [63595.61, 5258867.55], [73379.55, 5293111.33], [210354.7, 5229515.73], [362005.77, 5214839.82], [327761.98, 5307787.24], [464737.13, 5390950.73], [547900.62, 5386058.76], [665307.89, 5327355.12], [719119.56, 5342031.03], [841418.81, 5420302.55], [846310.78, 5479006.19], [782715.17, 5488790.13], [748471.38, 5625765.28], [777823.2, 5718712.71], [768039.26, 5836119.98], [684875.77, 5782308.32], [679983.8, 5860579.83], [758255.32, 5938851.35], [841418.81, 6031798.78], [851202.75, 6114962.26], [914798.35, 6271505.3], [748471.38, 6291073.18], [714227.59, 6354668.78], [635956.07, 6344884.84], [513656.83, 6447616.21], [322870.01, 6555239.55], [273950.31, 6643295.0]]], [[[15683655.21, 5090094.59], [15574808.88, 4961680.38], [15589484.79, 4786792.46], [15546680.06, 4662047.23], [15451286.65, 4551977.91], [15280067.7, 4402772.83], [15240931.94, 4446800.56], [15294743.61, 4505504.19], [15214026.11, 4493274.27], [15226256.03, 4407664.8], [15128416.64, 4297595.48], [15143092.55, 4251121.77], [15079496.94, 4226661.92], [15052591.11, 4278027.6], [14856912.31, 4229107.9], [14827560.5, 4243783.81], [14763964.89, 4229107.9], [14773748.83, 4194864.11], [14626989.73, 4087240.78], [14568286.09, 4075010.85], [14585407.99, 4023645.17], [14661233.52, 4035875.09], [14732167.08, 4004077.29], [14732167.08, 4084794.79], [14773748.83, 4067672.9], [14847128.37, 4087240.78], [14900940.04, 4077456.84], [14969427.62, 4131268.5], [15028131.26, 4119038.58], [15072158.99, 4131268.5], [15055037.09, 4075010.85], [15099064.82, 3955157.59], [15182228.31, 4052996.99], [15236039.97, 4092132.75], [15216472.09, 4182634.19], [15304527.55, 4119038.58], [15377907.1, 4121484.57], [15461070.59, 4194864.11], [15441502.71, 4116592.6], [15495314.37, 4163066.31], [15527112.18, 4211986.01], [15573585.89, 4258459.72], [15605383.69, 4241337.83], [15571139.91, 4192418.13], [15568693.92, 4155728.35], [15634735.51, 4194864.11], [15644519.45, 4253567.75], [15678763.24, 4265797.67], [15634735.51, 4329393.28], [15673871.27, 4432124.65], [15688547.18, 4593559.65], [15715453.02, 4647371.32], [15761926.73, 4630249.43], [15761926.73, 4715858.9], [15810846.43, 4806360.34], [15776602.64, 4933551.55], [15744804.83, 4967795.34], [15747250.82, 5080310.65], [15720344.99, 5055850.8], [15683655.21, 5090094.59]]]]}]}
    },
    7: {
        "geometry": POINT_paris_3857,
        "in_crs": 3857,
        "out_crs": 4326,
        "precision": 8,
        "return_value": {'type': 'Point', 'coordinates': [2.34886037, 48.8533241]}
    },
    8: {
        "geometry": LINESTRING_loire_3857,
        "in_crs": 3857,
        "out_crs": 4326,
        "precision": 8,
        "return_value": {'type': 'LineString', 'coordinates': [[-2.1368408, 47.28295555], [-1.88415531, 47.27550216], [-1.77978518, 47.20837422], [-1.56555172, 47.19717795], [-1.38427735, 47.2717751], [-1.30737303, 47.34626718], [-1.07116696, 47.36859436], [-0.93933101, 47.37603464], [-0.79101566, 47.37975441], [-0.70312503, 47.37975441], [-0.59875489, 47.40950297], [-0.47241215, 47.40950297], [-0.33508301, 47.40950297], [-0.2911377, 47.40578529], [-0.20874026, 47.33137713], [-0.04394531, 47.25313561], [0.08239743, 47.21956812], [0.16479495, 47.23448962], [0.43945314, 47.33510005], [0.604248, 47.36115298], [0.82397457, 47.41322032], [1.04370114, 47.41693747], [1.34033204, 47.55057927], [1.39526366, 47.63208194], [1.62597654, 47.7208492], [1.63696293, 47.78732553], [1.74682617, 47.83528341], [1.84021, 47.86108858], [1.96655274, 47.89793078], [2.20275882, 47.86477395], [2.31262206, 47.82053189], [2.65319827, 47.66908664], [2.76306151, 47.58764165], [2.95532227, 47.46894971], [2.85095214, 47.34254505], [3.0761719, 47.1673097], [3.09814452, 46.99524108], [3.49914554, 46.81885778], [3.68041991, 46.69466733], [3.70788572, 46.63057868], [3.83422855, 46.50595448], [4.02099611, 46.42649899], [4.05395503, 46.19884437], [4.06494143, 46.01603873], [4.03198242, 45.9129441], [4.10888674, 45.84410778], [4.21325688, 45.73685956], [4.18029787, 45.56021795], [4.25170899, 45.46783597], [4.20776368, 45.36372496], [4.14184566, 45.22461174], [4.03198242, 45.21106861], [3.92623903, 45.19171574], [3.92211918, 45.13943007], [3.91113278, 45.09679144], [3.9578247, 45.02015578], [3.90289308, 45.00268014], [3.91250613, 44.97645666], [3.93310549, 44.94730539], [3.90975953, 44.89382294]]}
    },
    9: {
        "geometry": POLYGON_france_3857,
        "in_crs": 3857,
        "out_crs": 4326,
        "precision": 8,
        "return_value": {'type': 'Polygon', 'coordinates': [[[2.46093751, 51.12421274], [1.71386716, 50.87531112], [1.71386716, 50.1205781], [0.39550783, 49.78126405], [0.04394531, 49.52520832], [0.35156251, 49.35375569], [-1.09863286, 49.23912086], [-1.27441402, 49.66762781], [-1.80175779, 49.66762781], [-1.58203122, 49.23912086], [-1.36230465, 48.60385761], [-2.59277345, 48.45835188], [-3.03222659, 48.77791277], [-4.61425781, 48.66194285], [-4.74609375, 48.34164617], [-4.39453124, 48.3708477], [-4.21874998, 48.16608541], [-4.61425781, 48.07807893], [-4.35058593, 47.72454452], [-4.04296873, 47.98992165], [-2.81250002, 47.69497437], [-2.02148436, 47.07012183], [-2.24121093, 46.92025532], [-1.23046871, 46.28622389], [-1.01074223, 45.76752298], [-0.65917971, 45.12005283], [-1.14257817, 45.4909457], [-1.14257817, 44.37098699], [-1.75781248, 43.2932003], [0.57128908, 42.65012184], [0.65917971, 42.87596407], [1.88964842, 42.45588766], [3.25195316, 42.35854393], [2.94433596, 42.97250156], [4.17480467, 43.51668853], [4.92187501, 43.48481212], [5.97656246, 43.10098285], [6.45996092, 43.19716726], [7.55859377, 43.70759351], [7.60253909, 44.08758504], [7.03125, 44.15068118], [6.7236328, 45.02695044], [6.98730469, 45.61403742], [6.89941406, 46.34692759], [6.15234372, 46.01222387], [6.1083984, 46.49839224], [6.81152343, 46.98025236], [7.55859377, 47.54687162], [7.6464844, 48.04870993], [8.2177734, 48.980217], [6.7236328, 49.09545219], [6.4160156, 49.46812405], [5.71289067, 49.41097318], [4.61425781, 50.00773902], [2.90039065, 50.62507309], [2.46093751, 51.12421274]]]}
    },
    10: {
        "geometry": MULTIPOINT_paris_tokyo_3857,
        "in_crs": 3857,
        "out_crs": 4326,
        "precision": 8,
        "return_value": {'type': 'MultiPoint', 'coordinates': [[2.34886037, 48.8533241], [139.75309031, 35.68537295]]}
    },
    11: {
        "geometry": MULTILINESTRING_loire_katsuragawa_river_3857,
        "in_crs": 3857,
        "out_crs": 4326,
        "precision": 8,
        "return_value": {'type': 'MultiLineString', 'coordinates': [[[-2.1368408, 47.28295555], [-1.88415531, 47.27550216], [-1.77978518, 47.20837422], [-1.56555172, 47.19717795], [-1.38427735, 47.2717751], [-1.30737303, 47.34626718], [-1.07116696, 47.36859436], [-0.93933101, 47.37603464], [-0.79101566, 47.37975441], [-0.70312503, 47.37975441], [-0.59875489, 47.40950297], [-0.47241215, 47.40950297], [-0.33508301, 47.40950297], [-0.2911377, 47.40578529], [-0.20874026, 47.33137713], [-0.04394531, 47.25313561], [0.08239743, 47.21956812], [0.16479495, 47.23448962], [0.43945314, 47.33510005], [0.604248, 47.36115298], [0.82397457, 47.41322032], [1.04370114, 47.41693747], [1.34033204, 47.55057927], [1.39526366, 47.63208194], [1.62597654, 47.7208492], [1.63696293, 47.78732553], [1.74682617, 47.83528341], [1.84021, 47.86108858], [1.96655274, 47.89793078], [2.20275882, 47.86477395], [2.31262206, 47.82053189], [2.65319827, 47.66908664], [2.76306151, 47.58764165], [2.95532227, 47.46894971], [2.85095214, 47.34254505], [3.0761719, 47.1673097], [3.09814452, 46.99524108], [3.49914554, 46.81885778], [3.68041991, 46.69466733], [3.70788572, 46.63057868], [3.83422855, 46.50595448], [4.02099611, 46.42649899], [4.05395503, 46.19884437], [4.06494143, 46.01603873], [4.03198242, 45.9129441], [4.10888674, 45.84410778], [4.21325688, 45.73685956], [4.18029787, 45.56021795], [4.25170899, 45.46783597], [4.20776368, 45.36372496], [4.14184566, 45.22461174], [4.03198242, 45.21106861], [3.92623903, 45.19171574], [3.92211918, 45.13943007], [3.91113278, 45.09679144], [3.9578247, 45.02015578], [3.90289308, 45.00268014], [3.91250613, 44.97645666], [3.93310549, 44.94730539], [3.90975953, 44.89382294]], [[135.42228699, 34.68291098], [135.5026245, 34.72242619], [135.61248783, 34.78899485], [135.68389895, 34.88705741], [135.73471072, 34.92422304], [135.73780056, 34.94139236], [135.70758815, 34.99822249], [135.69110874, 34.99822249], [135.65402988, 35.02999638], [135.57952882, 35.02212434], [135.54905895, 35.05262424], [135.51189421, 35.09266442], [135.51695819, 35.11653865], [135.49266811, 35.1291751], [135.50760269, 35.15121409], [135.51644328, 35.15345978], [135.51738741, 35.14665239], [135.53704264, 35.14430125], [135.54309369, 35.13215849], [135.56824212, 35.12829765], [135.57761909, 35.13886175], [135.57173971, 35.14558209], [135.58399201, 35.14419592], [135.60270311, 35.1384406], [135.60956956, 35.13212337], [135.63789371, 35.13984443], [135.63274385, 35.15409135], [135.64982414, 35.17079145], [135.67488669, 35.18664632], [135.68166736, 35.19667687], [135.70218083, 35.19836018], [135.70956229, 35.19302956], [135.71187976, 35.20256834], [135.71685787, 35.21161505], [135.72526933, 35.20130587], [135.73608397, 35.2103528], [135.74762822, 35.20383071], [135.75419428, 35.20873983], [135.75912953, 35.20183188], [135.76183319, 35.20453199], [135.77406402, 35.20558397], [135.77968595, 35.22199309], [135.77805515, 35.23573482]]]}
    },
    12: {
        "geometry": MULTIPOLYGON_france_japan_3857,
        "in_crs": 3857,
        "out_crs": 4326,
        "precision": 8,
        "return_value": {'type': 'MultiPolygon', 'coordinates': [[[[2.46093751, 51.12421274], [1.71386716, 50.87531112], [1.71386716, 50.1205781], [0.39550783, 49.78126405], [0.04394531, 49.52520832], [0.35156251, 49.35375569], [-1.09863286, 49.23912086], [-1.27441402, 49.66762781], [-1.80175779, 49.66762781], [-1.58203122, 49.23912086], [-1.36230465, 48.60385761], [-2.59277345, 48.45835188], [-3.03222659, 48.77791277], [-4.61425781, 48.66194285], [-4.74609375, 48.34164617], [-4.39453124, 48.3708477], [-4.21874998, 48.16608541], [-4.61425781, 48.07807893], [-4.35058593, 47.72454452], [-4.04296873, 47.98992165], [-2.81250002, 47.69497437], [-2.02148436, 47.07012183], [-2.24121093, 46.92025532], [-1.23046871, 46.28622389], [-1.01074223, 45.76752298], [-0.65917971, 45.12005283], [-1.14257817, 45.4909457], [-1.14257817, 44.37098699], [-1.75781248, 43.2932003], [0.57128908, 42.65012184], [0.65917971, 42.87596407], [1.88964842, 42.45588766], [3.25195316, 42.35854393], [2.94433596, 42.97250156], [4.17480467, 43.51668853], [4.92187501, 43.48481212], [5.97656246, 43.10098285], [6.45996092, 43.19716726], [7.55859377, 43.70759351], [7.60253909, 44.08758504], [7.03125, 44.15068118], [6.7236328, 45.02695044], [6.98730469, 45.61403742], [6.89941406, 46.34692759], [6.15234372, 46.01222387], [6.1083984, 46.49839224], [6.81152343, 46.98025236], [7.55859377, 47.54687162], [7.6464844, 48.04870993], [8.2177734, 48.980217], [6.7236328, 49.09545219], [6.4160156, 49.46812405], [5.71289067, 49.41097318], [4.61425781, 50.00773902], [2.90039065, 50.62507309], [2.46093751, 51.12421274]]], [[[140.88867186, 41.52502959], [139.91088864, 40.65563874], [140.04272458, 39.45316113], [139.65820315, 38.58252617], [138.80126957, 37.80544396], [137.26318357, 36.73888413], [136.91162106, 37.05517712], [137.39501952, 37.47485812], [136.66992188, 37.38761749], [136.77978512, 36.7740925], [135.90087892, 35.97800619], [136.03271487, 35.6394411], [135.46142578, 35.46066998], [135.2197266, 35.8356284], [133.46191403, 35.47856499], [133.19824214, 35.58585159], [132.62695315, 35.47856499], [132.71484378, 35.22767234], [131.39648435, 34.43409792], [130.86914058, 34.34343605], [131.02294923, 33.9615863], [131.70410155, 34.0526594], [132.34130856, 33.81566631], [132.34130856, 34.41597337], [132.71484378, 34.28899189], [133.3740234, 34.43409792], [133.85742186, 34.36157631], [134.47265626, 34.75966609], [135.00000003, 34.66935854], [135.39550785, 34.75966609], [135.24169921, 34.34343605], [135.63720704, 33.44977657], [136.38427738, 34.1799976], [136.86767575, 34.47033515], [136.69189449, 35.13787914], [137.48291014, 34.66935854], [138.14208986, 34.68742799], [138.8891602, 35.22767234], [138.71337894, 34.65128523], [139.19677731, 34.99400377], [139.4824219, 35.35321613], [139.89990234, 35.69299463], [140.18554683, 35.56798049], [139.87792972, 35.20972166], [139.85595702, 34.93998512], [140.44921872, 35.22767234], [140.53710935, 35.65729625], [140.84472655, 35.74651223], [140.44921872, 36.20882308], [140.80078123, 36.9498918], [140.93261717, 38.09998263], [141.17431645, 38.47939468], [141.59179689, 38.35888789], [141.59179689, 38.95940881], [142.03125003, 39.58875729], [141.72363283, 40.4636663], [141.43798824, 40.69729899], [141.45996094, 41.45919539], [141.21826176, 41.29431727], [140.88867186, 41.52502959]]]]}
    },
    13: {
        "geometry": GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan_3857,
        "in_crs": 3857,
        "out_crs": 4326,
        "precision": 8,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'MultiPoint', 'coordinates': [[2.34886037, 48.8533241], [139.75309031, 35.68537295]]}, {'type': 'MultiLineString', 'coordinates': [[[-2.1368408, 47.28295555], [-1.88415531, 47.27550216], [-1.77978518, 47.20837422], [-1.56555172, 47.19717795], [-1.38427735, 47.2717751], [-1.30737303, 47.34626718], [-1.07116696, 47.36859436], [-0.93933101, 47.37603464], [-0.79101566, 47.37975441], [-0.70312503, 47.37975441], [-0.59875489, 47.40950297], [-0.47241215, 47.40950297], [-0.33508301, 47.40950297], [-0.2911377, 47.40578529], [-0.20874026, 47.33137713], [-0.04394531, 47.25313561], [0.08239743, 47.21956812], [0.16479495, 47.23448962], [0.43945314, 47.33510005], [0.604248, 47.36115298], [0.82397457, 47.41322032], [1.04370114, 47.41693747], [1.34033204, 47.55057927], [1.39526366, 47.63208194], [1.62597654, 47.7208492], [1.63696293, 47.78732553], [1.74682617, 47.83528341], [1.84021, 47.86108858], [1.96655274, 47.89793078], [2.20275882, 47.86477395], [2.31262206, 47.82053189], [2.65319827, 47.66908664], [2.76306151, 47.58764165], [2.95532227, 47.46894971], [2.85095214, 47.34254505], [3.0761719, 47.1673097], [3.09814452, 46.99524108], [3.49914554, 46.81885778], [3.68041991, 46.69466733], [3.70788572, 46.63057868], [3.83422855, 46.50595448], [4.02099611, 46.42649899], [4.05395503, 46.19884437], [4.06494143, 46.01603873], [4.03198242, 45.9129441], [4.10888674, 45.84410778], [4.21325688, 45.73685956], [4.18029787, 45.56021795], [4.25170899, 45.46783597], [4.20776368, 45.36372496], [4.14184566, 45.22461174], [4.03198242, 45.21106861], [3.92623903, 45.19171574], [3.92211918, 45.13943007], [3.91113278, 45.09679144], [3.9578247, 45.02015578], [3.90289308, 45.00268014], [3.91250613, 44.97645666], [3.93310549, 44.94730539], [3.90975953, 44.89382294]], [[135.42228699, 34.68291098], [135.5026245, 34.72242619], [135.61248783, 34.78899485], [135.68389895, 34.88705741], [135.73471072, 34.92422304], [135.73780056, 34.94139236], [135.70758815, 34.99822249], [135.69110874, 34.99822249], [135.65402988, 35.02999638], [135.57952882, 35.02212434], [135.54905895, 35.05262424], [135.51189421, 35.09266442], [135.51695819, 35.11653865], [135.49266811, 35.1291751], [135.50760269, 35.15121409], [135.51644328, 35.15345978], [135.51738741, 35.14665239], [135.53704264, 35.14430125], [135.54309369, 35.13215849], [135.56824212, 35.12829765], [135.57761909, 35.13886175], [135.57173971, 35.14558209], [135.58399201, 35.14419592], [135.60270311, 35.1384406], [135.60956956, 35.13212337], [135.63789371, 35.13984443], [135.63274385, 35.15409135], [135.64982414, 35.17079145], [135.67488669, 35.18664632], [135.68166736, 35.19667687], [135.70218083, 35.19836018], [135.70956229, 35.19302956], [135.71187976, 35.20256834], [135.71685787, 35.21161505], [135.72526933, 35.20130587], [135.73608397, 35.2103528], [135.74762822, 35.20383071], [135.75419428, 35.20873983], [135.75912953, 35.20183188], [135.76183319, 35.20453199], [135.77406402, 35.20558397], [135.77968595, 35.22199309], [135.77805515, 35.23573482]]]}, {'type': 'MultiPolygon', 'coordinates': [[[[2.211e-05, 0.00045926], [1.54e-05, 0.00045702], [1.54e-05, 0.00045024], [3.55e-06, 0.00044719], [3.9e-07, 0.00044489], [3.16e-06, 0.00044335], [-9.87e-06, 0.00044232], [-1.145e-05, 0.00044617], [-1.619e-05, 0.00044617], [-1.421e-05, 0.00044232], [-1.224e-05, 0.00043662], [-2.329e-05, 0.00043531], [-2.724e-05, 0.00043818], [-4.145e-05, 0.00043714], [-4.263e-05, 0.00043426], [-3.948e-05, 0.00043452], [-3.79e-05, 0.00043268], [-4.145e-05, 0.00043189], [-3.908e-05, 0.00042872], [-3.632e-05, 0.0004311], [-2.527e-05, 0.00042845], [-1.816e-05, 0.00042284], [-2.013e-05, 0.00042149], [-1.105e-05, 0.0004158], [-9.08e-06, 0.00041114], [-5.92e-06, 0.00040532], [-1.026e-05, 0.00040865], [-1.026e-05, 0.00039859], [-1.579e-05, 0.00038891], [5.13e-06, 0.00038313], [5.92e-06, 0.00038516], [1.698e-05, 0.00038139], [2.921e-05, 0.00038051], [2.645e-05, 0.00038603], [3.75e-05, 0.00039092], [4.421e-05, 0.00039063], [5.369e-05, 0.00038718], [5.803e-05, 0.00038805], [6.79e-05, 0.00039263], [6.829e-05, 0.00039605], [6.316e-05, 0.00039661], [6.04e-05, 0.00040448], [6.277e-05, 0.00040976], [6.198e-05, 0.00041634], [5.527e-05, 0.00041333], [5.487e-05, 0.0004177], [6.119e-05, 0.00042203], [6.79e-05, 0.00042712], [6.869e-05, 0.00043163], [7.382e-05, 0.00044], [6.04e-05, 0.00044103], [5.764e-05, 0.00044438], [5.132e-05, 0.00044387], [4.145e-05, 0.00044923], [2.605e-05, 0.00045477], [2.211e-05, 0.00045926]]], [[[0.00126562, 0.00037303], [0.00125684, 0.00036522], [0.00125803, 0.00035441], [0.00125457, 0.00034659], [0.00124687, 0.00033961], [0.00123306, 0.00033003], [0.0012299, 0.00033287], [0.00123424, 0.00033664], [0.00122773, 0.00033586], [0.00122871, 0.00033035], [0.00122082, 0.0003232], [0.001222, 0.00032015], [0.00121687, 0.00031855], [0.0012147, 0.00032192], [0.00119891, 0.00031871], [0.00119654, 0.00031967], [0.00119141, 0.00031871], [0.0011922, 0.00031646], [0.00118035, 0.00030933], [0.00117562, 0.00030851], [0.001177, 0.00030508], [0.00118312, 0.0003059], [0.00118884, 0.00030377], [0.00118884, 0.00030916], [0.0011922, 0.00030802], [0.00119812, 0.00030933], [0.00120246, 0.00030868], [0.00120799, 0.00031225], [0.00121273, 0.00031144], [0.00121628, 0.00031225], [0.0012149, 0.00030851], [0.00121845, 0.00030048], [0.00122516, 0.00030704], [0.0012295, 0.00030965], [0.00122792, 0.00031565], [0.00123503, 0.00031144], [0.00124095, 0.0003116], [0.00124766, 0.00031646], [0.00124608, 0.00031128], [0.00125043, 0.00031436], [0.00125299, 0.00031758], [0.00125674, 0.00032064], [0.00125931, 0.00031951], [0.00125654, 0.00031629], [0.00125635, 0.00031387], [0.00126168, 0.00031646], [0.00126247, 0.00032031], [0.00126523, 0.00032112], [0.00126168, 0.00032527], [0.00126483, 0.00033193], [0.00126602, 0.00034226], [0.00126819, 0.00034567], [0.00127194, 0.00034458], [0.00127194, 0.00034998], [0.00127589, 0.00035563], [0.00127313, 0.00036349], [0.00127056, 0.00036559], [0.00127076, 0.00037243], [0.00126859, 0.00037095], [0.00126562, 0.00037303]]]]}]}
    }
}

if test_dependencies()['ogr']:
    geometry_to_ogr_geometry_parameters = {
        0: {
            "geometry": POINT,
            "return_value": ogr.CreateGeometryFromJson(str(POINT))
        },
        1: {
            "geometry": POINT_WITH_BBOX,
            "return_value": ogr.CreateGeometryFromJson(str(POINT))
        },
        2: {
            "geometry": POINT_EMPTY,
            "return_value": ogr.CreateGeometryFromWkt(POINT_EMPTY_WKT)
        },
        3: {
            "geometry": LINESTRING,
            "return_value": ogr.CreateGeometryFromJson(str(LINESTRING))
        },
        4: {
            "geometry": LINESTRING_WITH_BBOX,
            "return_value": ogr.CreateGeometryFromJson(str(LINESTRING))
        },
        5: {
            "geometry": LINESTRING_EMPTY,
            "return_value": ogr.CreateGeometryFromWkt(LINESTRING_EMPTY_WKT)
        },
        6: {
            "geometry": POLYGON,
            "return_value": ogr.CreateGeometryFromJson(str(POLYGON))
        },
        7: {
            "geometry": POLYGON_WITH_BBOX,
            "return_value": ogr.CreateGeometryFromJson(str(POLYGON))
        },
        8: {
            "geometry": POLYGON_EMPTY,
            "return_value": ogr.CreateGeometryFromWkt(POLYGON_EMPTY_WKT)
        },
        9: {
            "geometry": MULTIPOINT,
            "return_value": ogr.CreateGeometryFromJson(str(MULTIPOINT))
        },
        10: {
            "geometry": MULTIPOINT_WITH_BBOX,
            "return_value": ogr.CreateGeometryFromJson(str(MULTIPOINT))
        },
        11: {
            "geometry": MULTIPOINT_EMPTY,
            "return_value": ogr.CreateGeometryFromWkt(MULTIPOINT_EMPTY_WKT)
        },
        12: {
            "geometry": MULTILINESTRING,
            "return_value": ogr.CreateGeometryFromJson(str(MULTILINESTRING))
        },
        13: {
            "geometry": MULTILINESTRING_WITH_BBOX,
            "return_value": ogr.CreateGeometryFromJson(str(MULTILINESTRING))
        },
        14: {
            "geometry": MULTILINESTRING_EMPTY,
            "return_value": ogr.CreateGeometryFromWkt(MULTILINESTRING_EMPTY_WKT)
        },
        15: {
            "geometry": MULTIPOLYGON,
            "return_value": ogr.CreateGeometryFromJson(str(MULTIPOLYGON))
        },
        16: {
            "geometry": MULTIPOLYGON_WITH_BBOX,
            "return_value": ogr.CreateGeometryFromJson(str(MULTIPOLYGON))
        },
        17: {
            "geometry": MULTIPOLYGON_EMPTY,
            "return_value": ogr.CreateGeometryFromWkt(MULTIPOLYGON_EMPTY_WKT)
        },
        18: {
            "geometry": GEOMETRYCOLLECTION,
            "return_value": ogr.CreateGeometryFromJson(str(GEOMETRYCOLLECTION))
        },
        19: {
            "geometry": GEOMETRYCOLLECTION_WITH_BBOX,
            "return_value": ogr.CreateGeometryFromJson(str(GEOMETRYCOLLECTION))
        },
        20: {
            "geometry": GEOMETRYCOLLECTION_EMPTY,
            "return_value": ogr.CreateGeometryFromWkt(GEOMETRYCOLLECTION_EMPTY_WKT)
        },
        21: {
            "geometry": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
            "return_value": ogr.CreateGeometryFromWkt(GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT)
        },
    }


    ogr_geometry_to_geometry_parameters = {
        0: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(POINT)),
            "bbox": False,
            "return_value": POINT,
        },
        1: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(POINT)),
            "bbox": True,
            "return_value": POINT_WITH_BBOX,
        },
        2: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(POINT_EMPTY_WKT),
            "bbox": True,
            "return_value": POINT_EMPTY,
        },
        3: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(LINESTRING)),
            "bbox": False,
            "return_value": LINESTRING,
        },
        4: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(LINESTRING)),
            "bbox": True,
            "return_value": LINESTRING_WITH_BBOX,
        },
        5: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(LINESTRING_EMPTY_WKT),
            "bbox": False,
            "return_value": LINESTRING_EMPTY,
        },
        6: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(POLYGON)),
            "bbox": False,
            "return_value": POLYGON,
        },
        7: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(POLYGON)),
            "bbox": True,
            "return_value": POLYGON_WITH_BBOX,
        },
        8: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(POLYGON_EMPTY_WKT),
            "bbox": True,
            "return_value": POLYGON_EMPTY,
        },
        9: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(MULTIPOINT)),
            "bbox": False,
            "return_value": MULTIPOINT,
        },
        10: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(MULTIPOINT)),
            "bbox": True,
            "return_value": MULTIPOINT_WITH_BBOX,
        },
        11: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(MULTIPOINT_EMPTY_WKT),
            "bbox": False,
            "return_value": MULTIPOINT_EMPTY,
        },
        12: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(MULTILINESTRING)),
            "bbox": False,
            "return_value": MULTILINESTRING,
        },
        13: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(MULTILINESTRING)),
            "bbox": True,
            "return_value": MULTILINESTRING_WITH_BBOX,
        },
        14: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(MULTILINESTRING_EMPTY_WKT),
            "bbox": True,
            "return_value": MULTILINESTRING_EMPTY,
        },
        15: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(MULTIPOLYGON)),
            "bbox": False,
            "return_value": MULTIPOLYGON,
        },
        16: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(MULTIPOLYGON)),
            "bbox": True,
            "return_value": MULTIPOLYGON_WITH_BBOX,
        },
        17: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(MULTIPOLYGON_EMPTY_WKT),
            "bbox": True,
            "return_value": MULTIPOLYGON_EMPTY,
        },
        18: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(GEOMETRYCOLLECTION)),
            "bbox": False,
            "return_value": GEOMETRYCOLLECTION,
        },
        19: {
            "ogr_geometry": ogr.CreateGeometryFromJson(str(GEOMETRYCOLLECTION)),
            "bbox": True,
            "return_value": GEOMETRYCOLLECTION_WITH_BBOX,
        },
        20: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(GEOMETRYCOLLECTION_EMPTY_WKT),
            "bbox": True,
            "return_value": GEOMETRYCOLLECTION_EMPTY,
        },
        21: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT),
            "bbox": False,
            "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES,
        },
        22: {
            "ogr_geometry": ogr.CreateGeometryFromWkt(GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WKT),
            "bbox": True,
            "return_value": GEOMETRY_COLLECTION_WITH_EMPTY_GEOMETRIES_WITH_BBOX,
        },
    }


def test_all():

    # geometry_type_to_2d_geometry_type
    print(test_function(geometry_type_to_2d_geometry_type, geometry_type_to_2d_geometry_type_parameters))

    # geometry_to_2d_geometry
    print(test_function(geometry_to_2d_geometry, geometry_to_2d_geometry_parameters))

    # geometry_to_geometry_collection
    print(test_function(geometry_to_geometry_collection, geometry_to_geometry_collection_parameters))

    # multi_geometry_to_single_geometry
    print(test_function(multi_geometry_to_single_geometry, multi_geometry_to_single_geometry_parameters))

    # single_geometry_to_multi_geometry
    print(test_function(single_geometry_to_multi_geometry, single_geometry_to_multi_geometry_parameters))

    # geometry_to_multi_geometry
    print(test_function(geometry_to_multi_geometry, geometry_to_multi_geometry_parameters))

    # geometry_to_wkb
    print(test_function(geometry_to_wkb, geometry_to_wkb_parameters))

    # wkb_to_geometry
    print(test_function(wkb_to_geometry, wkb_to_geometry_parameters))

    # geometry_to_wkt
    print(test_function(geometry_to_wkt, geometry_to_wkt_parameters))

    # wkt_to_geometry
    print(test_function(wkt_to_geometry, wkt_to_geometry_parameters))

    # force_rhr
    print(test_function(force_rhr, force_rhr_parameters))

    # geometry_to_bbox_parameters
    print(test_function(geometry_to_bbox, geometry_to_bbox_parameters))

    # reproject_geometry
    print(test_function(reproject_geometry, reproject_geometry_parameters))

    if test_dependencies()['ogr']:
        # geometry_to_ogr_geometry
        print(test_function(geometry_to_ogr_geometry, geometry_to_ogr_geometry_parameters))

        # ogr_geometry_to_geometry
        print(test_function(ogr_geometry_to_geometry, ogr_geometry_to_geometry_parameters))


if __name__ == '__main__':
    test_all()
