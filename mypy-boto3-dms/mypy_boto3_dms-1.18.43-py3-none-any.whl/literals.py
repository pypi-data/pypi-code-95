"""
Type annotations for dms service literal definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_dms/literals.html)

Usage::

    ```python
    from mypy_boto3_dms.literals import AuthMechanismValueType

    data: AuthMechanismValueType = "default"
    ```
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AuthMechanismValueType",
    "AuthTypeValueType",
    "CannedAclForObjectsValueType",
    "CharLengthSemanticsType",
    "CompressionTypeValueType",
    "DataFormatValueType",
    "DatePartitionDelimiterValueType",
    "DatePartitionSequenceValueType",
    "DescribeCertificatesPaginatorName",
    "DescribeConnectionsPaginatorName",
    "DescribeEndpointTypesPaginatorName",
    "DescribeEndpointsPaginatorName",
    "DescribeEventSubscriptionsPaginatorName",
    "DescribeEventsPaginatorName",
    "DescribeOrderableReplicationInstancesPaginatorName",
    "DescribeReplicationInstancesPaginatorName",
    "DescribeReplicationSubnetGroupsPaginatorName",
    "DescribeReplicationTaskAssessmentResultsPaginatorName",
    "DescribeReplicationTasksPaginatorName",
    "DescribeSchemasPaginatorName",
    "DescribeTableStatisticsPaginatorName",
    "DmsSslModeValueType",
    "EncodingTypeValueType",
    "EncryptionModeValueType",
    "EndpointDeletedWaiterName",
    "EndpointSettingTypeValueType",
    "KafkaSecurityProtocolType",
    "MessageFormatValueType",
    "MigrationTypeValueType",
    "NestingLevelValueType",
    "ParquetVersionValueType",
    "PluginNameValueType",
    "RedisAuthTypeValueType",
    "RefreshSchemasStatusTypeValueType",
    "ReleaseStatusValuesType",
    "ReloadOptionValueType",
    "ReplicationEndpointTypeValueType",
    "ReplicationInstanceAvailableWaiterName",
    "ReplicationInstanceDeletedWaiterName",
    "ReplicationTaskDeletedWaiterName",
    "ReplicationTaskReadyWaiterName",
    "ReplicationTaskRunningWaiterName",
    "ReplicationTaskStoppedWaiterName",
    "SafeguardPolicyType",
    "SourceTypeType",
    "SslSecurityProtocolValueType",
    "StartReplicationTaskTypeValueType",
    "TargetDbTypeType",
    "TestConnectionSucceedsWaiterName",
    "ServiceName",
)


AuthMechanismValueType = Literal["default", "mongodb_cr", "scram_sha_1"]
AuthTypeValueType = Literal["no", "password"]
CannedAclForObjectsValueType = Literal[
    "authenticated-read",
    "aws-exec-read",
    "bucket-owner-full-control",
    "bucket-owner-read",
    "none",
    "private",
    "public-read",
    "public-read-write",
]
CharLengthSemanticsType = Literal["byte", "char", "default"]
CompressionTypeValueType = Literal["gzip", "none"]
DataFormatValueType = Literal["csv", "parquet"]
DatePartitionDelimiterValueType = Literal["DASH", "NONE", "SLASH", "UNDERSCORE"]
DatePartitionSequenceValueType = Literal["DDMMYYYY", "MMYYYYDD", "YYYYMM", "YYYYMMDD", "YYYYMMDDHH"]
DescribeCertificatesPaginatorName = Literal["describe_certificates"]
DescribeConnectionsPaginatorName = Literal["describe_connections"]
DescribeEndpointTypesPaginatorName = Literal["describe_endpoint_types"]
DescribeEndpointsPaginatorName = Literal["describe_endpoints"]
DescribeEventSubscriptionsPaginatorName = Literal["describe_event_subscriptions"]
DescribeEventsPaginatorName = Literal["describe_events"]
DescribeOrderableReplicationInstancesPaginatorName = Literal[
    "describe_orderable_replication_instances"
]
DescribeReplicationInstancesPaginatorName = Literal["describe_replication_instances"]
DescribeReplicationSubnetGroupsPaginatorName = Literal["describe_replication_subnet_groups"]
DescribeReplicationTaskAssessmentResultsPaginatorName = Literal[
    "describe_replication_task_assessment_results"
]
DescribeReplicationTasksPaginatorName = Literal["describe_replication_tasks"]
DescribeSchemasPaginatorName = Literal["describe_schemas"]
DescribeTableStatisticsPaginatorName = Literal["describe_table_statistics"]
DmsSslModeValueType = Literal["none", "require", "verify-ca", "verify-full"]
EncodingTypeValueType = Literal["plain", "plain-dictionary", "rle-dictionary"]
EncryptionModeValueType = Literal["sse-kms", "sse-s3"]
EndpointDeletedWaiterName = Literal["endpoint_deleted"]
EndpointSettingTypeValueType = Literal["boolean", "enum", "integer", "string"]
KafkaSecurityProtocolType = Literal["plaintext", "sasl-ssl", "ssl-authentication", "ssl-encryption"]
MessageFormatValueType = Literal["json", "json-unformatted"]
MigrationTypeValueType = Literal["cdc", "full-load", "full-load-and-cdc"]
NestingLevelValueType = Literal["none", "one"]
ParquetVersionValueType = Literal["parquet-1-0", "parquet-2-0"]
PluginNameValueType = Literal["no-preference", "pglogical", "test-decoding"]
RedisAuthTypeValueType = Literal["auth-role", "auth-token", "none"]
RefreshSchemasStatusTypeValueType = Literal["failed", "refreshing", "successful"]
ReleaseStatusValuesType = Literal["beta"]
ReloadOptionValueType = Literal["data-reload", "validate-only"]
ReplicationEndpointTypeValueType = Literal["source", "target"]
ReplicationInstanceAvailableWaiterName = Literal["replication_instance_available"]
ReplicationInstanceDeletedWaiterName = Literal["replication_instance_deleted"]
ReplicationTaskDeletedWaiterName = Literal["replication_task_deleted"]
ReplicationTaskReadyWaiterName = Literal["replication_task_ready"]
ReplicationTaskRunningWaiterName = Literal["replication_task_running"]
ReplicationTaskStoppedWaiterName = Literal["replication_task_stopped"]
SafeguardPolicyType = Literal[
    "exclusive-automatic-truncation",
    "rely-on-sql-server-replication-agent",
    "shared-automatic-truncation",
]
SourceTypeType = Literal["replication-instance"]
SslSecurityProtocolValueType = Literal["plaintext", "ssl-encryption"]
StartReplicationTaskTypeValueType = Literal[
    "reload-target", "resume-processing", "start-replication"
]
TargetDbTypeType = Literal["multiple-databases", "specific-database"]
TestConnectionSucceedsWaiterName = Literal["test_connection_succeeds"]
ServiceName = Literal[
    "accessanalyzer",
    "acm",
    "acm-pca",
    "alexaforbusiness",
    "amp",
    "amplify",
    "amplifybackend",
    "apigateway",
    "apigatewaymanagementapi",
    "apigatewayv2",
    "appconfig",
    "appflow",
    "appintegrations",
    "application-autoscaling",
    "application-insights",
    "applicationcostprofiler",
    "appmesh",
    "apprunner",
    "appstream",
    "appsync",
    "athena",
    "auditmanager",
    "autoscaling",
    "autoscaling-plans",
    "backup",
    "batch",
    "braket",
    "budgets",
    "ce",
    "chime",
    "chime-sdk-identity",
    "chime-sdk-messaging",
    "cloud9",
    "clouddirectory",
    "cloudformation",
    "cloudfront",
    "cloudhsm",
    "cloudhsmv2",
    "cloudsearch",
    "cloudsearchdomain",
    "cloudtrail",
    "cloudwatch",
    "codeartifact",
    "codebuild",
    "codecommit",
    "codedeploy",
    "codeguru-reviewer",
    "codeguruprofiler",
    "codepipeline",
    "codestar",
    "codestar-connections",
    "codestar-notifications",
    "cognito-identity",
    "cognito-idp",
    "cognito-sync",
    "comprehend",
    "comprehendmedical",
    "compute-optimizer",
    "config",
    "connect",
    "connect-contact-lens",
    "connectparticipant",
    "cur",
    "customer-profiles",
    "databrew",
    "dataexchange",
    "datapipeline",
    "datasync",
    "dax",
    "detective",
    "devicefarm",
    "devops-guru",
    "directconnect",
    "discovery",
    "dlm",
    "dms",
    "docdb",
    "ds",
    "dynamodb",
    "dynamodbstreams",
    "ebs",
    "ec2",
    "ec2-instance-connect",
    "ecr",
    "ecr-public",
    "ecs",
    "efs",
    "eks",
    "elastic-inference",
    "elasticache",
    "elasticbeanstalk",
    "elastictranscoder",
    "elb",
    "elbv2",
    "emr",
    "emr-containers",
    "es",
    "events",
    "finspace",
    "finspace-data",
    "firehose",
    "fis",
    "fms",
    "forecast",
    "forecastquery",
    "frauddetector",
    "fsx",
    "gamelift",
    "glacier",
    "globalaccelerator",
    "glue",
    "greengrass",
    "greengrassv2",
    "groundstation",
    "guardduty",
    "health",
    "healthlake",
    "honeycode",
    "iam",
    "identitystore",
    "imagebuilder",
    "importexport",
    "inspector",
    "iot",
    "iot-data",
    "iot-jobs-data",
    "iot1click-devices",
    "iot1click-projects",
    "iotanalytics",
    "iotdeviceadvisor",
    "iotevents",
    "iotevents-data",
    "iotfleethub",
    "iotsecuretunneling",
    "iotsitewise",
    "iotthingsgraph",
    "iotwireless",
    "ivs",
    "kafka",
    "kafkaconnect",
    "kendra",
    "kinesis",
    "kinesis-video-archived-media",
    "kinesis-video-media",
    "kinesis-video-signaling",
    "kinesisanalytics",
    "kinesisanalyticsv2",
    "kinesisvideo",
    "kms",
    "lakeformation",
    "lambda",
    "lex-models",
    "lex-runtime",
    "lexv2-models",
    "lexv2-runtime",
    "license-manager",
    "lightsail",
    "location",
    "logs",
    "lookoutequipment",
    "lookoutmetrics",
    "lookoutvision",
    "machinelearning",
    "macie",
    "macie2",
    "managedblockchain",
    "marketplace-catalog",
    "marketplace-entitlement",
    "marketplacecommerceanalytics",
    "mediaconnect",
    "mediaconvert",
    "medialive",
    "mediapackage",
    "mediapackage-vod",
    "mediastore",
    "mediastore-data",
    "mediatailor",
    "memorydb",
    "meteringmarketplace",
    "mgh",
    "mgn",
    "migrationhub-config",
    "mobile",
    "mq",
    "mturk",
    "mwaa",
    "neptune",
    "network-firewall",
    "networkmanager",
    "nimble",
    "opensearch",
    "opsworks",
    "opsworkscm",
    "organizations",
    "outposts",
    "personalize",
    "personalize-events",
    "personalize-runtime",
    "pi",
    "pinpoint",
    "pinpoint-email",
    "pinpoint-sms-voice",
    "polly",
    "pricing",
    "proton",
    "qldb",
    "qldb-session",
    "quicksight",
    "ram",
    "rds",
    "rds-data",
    "redshift",
    "redshift-data",
    "rekognition",
    "resource-groups",
    "resourcegroupstaggingapi",
    "robomaker",
    "route53",
    "route53-recovery-cluster",
    "route53-recovery-control-config",
    "route53-recovery-readiness",
    "route53domains",
    "route53resolver",
    "s3",
    "s3control",
    "s3outposts",
    "sagemaker",
    "sagemaker-a2i-runtime",
    "sagemaker-edge",
    "sagemaker-featurestore-runtime",
    "sagemaker-runtime",
    "savingsplans",
    "schemas",
    "sdb",
    "secretsmanager",
    "securityhub",
    "serverlessrepo",
    "service-quotas",
    "servicecatalog",
    "servicecatalog-appregistry",
    "servicediscovery",
    "ses",
    "sesv2",
    "shield",
    "signer",
    "sms",
    "sms-voice",
    "snow-device-management",
    "snowball",
    "sns",
    "sqs",
    "ssm",
    "ssm-contacts",
    "ssm-incidents",
    "sso",
    "sso-admin",
    "sso-oidc",
    "stepfunctions",
    "storagegateway",
    "sts",
    "support",
    "swf",
    "synthetics",
    "textract",
    "timestream-query",
    "timestream-write",
    "transcribe",
    "transfer",
    "translate",
    "waf",
    "waf-regional",
    "wafv2",
    "wellarchitected",
    "workdocs",
    "worklink",
    "workmail",
    "workmailmessageflow",
    "workspaces",
    "xray",
]
