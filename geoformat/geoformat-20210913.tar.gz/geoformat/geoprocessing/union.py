from geoformat.conversion.geometry_conversion import (
    geometry_to_ogr_geometry,
    ogr_geometry_to_geometry
)


def union_by_split(geometry_list, split_factor=2, bbox=True):
    """
    Union geometry list with split list method (split_factor default 2 by 2)
    * OGR dependencie : Union *
    """

    len_list = len(geometry_list)
    if len_list > split_factor:
        union_geom_list = []
        for i in range(split_factor):
            # first iteration
            if i == 0:
                split_geometry_list = geometry_list[:int(len_list / split_factor)]
            # last iteration
            elif i == split_factor - 1:
                begin = int(len_list / split_factor) * i
                split_geometry_list = geometry_list[begin:]
            # others iterations
            else:
                begin = int(len_list / split_factor) * i
                end = (int(len_list / split_factor)) * (i + 1)
                split_geometry_list = geometry_list[begin:end]

            # adding union to geom list
            union_geom_list.append(union_by_split(split_geometry_list, split_factor))

        for i, union_geom in enumerate(union_geom_list):
            if i == 0:
                ogr_geom_unioned = geometry_to_ogr_geometry(union_geom)
            else:
                temp_geom = geometry_to_ogr_geometry(union_geom)
                ogr_geom_unioned = ogr_geom_unioned.Union(temp_geom)

        geojson_unioned = ogr_geometry_to_geometry(ogr_geom_unioned, bbox=bbox)

        return geojson_unioned

    else:
        if len(geometry_list) > 1:

            for i, union_geom in enumerate(geometry_list):
                if i == 0:
                    ogr_geom_unioned = geometry_to_ogr_geometry(union_geom)
                else:
                    temp_geom = geometry_to_ogr_geometry(union_geom)
                    ogr_geom_unioned = ogr_geom_unioned.Union(temp_geom)

            geojson_unioned = ogr_geometry_to_geometry(ogr_geom_unioned, bbox=bbox)

            return geojson_unioned

        else:
            return geometry_list[0]
