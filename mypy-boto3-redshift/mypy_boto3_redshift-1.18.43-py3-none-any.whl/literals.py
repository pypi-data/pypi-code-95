"""
Type annotations for redshift service literal definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_redshift/literals.html)

Usage::

    ```python
    from mypy_boto3_redshift.literals import ActionTypeType

    data: ActionTypeType = "recommend-node-config"
    ```
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "ActionTypeType",
    "AquaConfigurationStatusType",
    "AquaStatusType",
    "AuthorizationStatusType",
    "ClusterAvailableWaiterName",
    "ClusterDeletedWaiterName",
    "ClusterRestoredWaiterName",
    "DataShareStatusForConsumerType",
    "DataShareStatusForProducerType",
    "DataShareStatusType",
    "DescribeClusterDbRevisionsPaginatorName",
    "DescribeClusterParameterGroupsPaginatorName",
    "DescribeClusterParametersPaginatorName",
    "DescribeClusterSecurityGroupsPaginatorName",
    "DescribeClusterSnapshotsPaginatorName",
    "DescribeClusterSubnetGroupsPaginatorName",
    "DescribeClusterTracksPaginatorName",
    "DescribeClusterVersionsPaginatorName",
    "DescribeClustersPaginatorName",
    "DescribeDefaultClusterParametersPaginatorName",
    "DescribeEndpointAccessPaginatorName",
    "DescribeEndpointAuthorizationPaginatorName",
    "DescribeEventSubscriptionsPaginatorName",
    "DescribeEventsPaginatorName",
    "DescribeHsmClientCertificatesPaginatorName",
    "DescribeHsmConfigurationsPaginatorName",
    "DescribeNodeConfigurationOptionsPaginatorName",
    "DescribeOrderableClusterOptionsPaginatorName",
    "DescribeReservedNodeOfferingsPaginatorName",
    "DescribeReservedNodesPaginatorName",
    "DescribeScheduledActionsPaginatorName",
    "DescribeSnapshotCopyGrantsPaginatorName",
    "DescribeSnapshotSchedulesPaginatorName",
    "DescribeTableRestoreStatusPaginatorName",
    "DescribeTagsPaginatorName",
    "DescribeUsageLimitsPaginatorName",
    "GetReservedNodeExchangeOfferingsPaginatorName",
    "ModeType",
    "NodeConfigurationOptionsFilterNameType",
    "OperatorTypeType",
    "ParameterApplyTypeType",
    "PartnerIntegrationStatusType",
    "ReservedNodeOfferingTypeType",
    "ScheduleStateType",
    "ScheduledActionFilterNameType",
    "ScheduledActionStateType",
    "ScheduledActionTypeValuesType",
    "SnapshotAttributeToSortByType",
    "SnapshotAvailableWaiterName",
    "SortByOrderType",
    "SourceTypeType",
    "TableRestoreStatusTypeType",
    "UsageLimitBreachActionType",
    "UsageLimitFeatureTypeType",
    "UsageLimitLimitTypeType",
    "UsageLimitPeriodType",
    "ServiceName",
)


ActionTypeType = Literal["recommend-node-config", "resize-cluster", "restore-cluster"]
AquaConfigurationStatusType = Literal["auto", "disabled", "enabled"]
AquaStatusType = Literal["applying", "disabled", "enabled"]
AuthorizationStatusType = Literal["Authorized", "Revoking"]
ClusterAvailableWaiterName = Literal["cluster_available"]
ClusterDeletedWaiterName = Literal["cluster_deleted"]
ClusterRestoredWaiterName = Literal["cluster_restored"]
DataShareStatusForConsumerType = Literal["ACTIVE", "AVAILABLE"]
DataShareStatusForProducerType = Literal[
    "ACTIVE", "AUTHORIZED", "DEAUTHORIZED", "PENDING_AUTHORIZATION", "REJECTED"
]
DataShareStatusType = Literal[
    "ACTIVE", "AUTHORIZED", "AVAILABLE", "DEAUTHORIZED", "PENDING_AUTHORIZATION", "REJECTED"
]
DescribeClusterDbRevisionsPaginatorName = Literal["describe_cluster_db_revisions"]
DescribeClusterParameterGroupsPaginatorName = Literal["describe_cluster_parameter_groups"]
DescribeClusterParametersPaginatorName = Literal["describe_cluster_parameters"]
DescribeClusterSecurityGroupsPaginatorName = Literal["describe_cluster_security_groups"]
DescribeClusterSnapshotsPaginatorName = Literal["describe_cluster_snapshots"]
DescribeClusterSubnetGroupsPaginatorName = Literal["describe_cluster_subnet_groups"]
DescribeClusterTracksPaginatorName = Literal["describe_cluster_tracks"]
DescribeClusterVersionsPaginatorName = Literal["describe_cluster_versions"]
DescribeClustersPaginatorName = Literal["describe_clusters"]
DescribeDefaultClusterParametersPaginatorName = Literal["describe_default_cluster_parameters"]
DescribeEndpointAccessPaginatorName = Literal["describe_endpoint_access"]
DescribeEndpointAuthorizationPaginatorName = Literal["describe_endpoint_authorization"]
DescribeEventSubscriptionsPaginatorName = Literal["describe_event_subscriptions"]
DescribeEventsPaginatorName = Literal["describe_events"]
DescribeHsmClientCertificatesPaginatorName = Literal["describe_hsm_client_certificates"]
DescribeHsmConfigurationsPaginatorName = Literal["describe_hsm_configurations"]
DescribeNodeConfigurationOptionsPaginatorName = Literal["describe_node_configuration_options"]
DescribeOrderableClusterOptionsPaginatorName = Literal["describe_orderable_cluster_options"]
DescribeReservedNodeOfferingsPaginatorName = Literal["describe_reserved_node_offerings"]
DescribeReservedNodesPaginatorName = Literal["describe_reserved_nodes"]
DescribeScheduledActionsPaginatorName = Literal["describe_scheduled_actions"]
DescribeSnapshotCopyGrantsPaginatorName = Literal["describe_snapshot_copy_grants"]
DescribeSnapshotSchedulesPaginatorName = Literal["describe_snapshot_schedules"]
DescribeTableRestoreStatusPaginatorName = Literal["describe_table_restore_status"]
DescribeTagsPaginatorName = Literal["describe_tags"]
DescribeUsageLimitsPaginatorName = Literal["describe_usage_limits"]
GetReservedNodeExchangeOfferingsPaginatorName = Literal["get_reserved_node_exchange_offerings"]
ModeType = Literal["high-performance", "standard"]
NodeConfigurationOptionsFilterNameType = Literal[
    "EstimatedDiskUtilizationPercent", "Mode", "NodeType", "NumberOfNodes"
]
OperatorTypeType = Literal["between", "eq", "ge", "gt", "in", "le", "lt"]
ParameterApplyTypeType = Literal["dynamic", "static"]
PartnerIntegrationStatusType = Literal["Active", "ConnectionFailure", "Inactive", "RuntimeFailure"]
ReservedNodeOfferingTypeType = Literal["Regular", "Upgradable"]
ScheduleStateType = Literal["ACTIVE", "FAILED", "MODIFYING"]
ScheduledActionFilterNameType = Literal["cluster-identifier", "iam-role"]
ScheduledActionStateType = Literal["ACTIVE", "DISABLED"]
ScheduledActionTypeValuesType = Literal["PauseCluster", "ResizeCluster", "ResumeCluster"]
SnapshotAttributeToSortByType = Literal["CREATE_TIME", "SOURCE_TYPE", "TOTAL_SIZE"]
SnapshotAvailableWaiterName = Literal["snapshot_available"]
SortByOrderType = Literal["ASC", "DESC"]
SourceTypeType = Literal[
    "cluster",
    "cluster-parameter-group",
    "cluster-security-group",
    "cluster-snapshot",
    "scheduled-action",
]
TableRestoreStatusTypeType = Literal["CANCELED", "FAILED", "IN_PROGRESS", "PENDING", "SUCCEEDED"]
UsageLimitBreachActionType = Literal["disable", "emit-metric", "log"]
UsageLimitFeatureTypeType = Literal["concurrency-scaling", "spectrum"]
UsageLimitLimitTypeType = Literal["data-scanned", "time"]
UsageLimitPeriodType = Literal["daily", "monthly", "weekly"]
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
