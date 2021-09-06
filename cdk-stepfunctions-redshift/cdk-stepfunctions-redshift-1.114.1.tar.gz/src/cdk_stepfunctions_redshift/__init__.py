'''
## Welcome to the cdk-stepfunctions-redshift project!

`cdk-stepfunctions-redshift` provides `SfnRedshiftTasker` which is a JSII construct library to build AWS Serverless
infrastructure to easily orchestrate Amazon Redshift using AWS stepfunctions.

When you deploy a `SfnRedshiftTasker` you will get:

* A Lambda function for invoking tasks on an Amazon Redshift cluster
* A DDB Table to track ongoing-executions
* An Event rule to monitor Amazon Redshift Data API completion events and route them to SQS
* An SQS queue to receive above mentioned Amazon Redshift Data API completion events
* A Lambda function to process API Completions events (by default same function as the one above)
* A KMS key which encrypts data at rest.

This allows to easily create step-function tasks which execute a SQL command and will only complete
once Amazon Redshift finishes executing the corresponding statement.

## How it works

Serverless infrastructure will be spawn up for a specific (cluster, user, database). A Lambda function will be provided
which allows invoking statements as this user.  States can then be used to do a seemingly synchronous invocation of a
Amazon Redshift statement allowing your statemachines to have a simpler definition (see
[Example definition](README.md#example-definition-of-a-step-function-that-uses-the-exposed-lambda-function) for an example).

### Example flow

![alt text](images/aws-step-function-redshift-integration.png?raw=1)

1. A step-function step triggers the Lambda function provided by the construct. The step function step follows a
   structure for its invocation payload which includes designated fields of (SQL statement to execute, Step function
   task_token, Step function execution ARN)
2. The Lambda function will generate a unique ID based on the execution ARN and register the SQL invocation in a
   DynamoDB state table.
3. The lambda function then starts the statement using the Amazon Redshift data API using the Unique ID as statement
   name and requesting events for state changes.
4. As a result of step 3 Amazon Redshift executes the statement. Once that statement completes it emits an event. Our
   building blocks have put in place a Cloudwatch Rule to monitor these events.
5. The event gets placed into an SQS queue
6. This SQS queue is monitored by a Lambda function (could be the same as the previous one).
7. The Lambda function will check whether the finished query is related to a step function invocation in order to
   retrieve the task token of the step.
8. If it is then it will do a succeed/fail callback to the step-function step (using the task token) depending on
   success/failure of the SQL statement.
9. It will mark the invocation as processed in the state table.

## Example definition of a step function that uses the exposed lambda function

A state definition mostly comprises boiler plate code and
looks like:

```json
{
  "StateName": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
    "Parameters": {
      "FunctionName": "arn:aws:lambda:REGION:ACCOUNT_ID:function:FUNCTION_NAME",
      "Payload": {
        "taskToken.$": "$$.Task.Token",
        "executionArn.$": "$$.Execution.Id",
        "sqlStatement": "SQL_STATEMENT"
      }
    },
    "HeartbeatSeconds": 3600,
    "Next": "SUCCESS",
    "Catch": [
      {
         "ErrorEquals": [
            "States.Timeout"
         ],
         "Next": "cancelSlowQuery"
      },
      {
         "ErrorEquals": [
            "FAILED"
         ],
         "Next": "SQL_FAILURE"
      },
      {
        "ErrorEquals": [
          "States.ALL"
        ],
        "Next": "FAILURE"
      }
    ],
    "Retry": [
      {
        "ErrorEquals": [
          "Lambda.ServiceException",
          "Lambda.AWSLambdaException",
          "Lambda.SdkClientException"
        ],
        "IntervalSeconds": 2,
        "MaxAttempts": 6,
        "BackoffRate": 2
      },
      {
         "ErrorEquals": [
            "Lambda.TooManyRequestsException"
         ],
         "IntervalSeconds": 1,
         "MaxAttempts": 10,
         "BackoffRate": 1.5
      }
    ]
  }
}
```

Values that you want to fine tune per state:

* SQL_STATEMENT: The SQL statement that you want to run. If you want to run multiple statements in one go you should
  have it defined as a procedure on Amazon Redshift and you should call the procedure.
* 3600 (HeartbeatSeconds): How long the state will wait for feedback from the query (Note: maximum runtime is 24 hours,
  as per Amazon Redshift Data API).
* SUCCESS (Next): Name of the next state if the query execution succeeds.
* SQL_FAILURE (Catch.Next): Name of the next state if query execution fails.
* FAILURE (Catch.Next): Name of the next state if something else failed.

Values that depend on the deployment:

* REGION : AWS region in which is deployed e.g.: `eu-west-1`
* ACCOUNT_ID: Account ID in which we have this deployed e.g.: `012345678910`
* FUNCTION_NAME: The name of the function created by SfnRedshiftTasker (i.e.: `lambdaFunction` property)

### Retry logic

The provided Lambda function has a very limited running time. By default a concurrency of 1 is allowed therefore it is
recommended to aggressively retry throttled requests (`Lambda.TooManyRequestsException`). For other exceptions retry
mechanisms can be less aggressive. This is illustrated in the above example.

### Timeout

You can set a time budget using the `HeartbeatSeconds` parameter. If that time has passed a `States.Timeout` exception
is thrown which can be caught in order to implement custom handling. In the above example a timeout would result in
triggering the `cancelSlowQuery` state.

## How to use

This is a construct so you can use it from a CDK Stack. An example stack can be found at [integ.default.ts](src/integ.default.ts)
.  That stack sets up an Amazon Redshift cluster, the `SfnRedshiftTasker` infra and some state machines that use the
functionality. It can be launched by compiling the code (which creates a lib directory) and deploying the CDK app:
`yarn compile && npx cdk --app ./lib/integ.default.js deploy`

### Considerations

When using this approach do keep in mind the considerations of the [Amazon Redshift Data API](https://docs.aws.amazon.com/redshift/latest/mgmt/data-api.html#data-api-calling-considerations).

These shouldn't be blockers:

* If query result is too big consider using `UNLOAD` rather than `SELECT`.
* If the statement size is too big consider splitting up the statement in multiple statements. For example by
  defining and utilizing views or encapsulating the logic in a stored procedure.

### Handling of step timeout

Users can manually add a `Catch` for `States.Timeout`, which gets thrown after `HeartbeatSeconds` has passed. By
catching this exception they can transition to a state for handling this scenario.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_dynamodb
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_python
import aws_cdk.aws_sqs
import aws_cdk.core


@jsii.data_type(
    jsii_type="cdk-stepfunctions-redshift.RedshiftTargetProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_identifier": "clusterIdentifier",
        "db_name": "dbName",
        "db_user": "dbUser",
    },
)
class RedshiftTargetProps:
    def __init__(
        self,
        *,
        cluster_identifier: builtins.str,
        db_name: builtins.str,
        db_user: builtins.str,
    ) -> None:
        '''The details of the Redshift target in which you will execute SQL statements.

        :param cluster_identifier: The cluster identifier (name) in which the SQL statement will be executed. This is the part of the FQDN up to the first '.'.
        :param db_name: The Redshift database name in which the SQL statement will be executed.
        :param db_user: The Redshift database user that will execute the Redshift tasks.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_identifier": cluster_identifier,
            "db_name": db_name,
            "db_user": db_user,
        }

    @builtins.property
    def cluster_identifier(self) -> builtins.str:
        '''The cluster identifier (name) in which the SQL statement will be executed.

        This is the part of the FQDN up to the
        first '.'.
        '''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_name(self) -> builtins.str:
        '''The Redshift database name in which the SQL statement will be executed.'''
        result = self._values.get("db_name")
        assert result is not None, "Required property 'db_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_user(self) -> builtins.str:
        '''The Redshift database user that will execute the Redshift tasks.'''
        result = self._values.get("db_user")
        assert result is not None, "Required property 'db_user' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftTargetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SfnRedshiftTasker(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-stepfunctions-redshift.SfnRedshiftTasker",
):
    '''Create infrastructure to easily create tasks in a Stepfunction that run a SQL statement on a Redshift cluster and await completion.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        redshift_target_props: RedshiftTargetProps,
        completer_existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        completer_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        create_callback_infra: typing.Optional[builtins.bool] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        enable_queue_purging: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        encryption_key_props: typing.Optional[aws_cdk.aws_kms.KeyProps] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_table_obj: typing.Optional[aws_cdk.aws_dynamodb.Table] = None,
        log_level: typing.Optional[builtins.str] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        powertools_arn: typing.Optional[builtins.str] = None,
        python_layer_version_props: typing.Optional[aws_cdk.aws_lambda_python.PythonLayerVersionProps] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        starter_existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        starter_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        table_permissions: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates the infrastructure to allow stepfunction tasks that execute SQL commands and await their completion.

        :param scope: Scope within where this infrastructure is created.
        :param id: Identifier to name this building block.
        :param redshift_target_props: The details of the Redshift target in which you will execute SQL statements.
        :param completer_existing_lambda_obj: Existing instance of Lambda Function object that completes execution, if this is set then the completerLambdaFunctionProps is ignored. Default: - None
        :param completer_lambda_function_props: User provided props to override the default props for the Lambda function that completes execution. If completerExistingLambdaObj and this is omitted the Lambda function for starting executions is re-used. Default: - Re-use starter Lambda function.
        :param create_callback_infra: Setup the infrastructure to support the step function callback mechanism. If you never want to trigger Redshift statements from a step function then set this to false to avoid creating an SQS queue and the required polling. If you already have an SfnRedshiftTasker setup you should disable this as well (e.g. adding function for another cluster/database/username). Default: - true
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param enable_encryption_with_customer_managed_key: Use a KMS Key, either managed by this CDK app, or imported. If importing an encryption key, it must be specified in the encryptionKey property for this construct. Default: - true (encryption enabled, managed by this CDK app).
        :param enable_queue_purging: Whether to grant additional permissions to the Lambda function enabling it to purge the SQS queue. Default: - "false", disabled by default.
        :param encryption_key: An optional, imported encryption key to encrypt the SQS queue, and SNS Topic. Default: - not specified.
        :param encryption_key_props: Optional user-provided props to override the default props for the encryption key. Default: - Default props are used.
        :param existing_queue_obj: Existing instance of SQS queue object, if this is set then the queueProps is ignored. Default: - None
        :param existing_table_obj: Existing instance of DynamoDB table object, If this is set then the dynamoTableProps is ignored. Default: - None
        :param log_level: Optional log level to be used for Lambda functions. Default: - INFO
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param powertools_arn: The ARN of a lambda layer containing the AWS Lambda powertools. Default: - Not provided then an application will be created from the serverless application registry to get the layer. If you plan to create multiple SfnRedshiftTaskers then you can reuse the powertoolsArn from the first instance.
        :param python_layer_version_props: Optional user provided props to override the shared layer. Default: - None
        :param queue_props: User provided props to override the default props for the SQS queue. Default: - Default props are used
        :param starter_existing_lambda_obj: Existing instance of Lambda Function object that starts execution, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param starter_lambda_function_props: User provided props to override the default props for the Lambda function that starts execution. Default: - Default props are used
        :param table_permissions: Optional table permissions to grant to the Lambda function. One of the following may be specified: "All", "Read", "ReadWrite", "Write". Default: - Read/write access is given to the Lambda function if no value is specified.
        '''
        props = SfnRedshiftTaskerProps(
            redshift_target_props=redshift_target_props,
            completer_existing_lambda_obj=completer_existing_lambda_obj,
            completer_lambda_function_props=completer_lambda_function_props,
            create_callback_infra=create_callback_infra,
            dead_letter_queue_props=dead_letter_queue_props,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            dynamo_table_props=dynamo_table_props,
            enable_encryption_with_customer_managed_key=enable_encryption_with_customer_managed_key,
            enable_queue_purging=enable_queue_purging,
            encryption_key=encryption_key,
            encryption_key_props=encryption_key_props,
            existing_queue_obj=existing_queue_obj,
            existing_table_obj=existing_table_obj,
            log_level=log_level,
            max_receive_count=max_receive_count,
            powertools_arn=powertools_arn,
            python_layer_version_props=python_layer_version_props,
            queue_props=queue_props,
            starter_existing_lambda_obj=starter_existing_lambda_obj,
            starter_lambda_function_props=starter_lambda_function_props,
            table_permissions=table_permissions,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        '''The Lambda function which can be used from a Step function task to invoke a SQL statement.'''
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="powertoolsArn")
    def powertools_arn(self) -> builtins.str:
        '''The ARN of a layer hosting AWS Lambda powertools.'''
        return typing.cast(builtins.str, jsii.get(self, "powertoolsArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackingTable")
    def tracking_table(self) -> aws_cdk.aws_dynamodb.Table:
        '''A state table that tracks the Redshift statements being executed.'''
        return typing.cast(aws_cdk.aws_dynamodb.Table, jsii.get(self, "trackingTable"))


@jsii.data_type(
    jsii_type="cdk-stepfunctions-redshift.SfnRedshiftTaskerProps",
    jsii_struct_bases=[],
    name_mapping={
        "redshift_target_props": "redshiftTargetProps",
        "completer_existing_lambda_obj": "completerExistingLambdaObj",
        "completer_lambda_function_props": "completerLambdaFunctionProps",
        "create_callback_infra": "createCallbackInfra",
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "dynamo_table_props": "dynamoTableProps",
        "enable_encryption_with_customer_managed_key": "enableEncryptionWithCustomerManagedKey",
        "enable_queue_purging": "enableQueuePurging",
        "encryption_key": "encryptionKey",
        "encryption_key_props": "encryptionKeyProps",
        "existing_queue_obj": "existingQueueObj",
        "existing_table_obj": "existingTableObj",
        "log_level": "logLevel",
        "max_receive_count": "maxReceiveCount",
        "powertools_arn": "powertoolsArn",
        "python_layer_version_props": "pythonLayerVersionProps",
        "queue_props": "queueProps",
        "starter_existing_lambda_obj": "starterExistingLambdaObj",
        "starter_lambda_function_props": "starterLambdaFunctionProps",
        "table_permissions": "tablePermissions",
    },
)
class SfnRedshiftTaskerProps:
    def __init__(
        self,
        *,
        redshift_target_props: RedshiftTargetProps,
        completer_existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        completer_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        create_callback_infra: typing.Optional[builtins.bool] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        enable_queue_purging: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        encryption_key_props: typing.Optional[aws_cdk.aws_kms.KeyProps] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        existing_table_obj: typing.Optional[aws_cdk.aws_dynamodb.Table] = None,
        log_level: typing.Optional[builtins.str] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        powertools_arn: typing.Optional[builtins.str] = None,
        python_layer_version_props: typing.Optional[aws_cdk.aws_lambda_python.PythonLayerVersionProps] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        starter_existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        starter_lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
        table_permissions: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param redshift_target_props: The details of the Redshift target in which you will execute SQL statements.
        :param completer_existing_lambda_obj: Existing instance of Lambda Function object that completes execution, if this is set then the completerLambdaFunctionProps is ignored. Default: - None
        :param completer_lambda_function_props: User provided props to override the default props for the Lambda function that completes execution. If completerExistingLambdaObj and this is omitted the Lambda function for starting executions is re-used. Default: - Re-use starter Lambda function.
        :param create_callback_infra: Setup the infrastructure to support the step function callback mechanism. If you never want to trigger Redshift statements from a step function then set this to false to avoid creating an SQS queue and the required polling. If you already have an SfnRedshiftTasker setup you should disable this as well (e.g. adding function for another cluster/database/username). Default: - true
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param enable_encryption_with_customer_managed_key: Use a KMS Key, either managed by this CDK app, or imported. If importing an encryption key, it must be specified in the encryptionKey property for this construct. Default: - true (encryption enabled, managed by this CDK app).
        :param enable_queue_purging: Whether to grant additional permissions to the Lambda function enabling it to purge the SQS queue. Default: - "false", disabled by default.
        :param encryption_key: An optional, imported encryption key to encrypt the SQS queue, and SNS Topic. Default: - not specified.
        :param encryption_key_props: Optional user-provided props to override the default props for the encryption key. Default: - Default props are used.
        :param existing_queue_obj: Existing instance of SQS queue object, if this is set then the queueProps is ignored. Default: - None
        :param existing_table_obj: Existing instance of DynamoDB table object, If this is set then the dynamoTableProps is ignored. Default: - None
        :param log_level: Optional log level to be used for Lambda functions. Default: - INFO
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param powertools_arn: The ARN of a lambda layer containing the AWS Lambda powertools. Default: - Not provided then an application will be created from the serverless application registry to get the layer. If you plan to create multiple SfnRedshiftTaskers then you can reuse the powertoolsArn from the first instance.
        :param python_layer_version_props: Optional user provided props to override the shared layer. Default: - None
        :param queue_props: User provided props to override the default props for the SQS queue. Default: - Default props are used
        :param starter_existing_lambda_obj: Existing instance of Lambda Function object that starts execution, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param starter_lambda_function_props: User provided props to override the default props for the Lambda function that starts execution. Default: - Default props are used
        :param table_permissions: Optional table permissions to grant to the Lambda function. One of the following may be specified: "All", "Read", "ReadWrite", "Write". Default: - Read/write access is given to the Lambda function if no value is specified.

        :summary: The properties for the Construct
        '''
        if isinstance(redshift_target_props, dict):
            redshift_target_props = RedshiftTargetProps(**redshift_target_props)
        if isinstance(completer_lambda_function_props, dict):
            completer_lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**completer_lambda_function_props)
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = aws_cdk.aws_sqs.QueueProps(**dead_letter_queue_props)
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = aws_cdk.aws_dynamodb.TableProps(**dynamo_table_props)
        if isinstance(encryption_key_props, dict):
            encryption_key_props = aws_cdk.aws_kms.KeyProps(**encryption_key_props)
        if isinstance(python_layer_version_props, dict):
            python_layer_version_props = aws_cdk.aws_lambda_python.PythonLayerVersionProps(**python_layer_version_props)
        if isinstance(queue_props, dict):
            queue_props = aws_cdk.aws_sqs.QueueProps(**queue_props)
        if isinstance(starter_lambda_function_props, dict):
            starter_lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**starter_lambda_function_props)
        self._values: typing.Dict[str, typing.Any] = {
            "redshift_target_props": redshift_target_props,
        }
        if completer_existing_lambda_obj is not None:
            self._values["completer_existing_lambda_obj"] = completer_existing_lambda_obj
        if completer_lambda_function_props is not None:
            self._values["completer_lambda_function_props"] = completer_lambda_function_props
        if create_callback_infra is not None:
            self._values["create_callback_infra"] = create_callback_infra
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if enable_encryption_with_customer_managed_key is not None:
            self._values["enable_encryption_with_customer_managed_key"] = enable_encryption_with_customer_managed_key
        if enable_queue_purging is not None:
            self._values["enable_queue_purging"] = enable_queue_purging
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_key_props is not None:
            self._values["encryption_key_props"] = encryption_key_props
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if existing_table_obj is not None:
            self._values["existing_table_obj"] = existing_table_obj
        if log_level is not None:
            self._values["log_level"] = log_level
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if powertools_arn is not None:
            self._values["powertools_arn"] = powertools_arn
        if python_layer_version_props is not None:
            self._values["python_layer_version_props"] = python_layer_version_props
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if starter_existing_lambda_obj is not None:
            self._values["starter_existing_lambda_obj"] = starter_existing_lambda_obj
        if starter_lambda_function_props is not None:
            self._values["starter_lambda_function_props"] = starter_lambda_function_props
        if table_permissions is not None:
            self._values["table_permissions"] = table_permissions

    @builtins.property
    def redshift_target_props(self) -> RedshiftTargetProps:
        '''The details of the Redshift target in which you will execute SQL statements.'''
        result = self._values.get("redshift_target_props")
        assert result is not None, "Required property 'redshift_target_props' is missing"
        return typing.cast(RedshiftTargetProps, result)

    @builtins.property
    def completer_existing_lambda_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object that completes execution, if this is set then the completerLambdaFunctionProps is ignored.

        :default: - None
        '''
        result = self._values.get("completer_existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def completer_lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''User provided props to override the default props for the Lambda function that completes execution.

        If
        completerExistingLambdaObj and this is omitted the Lambda function for starting executions is re-used.

        :default: - Re-use starter Lambda function.
        '''
        result = self._values.get("completer_lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def create_callback_infra(self) -> typing.Optional[builtins.bool]:
        '''Setup the infrastructure to support the step function callback mechanism.

        If you never want to trigger Redshift
        statements from a step function then set this to false to avoid creating an SQS queue and the required polling.
        If you already have an SfnRedshiftTasker setup you should disable this as well (e.g. adding function for another cluster/database/username).

        :default: - true
        '''
        result = self._values.get("create_callback_infra")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dead_letter_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties for the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a secondary queue to be used as a dead letter queue.

        :default: - true.
        '''
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dynamo_table_props(self) -> typing.Optional[aws_cdk.aws_dynamodb.TableProps]:
        '''Optional user provided props to override the default props.

        :default: - Default props are used
        '''
        result = self._values.get("dynamo_table_props")
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.TableProps], result)

    @builtins.property
    def enable_encryption_with_customer_managed_key(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Use a KMS Key, either managed by this CDK app, or imported.

        If importing an encryption key, it must be specified in
        the encryptionKey property for this construct.

        :default: - true (encryption enabled, managed by this CDK app).
        '''
        result = self._values.get("enable_encryption_with_customer_managed_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_queue_purging(self) -> typing.Optional[builtins.bool]:
        '''Whether to grant additional permissions to the Lambda function enabling it to purge the SQS queue.

        :default: - "false", disabled by default.
        '''
        result = self._values.get("enable_queue_purging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.Key]:
        '''An optional, imported encryption key to encrypt the SQS queue, and SNS Topic.

        :default: - not specified.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.Key], result)

    @builtins.property
    def encryption_key_props(self) -> typing.Optional[aws_cdk.aws_kms.KeyProps]:
        '''Optional user-provided props to override the default props for the encryption key.

        :default: - Default props are used.
        '''
        result = self._values.get("encryption_key_props")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.KeyProps], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''Existing instance of SQS queue object, if this is set then the queueProps is ignored.

        :default: - None
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], result)

    @builtins.property
    def existing_table_obj(self) -> typing.Optional[aws_cdk.aws_dynamodb.Table]:
        '''Existing instance of DynamoDB table object, If this is set then the dynamoTableProps is ignored.

        :default: - None
        '''
        result = self._values.get("existing_table_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.Table], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''Optional log level to be used for Lambda functions.

        :default: - INFO
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: - required field if deployDeadLetterQueue=true.
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def powertools_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of a lambda layer containing the AWS Lambda powertools.

        :default:

        - Not provided then an application will be created from the serverless application registry to get the layer. If you plan to create
        multiple SfnRedshiftTaskers then you can reuse the powertoolsArn from the first instance.
        '''
        result = self._values.get("powertools_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def python_layer_version_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda_python.PythonLayerVersionProps]:
        '''Optional user provided props to override the shared layer.

        :default: - None
        '''
        result = self._values.get("python_layer_version_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda_python.PythonLayerVersionProps], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''User provided props to override the default props for the SQS queue.

        :default: - Default props are used
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def starter_existing_lambda_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        '''Existing instance of Lambda Function object that starts execution, if this is set then the lambdaFunctionProps is ignored.

        :default: - None
        '''
        result = self._values.get("starter_existing_lambda_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Function], result)

    @builtins.property
    def starter_lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        '''User provided props to override the default props for the Lambda function that starts execution.

        :default: - Default props are used
        '''
        result = self._values.get("starter_lambda_function_props")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FunctionProps], result)

    @builtins.property
    def table_permissions(self) -> typing.Optional[builtins.str]:
        '''Optional table permissions to grant to the Lambda function.

        One of the following may be specified: "All", "Read", "ReadWrite", "Write".

        :default: - Read/write access is given to the Lambda function if no value is specified.
        '''
        result = self._values.get("table_permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SfnRedshiftTaskerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RedshiftTargetProps",
    "SfnRedshiftTasker",
    "SfnRedshiftTaskerProps",
]

publication.publish()
