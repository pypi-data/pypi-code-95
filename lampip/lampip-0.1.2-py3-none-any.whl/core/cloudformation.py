from typing import Dict

import boto3
from botocore.exceptions import ClientError
from termcolor import cprint

STACKNAME = "lampip"

TEMPLATE = """\
AWSTemplateFormatVersion: 2010-09-09
Resources:
  DeploymentBucket:
    Type: 'AWS::S3::Bucket'
"""


def _create_stack_if_not_exists():
    kargs = {"TemplateBody": TEMPLATE, "Capabilities": ["CAPABILITY_IAM"]}
    cf = boto3.resource("cloudformation")
    stack = cf.Stack(STACKNAME)
    try:
        _ = stack.stack_id
        # if exists
    except ClientError:
        # if not exists
        cprint(f"Create the new cloudformation stack: {STACKNAME}", color="green")
        cf.create_stack(StackName=STACKNAME, **kargs)
        print("waiting stack create completed ...")
        cfcli = boto3.client("cloudformation")
        waiter = cfcli.get_waiter("stack_create_complete")
        waiter.wait(StackName=STACKNAME)
        print("DONE")


def get_cf_resources() -> Dict:
    _create_stack_if_not_exists()
    cf = boto3.resource("cloudformation")
    return {
        "DeploymentBucketName": cf.StackResource(
            STACKNAME, "DeploymentBucket"
        ).physical_resource_id
    }
