"""
Type annotations for resourcegroupstaggingapi service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_resourcegroupstaggingapi/type_defs.html)

Usage::

    ```python
    from mypy_boto3_resourcegroupstaggingapi.type_defs import ComplianceDetailsTypeDef

    data: ComplianceDetailsTypeDef = {...}
    ```
"""
import sys
from typing import Any, Dict, List, Mapping, Sequence

from .literals import ErrorCodeType, GroupByAttributeType, TargetIdTypeType

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "ComplianceDetailsTypeDef",
    "DescribeReportCreationOutputTypeDef",
    "FailureInfoTypeDef",
    "GetComplianceSummaryInputRequestTypeDef",
    "GetComplianceSummaryOutputTypeDef",
    "GetResourcesInputRequestTypeDef",
    "GetResourcesOutputTypeDef",
    "GetTagKeysInputRequestTypeDef",
    "GetTagKeysOutputTypeDef",
    "GetTagValuesInputRequestTypeDef",
    "GetTagValuesOutputTypeDef",
    "PaginatorConfigTypeDef",
    "ResourceTagMappingTypeDef",
    "ResponseMetadataTypeDef",
    "StartReportCreationInputRequestTypeDef",
    "SummaryTypeDef",
    "TagFilterTypeDef",
    "TagResourcesInputRequestTypeDef",
    "TagResourcesOutputTypeDef",
    "TagTypeDef",
    "UntagResourcesInputRequestTypeDef",
    "UntagResourcesOutputTypeDef",
)

ComplianceDetailsTypeDef = TypedDict(
    "ComplianceDetailsTypeDef",
    {
        "NoncompliantKeys": List[str],
        "KeysWithNoncompliantValues": List[str],
        "ComplianceStatus": bool,
    },
    total=False,
)

DescribeReportCreationOutputTypeDef = TypedDict(
    "DescribeReportCreationOutputTypeDef",
    {
        "Status": str,
        "S3Location": str,
        "ErrorMessage": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

FailureInfoTypeDef = TypedDict(
    "FailureInfoTypeDef",
    {
        "StatusCode": int,
        "ErrorCode": ErrorCodeType,
        "ErrorMessage": str,
    },
    total=False,
)

GetComplianceSummaryInputRequestTypeDef = TypedDict(
    "GetComplianceSummaryInputRequestTypeDef",
    {
        "TargetIdFilters": Sequence[str],
        "RegionFilters": Sequence[str],
        "ResourceTypeFilters": Sequence[str],
        "TagKeyFilters": Sequence[str],
        "GroupBy": Sequence[GroupByAttributeType],
        "MaxResults": int,
        "PaginationToken": str,
    },
    total=False,
)

GetComplianceSummaryOutputTypeDef = TypedDict(
    "GetComplianceSummaryOutputTypeDef",
    {
        "SummaryList": List["SummaryTypeDef"],
        "PaginationToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetResourcesInputRequestTypeDef = TypedDict(
    "GetResourcesInputRequestTypeDef",
    {
        "PaginationToken": str,
        "TagFilters": Sequence["TagFilterTypeDef"],
        "ResourcesPerPage": int,
        "TagsPerPage": int,
        "ResourceTypeFilters": Sequence[str],
        "IncludeComplianceDetails": bool,
        "ExcludeCompliantResources": bool,
        "ResourceARNList": Sequence[str],
    },
    total=False,
)

GetResourcesOutputTypeDef = TypedDict(
    "GetResourcesOutputTypeDef",
    {
        "PaginationToken": str,
        "ResourceTagMappingList": List["ResourceTagMappingTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetTagKeysInputRequestTypeDef = TypedDict(
    "GetTagKeysInputRequestTypeDef",
    {
        "PaginationToken": str,
    },
    total=False,
)

GetTagKeysOutputTypeDef = TypedDict(
    "GetTagKeysOutputTypeDef",
    {
        "PaginationToken": str,
        "TagKeys": List[str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetTagValuesInputRequestTypeDef = TypedDict(
    "_RequiredGetTagValuesInputRequestTypeDef",
    {
        "Key": str,
    },
)
_OptionalGetTagValuesInputRequestTypeDef = TypedDict(
    "_OptionalGetTagValuesInputRequestTypeDef",
    {
        "PaginationToken": str,
    },
    total=False,
)


class GetTagValuesInputRequestTypeDef(
    _RequiredGetTagValuesInputRequestTypeDef, _OptionalGetTagValuesInputRequestTypeDef
):
    pass


GetTagValuesOutputTypeDef = TypedDict(
    "GetTagValuesOutputTypeDef",
    {
        "PaginationToken": str,
        "TagValues": List[str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

ResourceTagMappingTypeDef = TypedDict(
    "ResourceTagMappingTypeDef",
    {
        "ResourceARN": str,
        "Tags": List["TagTypeDef"],
        "ComplianceDetails": "ComplianceDetailsTypeDef",
    },
    total=False,
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, Any],
        "RetryAttempts": int,
    },
)

StartReportCreationInputRequestTypeDef = TypedDict(
    "StartReportCreationInputRequestTypeDef",
    {
        "S3Bucket": str,
    },
)

SummaryTypeDef = TypedDict(
    "SummaryTypeDef",
    {
        "LastUpdated": str,
        "TargetId": str,
        "TargetIdType": TargetIdTypeType,
        "Region": str,
        "ResourceType": str,
        "NonCompliantResources": int,
    },
    total=False,
)

TagFilterTypeDef = TypedDict(
    "TagFilterTypeDef",
    {
        "Key": str,
        "Values": Sequence[str],
    },
    total=False,
)

TagResourcesInputRequestTypeDef = TypedDict(
    "TagResourcesInputRequestTypeDef",
    {
        "ResourceARNList": Sequence[str],
        "Tags": Mapping[str, str],
    },
)

TagResourcesOutputTypeDef = TypedDict(
    "TagResourcesOutputTypeDef",
    {
        "FailedResourcesMap": Dict[str, "FailureInfoTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

UntagResourcesInputRequestTypeDef = TypedDict(
    "UntagResourcesInputRequestTypeDef",
    {
        "ResourceARNList": Sequence[str],
        "TagKeys": Sequence[str],
    },
)

UntagResourcesOutputTypeDef = TypedDict(
    "UntagResourcesOutputTypeDef",
    {
        "FailedResourcesMap": Dict[str, "FailureInfoTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)
