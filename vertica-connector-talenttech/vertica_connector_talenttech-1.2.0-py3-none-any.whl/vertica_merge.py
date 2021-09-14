import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.captureWarnings(True)


def merge(
    table_name,
    staging_table_name,
    vertica_cnx,
    fields,
    key_fields=["id"],
    filter_merge_fields=None,
    debug=False

):
    """
    :param debug:
    :param table_name:  main_table to update
    :param staging_table_name: temp table for using to update
    :param vertica_cnx: vertica connection for using
    :param filter_merge_fields:
    :param fields: fields needed to update
    :param key_fields: fields to join with temp table
    :return: Nothing
    """

    sql = """MERGE INTO {table_name} src
             USING {staging_table_name} tgt
                ON {join_key_fields}
             WHEN MATCHED {filter_merge_condition} THEN
             UPDATE SET {update_fields}
             WHEN NOT MATCHED THEN
             INSERT ({columns})  VALUES ({insert_fields})"""

    join_key_fields = " AND ".join(
        ['tgt."{field}"=src.{field}'.format(field=key) for key in key_fields]
    )

    update_fields = ",".join(
        ['"{field}"=tgt."{field}"'.format(field=field) for field in fields]
    )
    if filter_merge_fields is not None:
        filter_merge_condition = " AND " + " AND ".join(
            [
                'tgt."{field}" <> src."{field}".format(field=field)'.format(field=field)
                for field in filter_merge_fields
            ]
        )
    else:
        filter_merge_condition = ""

    insert_fields = ",".join(['tgt."{}"'.format(field) for field in fields])
    columns = ",".join(['"{}"'.format(field) for field in fields])

    sql = sql.format(
        table_name=table_name,
        staging_table_name=staging_table_name,
        join_key_fields=join_key_fields,
        filter_merge_condition=filter_merge_condition,
        update_fields=update_fields,
        insert_fields=insert_fields,
        columns=columns
    )
    cursor = vertica_cnx.cursor()
    if debug:
        logging.info(sql)
    cursor.execute(sql)
