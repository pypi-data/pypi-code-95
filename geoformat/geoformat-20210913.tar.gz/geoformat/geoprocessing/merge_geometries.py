from geoformat.conversion.geometry_conversion import geometry_to_bbox
from geoformat.geoprocessing.connectors.operations import coordinates_to_bbox
from geoformat.geoprocessing.geoparameters.bbox import bbox_union


def merge_geometries(geom_a, geom_b, bbox=True):
    """
    geom_a
    geom_b
    bbox = True (default) + 5 % time


    Return a merging geometry result of adding two differents geometries
    !! Carfull this function does not "union" two geometry that intersects it add a geometry to an other !!

    Merging Table :

        Single AND Single
            Point + Point = MultiPoint
            LineString + LineString = MultiLineString
            Polygon + Polygon = MultiPolygon

        Single AND Multi
            Point + MultiPoint = MultiPoint
            LineString  + MultiLineString = MultiLineString
            Polygon + MultiPolygon = MultiPolygon

        Mixed Geometries Types and GeometryCollection
            Point + Polygon = GeometryCollection(Point, Polygon)
            GeometryCollection(Polygon + LineString) + LineSting = GeometryCollection(Polygon + MultiLineString)
            GeometryCollection(MultiPolygon, LineString), GeometryCollection(MultiPoint, LineString)
                = GeometryCollection(MultiPolygon, MultiLineString, MultiPoint)



    How does it works ?

        - first if geometry categories are the same

        - if geometry categories are differents or GeometryCollection
            We will have a GeometryCollection

    """
    new_geom = {}

    # check if geometries are empty
    geom_a_not_empty, geom_b_not_empty = False, False

    if geom_a.get('coordinates', geom_a.get('geometries')):
        geom_a_not_empty = True
    if geom_b.get('coordinates', geom_b.get('geometries')):
        geom_b_not_empty = True

    # if geometry is not empty
    if geom_a_not_empty is True and geom_b_not_empty is True:
        # if same geometry category (Point, MultiPoint), (LineString, MultiLineString), (Polygon, MultiPolygon)
        if geom_a['type'].replace('Multi', '') == geom_b['type'].replace('Multi', '') and geom_a[
            'type'] != 'GeometryCollection' and geom_b['type'] != 'GeometryCollection':
            new_geom_type = str(geom_a['type'])
            coordinates_or_geometries = list(geom_a['coordinates'])
            key_coordinates_or_geometry = 'coordinates'
            if 'Multi' in geom_a['type']:
                if 'Multi' in geom_b['type']:
                    for geom_coordinates in geom_b['coordinates']:
                        if geom_coordinates not in coordinates_or_geometries:
                            coordinates_or_geometries.append(list(geom_coordinates))
                else:
                    if geom_b['coordinates'] not in coordinates_or_geometries:
                        coordinates_or_geometries.append(list(geom_b['coordinates']))

            else:
                if 'Multi' in geom_b['type']:
                    coordinates_or_geometries = [coordinates_or_geometries]
                    len_coordinates_or_geometries = len(coordinates_or_geometries)
                    for geom_coordinates in geom_b['coordinates']:
                        if geom_coordinates not in coordinates_or_geometries:
                            coordinates_or_geometries.append(list(geom_coordinates))
                    if len_coordinates_or_geometries < len(coordinates_or_geometries):
                        new_geom_type = 'Multi' + new_geom_type
                else:
                    if geom_a['coordinates'] != geom_b['coordinates']:
                        coordinates_or_geometries = [coordinates_or_geometries, list(geom_b['coordinates'])]
                        # add Mutli to type
                        new_geom_type = 'Multi' + new_geom_type

            new_geom['type'] = new_geom_type
            new_geom[key_coordinates_or_geometry] = coordinates_or_geometries
        else:
            if geom_a['type'] == 'GeometryCollection' and geom_b['type'] == 'GeometryCollection':
                # first loop on geom_a geometries
                for i_a, geojson_geometrie_a in enumerate(geom_a['geometries']):
                    if i_a == 0:
                        new_geom = geojson_geometrie_a
                    else:
                        new_geom = merge_geometries(new_geom, geojson_geometrie_a, bbox=bbox)

                # add geom_ b geometries
                for geojson_geometrie_b in geom_b['geometries']:
                    new_geom = merge_geometries(new_geom, geojson_geometrie_b, bbox=bbox)

            elif geom_a['type'] == 'GeometryCollection' or geom_b['type'] == 'GeometryCollection':
                if geom_a['type'] == 'GeometryCollection':
                    ori_geom_collect = dict(geom_a)
                    ori_geom_simple = dict(geom_b)
                else:
                    ori_geom_collect = dict(geom_b)
                    ori_geom_simple = dict(geom_a)

                # first loop on ori_geom_collect geometries
                for i_a, geojson_geometrie_a in enumerate(ori_geom_collect['geometries']):
                    if i_a == 0:
                        new_geom = geojson_geometrie_a
                    else:
                        new_geom = merge_geometries(new_geom, geojson_geometrie_a, bbox=bbox)

                added_geom = False
                # then we see if ori_geom_simple as similar geom type in ori_geom_collect else we had
                for i_geom, geometry in enumerate(new_geom['geometries']):
                    if geometry['type'].replace('Multi', '') == ori_geom_simple['type'].replace('Multi', ''):
                        replace_geom = merge_geometries(geometry, ori_geom_simple, bbox=bbox)
                        new_geom['geometries'][i_geom] = replace_geom
                        added_geom = True
                        # end loop
                        break

                if added_geom is False:
                    # if not break we had ori_geom_simple to new_geom GEOMETRYCOLLECTION
                    new_geom['geometries'] = new_geom['geometries'] + [dict(ori_geom_simple)]

            else:
                new_geom['type'] = 'GeometryCollection'
                new_geom['geometries'] = [dict(geom_a), dict(geom_b)]

    else:
        if geom_a_not_empty is True:
            new_geom_type = str(geom_a['type'])
            coordinates_or_geometries = list(geom_a['coordinates'])
        elif geom_b_not_empty is True:
            new_geom_type = str(geom_b['type'])
            coordinates_or_geometries = list(geom_b['coordinates'])

        # both geometries are empty
        else:
            if geom_a['type'] == geom_b['type']:
                new_geom_type = str(geom_a['type'])
            else:
                new_geom_type = 'GeometryCollection'

            coordinates_or_geometries = []

        if new_geom_type == 'GeometryCollection':
            key_coordinates_or_geometry = 'geometries'
        else:
            key_coordinates_or_geometry = 'coordinates'

        # add type and coordinates/geometries
        new_geom['type'] = new_geom_type
        new_geom[key_coordinates_or_geometry] = coordinates_or_geometries

    if bbox is True:
        new_geom['bbox'] = geometry_to_bbox(new_geom)

    return new_geom
