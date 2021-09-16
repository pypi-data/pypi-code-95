import textwrap
from typing import Dict
from typing import List
from typing import Optional

from tecton.interactive.feature_set_config import FeatureDefinitionAndJoinConfig
from tecton.interactive.feature_set_config import FeatureSetConfig
from tecton_spark.snowflake_pipeline_helper import pipeline_to_sql_string

TEMPORARY_SPINE_TABLE = "_tt_spine_table"

# TODO: We need to figure out a better way to format our SQL string
# The SQL string indents in this file are made intentionally to make the output more readable
def get_features_sql_str_for_spine(
    feature_set_config: FeatureSetConfig,
    timestamp_key: str,
    spine_sql: Optional[str] = None,
    spine_table_name: Optional[str] = None,
    include_feature_package_timestamp_columns: bool = False,
) -> str:
    """
    Get a SQL string to fetch features given the spine and feature set.
    spine_sql and spine_table_name cannot be both empty.

    :param feature_set_config: FeatureSetConfig instance.
    :param timestamp_key: Name of the time column in the spine.
    :param spine_sql: SQL str to get the spine.
    :param spine_table_name: Spine table name to get the spine.
    :param include_feature_package_timestamp_columns: (Optional) Include timestamp columns for every individual FeaturePackage.
    :return: A SQL string that can be used to fetch features.
    """
    if spine_table_name is None and spine_sql is None:
        raise ValueError("spine_sql and spine_table_name cannot both be empty")

    # Validate the data source type
    for package_and_config in feature_set_config._get_feature_definitions_and_join_configs():
        definition = package_and_config.definition
        if definition.wildcard_join_key is not None:
            raise ValueError("SQL string does not support wildcard")

    package_to_table = dict()
    sql_str = f"""
            WITH"""
    # Create a temp table for the spine if needed
    if spine_table_name is None:
        spine_table_name = TEMPORARY_SPINE_TABLE
        sql_str += f"""
                {spine_table_name} AS ({spine_sql}),
                """

    # Create a temp table for each feature
    for package_and_config in feature_set_config._get_feature_definitions_and_join_configs():
        definition = package_and_config.definition
        name = definition.name
        # Make sure it's a Feature View with pipeline
        assert definition.pipeline
        package_to_table[name] = _generate_temp_table_name(package_and_config)
        feature_sql_str = pipeline_to_sql_string(
            pipeline=definition.pipeline,
            virtual_data_sources=definition.virtual_data_sources,
            transformations=definition.new_transformations,
        )
        sql_str += f"""
                {package_to_table[name]} AS ({feature_sql_str}),
                """
    sql_str = textwrap.dedent(sql_str)
    left_table = spine_table_name
    package_and_config_list = feature_set_config._get_feature_definitions_and_join_configs()
    # Join the spine with all the temp tables
    for package_and_config in package_and_config_list:
        name = package_and_config.definition.name
        package_to_table[name] = _generate_temp_table_name(package_and_config)
        new_table = f"_join_{package_to_table[name]}"
        sql_str += _join_tables(
            spine=left_table,
            spine_timestamp_key=timestamp_key,
            feature=package_to_table[name],
            feature_timestamp_key=package_and_config.definition.timestamp_key,
            feature_columns=package_and_config.definition.view_schema.column_names(),
            join_keys=dict(package_and_config.join_keys),
            table_name=new_table,
            include_end_comma=(package_and_config != package_and_config_list[-1]),
            include_feature_package_timestamp_columns=include_feature_package_timestamp_columns,
        )
        left_table = new_table
    # Remove the last "," in the sql string
    sql_str = sql_str[:-1]
    # Finally select all from the final join table
    sql_str += textwrap.dedent(f"\nSELECT * FROM {left_table}")

    return textwrap.dedent(sql_str)


def _join_tables(
    spine: str,
    spine_timestamp_key: str,
    feature: str,
    feature_timestamp_key: str,
    feature_columns: List[str],
    join_keys: Dict[str, str],
    table_name: str,
    include_end_comma: bool = True,
    include_feature_package_timestamp_columns: bool = False,
) -> str:
    """
    Get a SQL string that joins two tables, with the given join keys
    This assumes there are no columns with the same name in the two tables besides the join keys and timestamp keys

    This function will first rename the join_keys/timestamp_key in the feature table to match the spine if needed,
    then using a window function to join with the spine to get the latest value that is no later than the spine's timestamp for each column.

    :param spine: the name of the spine table to join
    :param spine_timestamp_key: the name of the timestamp column in the spine table
    :param feature: the name of the feature table to join
    :param feature_timestamp_key: the name of the timestamp column in the feature table
    :param feature_columns: the names of the column in the feature table
    :param join_keys: Column names to join, key is the column name on the left and value is the column name on the right
    :param table_name: The name of the new joined table
    :param include_end_comma: (Optional) Include timestamp columns for every individual FeaturePackage.
    :param include_feature_package_timestamp_columns: (Optional) Include timestamp columns for every individual FeaturePackage.
    :return: A SQL string that generates the joined table
    """
    sql_str = f"""
        WITH"""
    if spine_timestamp_key == feature_timestamp_key and include_feature_package_timestamp_columns:
        raise ValueError(
            "Feature timestamp key need to have a different name than the spine's timestamp key when include_feature_package_timestamp_columns is true"
        )
    join_keys_with_timestamp = join_keys.copy()
    join_keys_with_timestamp[spine_timestamp_key] = feature_timestamp_key
    rename_needed = sum([1 for (k, v) in join_keys_with_timestamp.items() if k != v]) > 0

    # Rename feature columns if it's different than the spine keys
    if rename_needed:
        # Select all column beside the join keys and timestamp keys
        new_feature_columns = [column for column in feature_columns if column not in join_keys_with_timestamp.values()]
        # Rename columns
        for (k, v) in join_keys_with_timestamp.items():
            new_feature_columns.append(f"{v} as {k}")
        if include_feature_package_timestamp_columns:
            new_feature_columns.append(feature_timestamp_key)

        new_feature_select_condition = ", ".join(new_feature_columns)
        renamed_table_name = f"renamed_{feature}"
        sql_str += f"""
            {renamed_table_name} AS (
                SELECT {new_feature_select_condition}
                FROM
                {feature}
            ),
            """
        # Update the feature table name
        feature = renamed_table_name

    outter_join_keys_list = ", ".join(join_keys_with_timestamp.keys())
    join_keys_list = ", ".join(join_keys.keys())

    last_values = []
    for column in feature_columns:
        # We only need to select none join key columns
        if column not in join_keys_with_timestamp.values():
            last_values.append(
                f"""
                LAST_VALUE({column}) IGNORE NULLS OVER (PARTITION BY {join_keys_list} ORDER BY {spine_timestamp_key} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as {column}"""
            )
    last_values_select_condition = ",".join(last_values)

    # This window function will take the most recent value that is no later than the spine timestamp for every column
    sql_str += f"""
            OUTTER_JOINED AS (
                SELECT *
                FROM {feature}
                FULL JOIN {spine} USING({outter_join_keys_list})
            ),
            WINDOWED AS (
                SELECT {outter_join_keys_list},{last_values_select_condition}
                FROM OUTTER_JOINED
            )
        SELECT *
        FROM WINDOWED
        INNER JOIN {spine} USING({outter_join_keys_list})"""

    comma = "," if include_end_comma else ""
    return f"""
    {table_name} AS ({sql_str}){comma}
    """


def _generate_temp_table_name(package_and_config: Optional[FeatureDefinitionAndJoinConfig]) -> str:
    if package_and_config is not None:
        return package_and_config.definition.name + "_table"
