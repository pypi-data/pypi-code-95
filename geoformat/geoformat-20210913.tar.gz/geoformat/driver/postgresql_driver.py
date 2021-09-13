from geoformat.conf.fields_variable import geoformat_field_type_to_postgresql_type
from geoformat.conversion.feature_conversion import feature_deserialize
from geoformat.conversion.geometry_conversion import geometry_to_wkb, geometry_to_wkt

try:
    import psycopg2
    import psycopg2.extras
    import_psycopg2_success = True
except ImportError:
    import_psycopg2_success = False

from geoformat.conf.error_messages import import_psycopg2_error


def fields_metadata_to_create_table_fields_structure(
        geolayer_fields_metadata,
        consider_width_and_precision
):
    """
    This function convert geolayer's fields metadata to

    :param geolayer_fields_metadata: geolayer's fields metadata.
    :param consider_width_and_precision: True if you want consider field with and precision / False if you won't.
    :return:
    """
    field_structure_list = [None] * len(geolayer_fields_metadata)

    for i_field, (field_name, field_metadata) in enumerate(geolayer_fields_metadata.items()):
        field_type = field_metadata['type']
        field_type_pg = geoformat_field_type_to_postgresql_type[field_type]
        if consider_width_and_precision:
            if field_type in {'Real', 'String'}:
                width = field_metadata['width']
                if field_type == 'Real':
                    precision = field_metadata['precision']
                    suffix = '({width}, {precision})'.format(width=width, precision=precision)
                else:
                    suffix = '({width})'.format(width=width)
                field_type_pg = field_type_pg + suffix

        field_structure = '{field_name} {field_type_pg}'.format(field_name=field_name, field_type_pg=field_type_pg)
        field_index = field_metadata.get('index', i_field)
        field_structure_list[field_index] = field_structure

    table_fields_structure = ', '.join(field_structure_list)

    return table_fields_structure


def geometry_ref_to_geometry_field_structure(
        geometry_ref,
        geometry_field_name,
        constraint_geometry_type,
):
    srid = geometry_ref.get('crs', None)
    geometry_type = geometry_ref.get('type', None)
    geometry_field = '{geometry_field_name} geometry'.format(geometry_field_name=geometry_field_name)
    add_geometry_metadata = []

    # get geometry type
    if geometry_type:
        if constraint_geometry_type is True and len(geometry_type) == 1:
            geometry_type = list(geometry_type)[0]
            add_geometry_metadata.append("'{geometry_type}'".format(geometry_type=geometry_type))
        else:
            add_geometry_metadata.append("'Geometry'")
    # get srid
    if srid:
        add_geometry_metadata.append('{srid}'.format(srid=srid))

    # add geometry metadata
    if add_geometry_metadata:
        if len(add_geometry_metadata) > 1:
            add_geometry_metadata = ', '.join(add_geometry_metadata)
        else:
            add_geometry_metadata = add_geometry_metadata[0]

        geometry_field = '{geometry_field}({add_geometry_metadata})'.format(
            geometry_field=geometry_field,
            add_geometry_metadata=add_geometry_metadata
        )

    return geometry_field


def format_to_posgresq_values(geolayer):

    fields_metadata = geolayer['metadata'].get('fields', [])
    nb_features = len(geolayer['features'])
    nb_fields = len(fields_metadata)

    # add geometry field if necessary
    if 'geometry_ref' in geolayer['metadata']:
        nb_fields += 1
        srid = geolayer['metadata']['geometry_ref'].get('crs', None)

    field_structure_list = [None] * nb_fields
    # if there is field
    if fields_metadata:
        for i_field, (field_name, field_metadata) in enumerate(fields_metadata.items()):
            field_index = field_metadata.get('index', i_field)
            field_structure_list[field_index] = field_name

    # if features are serialized
    serialize = geolayer['metadata'].get('feature_serialize', False)

    values = [None] * nb_features
    for ii, (i_feat, feature) in enumerate(geolayer['features'].items()):
        feature_values_format = [None] * nb_fields
        # if features are serialized in geolayer we deserialize it
        if serialize is True:
            feature = feature_deserialize(feature, bbox=False)

        # add attributes data if exists
        feature_attributes = feature.get('attributes', None)
        if feature_attributes:
            # write field value if exists
            for i_field, field_name in enumerate(field_structure_list):
                if field_name in feature_attributes:
                    feature_values_format[i_field] = feature_attributes[field_name]

        # add geometry if exists
        if 'geometry' in feature:
            feature_geometry = feature['geometry']
            if srid:
                feature_geometry_wkt = geometry_to_wkt(feature_geometry)
                feature_geometry_for_pg = 'SRID={srid};{feature_geometry_wkt}'.format(
                    feature_geometry_wkt=feature_geometry_wkt,
                    srid=srid
                )
            else:
                feature_geometry_for_pg = geometry_to_wkb(feature_geometry)

            # add geometry to feature_values_format
            feature_values_format[-1] = feature_geometry_for_pg

        values[ii] = feature_values_format

    return values


def _method_execute_batch(cursor, schema, table_name, values):
    """
    Batch method to write data in postgresql table

    inspired by : https://www.datacareer.de/blog/improve-your-psycopg2-executions-for-postgresql-in-python/

    :param cursor: cursor
    :param schema:
    :param table_name:
    :param values:
    :return:
    """
    nb_fields = len(values[0])
    field_struct = ', '.join(['%s'] * nb_fields)
    insert_into_request = "INSERT INTO {schema}.{table} VALUES ({field_struct})".format(
        schema=schema,
        table=table_name,
        field_struct=field_struct
    )
    psycopg2.extras.execute_batch(
        cursor,
        insert_into_request,
        values
    )


def geolayer_to_postgres(
    geolayer,
    host,
    database_name,
    user,
    password,
    port=5432,
    schema='public',
    geometry_column_name='geom',
    overwrite=True,
    constraint_geometry_type=False,
    consider_width_and_precision=True
):
    """
    Convert geolayer to table in postgresql database.

    :param geolayer: input geolayer that we want create in postgresql
    :param host: host of postgresql server
    :param database_name: name of database
    :param user: name of user
    :param password: password for user
    :param port: port of database (default 5432).
    :param schema: name of the schema in which we want to insert the data (default public).
    :param geometry_column_name: name of geometry column (default geom).
    :param overwrite: True if table exists we drop it / False if table exists process fail (default True).
    :param constraint_geometry_type: geometry field in postgis can be forced to a single geometry type. True if want to
    add this constraint (it is only possible if geolayer contain only one geometry's type) / False if you wan't it
    (by default).
    :param consider_width_and_precision: add precision and width when create field (default True).
    """
    if import_psycopg2_success is True:
        # connect to database
        conn_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(
            host=host,
            user=user,
            password=password,
            dbname=database_name,
            port=port)
        database_connection = psycopg2.connect(conn_string)
        cursor = database_connection.cursor()

        # get table name
        table_name = geolayer['metadata']['name']

        # create schema if not exists
        create_schema_request = """
        CREATE SCHEMA IF NOT EXISTS {schema};
        """.format(schema=schema)
        cursor.execute(create_schema_request)

        # if overwrite
        if overwrite:
            overwrite_request = """
            DROP TABLE IF EXISTS {schema}.{table_name};
            """.format(schema=schema, table_name=table_name)
            cursor.execute(overwrite_request)
            database_connection.commit()

        # get attributes field table structure
        geolayer_fields_metadata = geolayer['metadata'].get('fields', None)
        table_fields_structure = ''
        if geolayer_fields_metadata:
            table_fields_structure = fields_metadata_to_create_table_fields_structure(
                geolayer_fields_metadata=geolayer_fields_metadata,
                consider_width_and_precision=consider_width_and_precision
            )

        # add geometry field
        geolayer_geometry_metadata = geolayer['metadata'].get('geometry_ref', None)
        if geolayer_geometry_metadata:
            if table_fields_structure:
                table_fields_structure += ', '

            table_fields_structure += geometry_ref_to_geometry_field_structure(
                geolayer_geometry_metadata,
                geometry_column_name,
                constraint_geometry_type,
            )

        # create table
        create_table_request = """
        CREATE TABLE {schema}.{table_name} ({table_fields_structure});
        """.format(schema=schema, table_name=table_name, table_fields_structure=table_fields_structure)
        cursor.execute(create_table_request)
        database_connection.commit()

        # insert into with batch execute
        # format data
        values = format_to_posgresq_values(geolayer)

        # insert into db
        _method_execute_batch(
            cursor=cursor,
            schema=schema,
            table_name=table_name,
            values=values
        )

        # end of transaction
        database_connection.commit()
    else:
        raise Exception(import_psycopg2_error)