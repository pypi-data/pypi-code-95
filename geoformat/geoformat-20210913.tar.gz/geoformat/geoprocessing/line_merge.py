from geoformat.conversion.geometry_conversion import (
    multi_geometry_to_single_geometry,
    geometry_to_geometry_collection
)
from geoformat.conversion.coordinates_conversion import format_coordinates
from geoformat.geoprocessing.connectors.operations import coordinates_to_bbox
from geoformat.geoprocessing.geoparameters.bbox import bbox_union


def line_merge(geometry, bbox=True):
    """
    Returns a (set of) LineString(s) formed by sewing together the constituent line work of a MULTILINESTRING.

    """

    def merge_loop_over_single_linestring(multilinestring):
        """
        This function define :
            * start_dict store each start point of a line part -> at each point you store the geom position in
            coordinates list.
            * end_dict store each end point point of a line part -> at each point you store the geom position in
            coordinates list.

            * hub_point with this two dictionaries we create hub_point that store for each unique point the counting
            number of times this point appears in the multilinestring.

            * we loop on each point in hub point and we try to know, if this point appears in two line, its position
            (start / end) for each of the lines to which it belongs. At this time you have 3 possibilities :
                # 2 points in start_dict
                # 2 points in end_dict
                # 1 point in start_dict and 1 point in end_dict

                * we initialize some variables :
                    [before loop}
                    - final_coordinates (list) [before loop] : store each part to create a new geometry in output.
                    - computed_idx_geom (set) [before loop] : for each point on which we loop we store the under
                     geometry index.
                    - reloop (bool) [before loop] : if condition above (pass_point is True) then reloop is True.

                    [reinitialize at each loop step's]
                    - for_point_computed_idx_geom : store for each of two points the under geometry index. If we have
                    just one index inside it means we've processed a line that starts and ends at the same place
                    (a loop). In this case we don't change the geometry.
                    - result_part_coordinates (list) : store part new geometry.
                    - pass_point (bool) : if the geometry to which the point belongs has already been modified,
                     then it is not modified and pass_point is True.

                for each of 3 possibilities we create a new under geometry (result_part_coordinates) that we store step
                by step in final_ordinates if pass_point is False and for_point_computed_idx_geom.

            * Then we recreate a new geometry with data in final_coordinates and we add non concerned, by merging, geometries (geometries
            that are'nt in computed_idx_geom).

            * We launch format coordinates to delete duplicate coordinates if exists
        """

        start_dict = {}
        end_dict = {}
        hub_point = {}

        single_geom_list = list(multi_geometry_to_single_geometry(multilinestring, bbox=False))

        for i_part_geom, single_geom in enumerate(single_geom_list):
            if single_geom['coordinates']:
                # begin
                start_point = tuple(single_geom['coordinates'][0])
                try:
                    start_dict[start_point].update({i_part_geom})
                except KeyError:
                    start_dict[start_point] = {i_part_geom}

                # end
                end_point = tuple(single_geom['coordinates'][-1])
                try:
                    end_dict[end_point].update({i_part_geom})
                except KeyError:
                    end_dict[end_point] = {i_part_geom}

                # count points occurrence
                # if count > 2 then we cannot merge geometries
                # count for start point
                hub_point = {point: len(start_dict[point]) for point in start_dict}
                # count for end point
                for end_point in end_dict:
                    if end_point in hub_point:
                        hub_point[end_point] = hub_point[end_point] + len(end_dict[end_point])
                    else:
                        hub_point[end_point] = len(end_dict[end_point])

        if hub_point:
            # loop over hub_point if at least one point exists more than one time we can merge
            # else we return input geometry
            to_merge = False
            for point, point_value in hub_point.items():
                if point_value > 1:
                    to_merge = True
                    break

            if to_merge is True:
                computed_idx_geom = set([])
                final_coordinates = []
                reloop = False

                for i_point, point in enumerate(hub_point):
                    if hub_point[point] == 2:
                        # here three configurations are possible
                        # 2 points in start_dict
                        # 2 points in end_dict
                        # 1 point in start_dict and 1 point in end_dict
                        # As it possible to have a point in both dict (third configuration) and a point is always located
                        # between end of first geom and begin of second geom we begin with end_dict then start_dict

                        result_part_coordinates = []
                        pass_point = False
                        for_point_computed_idx_geom = set([])
                        if point in end_dict:
                            if end_dict[point] & computed_idx_geom:
                                reloop = True
                                pass_point = True
                            else:
                                for i_idx, i_part_geom in enumerate(end_dict[point]):
                                    for_point_computed_idx_geom.update({i_part_geom})
                                    geom = multilinestring['coordinates'][i_part_geom]
                                    if i_idx == 0:
                                        result_part_coordinates += geom
                                    else:
                                        # reverse geom
                                        geom.reverse()
                                        # add to result
                                        result_part_coordinates = result_part_coordinates + geom[1:]

                        if point in start_dict:
                            if start_dict[point] & computed_idx_geom:
                                reloop = True
                                pass_point = True
                            else:
                                for i_idx, i_part_geom in enumerate(start_dict[point]):
                                    # add i_part_geom to computed_idx_geom
                                    for_point_computed_idx_geom.update({i_part_geom})
                                    geom = multilinestring['coordinates'][i_part_geom]
                                    if i_idx == 0:
                                        result_part_coordinates += geom[1:]
                                    else:
                                        # reverse geom
                                        geom.reverse()
                                        # add to result
                                        result_part_coordinates = geom + result_part_coordinates

                        # add result_part_coordinates to final_coordinates
                        if result_part_coordinates and not pass_point:
                            if len(for_point_computed_idx_geom) == 2:
                                final_coordinates.append(result_part_coordinates)
                            else:
                                i_part_geom = list(for_point_computed_idx_geom)[0]
                                geom = multilinestring['coordinates'][i_part_geom]
                                final_coordinates.append(geom)

                        # if this point is not passing we add geom part in computed_idx_geom
                        if not pass_point:
                            computed_idx_geom.update(for_point_computed_idx_geom)

                # add non-computed idx geom
                for i_part_geom, single_geom in enumerate(single_geom_list):
                    if not {i_part_geom} & computed_idx_geom:
                        final_coordinates.append(single_geom['coordinates'])

                if len(final_coordinates) == 1:
                    final_geometry = {'type': 'LineString', 'coordinates': final_coordinates[0]}
                    # we do not have to reloop
                    reloop = False
                else:
                    final_geometry = {'type': 'MultiLineString', 'coordinates': final_coordinates}

                if reloop:
                    final_geometry = merge_loop_over_single_linestring(final_geometry)

            #we return input geometry
            else:
                final_geometry = multilinestring
        else:
            final_geometry = multilinestring

        return final_geometry

    # init bbox for geometry collection
    bbox_geometry_collection = None

    # force input geometry to geometry collection
    geometry_collection = geometry_to_geometry_collection(geometry, bbox=False)
    # loop on each geometry
    new_geometry_collection = {'type': 'GeometryCollection', 'geometries': list(geometry_collection['geometries'])}

    for i_geom, geometry_in_collection in enumerate(geometry_collection['geometries']):
        # if there is linestring in geometry_in_collection type we launch a line_merge
        if "MULTILINESTRING" in geometry_in_collection['type'].upper():
            merged_geometry = merge_loop_over_single_linestring(geometry_in_collection)
        else:
            merged_geometry = geometry_in_collection

        # format coordinates delete duplicates coordinates
        merged_geometry['coordinates'] = format_coordinates(coordinates_list_tuple=merged_geometry['coordinates'],
                                                            delete_duplicate_following_coordinates=True)
        # add bbox geometry if required
        if bbox and merged_geometry['coordinates']:
            if 'bbox' not in merged_geometry:
                merged_geometry['bbox'] = coordinates_to_bbox(merged_geometry['coordinates'])
            if i_geom == 0:
                bbox_geometry_collection = merged_geometry['bbox']
            else:
                bbox_geometry_collection = bbox_union(bbox_geometry_collection, merged_geometry['bbox'])

        new_geometry_collection['geometries'][i_geom] = merged_geometry

    # add bbox to geometry collection
    if bbox and bbox_geometry_collection:
        new_geometry_collection['bbox'] = bbox_geometry_collection

    # if new_geometry_collection contain more than one geometry we return geometry collection
    if len(new_geometry_collection['geometries']) > 1:
        output_geometry_collection = new_geometry_collection
    # else we return a simple geometry or multi geometry
    else:
        # if geometry not empty
        if new_geometry_collection['geometries']:
            output_geometry_collection = new_geometry_collection['geometries'][0]
        else:
            output_geometry_collection = new_geometry_collection

    return output_geometry_collection
