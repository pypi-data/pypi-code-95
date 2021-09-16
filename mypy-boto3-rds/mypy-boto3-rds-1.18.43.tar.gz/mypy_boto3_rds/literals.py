"""
Type annotations for rds service literal definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_rds/literals.html)

Usage::

    ```python
    from mypy_boto3_rds.literals import ActivityStreamModeType

    data: ActivityStreamModeType = "async"
    ```
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "ActivityStreamModeType",
    "ActivityStreamStatusType",
    "ApplyMethodType",
    "AuthSchemeType",
    "DBClusterSnapshotAvailableWaiterName",
    "DBClusterSnapshotDeletedWaiterName",
    "DBInstanceAvailableWaiterName",
    "DBInstanceDeletedWaiterName",
    "DBProxyEndpointStatusType",
    "DBProxyEndpointTargetRoleType",
    "DBProxyStatusType",
    "DBSnapshotAvailableWaiterName",
    "DBSnapshotCompletedWaiterName",
    "DBSnapshotDeletedWaiterName",
    "DescribeCertificatesPaginatorName",
    "DescribeCustomAvailabilityZonesPaginatorName",
    "DescribeDBClusterBacktracksPaginatorName",
    "DescribeDBClusterEndpointsPaginatorName",
    "DescribeDBClusterParameterGroupsPaginatorName",
    "DescribeDBClusterParametersPaginatorName",
    "DescribeDBClusterSnapshotsPaginatorName",
    "DescribeDBClustersPaginatorName",
    "DescribeDBEngineVersionsPaginatorName",
    "DescribeDBInstanceAutomatedBackupsPaginatorName",
    "DescribeDBInstancesPaginatorName",
    "DescribeDBLogFilesPaginatorName",
    "DescribeDBParameterGroupsPaginatorName",
    "DescribeDBParametersPaginatorName",
    "DescribeDBProxiesPaginatorName",
    "DescribeDBProxyEndpointsPaginatorName",
    "DescribeDBProxyTargetGroupsPaginatorName",
    "DescribeDBProxyTargetsPaginatorName",
    "DescribeDBSecurityGroupsPaginatorName",
    "DescribeDBSnapshotsPaginatorName",
    "DescribeDBSubnetGroupsPaginatorName",
    "DescribeEngineDefaultClusterParametersPaginatorName",
    "DescribeEngineDefaultParametersPaginatorName",
    "DescribeEventSubscriptionsPaginatorName",
    "DescribeEventsPaginatorName",
    "DescribeExportTasksPaginatorName",
    "DescribeGlobalClustersPaginatorName",
    "DescribeInstallationMediaPaginatorName",
    "DescribeOptionGroupOptionsPaginatorName",
    "DescribeOptionGroupsPaginatorName",
    "DescribeOrderableDBInstanceOptionsPaginatorName",
    "DescribePendingMaintenanceActionsPaginatorName",
    "DescribeReservedDBInstancesOfferingsPaginatorName",
    "DescribeReservedDBInstancesPaginatorName",
    "DescribeSourceRegionsPaginatorName",
    "DownloadDBLogFilePortionPaginatorName",
    "EngineFamilyType",
    "FailoverStatusType",
    "IAMAuthModeType",
    "ReplicaModeType",
    "SourceTypeType",
    "TargetHealthReasonType",
    "TargetRoleType",
    "TargetStateType",
    "TargetTypeType",
    "WriteForwardingStatusType",
    "ServiceName",
)


ActivityStreamModeType = Literal["async", "sync"]
ActivityStreamStatusType = Literal["started", "starting", "stopped", "stopping"]
ApplyMethodType = Literal["immediate", "pending-reboot"]
AuthSchemeType = Literal["SECRETS"]
DBClusterSnapshotAvailableWaiterName = Literal["db_cluster_snapshot_available"]
DBClusterSnapshotDeletedWaiterName = Literal["db_cluster_snapshot_deleted"]
DBInstanceAvailableWaiterName = Literal["db_instance_available"]
DBInstanceDeletedWaiterName = Literal["db_instance_deleted"]
DBProxyEndpointStatusType = Literal[
    "available",
    "creating",
    "deleting",
    "incompatible-network",
    "insufficient-resource-limits",
    "modifying",
]
DBProxyEndpointTargetRoleType = Literal["READ_ONLY", "READ_WRITE"]
DBProxyStatusType = Literal[
    "available",
    "creating",
    "deleting",
    "incompatible-network",
    "insufficient-resource-limits",
    "modifying",
    "reactivating",
    "suspended",
    "suspending",
]
DBSnapshotAvailableWaiterName = Literal["db_snapshot_available"]
DBSnapshotCompletedWaiterName = Literal["db_snapshot_completed"]
DBSnapshotDeletedWaiterName = Literal["db_snapshot_deleted"]
DescribeCertificatesPaginatorName = Literal["describe_certificates"]
DescribeCustomAvailabilityZonesPaginatorName = Literal["describe_custom_availability_zones"]
DescribeDBClusterBacktracksPaginatorName = Literal["describe_db_cluster_backtracks"]
DescribeDBClusterEndpointsPaginatorName = Literal["describe_db_cluster_endpoints"]
DescribeDBClusterParameterGroupsPaginatorName = Literal["describe_db_cluster_parameter_groups"]
DescribeDBClusterParametersPaginatorName = Literal["describe_db_cluster_parameters"]
DescribeDBClusterSnapshotsPaginatorName = Literal["describe_db_cluster_snapshots"]
DescribeDBClustersPaginatorName = Literal["describe_db_clusters"]
DescribeDBEngineVersionsPaginatorName = Literal["describe_db_engine_versions"]
DescribeDBInstanceAutomatedBackupsPaginatorName = Literal["describe_db_instance_automated_backups"]
DescribeDBInstancesPaginatorName = Literal["describe_db_instances"]
DescribeDBLogFilesPaginatorName = Literal["describe_db_log_files"]
DescribeDBParameterGroupsPaginatorName = Literal["describe_db_parameter_groups"]
DescribeDBParametersPaginatorName = Literal["describe_db_parameters"]
DescribeDBProxiesPaginatorName = Literal["describe_db_proxies"]
DescribeDBProxyEndpointsPaginatorName = Literal["describe_db_proxy_endpoints"]
DescribeDBProxyTargetGroupsPaginatorName = Literal["describe_db_proxy_target_groups"]
DescribeDBProxyTargetsPaginatorName = Literal["describe_db_proxy_targets"]
DescribeDBSecurityGroupsPaginatorName = Literal["describe_db_security_groups"]
DescribeDBSnapshotsPaginatorName = Literal["describe_db_snapshots"]
DescribeDBSubnetGroupsPaginatorName = Literal["describe_db_subnet_groups"]
DescribeEngineDefaultClusterParametersPaginatorName = Literal[
    "describe_engine_default_cluster_parameters"
]
DescribeEngineDefaultParametersPaginatorName = Literal["describe_engine_default_parameters"]
DescribeEventSubscriptionsPaginatorName = Literal["describe_event_subscriptions"]
DescribeEventsPaginatorName = Literal["describe_events"]
DescribeExportTasksPaginatorName = Literal["describe_export_tasks"]
DescribeGlobalClustersPaginatorName = Literal["describe_global_clusters"]
DescribeInstallationMediaPaginatorName = Literal["describe_installation_media"]
DescribeOptionGroupOptionsPaginatorName = Literal["describe_option_group_options"]
DescribeOptionGroupsPaginatorName = Literal["describe_option_groups"]
DescribeOrderableDBInstanceOptionsPaginatorName = Literal["describe_orderable_db_instance_options"]
DescribePendingMaintenanceActionsPaginatorName = Literal["describe_pending_maintenance_actions"]
DescribeReservedDBInstancesOfferingsPaginatorName = Literal[
    "describe_reserved_db_instances_offerings"
]
DescribeReservedDBInstancesPaginatorName = Literal["describe_reserved_db_instances"]
DescribeSourceRegionsPaginatorName = Literal["describe_source_regions"]
DownloadDBLogFilePortionPaginatorName = Literal["download_db_log_file_portion"]
EngineFamilyType = Literal["MYSQL", "POSTGRESQL"]
FailoverStatusType = Literal["cancelling", "failing-over", "pending"]
IAMAuthModeType = Literal["DISABLED", "REQUIRED"]
ReplicaModeType = Literal["mounted", "open-read-only"]
SourceTypeType = Literal[
    "db-cluster",
    "db-cluster-snapshot",
    "db-instance",
    "db-parameter-group",
    "db-security-group",
    "db-snapshot",
]
TargetHealthReasonType = Literal[
    "AUTH_FAILURE",
    "CONNECTION_FAILED",
    "INVALID_REPLICATION_STATE",
    "PENDING_PROXY_CAPACITY",
    "UNREACHABLE",
]
TargetRoleType = Literal["READ_ONLY", "READ_WRITE", "UNKNOWN"]
TargetStateType = Literal["AVAILABLE", "REGISTERING", "UNAVAILABLE"]
TargetTypeType = Literal["RDS_INSTANCE", "RDS_SERVERLESS_ENDPOINT", "TRACKED_CLUSTER"]
WriteForwardingStatusType = Literal["disabled", "disabling", "enabled", "enabling", "unknown"]
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
