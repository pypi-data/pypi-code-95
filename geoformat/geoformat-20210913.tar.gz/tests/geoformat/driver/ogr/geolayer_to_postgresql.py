from tests.data.geolayers import geolayer_attributes_only
from geoformat.driver.ogr.ogr_driver import geolayer_to_ogr_layer, ogr_layer_to_geolayer
from tests.geoformat.driver.ogr_driver.compare_ogr_files import compare_geolayer


def test_postgresql_attributes(attributes_geolayer):
    host = 'localhost'
    database = 'test'
    user = 'postgres'
    password = 'postgres'
    port = 5432

    pg = "PG: host={host} dbname={db_name} user={user} password={password} port={port}"
    pg_connect = pg.format(host=host, db_name=database, user=user, password=password, port=port)

    path_geolayer_attirbutes_only = pg_connect

    # write file
    geolayer_to_ogr_layer(
        geolayer=attributes_geolayer,
        path=path_geolayer_attirbutes_only,
        driver_name='postgresql',
        ogr_options=['OVERWRITE=YES']
    )

    # open created just bellow geojson to geolayer (to compare to geolayer_attributes_only)
    ogr_geolayer_attributes = ogr_layer_to_geolayer(
        path=path_geolayer_attirbutes_only,
        layer_id_or_name=attributes_geolayer['metadata']['name']
    )

    # compare both geolayer
    compare_geolayer(attributes_geolayer, ogr_geolayer_attributes)


if __name__ == '__main__':
    test_postgresql_attributes(attributes_geolayer=geolayer_attributes_only)

