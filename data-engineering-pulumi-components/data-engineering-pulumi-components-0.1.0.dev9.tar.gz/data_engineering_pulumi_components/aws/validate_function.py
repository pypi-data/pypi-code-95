import json
from typing import Optional
from pathlib import Path

from data_engineering_pulumi_components.aws import Bucket
from data_engineering_pulumi_components.utils import Tagger
from pulumi import (
    AssetArchive,
    ComponentResource,
    FileArchive,
    FileAsset,
    Output,
    ResourceOptions,
)
from pulumi_aws.iam import Role, RolePolicy, RolePolicyAttachment
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, Permission
from pulumi_aws.s3 import BucketNotification, BucketNotificationLambdaFunctionArgs
from pulumi_aws.cloudwatch import EventRule, EventTarget


class ValidateMoveObjectFunction(ComponentResource):
    def __init__(
        self,
        pass_bucket: Bucket,
        fail_bucket: Bucket,
        name: str,
        source_bucket: Bucket,
        tagger: Tagger,
        trigger_on_object_create: bool = True,
        trigger_on_schedule: bool = True,
        schedule: str = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """
        Provides a Lambda function that inspects objects from a source bucket, and
        sends them to a pass or fail bucket depending on their response to validation
        tests.

        Parameters
        ----------
        pass_bucket : Bucket
            The bucket to copy data to upon passing validation.
        fail_bucket : Bucket
            The bucket to copy data to upon failing validation.
        name : str
            The name of the resource.
        source_bucket : Bucket
            The bucket to copy data from.
        tagger : Tagger
            A tagger resource.
        trigger_on_object_create: bool
            The lambda function is triggered when a object is created
        trigger_on_schedule: bool,
            The lambda function is triggered on a schedule
        schedule: str
            the schedule in which the lambda is triggered.
            The default is daily at midnight.
        opts : Optional[ResourceOptions]
            Options for the resource. By default, None.
        """
        super().__init__(
            t="data-engineering-pulumi-components:aws:validateMoveObjectFunction",
            name=name,
            props=None,
            opts=opts,
        )

        self._role = Role(
            resource_name=f"{name}-role",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
            name=f"{name}-validate",
            path="/service-role/",
            tags=tagger.create_tags(f"{name}-validate"),
            opts=ResourceOptions(parent=self),
        )
        self._rolePolicy = RolePolicy(
            resource_name=f"{name}-role-policy",
            name="s3-access",
            policy=Output.all(
                source_bucket.arn, pass_bucket.arn, fail_bucket.arn
            ).apply(
                lambda args: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "GetDeleteSourceBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[0]}/*", f"{args[0]}"],
                                "Action": [
                                    "s3:GetObject*",
                                    "s3:DeleteObject*",
                                    "s3:ListBucket*",
                                ],
                            },
                            {
                                "Sid": "PutPassBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[1]}/*"],
                                "Action": ["s3:PutObject*"],
                            },
                            {
                                "Sid": "PutFailBucket",
                                "Effect": "Allow",
                                "Resource": [f"{args[2]}/*"],
                                "Action": ["s3:PutObject*"],
                            },
                        ],
                    }
                )
            ),
            role=self._role.id,
            opts=ResourceOptions(parent=self._role),
        )
        self._rolePolicyAttachment = RolePolicyAttachment(
            resource_name=f"{name}-role-policy-attachment",
            policy_arn=(
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            ),
            role=self._role.name,
            opts=ResourceOptions(parent=self._role),
        )
        self._function = Function(
            resource_name=f"{name}-function",
            code=AssetArchive(
                assets={
                    ".": FileArchive(
                        str(Path(__file__).parent.absolute())
                        + "/lambda_/validate/dependencies.tar.gz"
                    ),
                    "validate.py": FileAsset(
                        str(Path(__file__).parent.absolute())
                        + "/lambda_/validate/validate.py"
                    ),
                }
            ),
            description=Output.all(source_bucket.name).apply(
                lambda args: f"Validates data from {args[0]}"
            ),
            environment=Output.all(
                source_bucket.name, pass_bucket.name, fail_bucket.name
            ).apply(
                lambda name: FunctionEnvironmentArgs(
                    variables={
                        "SOURCE_BUCKET": f"{name[0]}",
                        "PASS_BUCKET": f"{name[1]}",
                        "FAIL_BUCKET": f"{name[2]}",
                    }
                )
            ),
            handler="validate.handler",
            name=f"{name}-validate",
            role=self._role.arn,
            runtime="python3.8",
            tags=tagger.create_tags(f"{name}-validate"),
            timeout=300,
            opts=ResourceOptions(parent=self),
        )
        self._permission = Permission(
            resource_name=f"{name}-permission",
            action="lambda:InvokeFunction",
            function=self._function.arn,
            principal="s3.amazonaws.com",
            source_arn=source_bucket.arn,
            opts=ResourceOptions(parent=self._function),
        )

        if trigger_on_object_create:
            self._bucketNotification = BucketNotification(
                resource_name=f"{name}-bucket-notification",
                bucket=source_bucket.id,
                lambda_functions=[
                    BucketNotificationLambdaFunctionArgs(
                        events=["s3:ObjectCreated:*"],
                        lambda_function_arn=self._function.arn,
                    )
                ],
                opts=ResourceOptions(parent=self._permission),
            )

        if trigger_on_schedule:
            if schedule is None:
                schedule = "cron(0 0 ? * * *)"  # Every day at 00:00 UTC

            self._eventRule = EventRule(
                resource_name=f"{name}-run-validation-and-move",
                opts=ResourceOptions(parent=self),
                name=f"{name}-run-validation-and-move",
                description=f"Triggers the {name} lambda function to re-run "
                "validation and move files from landing to raw history",
                schedule_expression=schedule,
                tags=tagger.create_tags(f"{name}"),
            )

            self._eventPermission = Permission(
                resource_name=f"{name}-event-permission",
                action="lambda:InvokeFunction",
                function=self._function.arn,
                principal="events.amazonaws.com",
                source_arn=self._eventRule.arn,
                opts=ResourceOptions(parent=self._function),
            )
            self._eventTarget = EventTarget(
                resource_name=f"{name}",
                opts=ResourceOptions(parent=self._eventRule),
                arn=self._function.arn,
                rule=self._eventRule.name,
                input='{"scheduled_event": true}',
            )
