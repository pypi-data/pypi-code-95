"""
Type annotations for macie2 service literal definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_macie2/literals.html)

Usage::

    ```python
    from mypy_boto3_macie2.literals import AdminStatusType

    data: AdminStatusType = "DISABLING_IN_PROGRESS"
    ```
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AdminStatusType",
    "AllowsUnencryptedObjectUploadsType",
    "CurrencyType",
    "DayOfWeekType",
    "DescribeBucketsPaginatorName",
    "EffectivePermissionType",
    "EncryptionTypeType",
    "ErrorCodeType",
    "FindingActionTypeType",
    "FindingCategoryType",
    "FindingPublishingFrequencyType",
    "FindingStatisticsSortAttributeNameType",
    "FindingTypeType",
    "FindingsFilterActionType",
    "GetUsageStatisticsPaginatorName",
    "GroupByType",
    "IsDefinedInJobType",
    "IsMonitoredByJobType",
    "JobComparatorType",
    "JobStatusType",
    "JobTypeType",
    "LastRunErrorStatusCodeType",
    "ListClassificationJobsPaginatorName",
    "ListCustomDataIdentifiersPaginatorName",
    "ListFindingsFiltersPaginatorName",
    "ListFindingsPaginatorName",
    "ListInvitationsPaginatorName",
    "ListJobsFilterKeyType",
    "ListJobsSortAttributeNameType",
    "ListMembersPaginatorName",
    "ListOrganizationAdminAccountsPaginatorName",
    "MacieStatusType",
    "ManagedDataIdentifierSelectorType",
    "OrderByType",
    "RelationshipStatusType",
    "ScopeFilterKeyType",
    "SearchResourcesComparatorType",
    "SearchResourcesPaginatorName",
    "SearchResourcesSimpleCriterionKeyType",
    "SearchResourcesSortAttributeNameType",
    "SensitiveDataItemCategoryType",
    "SeverityDescriptionType",
    "SharedAccessType",
    "SimpleCriterionKeyForJobType",
    "StorageClassType",
    "TagTargetType",
    "TimeRangeType",
    "TypeType",
    "UnitType",
    "UsageStatisticsFilterComparatorType",
    "UsageStatisticsFilterKeyType",
    "UsageStatisticsSortKeyType",
    "UsageTypeType",
    "UserIdentityTypeType",
    "ServiceName",
)


AdminStatusType = Literal["DISABLING_IN_PROGRESS", "ENABLED"]
AllowsUnencryptedObjectUploadsType = Literal["FALSE", "TRUE", "UNKNOWN"]
CurrencyType = Literal["USD"]
DayOfWeekType = Literal[
    "FRIDAY", "MONDAY", "SATURDAY", "SUNDAY", "THURSDAY", "TUESDAY", "WEDNESDAY"
]
DescribeBucketsPaginatorName = Literal["describe_buckets"]
EffectivePermissionType = Literal["NOT_PUBLIC", "PUBLIC", "UNKNOWN"]
EncryptionTypeType = Literal["AES256", "NONE", "UNKNOWN", "aws:kms"]
ErrorCodeType = Literal["ClientError", "InternalError"]
FindingActionTypeType = Literal["AWS_API_CALL"]
FindingCategoryType = Literal["CLASSIFICATION", "POLICY"]
FindingPublishingFrequencyType = Literal["FIFTEEN_MINUTES", "ONE_HOUR", "SIX_HOURS"]
FindingStatisticsSortAttributeNameType = Literal["count", "groupKey"]
FindingTypeType = Literal[
    "Policy:IAMUser/S3BlockPublicAccessDisabled",
    "Policy:IAMUser/S3BucketEncryptionDisabled",
    "Policy:IAMUser/S3BucketPublic",
    "Policy:IAMUser/S3BucketReplicatedExternally",
    "Policy:IAMUser/S3BucketSharedExternally",
    "SensitiveData:S3Object/Credentials",
    "SensitiveData:S3Object/CustomIdentifier",
    "SensitiveData:S3Object/Financial",
    "SensitiveData:S3Object/Multiple",
    "SensitiveData:S3Object/Personal",
]
FindingsFilterActionType = Literal["ARCHIVE", "NOOP"]
GetUsageStatisticsPaginatorName = Literal["get_usage_statistics"]
GroupByType = Literal[
    "classificationDetails.jobId", "resourcesAffected.s3Bucket.name", "severity.description", "type"
]
IsDefinedInJobType = Literal["FALSE", "TRUE", "UNKNOWN"]
IsMonitoredByJobType = Literal["FALSE", "TRUE", "UNKNOWN"]
JobComparatorType = Literal["CONTAINS", "EQ", "GT", "GTE", "LT", "LTE", "NE", "STARTS_WITH"]
JobStatusType = Literal["CANCELLED", "COMPLETE", "IDLE", "PAUSED", "RUNNING", "USER_PAUSED"]
JobTypeType = Literal["ONE_TIME", "SCHEDULED"]
LastRunErrorStatusCodeType = Literal["ERROR", "NONE"]
ListClassificationJobsPaginatorName = Literal["list_classification_jobs"]
ListCustomDataIdentifiersPaginatorName = Literal["list_custom_data_identifiers"]
ListFindingsFiltersPaginatorName = Literal["list_findings_filters"]
ListFindingsPaginatorName = Literal["list_findings"]
ListInvitationsPaginatorName = Literal["list_invitations"]
ListJobsFilterKeyType = Literal["createdAt", "jobStatus", "jobType", "name"]
ListJobsSortAttributeNameType = Literal["createdAt", "jobStatus", "jobType", "name"]
ListMembersPaginatorName = Literal["list_members"]
ListOrganizationAdminAccountsPaginatorName = Literal["list_organization_admin_accounts"]
MacieStatusType = Literal["ENABLED", "PAUSED"]
ManagedDataIdentifierSelectorType = Literal["ALL", "EXCLUDE", "INCLUDE", "NONE"]
OrderByType = Literal["ASC", "DESC"]
RelationshipStatusType = Literal[
    "AccountSuspended",
    "Created",
    "EmailVerificationFailed",
    "EmailVerificationInProgress",
    "Enabled",
    "Invited",
    "Paused",
    "RegionDisabled",
    "Removed",
    "Resigned",
]
ScopeFilterKeyType = Literal[
    "OBJECT_EXTENSION", "OBJECT_KEY", "OBJECT_LAST_MODIFIED_DATE", "OBJECT_SIZE"
]
SearchResourcesComparatorType = Literal["EQ", "NE"]
SearchResourcesPaginatorName = Literal["search_resources"]
SearchResourcesSimpleCriterionKeyType = Literal[
    "ACCOUNT_ID", "S3_BUCKET_EFFECTIVE_PERMISSION", "S3_BUCKET_NAME", "S3_BUCKET_SHARED_ACCESS"
]
SearchResourcesSortAttributeNameType = Literal[
    "ACCOUNT_ID", "RESOURCE_NAME", "S3_CLASSIFIABLE_OBJECT_COUNT", "S3_CLASSIFIABLE_SIZE_IN_BYTES"
]
SensitiveDataItemCategoryType = Literal[
    "CREDENTIALS", "CUSTOM_IDENTIFIER", "FINANCIAL_INFORMATION", "PERSONAL_INFORMATION"
]
SeverityDescriptionType = Literal["High", "Low", "Medium"]
SharedAccessType = Literal["EXTERNAL", "INTERNAL", "NOT_SHARED", "UNKNOWN"]
SimpleCriterionKeyForJobType = Literal[
    "ACCOUNT_ID", "S3_BUCKET_EFFECTIVE_PERMISSION", "S3_BUCKET_NAME", "S3_BUCKET_SHARED_ACCESS"
]
StorageClassType = Literal[
    "DEEP_ARCHIVE",
    "GLACIER",
    "INTELLIGENT_TIERING",
    "ONEZONE_IA",
    "REDUCED_REDUNDANCY",
    "STANDARD",
    "STANDARD_IA",
]
TagTargetType = Literal["S3_OBJECT"]
TimeRangeType = Literal["MONTH_TO_DATE", "PAST_30_DAYS"]
TypeType = Literal["AES256", "NONE", "aws:kms"]
UnitType = Literal["TERABYTES"]
UsageStatisticsFilterComparatorType = Literal["CONTAINS", "EQ", "GT", "GTE", "LT", "LTE", "NE"]
UsageStatisticsFilterKeyType = Literal["accountId", "freeTrialStartDate", "serviceLimit", "total"]
UsageStatisticsSortKeyType = Literal[
    "accountId", "freeTrialStartDate", "serviceLimitValue", "total"
]
UsageTypeType = Literal["DATA_INVENTORY_EVALUATION", "SENSITIVE_DATA_DISCOVERY"]
UserIdentityTypeType = Literal[
    "AWSAccount", "AWSService", "AssumedRole", "FederatedUser", "IAMUser", "Root"
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
