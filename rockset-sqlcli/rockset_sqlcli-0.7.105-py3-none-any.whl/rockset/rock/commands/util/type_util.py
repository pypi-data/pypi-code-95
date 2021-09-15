class IntegrationType:
    DYNAMODB = "Amazon DynamoDB"
    MONGODB = "MongoDB"
    GCS = "Google Cloud Storage"
    KINESIS = "Amazon Kinesis"
    REDSHIFT = "Amazon Redshift"
    S3 = "Amazon S3"
    KAFKA = "Apache Kafka"
    UNKNOWN = "UNKNOWN"

    ACCESS_KEY = "AWS Access Key"  # deprecated
    EXTERNAL_ID = "AWS External ID"  # deprecated
    GCP_SERVICE_ACCOUNT = "GCP Service Account"  # deprecated

    @staticmethod
    def parse(string):
        return {
            'dynamodb': IntegrationType.DYNAMODB,
            'mongodb': IntegrationType.MONGODB,
            'gcs': IntegrationType.GCS,
            'kinesis': IntegrationType.KINESIS,
            'redshift': IntegrationType.REDSHIFT,
            's3': IntegrationType.S3,
            'kafka': IntegrationType.KAFKA,
        }.get(string.lower(), IntegrationType.UNKNOWN)

    @staticmethod
    def parse_from_integration(integration):
        if integration.get('dynamodb'):
            return IntegrationType.DYNAMODB
        if integration.get('gcs'):
            return IntegrationType.GCS
        if integration.get('kinesis'):
            return IntegrationType.KINESIS
        if integration.get('redshift'):
            return IntegrationType.REDSHIFT
        if integration.get('s3'):
            return IntegrationType.S3
        if integration.get('kafka'):
            return IntegrationType.KAFKA
        return IntegrationType.UNKNOWN


class TypeUtil:
    TYPE_COLLECTION = "COLLECTION"
    TYPE_INTEGRATION = "INTEGRATION"
    TYPE_WORKSPACE = "WORKSPACE"
    """
    returns resource type from upstream resource
    """
    @staticmethod
    def parse_resource_type(type):
        if type in ['c', 'col', 'collection', 'collections']:
            return TypeUtil.TYPE_COLLECTION
        elif type in ['i', 'int', 'integration', 'integrations']:
            return TypeUtil.TYPE_INTEGRATION
        elif type in ['w', 'ws', 'workspace', 'workspaces']:
            return TypeUtil.TYPE_WORKSPACE
        else:
            return None
