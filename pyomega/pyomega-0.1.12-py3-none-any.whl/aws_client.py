import os
import boto3


class AWSClient:

    def __init__(self, admin=False):
        self.aws_session_token = None

        if admin:
            if "LOCAL" in os.environ:
                self.aws_region = os.environ["ADMIN_AWS_REGION"]
                self.aws_access_key = os.environ["ADMIN_AWS_ACCESS_KEY_ID"]
                self.aws_secret_key = os.environ["ADMIN_AWS_SECRET_ACCESS_KEY"]
            else:
                sts = boto3.client('sts')
                response = sts.assume_role(
                    RoleArn=os.environ["ADMIN_STS_ROLE"],
                    RoleSessionName='my-random-session-name',
                    DurationSeconds=900  # how many seconds these credentials will work
                )
                self.aws_region = response['Credentials']['AccessKeyId']
                self.aws_access_key = response['Credentials']['SecretAccessKey']
                self.aws_session_token = response['Credentials']['SessionToken']
        else:
            self.aws_region = os.environ["AWS_REGION"]
            self.aws_access_key = os.environ["AWS_ACCESS_KEY_ID"]
            self.aws_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    def client(self, service):

        if "LOCAL" in os.environ:
            return boto3.client(service, region_name=self.aws_region,
                                aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key,
                                aws_session_token=self.aws_session_token)
        return boto3.client(service)

    def resource(self, service):
        if "LOCAL" in os.environ:
            return boto3.resource(service, region_name=self.aws_region,
                                  aws_access_key_id=self.aws_access_key,
                                  aws_secret_access_key=self.aws_secret_key,
                                  aws_session_token=self.aws_session_token)
        return boto3.resource(service)
