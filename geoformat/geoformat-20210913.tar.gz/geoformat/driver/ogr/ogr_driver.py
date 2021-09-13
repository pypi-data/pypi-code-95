import os.path
import sys

try:
    from osgeo import ogr, osr
    import_ogr_success = True
except ImportError:
    import_ogr_success = False

from geoformat.conf.error_messages import import_ogr_error

from geoformat.conf.driver_variable import (
    OGR_DRIVER_NAMES,
    OGR_FORMAT_ESRI_SHAPEFILE,
    OGR_FORMAT_KML,
    OGR_FORMAT_XLSX,
    OGR_FORMAT_CSV,
    OGR_FORMAT_GEOJSON,
    OGR_FORMAT_POSTGRESQL,
    field_driver_uncompatibility
)
from geoformat.conf.geometry_variable import (
    GEOMETRY_CODE_TO_GEOMETRY_TYPE,
    GEOMETRY_TYPE
)
from geoformat.conversion.geometry_conversion import (
    ogr_geometry_to_geometry,
    geometry_to_ogr_geometry
)
from geoformat.geoprocessing.connectors.predicates import bbox_intersects_bbox
from geoformat.geoprocessing.geoparameters.bbox import bbox_union
from geoformat.conf.fields_variable import (
    field_metadata_width_required,
    field_metadata_precision_required
)
from geoformat.conversion.feature_conversion import (
    feature_serialize,
    feature_deserialize
)


DATA_TYPE = {
    "OFSTBoolean": 1,
    "OFSTFloat32": 3,
    "OFSTInt16": 2,
    "OFSTNone": 0,
    "OFTBinary": 8,
    "OFTDate": 9,
    "OFTDateTime": 11,
    "OFTInteger": 0,
    "OFTInteger64": 12,
    "OFTInteger64List": 13,
    "OFTIntegerList": 1,
    "OFTReal": 2,
    "OFTRealList": 3,
    "OFTString": 4,
    "OFTStringList": 5,
    "OFTTime": 10,
    "OFTWideString": 6,
    "OFTWideStringList": 7
}

geoformat_field_type_to_ogr_field_type = {
    'Integer': 0,
    'IntegerList': 1,
    'Real': 2,
    'RealList': 3,
    'String': 4,
    'StringList': 5,
    'Binary': 8,
    'Date': 9,
    'Time': 10,
    'DateTime': 11,
    'Boolean': (0, 1)
}


ogr_field_type_to_geoformat_field_type = {
    8: 'Binary',
    9: 'Date',
    11: 'DateTime',
    0: 'Integer',
    12: 'Integer',
    13: 'IntegerList',
    1: 'IntegerList',
    2: 'Real',
    3: 'RealList',
    4: 'String',
    5: 'StringList',
    10: 'Time',
    6: 'String',
    7: 'StringList',
    (0, 1): 'Boolean',
    (0, 2): 'Integer',
    (2, 3): 'Real',
}


def ogr_layer_to_geolayer(
    path,
    layer_id_or_name=None,
    field_name_filter=None,
    driver_name=None,
    bbox_extent=True,
    bbox_filter=None,
    serialize=False,
    feature_limit=None,
    feature_offset=None
):
    """
    'ogr_layer_to_geolayer' permet d'ouvrier un fichier sig externe (attributaire ou géométrique), de le lire et de
    stocker des informations filtrées. Il faut lui renseigner un chemin vers le fichier (obligatoirement).

    :param path: chemin d'accès au fichier + nom fichier ; Format : string ; ex : "C:\foo\bar.shp"
    :param layer_id_or_name: identifiant ou nom table concernée ; Format : string ou integer ou none
    :param field_name_filter: liste noms des champs filtrant ; Format : StringList  ou none
    :param driver_name: format du fichier en lecture, le script peu le déterminer ; Format : string (majuscule) ou none
    :param bbox_extent: if you want to add bbox for each geometry and extent in metadata
    :param bbox_filter if wout want make a bbox filter when you import data
    :return: geolayer : layer au format geoformat basé sur le fichier path renseigné en entrée filtrées par field_name_filter
    """

    if import_ogr_success:
        # create output geolayer
        geolayer = {}

        # if driver name create it and create data source
        if driver_name:
            driver = ogr.GetDriverByName(driver_name)
            data_source = driver.Open(path)
        else:
            # or create datasource without driver
            data_source = ogr.Open(path)

        # open layer (table) - condition required for database
        if not layer_id_or_name:
            layer = data_source.GetLayer()
        else:
            if isinstance(layer_id_or_name, str):
                # if layer_id_or_name is string
                layer = data_source.GetLayerByName(layer_id_or_name)
            elif isinstance(layer_id_or_name, int):
                # # if layer_id_or_name is int
                layer = data_source.GetLayer(layer_id_or_name)
            else:
                raise Exception('layer_id_or_name must be a str or int value')

        # get layer definition
        layer_defn = layer.GetLayerDefn()

        # CREATE GEOLAYER METADATA
        # nom de la layer
        metadata = {'name': layer.GetName()}

        # creation du dictionnaire des métadonnées des champs et ajout du nombre de champ dans la layer
        fields_metadata = {}
        # boucle sur la structure des champs de la layer en entree
        if field_name_filter:
            # gestion de la correspondance de la case champs/field_name_filtres
            field_name_filter_up = [field_name.upper() for field_name in field_name_filter]
            # création liste vide pour stocker après le nom de champ initiaux de la table en entrée
            field_name_ori = []
            # récupération éléments pour chaque champ compris dans la layer definition

        if field_name_filter:
            # si field_name_filter on réinitialize l'ordre d'apparition des champs à 0
            i_field_filter = 0

        for i_field in range(layer_defn.GetFieldCount()):
            field_defn = layer_defn.GetFieldDefn(i_field)
            field_name = field_defn.GetName()
            field_type = field_defn.GetType()
            field_sub_type = field_defn.GetSubType()
            if field_sub_type:
                field_type = (field_type, field_sub_type)
            field_type = ogr_field_type_to_geoformat_field_type[field_type]
            field_width = field_defn.GetWidth()
            field_precision = field_defn.GetPrecision()

            # ecriture de la metadata des champs du filtre dans les metadonnees des champs
            write_metadata = True
            # vérification si field_name_filter renseigné
            if field_name_filter:
                # si field_name est dans field_name_filter (gestion de la casse)
                if field_name.upper() not in field_name_filter_up:
                    write_metadata = False
                else:
                    field_name_ori.append(field_name)

            if write_metadata:
                # create field metadata and add field type in it
                field_metadata = {
                    'type': field_type,
                }
                # add width (if required)
                if field_type in field_metadata_width_required:
                    field_metadata['width'] = field_width
                # add precision (if required)
                if field_type in field_metadata_precision_required:
                    field_metadata['precision']= field_precision
                # add index
                if field_name_filter:
                    field_index = i_field_filter
                    i_field_filter += 1
                else:
                    field_index = i_field
                field_metadata['index'] = field_index

                # add field to fields metadata dict
                fields_metadata[field_name] = field_metadata

        # write fields metadata
        field_name_list = None
        if fields_metadata:
            metadata['fields'] = fields_metadata
            if field_name_filter:
                field_name_list = field_name_ori
            else:
                field_name_list = list(metadata['fields'].keys())

        # if geometry
        if layer.GetGeomType() != 100:
            # add geometry metadata
            geometry_type = GEOMETRY_CODE_TO_GEOMETRY_TYPE[layer.GetGeomType()]
            metadata['geometry_ref'] = {'type': geometry_type}
            if layer.GetSpatialRef():
                metadata['geometry_ref']['crs'] = layer.GetSpatialRef().ExportToWkt()
            else:
                metadata['geometry_ref']['crs'] = None

            if bbox_extent:
                metadata['geometry_ref']['extent'] = None


        if serialize:
            metadata['feature_serialize'] = True

        # ajout des metadadonnees dans geolayer
        geolayer['metadata'] = metadata

        # creation des features indépendamment les unes des autres, création structure attributaire pour chaque feature
        geolayer['features'] = {}

        #
        # i_feat : feature_id in input layer
        # i_feat_writed : feature_id in output layer
        # write_feature : True|False say if a feature can or cannot be written this depending on
        # filters option setting :
        #                           bbox_filter
        #                           feature_limit
        #                           feature_offset
        i_feat_writed = 0
        # set who list unique geometry type in layer
        geom_type_set = set([])
        for i_feat, feature in enumerate(layer):
            # init
            write_feature = True
            # test feature offset and limit
            if feature_offset:
                if i_feat < feature_offset:
                    write_feature = False

            if feature_limit:
                # stop loop if feature_limit is reached
                if i_feat_writed == feature_limit:
                    break

            # create empty feature
            new_feature = {}
            if write_feature:

                ################################################################################################################
                #
                #   geometry
                #
                ################################################################################################################

                # test if geom in feature
                geom = feature.GetGeometryRef()
                if geom:
                    # get geometry type
                    if geom.GetGeometryType() != geoformat_geom_type_to_ogr_geom_type(
                            metadata['geometry_ref']['type']) or GEOMETRY_CODE_TO_GEOMETRY_TYPE[geom.GetGeometryType()] \
                            not in geom_type_set:
                        geom_type_set = set(
                            [GEOMETRY_CODE_TO_GEOMETRY_TYPE[geom.GetGeometryType()]] + list(geom_type_set))

                    # recuperation des geometries / ajout dans le dictionnaire des features
                    temp_bbox_extent = False
                    if bbox_filter is not None:
                        temp_bbox_extent = True

                    # bbox and extent must be computed
                    if bbox_extent or temp_bbox_extent:
                        geometry = ogr_geometry_to_geometry(geom, True)
                        if bbox_extent:
                            # modify extent in metadata
                            if geolayer['metadata']['geometry_ref']['extent'] is None:
                                geolayer['metadata']['geometry_ref']['extent'] = geometry['bbox']
                            else:
                                extent_bbox = geolayer['metadata']['geometry_ref']['extent']
                                extent_bbox = bbox_union(extent_bbox, geometry['bbox'])
                                geolayer['metadata']['geometry_ref']['extent'] = extent_bbox
                    else:
                        geometry = ogr_geometry_to_geometry(geom, False)

                    # check if geometry bbox intersects bbox filter
                    if bbox_filter:
                        feat_bbox = geometry['bbox']
                        if bbox_intersects_bbox(bbox_filter, feat_bbox):
                            if bbox_extent:
                                new_feature['geometry'] = geometry
                            else:
                                del geometry['bbox']
                                new_feature['geometry'] = geometry
                        else:
                            write_feature = False
                    else:
                        new_feature['geometry'] = geometry

            ################################################################################################################
            #
            #   attributes
            #
            ################################################################################################################
            if write_feature:
                if field_name_list:
                    # ajout des données attributaires
                    new_feature['attributes'] = {}
                    # recuperation des informations attributaires pour les features
                    # si option filtre sur champ
                    for field_name in field_name_list:
                        if geolayer['metadata']['fields'][field_name]['type'] == "Binary":
                            field_value = feature.GetFieldAsBinary(field_name)
                        else:
                            field_value = feature.GetField(field_name)
                        if geolayer['metadata']['fields'][field_name]['type'] == "Boolean":
                            field_value = bool(field_value)
                        new_feature['attributes'][field_name] = field_value

                if serialize:
                    new_feature = feature_serialize(new_feature)

                geolayer['features'][i_feat_writed] = new_feature
                i_feat_writed += 1

        ## Check layer metadata

        # GEOMETRY METADATA
        # if there is a difference between layer metadata geom type and scan
        if 'geometry_ref' in metadata:
            if geom_type_set != set(metadata['geometry_ref']['type']):
                if len(geom_type_set) == 0:
                    # There is no goemetry then we delete geometry_ref metadata
                    del metadata['geometry_ref']
                elif len(geom_type_set) == 1:
                    metadata['geometry_ref']['type'] = list(geom_type_set)[0]
                else:
                    metadata['geometry_ref']['type'] = list(geom_type_set)

        return geolayer

    else:
        raise Exception(import_ogr_error)


def ogr_layers_to_geocontainer(
        path,
        field_name_filter=None,
        driver_name=None,
        bbox_extent=True,
        bbox_filter=None,
        feature_limit=None,
        serialize=False
):
    """
    'ogr_layers_to_geocontainer' crée une géodatasource comprenant des géolayers (format geoformat). Elle requiere
    la fonction layer_to_geoformat car elle boucle sur la fonction layer_to_geoformat, ce qui permet de récupérer les
    différentes géolayer et de les encapsuler dans une datasource.

    :param path: chemin d'accès au fichier + nom fichier ; Format : string ou list
    :param field_name_filter: liste noms des champs filtrant, même filtre pour tous; Format : StringList  ou none
    :param driver_name: format(s) fichier en lecture, script peu le déterminer ; Format : string (majuscule) ou liste ou none
    :param bbox_extent: if you want to add bbox for each geometry and extent in metadata
    :param bbox_filter: if you want filter input feature with a given bbox


    :return: géodatasource : un conteneur de layer au geoformat, filtrées par le fiel_name_filter
    """

    # fonction qui permet de boucler sur la 'layer_to_geoformat'
    def loop_list_layer(
        path,
        field_name_filter=None,
        driver_name=None,
        bbox_extent=None,
        bbox_filter=None,
        serialize=False
    ):
        """
        'loop_list_layer' permet de lancer en boucle la fonction ogr_layer_to_geolayer.

        :param path: chemin d'un fichier
        :param field_name_filter: liste noms des champs filtrant
        :param driver_name: format fichier en lecture
        :return: yield de géolayer
        """

        if driver_name:
            # si driver_name renseigné
            driver = ogr.GetDriverByName(driver_name)
            data_source = driver.Open(path)


        else:
            # détection interne du driver via la fonction ogr.open()
            data_source = ogr.Open(path)

        # lancement de la fonction ogr_layer_to_geolayer() et récupération des layers au fur et à mesure
        for layer_id, layer in enumerate(data_source):
            geolayer = ogr_layer_to_geolayer(path, layer_id, field_name_filter=field_name_filter,
                                             driver_name=driver_name, bbox_extent=bbox_extent, bbox_filter=bbox_filter,
                                             feature_limit=feature_limit, serialize=serialize)
            yield geolayer

    # création du conteneur de layers
    geocontainer = {'layers': {}, 'metadata': {}}

    # init parameters
    temp_layer_path, temp_field_name_filter, temp_driver_name, temp_bbox_extent, temp_bbox_filter = None, None, None, None, None

    # test si le path est une liste, si oui : boucle pour chaque élément de la liste
    if isinstance(path, str):
        path = [path]

    for i_path, temp_layer_path in enumerate(path):

        if not isinstance(temp_layer_path, str):
            sys.exit('path must be a string')

        temp_field_name_filter = None
        # test si field_name_filter renseigné
        if field_name_filter:
            if isinstance(field_name_filter[i_path], str):
                temp_field_name_filter = field_name_filter
            else:
                temp_field_name_filter = field_name_filter[i_path]
        temp_driver_name = None

        # test driver_name
        if driver_name:
            temp_driver_name = driver_name[i_path]
            if isinstance(driver_name, list):
                temp_driver_name = driver_name[i_path]
            else:
                temp_driver_name = driver_name

        # test bbox extent
        if bbox_extent:
            if isinstance(bbox_extent, list):
                temp_bbox_extent = bbox_extent[i_path]
            else:
                temp_bbox_extent = bbox_extent

        # si bbox filter
        if bbox_filter:
            if isinstance(bbox_extent, list):
                temp_bbox_filter = bbox_extent[i_path]
            else:
                temp_bbox_filter = bbox_filter

        # lancement de la fonction loop_list_layer
        for i_geolayer, geolayer in enumerate(
                loop_list_layer(temp_layer_path, temp_field_name_filter, temp_driver_name, temp_bbox_extent,
                                temp_bbox_filter, serialize)):
            # stockage des returns yield de la fonction loop
            geolayer_name = geolayer['metadata']['name']
            geocontainer['layers'][geolayer_name] = geolayer
            if temp_bbox_extent:
                geolayer_extent = geolayer['metadata']['geometry_ref']['extent']
                if i_geolayer == 0:
                    geocontainer_extent = geolayer_extent
                else:
                    geocontainer_extent = bbox_union(geocontainer_extent, geolayer_extent)
                geocontainer['metadata']['extent'] = geocontainer_extent

    return geocontainer


def geolayer_to_ogr_layer(
        geolayer,
        path,
        driver_name,
        ogr_options=None,
        order_fields=True,
):
    """
    This function allow to convert a geolayer to an other GIS format with GDAL/OGR library.

    Supported format :
        - esri shapefile
        - geojson
        - kml
        - postgresql

    WARNING : this function does not modify geolayer to be compatible with output format. You have to do that by
    yourself. However, this function verbally lists incompatibilities (wrong field type, incompatible geometry type
    combination) for the desired output format.

    :param geolayer: input geolayer that we want to convert.
    :param path: export output path (can be a file / a directory or a link to database).
    :param driver_name: output format.
    :param ogr_options: OGR/GDAL allow some options that you can use, example for postgres ogr_options=['OVERWRITE=YES']
    :param order_fields: True
    """

    if import_ogr_success:
        # création de l'ensemble des informations pour créer un fichier au format SIG
        # création d'un driver
        driver_name = driver_name.upper()
        if driver_name not in OGR_DRIVER_NAMES:
            raise ValueError("The given driver name {} is not correct.".format(driver_name))
        driver = ogr.GetDriverByName(driver_name)

        # récupération du path en 2 parties : la racine et l'extension
        (root, ext) = os.path.splitext(path)

        # test si il y a pas une extension
        if ext == '':
            # alors c'est un dossier ou l'adresse d'une base de données
            # recupération du nom de la layer
            layer_name = geolayer['metadata']['name']
            # si le chemin est bien un dossier existant
            if os.path.isdir(root):
                # récupération de l'extension suivant le driver_name
                # TODO add other drivers
                if driver_name == OGR_FORMAT_ESRI_SHAPEFILE:
                    # if geometry in geolayer
                    if 'geometry_ref' in geolayer["metadata"]:
                        new_ext = '.shp'
                    # else we write only dbf
                    else:
                        new_ext = '.dbf'
                elif driver_name == OGR_FORMAT_KML:
                    new_ext = '.kml'
                elif driver_name == OGR_FORMAT_XLSX:
                    new_ext = '.xlsx'
                elif driver_name== OGR_FORMAT_CSV:
                    new_ext = '.csv'
                elif driver_name == OGR_FORMAT_GEOJSON:
                    new_ext = '.geojson'
                else:
                    sys.exit('format non pris en compte')
                new_path = os.path.join(root, layer_name + new_ext)
            else:
                # Then we suppose that is a datasource
                if ogr.Open(root) is not None:
                    if driver_name == OGR_FORMAT_POSTGRESQL:
                        new_path = path
                    else:
                        raise ValueError("Given file is a datasource but the driver_name is not {}".format(
                            OGR_FORMAT_POSTGRESQL))
                else:
                    raise FileNotFoundError("Your path does not exists or is invalid")
            data_source = driver.CreateDataSource(new_path)
        else:
            if driver_name == OGR_FORMAT_XLSX:
                # on test s'il existe
                data_source = driver.Open(path, 1)
                if not data_source:
                    data_source = driver.CreateDataSource(path)
            else:
                # alors c'est un fichier
                data_source = driver.CreateDataSource(path)

        # récupération dans geolayer des informations nécessaires à la création d'une layer : nom, projection, geometry_type
        layer_name = geolayer['metadata']['name']

        # init
        # coordinates reference system (crs) information
        layer_crs = None
        # layer geometry type
        layer_ogr_geom_type = geoformat_geom_type_to_ogr_geom_type(geoformat_geom_type=None)

        if 'geometry_ref' in geolayer['metadata']:
            layer_crs = None
            if 'crs' in geolayer['metadata']['geometry_ref']:
                crs_data = geolayer['metadata']['geometry_ref']['crs']
                # from EPSG
                if crs_data is None:
                    layer_crs = None
                elif isinstance(crs_data, int):
                    layer_crs = osr.SpatialReference()
                    layer_crs.ImportFromEPSG(crs_data)
                # from OGC WKT
                elif isinstance(crs_data, str):
                    try:
                        layer_crs = osr.SpatialReference(crs_data)
                    except:
                        # si le format n'est pas reconnu tant pis pas de ref spatiale
                        print('WARNING: projection not recognized')
                else:
                    print('WARNING: crs value must be an ESPG code or a OGC WKT projection')

            if 'type' in geolayer['metadata']['geometry_ref']:
                layer_ogr_geom_type = verify_geom_compatibility(driver_name, geolayer['metadata']['geometry_ref']['type'])
            else:
                raise ValueError("A type shall be found in geometry_ref.")

        if 'feature_serialize' in geolayer['metadata']:
            serialize = geolayer['metadata']['feature_serialize']
        else:
            serialize = False

        # Create Layer
        if ogr_options:
            layer = data_source.CreateLayer(layer_name,
                                            srs=layer_crs,
                                            geom_type=layer_ogr_geom_type,
                                            options=ogr_options)
        else:
            layer = data_source.CreateLayer(layer_name,
                                            srs=layer_crs,
                                            geom_type=layer_ogr_geom_type)


        # création des fields (structure du fichier)
        # si l'on souhaite que l'ordre d'apparition des champs soit conservée
        if 'fields' in geolayer['metadata']:
            if order_fields:
                field_name_list = [None] * len(geolayer['metadata']['fields'])
                for i_field, field_name in enumerate(geolayer['metadata']['fields']):
                    field_name_list[geolayer['metadata']['fields'][field_name].get('index', i_field)] = field_name
            else:
                field_name_list = list(geolayer['metadata']['fields'].keys())

            # check if field type is compatible with output format
            field_type_error = []
            for field_name in field_name_list:
                # récupération des informations nécessaire à la création des champs
                geoformat_field_type = geolayer['metadata']['fields'][field_name]['type']
                driver_name_field_type_combination = (driver_name, geoformat_field_type)
                if driver_name_field_type_combination in field_driver_uncompatibility:
                    field_type_error.append(field_driver_uncompatibility[driver_name_field_type_combination].format(
                        field_name=field_name,
                        ogr_format=driver_name)
                    )

            if field_type_error:
                error_message = '\n'
                for error in field_type_error:
                    error_message += '\t' + error +'\n'
                raise Exception(error_message)

            ogr_layer_field_type = {}
            for field_name in field_name_list:
                # get necessary data to create field
                geoformat_field_type = geolayer['metadata']['fields'][field_name]['type']
                field_type = geoformat_field_type_to_ogr_field_type[geoformat_field_type]
                ogr_layer_field_type[field_name] = field_type
                if isinstance(field_type, tuple):
                    (field_type, field_sub_type) = field_type
                else:
                    field_sub_type = 0
                field_width = geolayer['metadata']['fields'][field_name].get('width', 0)
                field_precision = geolayer['metadata']['fields'][field_name].get('precision', 0)

                # création de la définition du champ (type, longueur, precision
                field = ogr.FieldDefn(field_name, field_type)
                field.SetSubType(field_sub_type)
                # ogr does not allow precision at 0 for real and realList
                if field_type in {2, 3} and field_precision == 0:
                    field_width += 1
                    field_precision += 1

                field.SetWidth(field_width)
                field.SetPrecision(field_precision)

                # création du champ
                layer.CreateField(field)

            # creation table de correspondance [au cas où la taille des champs est réduite lors de la création de la layer]
            # example DBF = 10 char maximum
            # if layerDefn() is define
            try:
                ct_field_name = {}
                for i in range(layer.GetLayerDefn().GetFieldCount()):
                    ct_field_name[field_name_list[i]] = layer.GetLayerDefn().GetFieldDefn(i).GetName()
            except:
                ct_field_name = {field_name: field_name for field_name in field_name_list}

        # création des features
        for i_feat in geolayer['features']:
            try:
                feature_ogr = ogr.Feature(layer.GetLayerDefn())
            except:
                feature_ogr = ogr.Feature()

            feature_geoformat = geolayer['features'][i_feat]

            if serialize:
                feature_geoformat = feature_deserialize(feature_geoformat)

            # if geometry in feature
            if 'geometry' in feature_geoformat:
                # get geometry
                geometry = feature_geoformat['geometry']
                # transform geometry to ogr geometry
                geom_ogr = geometry_to_ogr_geometry(geometry)
                # add geometry in ogr feature object
                feature_ogr.SetGeometry(geom_ogr)

            # test if attributes data in feature
            if 'attributes' in feature_geoformat:
                # loop on each layer [metadata] fields
                for field_name in geolayer['metadata']['fields']:
                    # we recuperate true field name [in case it has been truncated]
                    true_field_name = ct_field_name[field_name]
                    value_field = feature_geoformat['attributes'].get(field_name)
                    # if field value exists and is not NULL
                    if value_field is not None:
                        # convert binary field to hex and write it with SetFieldBinaryFromHexString
                        if ogr_layer_field_type[field_name] == 8:
                            value_field = value_field.hex()
                            feature_ogr.SetFieldBinaryFromHexString(true_field_name, value_field)
                        else:
                            # write data if error change field_value to string
                            try:
                                feature_ogr.SetField(true_field_name, value_field)
                            except (NotImplementedError, TypeError):
                                feature_ogr.SetField(true_field_name, str(value_field))

            layer.CreateFeature(feature_ogr)

        data_source.Destroy()
    else:
        raise Exception(import_ogr_error)


def geocontainer_to_ogr_data_source(
        geocontainer,
        path,
        driver_name,
        export_layer_list=None,
        ogr_options=None,
        order_fields=False
    ):
    """
    'geocontainer_to_ogr_data_source' est une procedure qui permet d'exporter une sélection ou l'ensemble des layers d'une
    datasource aux formats voulus. Le path renseignée peut être un dossier, une datasource, ou un fichier. On peut
    renseigner une liste ou un nom de layer pour filtrer l'export.

    :param geocontainer: la géodatasource complete
    :param path: chemin où aller sauvegarder (il peut être une liste ou un str)
    :param driver_name: le nom du drive peut etre une liste ou un seul qu'on applique à tous
    :param export_layer_list: liste des layers de la datasource a exporter, peut être list ou str. Si export_layer_list
    non rempli alors on exporte toutes les layers, si export layer_list rempli = on exporte que ces layers là.
    Variable possible pour cette list : 'tc', 'ref_a', 'ref_b' (seulement)
    """

    if import_ogr_success:
        if export_layer_list:
            # test si il y a une liste des layers à exporter
            if isinstance(export_layer_list, list):
                for i_layer, export_layer_name in enumerate(export_layer_list):
                    # test si la layer fait partie de la liste des layers à sauvegarder
                    if export_layer_name in geocontainer['layers'].keys():
                        geolayer = geocontainer['layers'][export_layer_name]
                        if isinstance(path, list):
                            # path = fichier en dur
                            if isinstance(driver_name, list):
                                geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name[i_layer],
                                                      ogr_options=ogr_options[i_layer], order_fields=order_fields)
                            else:
                                geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name, ogr_options=ogr_options,
                                                      order_fields=order_fields)
                        else:
                            # path = dossier ou database
                            if isinstance(driver_name, list):
                                geolayer_to_ogr_layer(geolayer, path, driver_name[i_layer],
                                                      ogr_options=ogr_options[i_layer], order_fields=order_fields)
                            else:
                                geolayer_to_ogr_layer(geolayer, path, driver_name, ogr_options=ogr_options,
                                                      order_fields=order_fields)

            # si export_layer_list n'est pas une liste, elle contient qu'une valeur
            elif isinstance(export_layer_list, str):
                geolayer = geocontainer['layers'][export_layer_list]
                geolayer_to_ogr_layer(geolayer, path, driver_name, ogr_options=ogr_options, order_fields=order_fields)


        # si export_layer_list=None alors on exporte l'ensemble des layers de la geocontainer
        else:
            for i_layer, layer_name in enumerate(geocontainer['layers']):
                geolayer = geocontainer['layers'][layer_name]
                # si le path est une liste :
                if isinstance(path, list):
                    # et si le driver_name est une liste
                    if isinstance(driver_name, list):
                        geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name[i_layer],
                                              ogr_options=ogr_options[i_layer], order_fields=order_fields)
                    # si non utiliser toujours le même driver
                    else:
                        geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name, ogr_options=ogr_options,
                                              order_fields=order_fields)
                # sinon utiliser le même dossier
                else:
                    # test sur le driver_name pour voir lequel on donne
                    if isinstance(driver_name, list):
                        geolayer_to_ogr_layer(geolayer, path, driver_name[i_layer], ogr_options=ogr_options[i_layer],
                                              order_fields=order_fields)
                    else:
                        geolayer_to_ogr_layer(
                            geolayer,
                            path,
                            driver_name,
                            ogr_options=ogr_options,
                            order_fields=order_fields
                        )
    else:
        raise Exception(import_ogr_error)


def geoformat_geom_type_to_ogr_geom_type(geoformat_geom_type):
    """
    Make transformation between Geoformat geometry type to OGR geometry type

    :param geoformat_geom_type: (str) Geoformat geometry type
    :return: (int) ogr geom type correspondance
    """
    if geoformat_geom_type is None:
        return GEOMETRY_TYPE["None"]
    if geoformat_geom_type.upper() == 'GEOMETRY':  # Geometry
        return GEOMETRY_TYPE['Unknown']
    if geoformat_geom_type.upper() == 'POINT25D':  # Point25D
        return GEOMETRY_TYPE["Point25D"]
    if geoformat_geom_type.upper() == 'LINESTRING25D':  # LineString25D
        return GEOMETRY_TYPE["LineString25D"]
    if geoformat_geom_type.upper() == 'POLYGON25D':  # Polygon25D
        return GEOMETRY_TYPE["Polygon25D"]
    if geoformat_geom_type.upper() == 'MULTIPOINT25D':  # MultiPoint25D
        return GEOMETRY_TYPE["MultiPoint25D"]
    if geoformat_geom_type.upper() == 'MULTILINESTRING25D':  # MultiLineString25D
        return GEOMETRY_TYPE["MultiLineString25D"]
    if geoformat_geom_type.upper() == 'MULTIPOLYGON25D':  # MultiPolygon25D
        return GEOMETRY_TYPE["MultiPolygon25D"]
    if geoformat_geom_type.upper() == 'POINT':  # Point
        return GEOMETRY_TYPE["Point"]
    if geoformat_geom_type.upper() == 'LINESTRING':  # LineString
        return GEOMETRY_TYPE["LineString"]
    if geoformat_geom_type.upper() == 'POLYGON':  # Polygon
        return GEOMETRY_TYPE["Polygon"]
    if geoformat_geom_type.upper() == 'MULTIPOINT':  # MultiPoint
        return GEOMETRY_TYPE["MultiPoint"]
    if geoformat_geom_type.upper() == 'MULTILINESTRING':  # MultiLineString
        return GEOMETRY_TYPE["MultiLineString"]
    if geoformat_geom_type.upper() == 'MULTIPOLYGON':  # MultiPolygon
        return GEOMETRY_TYPE["MultiPolygon"]
    if geoformat_geom_type.upper() == 'GEOMETRYCOLLECTION':  # GeometryCollection
        return GEOMETRY_TYPE["GeometryCollection"]
    if geoformat_geom_type.upper() == 'NO GEOMETRY':  # No Geometry
        return GEOMETRY_TYPE["None"]


def verify_geom_compatibility(driver_name, metadata_geometry_type):
    """

    OGR Geometry Type List :
        -2147483647: 'Point25D'
        -2147483646: 'LineString25D'
        -2147483645: 'Polygon25D'
        -2147483644: 'MultiPoint25D'
        -2147483643: 'MultiLineString25D'
        -2147483642: 'MultiPolygon25D'
                  0: 'Geometry'
                  1: 'Point'
                  2: 'LineString'
                  3: 'Polygon'
                  4: 'MultiPoint'
                  5: 'MultiLineString'
                  6: 'MultiPolygon'
                  7: 'GeometryCollection'
                100: 'No Geometry'

    [[0],[1], [2, 5], [3, 6], [4], [100]],  # 'Esri Shapefile'
    [[1, 4], [2, 5], [3, 6], [100]],  # TAB 'Mapinfo File'
    [[1, 4], [2, 5], [3, 6], [100]],  # MIF/MID 'Mapinfo File'
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # KML
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # GML
    [[0, 1, 2, 3, 4, 5, 6, 7, 100]],  # GeoJSON
    [[1], [2], [3, 6], [4], [5], [100]],  # Geoconcept
    [[1], [2, 5], [3, 6], [4], [100]],  # FileGDB
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # SQLite
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # POSTGRESQL
    [[1, 2, 3, 4, 5, 6, 7, 100]]   # CSV
    ],

    """

    if isinstance(metadata_geometry_type, str):
        metadata_geometry_type = [metadata_geometry_type.upper()]
    elif isinstance(metadata_geometry_type, (tuple, list, set)):
        metadata_geometry_type = [value.upper() for value in metadata_geometry_type]

    set_geometry_type = set(metadata_geometry_type)

    if driver_name.upper() == OGR_FORMAT_ESRI_SHAPEFILE:
        # POLYGON
        set_polygon = {'NO GEOMETRY', 'POLYGON', 'MULTIPOLYGON'}
        if len(set_geometry_type) <= 3 and len(set_geometry_type.difference(set_polygon)) == 0:
            return 3
        # LINESTRING
        set_linestring = {'NO GEOMETRY', 'LINESTRING', 'MULTILINESTRING'}
        if len(set_geometry_type) <= 3 and len(set_geometry_type.difference(set_linestring)) == 0:
            return 2
        # POINT
        set_point = {'NO GEOMETRY', 'POINT', 'MULTIPOINT'}
        if len(set_geometry_type) <= 3 and len(set_geometry_type.difference(set_point)) == 0:
            return 1

    if driver_name.upper() == OGR_FORMAT_POSTGRESQL:
        if len(set_geometry_type) > 1:
            return 0
        else:
            return geoformat_geom_type_to_ogr_geom_type(metadata_geometry_type[0])

    if driver_name.upper() == OGR_FORMAT_GEOJSON:
        return 0

    if driver_name.upper() == OGR_FORMAT_CSV:
        return 100
