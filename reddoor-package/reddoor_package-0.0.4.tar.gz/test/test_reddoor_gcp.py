from reddoor_gcp import *

def test_upload():
        gc_ser = GoogleCloudService('json/KeywordTag-3c600346e709.json')
        sql_config = {
                "host": "35.200.15.129",
                "connect_timeout": 60,
                "read_timeout": 60,
                "write_timeout": 60,
                "max_allowed_packet": 102400,
                "user": "cdpdev",
                "password": "cdp!@#",
                "db": "cdpplatformdb",
                "charset": "utf8mb4"
        }
        sql = 'SELECT * FROM cdpplatformdb.product WHERE owner = "cdppj"'
        bucket_name = 'cdpplatform_temp'
        bucket_file = arrow.now().format('YYYYMMDDHHmmss') + '.csv'
        table_id = os.path.splitext(bucket_file)[0]

        status, result = gc_ser.mysql_to_gcs(sql, sql_config, bucket_name, bucket_file)
        if status == 'ok':
                gc_ser.gcs_to_bq(
                bucket = bucket_name, 
                source_objects = bucket_file, 
                destination_project_dataset_table = f'all_temp.{table_id}', 
                schema_fields = result['schema'], 
                skip_leading_rows = 1
                )