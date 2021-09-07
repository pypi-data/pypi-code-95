from dataclasses import dataclass

from aws_cdk.aws_efs import ThroughputMode, PerformanceMode
from aws_cdk.core import RemovalPolicy, Size


@dataclass
class EfsProps:
    """
    Custom EFS properties.

    https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_efs/FileSystemProps.html
    """

    performance_mode: PerformanceMode = None
    throughput_mode: ThroughputMode = None
    provisioned_throughput_per_second: Size = None
    removal_policy: RemovalPolicy = RemovalPolicy.DESTROY
