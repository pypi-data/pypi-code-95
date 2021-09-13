import copy

from geoformat.conf.format_data import value_to_iterable_value
from geoformat.conversion.geometry_conversion import (
    multi_geometry_to_single_geometry,
    geometry_type_to_2d_geometry_type,
    geometry_to_2d_geometry,
    reproject_geometry
)
from geoformat.geoprocessing.geoparameters.bbox import (
    bbox_union
)

from geoformat.conversion.feature_conversion import feature_serialize


def multi_geometry_to_single_geometry_geolayer(geolayer):
    # creation de l'output en copiant les metadata de l'input
    geolayer_out = copy.deepcopy(geolayer)

    del geolayer_out['features']
    if geolayer['metadata']['geometry_ref']['type'].upper() == 'MULTIPOINT':  # 'MultiPoint'
        geolayer_out['metadata']['geometry_ref']['type'] = 'Point'
    elif geolayer['metadata']['geometry_ref']['type'].upper() == 'MULTILINESTRING':  # 'MultiLineString'
        geolayer_out['metadata']['geometry_ref']['type'] = 'LineString'
    elif geolayer['metadata']['geometry_ref']['type'].upper() == 'MULTIPOLYGON':  # 'MultiPolygon'
        geolayer_out['metadata']['geometry_ref']['type'] = 'Polygon'

    # boucle et transformation des géométries multi part en single part
    new_i_feat = 0
    geolayer_out['features'] = {}
    for i_feat in geolayer['features']:

        feature = geolayer['features'][i_feat]
        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        geometry = feature['geometry']
        for new_geometry in multi_geometry_to_single_geometry(geometry):
            new_feature = {'attributes': feature['attributes'],
                           'geometry': new_geometry}

            # if feature is serialized
            if 'feature_serialize' in geolayer['metadata']:
                if geolayer['metadata']['feature_serialize']:
                    new_feature = str(new_feature)

            geolayer_out['features'][new_i_feat] = new_feature
            new_i_feat += 1

    return geolayer_out


def geolayer_to_2d_geolayer(input_geolayer):
    """

    :param input_geolayer:
    :return:
    """
    new_geolayer = {'features': {}, 'metadata': copy.deepcopy(input_geolayer['metadata'])}
    input_geometry_type = input_geolayer['metadata']['geometry_ref']['type']
    if isinstance(input_geometry_type, (list, tuple)):
        new_geometry_type = []
        for geom_type in input_geometry_type:
            new_geometry_type.append(geometry_type_to_2d_geometry_type(geom_type))
    else:
        new_geometry_type = geometry_type_to_2d_geometry_type(input_geometry_type)
    new_geolayer['metadata']['geometry_ref']['type'] = new_geometry_type

    if 'extent' in new_geolayer['metadata']['geometry_ref']:
        bbox_extent = True
    else:
        bbox_extent = False

    for i_feat in input_geolayer['features']:
        input_feature = input_geolayer['features'][i_feat]
        if 'feature_serialize' in input_geolayer['metadata']:
            if input_geolayer['metadata']['feature_serialize'] == True:
                input_feature = eval(input_feature)

        output_feature = copy.deepcopy(input_feature)

        if 'geometry' in input_feature:
            input_geometry = input_feature['geometry']
            new_geometry = geometry_to_2d_geometry(input_geometry, bbox=bbox_extent)
            output_feature['geometry'] = new_geometry

        if 'feature_serialize' in input_geolayer['metadata']:
            if input_geolayer['metadata']['feature_serialize'] == True:
                output_feature = str(output_feature)

        new_geolayer['features'][i_feat] = output_feature

    return new_geolayer


def create_geolayer_from_i_feat_list(geolayer, i_feat_list, serialize=False, reset_i_feat=True):
    """
    Create a new layer with i_feat_list from an input layer
    """
    i_feat_list = value_to_iterable_value(value=i_feat_list, output_iterable_type=list)

    new_layer = {
        'metadata': dict(geolayer['metadata'])
    }

    if serialize:
        geolayer['metadata']['feature_serialize'] = True

    new_layer['features'] = {}
    for new_i_feat, i_feat in enumerate(i_feat_list):
        if i_feat in geolayer['features']:
            if serialize:
                new_feature = feature_serialize(geolayer['features'][i_feat])
            else:
                new_feature = geolayer['features'][i_feat]

        if reset_i_feat:
            new_layer['features'][new_i_feat] = new_feature
        else:
            new_layer['features'][i_feat] = new_feature

    return new_layer


def reproject_geolayer(geolayer, out_crs, in_crs=None):
    """
    Reproject geolayer from crs to an other

    :param geolayer: input geolayer.
    :param out_crs: new crs.
    :param in_crs:  input geolayer crs (if not present in geolayer metadata).
    :return:
    """

    geolayer = copy.deepcopy(geolayer)
    if not in_crs:
        in_crs = geolayer['metadata']['geometry_ref']['crs']

    # change metadata
    geolayer['metadata']['geometry_ref']['crs'] = out_crs


    # reproject geometry
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if geometry in feature
        if 'geometry' in feature.keys():
            feature_geometry = feature['geometry']
            new_geometry = reproject_geometry(
                geometry=feature_geometry,
                in_crs=in_crs,
                out_crs=out_crs,
            )

            # assign new geometry
            feature['geometry'] = new_geometry


    return geolayer
