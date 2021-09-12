from cnvrg.modules.data_connector.base_connector import BaseConnector as _BaseConnector
from cnvrg.modules.data_connector.files_connector import DatasetConnector, S3BucketConnector
from cnvrg.modules.data_connector.sql_connector import MysqlConnector, SnowflakeConnector, HiveConnector
from cnvrg.modules.data_connector.stream_connector import KafkaConnector



def DataConnector(data_connector, **kwargs):
    connector = _BaseConnector(data_connector)
    if connector.connector_type() == HiveConnector.key_type():
        return HiveConnector(data_connector)

    if connector.connector_type() == MysqlConnector.key_type():
        return MysqlConnector(data_connector)

    if connector.connector_type() == SnowflakeConnector.key_type():
        return SnowflakeConnector(data_connector)

    if connector.connector_type() == DatasetConnector.key_type():
        return DatasetConnector(data_connector, **kwargs)

    if connector.connector_type() == S3BucketConnector.key_type():
        return S3BucketConnector(data_connector)

    if connector.connector_type() == KafkaConnector.key_type():
        return KafkaConnector(data_connector)
