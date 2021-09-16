"""
Type annotations for ecs service literal definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_ecs/literals.html)

Usage::

    ```python
    from mypy_boto3_ecs.literals import AgentUpdateStatusType

    data: AgentUpdateStatusType = "FAILED"
    ```
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AgentUpdateStatusType",
    "AssignPublicIpType",
    "CapacityProviderFieldType",
    "CapacityProviderStatusType",
    "CapacityProviderUpdateStatusType",
    "ClusterFieldType",
    "ClusterSettingNameType",
    "CompatibilityType",
    "ConnectivityType",
    "ContainerConditionType",
    "ContainerInstanceFieldType",
    "ContainerInstanceStatusType",
    "DeploymentControllerTypeType",
    "DeploymentRolloutStateType",
    "DesiredStatusType",
    "DeviceCgroupPermissionType",
    "EFSAuthorizationConfigIAMType",
    "EFSTransitEncryptionType",
    "EnvironmentFileTypeType",
    "ExecuteCommandLoggingType",
    "FirelensConfigurationTypeType",
    "HealthStatusType",
    "IpcModeType",
    "LaunchTypeType",
    "ListAccountSettingsPaginatorName",
    "ListAttributesPaginatorName",
    "ListClustersPaginatorName",
    "ListContainerInstancesPaginatorName",
    "ListServicesPaginatorName",
    "ListTaskDefinitionFamiliesPaginatorName",
    "ListTaskDefinitionsPaginatorName",
    "ListTasksPaginatorName",
    "LogDriverType",
    "ManagedAgentNameType",
    "ManagedScalingStatusType",
    "ManagedTerminationProtectionType",
    "NetworkModeType",
    "PidModeType",
    "PlacementConstraintTypeType",
    "PlacementStrategyTypeType",
    "PlatformDeviceTypeType",
    "PropagateTagsType",
    "ProxyConfigurationTypeType",
    "ResourceTypeType",
    "ScaleUnitType",
    "SchedulingStrategyType",
    "ScopeType",
    "ServiceFieldType",
    "ServicesInactiveWaiterName",
    "ServicesStableWaiterName",
    "SettingNameType",
    "SortOrderType",
    "StabilityStatusType",
    "TargetTypeType",
    "TaskDefinitionFamilyStatusType",
    "TaskDefinitionFieldType",
    "TaskDefinitionPlacementConstraintTypeType",
    "TaskDefinitionStatusType",
    "TaskFieldType",
    "TaskSetFieldType",
    "TaskStopCodeType",
    "TasksRunningWaiterName",
    "TasksStoppedWaiterName",
    "TransportProtocolType",
    "UlimitNameType",
    "ServiceName",
)


AgentUpdateStatusType = Literal["FAILED", "PENDING", "STAGED", "STAGING", "UPDATED", "UPDATING"]
AssignPublicIpType = Literal["DISABLED", "ENABLED"]
CapacityProviderFieldType = Literal["TAGS"]
CapacityProviderStatusType = Literal["ACTIVE", "INACTIVE"]
CapacityProviderUpdateStatusType = Literal[
    "DELETE_COMPLETE",
    "DELETE_FAILED",
    "DELETE_IN_PROGRESS",
    "UPDATE_COMPLETE",
    "UPDATE_FAILED",
    "UPDATE_IN_PROGRESS",
]
ClusterFieldType = Literal["ATTACHMENTS", "CONFIGURATIONS", "SETTINGS", "STATISTICS", "TAGS"]
ClusterSettingNameType = Literal["containerInsights"]
CompatibilityType = Literal["EC2", "EXTERNAL", "FARGATE"]
ConnectivityType = Literal["CONNECTED", "DISCONNECTED"]
ContainerConditionType = Literal["COMPLETE", "HEALTHY", "START", "SUCCESS"]
ContainerInstanceFieldType = Literal["TAGS"]
ContainerInstanceStatusType = Literal[
    "ACTIVE", "DEREGISTERING", "DRAINING", "REGISTERING", "REGISTRATION_FAILED"
]
DeploymentControllerTypeType = Literal["CODE_DEPLOY", "ECS", "EXTERNAL"]
DeploymentRolloutStateType = Literal["COMPLETED", "FAILED", "IN_PROGRESS"]
DesiredStatusType = Literal["PENDING", "RUNNING", "STOPPED"]
DeviceCgroupPermissionType = Literal["mknod", "read", "write"]
EFSAuthorizationConfigIAMType = Literal["DISABLED", "ENABLED"]
EFSTransitEncryptionType = Literal["DISABLED", "ENABLED"]
EnvironmentFileTypeType = Literal["s3"]
ExecuteCommandLoggingType = Literal["DEFAULT", "NONE", "OVERRIDE"]
FirelensConfigurationTypeType = Literal["fluentbit", "fluentd"]
HealthStatusType = Literal["HEALTHY", "UNHEALTHY", "UNKNOWN"]
IpcModeType = Literal["host", "none", "task"]
LaunchTypeType = Literal["EC2", "EXTERNAL", "FARGATE"]
ListAccountSettingsPaginatorName = Literal["list_account_settings"]
ListAttributesPaginatorName = Literal["list_attributes"]
ListClustersPaginatorName = Literal["list_clusters"]
ListContainerInstancesPaginatorName = Literal["list_container_instances"]
ListServicesPaginatorName = Literal["list_services"]
ListTaskDefinitionFamiliesPaginatorName = Literal["list_task_definition_families"]
ListTaskDefinitionsPaginatorName = Literal["list_task_definitions"]
ListTasksPaginatorName = Literal["list_tasks"]
LogDriverType = Literal[
    "awsfirelens", "awslogs", "fluentd", "gelf", "journald", "json-file", "splunk", "syslog"
]
ManagedAgentNameType = Literal["ExecuteCommandAgent"]
ManagedScalingStatusType = Literal["DISABLED", "ENABLED"]
ManagedTerminationProtectionType = Literal["DISABLED", "ENABLED"]
NetworkModeType = Literal["awsvpc", "bridge", "host", "none"]
PidModeType = Literal["host", "task"]
PlacementConstraintTypeType = Literal["distinctInstance", "memberOf"]
PlacementStrategyTypeType = Literal["binpack", "random", "spread"]
PlatformDeviceTypeType = Literal["GPU"]
PropagateTagsType = Literal["SERVICE", "TASK_DEFINITION"]
ProxyConfigurationTypeType = Literal["APPMESH"]
ResourceTypeType = Literal["GPU", "InferenceAccelerator"]
ScaleUnitType = Literal["PERCENT"]
SchedulingStrategyType = Literal["DAEMON", "REPLICA"]
ScopeType = Literal["shared", "task"]
ServiceFieldType = Literal["TAGS"]
ServicesInactiveWaiterName = Literal["services_inactive"]
ServicesStableWaiterName = Literal["services_stable"]
SettingNameType = Literal[
    "awsvpcTrunking",
    "containerInsights",
    "containerInstanceLongArnFormat",
    "serviceLongArnFormat",
    "taskLongArnFormat",
]
SortOrderType = Literal["ASC", "DESC"]
StabilityStatusType = Literal["STABILIZING", "STEADY_STATE"]
TargetTypeType = Literal["container-instance"]
TaskDefinitionFamilyStatusType = Literal["ACTIVE", "ALL", "INACTIVE"]
TaskDefinitionFieldType = Literal["TAGS"]
TaskDefinitionPlacementConstraintTypeType = Literal["memberOf"]
TaskDefinitionStatusType = Literal["ACTIVE", "INACTIVE"]
TaskFieldType = Literal["TAGS"]
TaskSetFieldType = Literal["TAGS"]
TaskStopCodeType = Literal["EssentialContainerExited", "TaskFailedToStart", "UserInitiated"]
TasksRunningWaiterName = Literal["tasks_running"]
TasksStoppedWaiterName = Literal["tasks_stopped"]
TransportProtocolType = Literal["tcp", "udp"]
UlimitNameType = Literal[
    "core",
    "cpu",
    "data",
    "fsize",
    "locks",
    "memlock",
    "msgqueue",
    "nice",
    "nofile",
    "nproc",
    "rss",
    "rtprio",
    "rttime",
    "sigpending",
    "stack",
]
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
