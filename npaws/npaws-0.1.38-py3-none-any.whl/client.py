import boto3
from .config import (
    AWS_ACC_KEY_ID,
    AWS_SEC_ACC_KEY,
    AWS_REGION_NAME
)


class Boto3Client():
    """
    """
    
    def __init__(self,
                 service: str,
                 aws_access_key_id: str = AWS_ACC_KEY_ID,
                 aws_secret_access_key: str = AWS_SEC_ACC_KEY,
                 region_name: str = AWS_REGION_NAME):
        """
        """
        self._client = boto3.client(service,
                                    aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)
        self._inherit_from_boto3()
    
    def _inherit_from_boto3(self):
        """
        """
        for attr in self._client.__dir__():
            if not attr.startswith('__'):
                setattr(self, attr, getattr(self._client, attr))