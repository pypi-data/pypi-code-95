"""
Type annotations for servicecatalog service literal definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_servicecatalog/literals.html)

Usage::

    ```python
    from mypy_boto3_servicecatalog.literals import AccessLevelFilterKeyType

    data: AccessLevelFilterKeyType = "Account"
    ```
"""
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = (
    "AccessLevelFilterKeyType",
    "AccessStatusType",
    "ChangeActionType",
    "CopyOptionType",
    "CopyProductStatusType",
    "DescribePortfolioShareTypeType",
    "EvaluationTypeType",
    "ListAcceptedPortfolioSharesPaginatorName",
    "ListConstraintsForPortfolioPaginatorName",
    "ListLaunchPathsPaginatorName",
    "ListOrganizationPortfolioAccessPaginatorName",
    "ListPortfoliosForProductPaginatorName",
    "ListPortfoliosPaginatorName",
    "ListPrincipalsForPortfolioPaginatorName",
    "ListProvisionedProductPlansPaginatorName",
    "ListProvisioningArtifactsForServiceActionPaginatorName",
    "ListRecordHistoryPaginatorName",
    "ListResourcesForTagOptionPaginatorName",
    "ListServiceActionsForProvisioningArtifactPaginatorName",
    "ListServiceActionsPaginatorName",
    "ListTagOptionsPaginatorName",
    "OrganizationNodeTypeType",
    "PortfolioShareTypeType",
    "PrincipalTypeType",
    "ProductSourceType",
    "ProductTypeType",
    "ProductViewFilterByType",
    "ProductViewSortByType",
    "PropertyKeyType",
    "ProvisionedProductPlanStatusType",
    "ProvisionedProductPlanTypeType",
    "ProvisionedProductStatusType",
    "ProvisionedProductViewFilterByType",
    "ProvisioningArtifactGuidanceType",
    "ProvisioningArtifactPropertyNameType",
    "ProvisioningArtifactTypeType",
    "RecordStatusType",
    "ReplacementType",
    "RequiresRecreationType",
    "ResourceAttributeType",
    "ScanProvisionedProductsPaginatorName",
    "SearchProductsAsAdminPaginatorName",
    "ServiceActionAssociationErrorCodeType",
    "ServiceActionDefinitionKeyType",
    "ServiceActionDefinitionTypeType",
    "ShareStatusType",
    "SortOrderType",
    "StackInstanceStatusType",
    "StackSetOperationTypeType",
    "StatusType",
    "ServiceName",
)


AccessLevelFilterKeyType = Literal["Account", "Role", "User"]
AccessStatusType = Literal["DISABLED", "ENABLED", "UNDER_CHANGE"]
ChangeActionType = Literal["ADD", "MODIFY", "REMOVE"]
CopyOptionType = Literal["CopyTags"]
CopyProductStatusType = Literal["FAILED", "IN_PROGRESS", "SUCCEEDED"]
DescribePortfolioShareTypeType = Literal[
    "ACCOUNT", "ORGANIZATION", "ORGANIZATIONAL_UNIT", "ORGANIZATION_MEMBER_ACCOUNT"
]
EvaluationTypeType = Literal["DYNAMIC", "STATIC"]
ListAcceptedPortfolioSharesPaginatorName = Literal["list_accepted_portfolio_shares"]
ListConstraintsForPortfolioPaginatorName = Literal["list_constraints_for_portfolio"]
ListLaunchPathsPaginatorName = Literal["list_launch_paths"]
ListOrganizationPortfolioAccessPaginatorName = Literal["list_organization_portfolio_access"]
ListPortfoliosForProductPaginatorName = Literal["list_portfolios_for_product"]
ListPortfoliosPaginatorName = Literal["list_portfolios"]
ListPrincipalsForPortfolioPaginatorName = Literal["list_principals_for_portfolio"]
ListProvisionedProductPlansPaginatorName = Literal["list_provisioned_product_plans"]
ListProvisioningArtifactsForServiceActionPaginatorName = Literal[
    "list_provisioning_artifacts_for_service_action"
]
ListRecordHistoryPaginatorName = Literal["list_record_history"]
ListResourcesForTagOptionPaginatorName = Literal["list_resources_for_tag_option"]
ListServiceActionsForProvisioningArtifactPaginatorName = Literal[
    "list_service_actions_for_provisioning_artifact"
]
ListServiceActionsPaginatorName = Literal["list_service_actions"]
ListTagOptionsPaginatorName = Literal["list_tag_options"]
OrganizationNodeTypeType = Literal["ACCOUNT", "ORGANIZATION", "ORGANIZATIONAL_UNIT"]
PortfolioShareTypeType = Literal["AWS_ORGANIZATIONS", "AWS_SERVICECATALOG", "IMPORTED"]
PrincipalTypeType = Literal["IAM"]
ProductSourceType = Literal["ACCOUNT"]
ProductTypeType = Literal["CLOUD_FORMATION_TEMPLATE", "MARKETPLACE"]
ProductViewFilterByType = Literal["FullTextSearch", "Owner", "ProductType", "SourceProductId"]
ProductViewSortByType = Literal["CreationDate", "Title", "VersionCount"]
PropertyKeyType = Literal["LAUNCH_ROLE", "OWNER"]
ProvisionedProductPlanStatusType = Literal[
    "CREATE_FAILED",
    "CREATE_IN_PROGRESS",
    "CREATE_SUCCESS",
    "EXECUTE_FAILED",
    "EXECUTE_IN_PROGRESS",
    "EXECUTE_SUCCESS",
]
ProvisionedProductPlanTypeType = Literal["CLOUDFORMATION"]
ProvisionedProductStatusType = Literal[
    "AVAILABLE", "ERROR", "PLAN_IN_PROGRESS", "TAINTED", "UNDER_CHANGE"
]
ProvisionedProductViewFilterByType = Literal["SearchQuery"]
ProvisioningArtifactGuidanceType = Literal["DEFAULT", "DEPRECATED"]
ProvisioningArtifactPropertyNameType = Literal["Id"]
ProvisioningArtifactTypeType = Literal[
    "CLOUD_FORMATION_TEMPLATE", "MARKETPLACE_AMI", "MARKETPLACE_CAR"
]
RecordStatusType = Literal["CREATED", "FAILED", "IN_PROGRESS", "IN_PROGRESS_IN_ERROR", "SUCCEEDED"]
ReplacementType = Literal["CONDITIONAL", "FALSE", "TRUE"]
RequiresRecreationType = Literal["ALWAYS", "CONDITIONALLY", "NEVER"]
ResourceAttributeType = Literal[
    "CREATIONPOLICY", "DELETIONPOLICY", "METADATA", "PROPERTIES", "TAGS", "UPDATEPOLICY"
]
ScanProvisionedProductsPaginatorName = Literal["scan_provisioned_products"]
SearchProductsAsAdminPaginatorName = Literal["search_products_as_admin"]
ServiceActionAssociationErrorCodeType = Literal[
    "DUPLICATE_RESOURCE", "INTERNAL_FAILURE", "LIMIT_EXCEEDED", "RESOURCE_NOT_FOUND", "THROTTLING"
]
ServiceActionDefinitionKeyType = Literal["AssumeRole", "Name", "Parameters", "Version"]
ServiceActionDefinitionTypeType = Literal["SSM_AUTOMATION"]
ShareStatusType = Literal[
    "COMPLETED", "COMPLETED_WITH_ERRORS", "ERROR", "IN_PROGRESS", "NOT_STARTED"
]
SortOrderType = Literal["ASCENDING", "DESCENDING"]
StackInstanceStatusType = Literal["CURRENT", "INOPERABLE", "OUTDATED"]
StackSetOperationTypeType = Literal["CREATE", "DELETE", "UPDATE"]
StatusType = Literal["AVAILABLE", "CREATING", "FAILED"]
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
