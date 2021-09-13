"""
Contributors :
  Guilhain Averlant (Maintainer)
  Eliette Catelin
  Quentin Lecuire
  Charlotte Montesinos Chevalley
  Coralie Rabiniaux
"""

from geoformat.constraints.primary_key import create_pk

from geoformat.conversion.bbox_conversion import (
    envelope_to_bbox,
    bbox_to_envelope,
    bbox_extent_to_2d_bbox_extent,
    bbox_to_polygon_coordinates
)
from geoformat.conversion.bytes_conversion import (
    int_to_4_bytes_integer,
    float_to_double_8_bytes_array,
    coordinates_list_to_bytes,
    double_8_bytes_to_float,
    integer_4_bytes_to_int
)
from geoformat.conversion.coordinates_conversion import (
    format_coordinates,
    coordinates_to_2d_coordinates,
    coordinates_to_centroid
)
from geoformat.conversion.feature_conversion import (
    feature_serialize,
    feature_deserialize,
    features_geometry_ref_scan,
    check_if_value_is_from_datetime_lib,
    check_if_value_is_date,
    check_if_value_is_datetime,
    check_if_value_is_time,
    return_if_value_is_time_date_or_datetime,
    features_fields_type_scan,
    feature_list_to_geolayer,
    feature_filter_geometry,
    feature_filter_attributes,
    feature_filter,
    features_filter
)
from geoformat.conversion.fields_conversion import (
    update_field_index,
    recast_field_value,
    recast_field,
    drop_field
)

from geoformat.conversion.geolayer_conversion import (
    multi_geometry_to_single_geometry_geolayer,
    geolayer_to_2d_geolayer,
    create_geolayer_from_i_feat_list,
    reproject_geolayer
)

from geoformat.conversion.geometry_conversion import (
    geometry_type_to_2d_geometry_type,
    geometry_to_2d_geometry,
    geometry_to_geometry_collection,
    single_geometry_to_multi_geometry,
    multi_geometry_to_single_geometry,
    geometry_to_multi_geometry,
    ogr_geometry_to_geometry,
    geometry_to_ogr_geometry,
    geometry_to_wkb,
    wkb_to_geometry,
    geometry_to_wkt,
    wkt_to_geometry,
    force_rhr,
    geometry_to_bbox,
    reproject_geometry
)

from geoformat.conversion.metadata_conversion import (
    geometries_scan_to_geometries_metadata,
    fields_scan_to_fields_metadata,
    reorder_metadata_field_index_after_field_drop
)

from geoformat.conversion.precision_tolerance_conversion import (
    deduce_rounding_value_from_float,
    deduce_precision_from_round
)

from geoformat.conversion.segment_conversion import segment_list_to_linestring

from geoformat.db.db_request import (
    sql,
    sql_select_to_geolayer
)

from geoformat.driver.ogr.ogr_driver import (
    ogr_layer_to_geolayer,
    ogr_layers_to_geocontainer,
    geolayer_to_ogr_layer,
    geocontainer_to_ogr_data_source,
    geoformat_geom_type_to_ogr_geom_type,
    verify_geom_compatibility
)


from geoformat.driver.geojson_driver import (
    feature_attributes_to_properties,
    geoformat_feature_to_geojson_feature,
    geolayer_to_geojson,
    load_json_data,
    json_object_to_feature_generator,
    from_geojson_get_features_list,
    geojson_to_geolayer
)

from geoformat.driver.postgresql_driver import (
    fields_metadata_to_create_table_fields_structure,
    geometry_ref_to_geometry_field_structure,
    format_to_posgresq_values,
    geolayer_to_postgres
)

from geoformat.explore_data.print_data import (
    print_features_data_table,
    print_metadata_field_table
)

from geoformat.explore_data.random_geometry import (
    random_point,
    random_segment,
    random_bbox
)

from geoformat.geoprocessing.connectors.operations import (
    coordinates_to_point,
    coordinates_to_segment,
    coordinates_to_bbox,
    segment_to_bbox
)

from geoformat.geoprocessing.connectors.predicates import (
    point_intersects_point,
    point_intersects_segment,
    point_intersects_bbox,
    segment_intersects_segment,
    segment_intersects_bbox,
    bbox_intersects_bbox,
    ccw_or_cw_segments,
    point_position_segment
)

from geoformat.geoprocessing.generalization.ramer_douglas_peucker import ramer_douglas_peucker
from geoformat.geoprocessing.generalization.visvalingam_whyatt import visvalingam_whyatt

from geoformat.geoprocessing.geoparameters.bbox import (
    extent_bbox,
    bbox_union,
    point_bbox_position
)

from geoformat.geoprocessing.geoparameters.boundaries import(
    ccw_or_cw_boundary
)

from geoformat.geoprocessing.geoparameters.lines import (
    get_slope_between_two_points,
    get_intercept_from_point_and_slope,
    get_slope_from_point_and_intercept,
    line_parameters,
    perpendicular_line_parameters_at_point,
    point_at_distance_with_line_parameters,
    crossing_point_from_lines_parameters
)

from geoformat.geoprocessing.matrix.adjacency import (
    create_adjacency_matrix,
    get_area_intersecting_neighbors_i_feat,
    get_neighbor_i_feat
)

from geoformat.geoprocessing.measure.area import shoelace_formula, triangle_area

from geoformat.geoprocessing.measure.distance import (
    euclidean_distance,
    manhattan_distance,
    euclidean_distance_point_vs_segment,
    point_vs_segment_distance
)

from geoformat.geoprocessing.measure.length import segment_length

from geoformat.geoprocessing.area import geometry_area

from geoformat.geoprocessing.length import geometry_length

from geoformat.geoprocessing.line_merge import line_merge

from geoformat.geoprocessing.merge_geometries import merge_geometries

from geoformat.geoprocessing.point_on_linestring import (
    point_at_a_distance_on_segment,
    points_on_linestring_distance
)

from geoformat.geoprocessing.simplify import (simplify)

from geoformat.geoprocessing.split import (
    segment_split_by_point,
    linestring_split_by_point
)

from geoformat.geoprocessing.union import union_by_split

from geoformat.index.attributes.hash import create_attribute_index

from geoformat.index.geometry.grid import (
    bbox_to_g_id,
    point_to_g_id,
    g_id_to_bbox,
    g_id_to_point,
    g_id_neighbor_in_grid_index,
    create_grid_index,
    grid_index_to_geolayer
)

from geoformat.obj.geocontainer import get_geocontainer_extent

from geoformat.obj.geometry import (
    len_coordinates,
    len_coordinates_in_geometry
)

from geoformat.processing.data.clauses import (
    clause_where,
    clause_group_by,
    clause_order_by
)

from geoformat.processing.data.field_statistics import field_statistics

from geoformat._version import __version__

__all__ = (
    # constraints
    [create_pk] +
    # conversion.bbox
    [envelope_to_bbox, bbox_to_envelope, bbox_extent_to_2d_bbox_extent,  bbox_to_polygon_coordinates] +
    # conversion.bytes
    [int_to_4_bytes_integer, float_to_double_8_bytes_array, coordinates_list_to_bytes, double_8_bytes_to_float,
     integer_4_bytes_to_int] +
    # conversion.coordinates
    [format_coordinates, coordinates_to_2d_coordinates, coordinates_to_centroid] +
    # conversion.feature
    [feature_serialize, feature_deserialize, features_geometry_ref_scan, check_if_value_is_from_datetime_lib,
     check_if_value_is_date, check_if_value_is_datetime, check_if_value_is_time,
     return_if_value_is_time_date_or_datetime, features_fields_type_scan, feature_list_to_geolayer,
     feature_filter_geometry, feature_filter_attributes, feature_filter, features_filter] +
    # conversion.fields
    [update_field_index, recast_field_value, recast_field, drop_field] +
    # conversion.geolayer
    [multi_geometry_to_single_geometry_geolayer, geolayer_to_2d_geolayer, create_geolayer_from_i_feat_list,
     reproject_geolayer] +
    # conversion.geometry
    [geometry_type_to_2d_geometry_type, geometry_to_2d_geometry, geometry_to_geometry_collection,
     single_geometry_to_multi_geometry, multi_geometry_to_single_geometry, geometry_to_multi_geometry,
     ogr_geometry_to_geometry, geometry_to_ogr_geometry, geometry_to_wkb, wkb_to_geometry, geometry_to_wkt,
     wkt_to_geometry, force_rhr, geometry_to_bbox, reproject_geometry] +
    # conversion.metadata
    [geometries_scan_to_geometries_metadata, fields_scan_to_fields_metadata,
     reorder_metadata_field_index_after_field_drop] +
    # conversion.precision_tolerance
    [deduce_rounding_value_from_float, deduce_precision_from_round] +
    # conversion.segment_conversion
    [segment_list_to_linestring] +
    # db
    [sql, sql_select_to_geolayer] +
    # driver.ogr
    [ogr_layer_to_geolayer, ogr_layers_to_geocontainer, geolayer_to_ogr_layer, geocontainer_to_ogr_data_source,
     geoformat_geom_type_to_ogr_geom_type, verify_geom_compatibility] +
    # driver.geojson
    [feature_attributes_to_properties, geoformat_feature_to_geojson_feature, geolayer_to_geojson, load_json_data,
     json_object_to_feature_generator, from_geojson_get_features_list, geojson_to_geolayer] +
    # driver.prostgresql
    [fields_metadata_to_create_table_fields_structure, geometry_ref_to_geometry_field_structure,
     format_to_posgresq_values, geolayer_to_postgres] +
    # explore_data.print_data
    [print_features_data_table, print_metadata_field_table] +
    # explore_data.random_geometry
    [random_point, random_segment, random_bbox] +
    # geoprocessing.connectors.operations
    [coordinates_to_point, coordinates_to_segment, coordinates_to_bbox, segment_to_bbox] +
    # geoprocessing.connectors.predicates
    [point_intersects_point, point_intersects_segment, point_intersects_bbox, segment_intersects_segment,
     segment_intersects_segment, segment_intersects_bbox, bbox_intersects_bbox, ccw_or_cw_segments,
     point_position_segment] +
    # geoprocessing.generalization
    [ramer_douglas_peucker, visvalingam_whyatt] +
    # geoprocessing.geoparameters.bbox
    [extent_bbox, bbox_union, point_bbox_position] +
    # geoprocessing.geoparameters.boundaries
    [ccw_or_cw_boundary] +
    # geoprocessing.geoparameters.lines
    [get_slope_between_two_points, get_intercept_from_point_and_slope, get_slope_from_point_and_intercept,
     line_parameters, perpendicular_line_parameters_at_point, point_at_distance_with_line_parameters,
     crossing_point_from_lines_parameters] +
    # geoprocession.matrix.adjacency
    [create_adjacency_matrix, get_area_intersecting_neighbors_i_feat, get_neighbor_i_feat] +
    # geoprocessing.measure.area
    [shoelace_formula, triangle_area] +
    # geoprocessing.measure.distance
    [euclidean_distance, manhattan_distance, euclidean_distance_point_vs_segment, point_vs_segment_distance] +
    # geoprocessing.measure.length
    [segment_length] +
    # geoprocessing.area
    [geometry_area] +
    # geoprocessing.length
    [geometry_length] +
    # geoprocessing.line_merge
    [line_merge] +
    # geoprocessing.merge_geometries
    [merge_geometries] +
    # geoprocessing.point_on_linestring
    [point_at_a_distance_on_segment, points_on_linestring_distance] +
    # geoprocessing.simplify
    [simplify] +
    # geoprocessing.split
    [segment_split_by_point, linestring_split_by_point] +
    # geoprocessing.union
    [union_by_split] +
    # index.attributes.hash
    [create_attribute_index] +
    # index.geometry.grid
    [bbox_to_g_id, point_to_g_id, g_id_to_bbox, g_id_to_point, g_id_neighbor_in_grid_index, create_grid_index,
     grid_index_to_geolayer] +
    # obj.geocontainer
    [get_geocontainer_extent] +
    # obj.geometry
    [len_coordinates, len_coordinates_in_geometry] +
    # processing.data.clauses
    [clause_where, clause_group_by, clause_order_by] +
    # processing.data.fields_statistics
    [field_statistics]
)
