from copy import Error
import secrets

import boto3
import os
import time

from data_engineering_pulumi_components.aws import CuratedBucket
from data_engineering_pulumi_components.pipelines import CuratedToAthenaDatabasePipeline
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ResourceOptions, export, FileAsset
from pulumi_aws.s3 import BucketObject
from pulumi_aws import Provider, ProviderAssumeRoleArgs

from tests_end_to_end.pulumi_context import TestInfrastructure
from tests_end_to_end.utils import empty_bucket_with_assumed_role

test_run_id = secrets.token_hex(3)

role_arn = os.environ["TEST_CURATION_ARN"]

sts_client = boto3.client("sts")
assumed_role_object = sts_client.assume_role(
    RoleArn=role_arn, RoleSessionName="AssumedRoleSession1"
)
assume_creds = assumed_role_object["Credentials"]
access_key_id = assume_creds["AccessKeyId"]
secret_access_key = assume_creds["SecretAccessKey"]
session_token = assume_creds["SessionToken"]

client = boto3.client(
    "s3",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    aws_session_token=session_token,
)
athena_client = boto3.client(
    "athena",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    aws_session_token=session_token,
)
glue_client = boto3.client(
    "glue",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    aws_session_token=session_token,
)
test_data_file_path = "test_files/test_dataset.csv"
test_data_file = FileAsset(os.path.join(os.path.dirname(__file__), test_data_file_path))


class AthenaExecutionFailure(Exception):
    pass


def crawlerStarter(name):
    try:
        glue_client.start_crawler(Name=name)
    except Error as e:
        print(e)
    # I'm leaving this in as a record of what was a mostly functional waiter
    # for the crawler. Will go back in another ticket and reinstate this over
    # the 500 second wait time.
    #
    # moderate delay to let it get going
    # time.sleep(40)
    # response = glue_client.get_crawler_metrics(CrawlerNameList=[name])
    # time_left = response["CrawlerMetricsList"][0]["TimeLeftSeconds"]
    # last_runtime = response["CrawlerMetricsList"][0]["LastRuntimeSeconds"]
    # wait_attempts = 0
    # while time_left > 0 and wait_attempts < 3:
    #     print(
    #         "Crawler is still running, with an estimated "
    #         + str(time_left)
    #         + " seconds to go!"
    #     )
    #     sleep_time = time_left + 5
    #     print("Sleeping for " + str(sleep_time))
    #     time.sleep(sleep_time)  # Give a 5 second buffer in-case nearly done
    #     wait_attempts += 1
    #     response = glue_client.get_crawler_metrics(CrawlerNameList=[name])
    #     time_left = response["CrawlerMetricsList"][0]["TimeLeftSeconds"]
    #     last_runtime = response["CrawlerMetricsList"][0]["LastRuntimeSeconds"]
    # if time_left == 0 and last_runtime != 0:
    #     print("Crawler has run! Waiting to allow stop")
    #     time.sleep(100)
    # else:
    #     print("Beware! Crawler could not finish before tests started!")


def athenaCompletionWaiter(client, query_id):
    status = client.get_query_execution(QueryExecutionId=query_id)
    state = status["QueryExecution"]["Status"]["State"]
    attempt_count = 1
    # Pulumi can execute the queries quick enough that the athena end may not
    # have finished. Athena doesn't supply waiters, so I've made a DIY one.
    try:
        while ((state == "QUEUED") or (state == "RUNNING")) and attempt_count < 5:
            time.sleep(5)
            attempt_count += 1
            status = athena_client.get_query_execution(QueryExecutionId=query_id)
            state = status["QueryExecution"]["Status"]["State"]
        if state != "SUCCEEDED":
            raise AthenaExecutionFailure
    except AthenaExecutionFailure:
        print(
            "Athena has not completed within 25 seconds,"
            + "finishing in state "
            + state
        )
    return state


def pulumi_program():
    tagger = Tagger(environment_name="test")
    provider = Provider(
        resource_name="dataAccount",
        region="eu-west-1",
        assume_role=ProviderAssumeRoleArgs(role_arn=role_arn),
    )
    curatedBucket = CuratedBucket(
        name=test_run_id, tagger=tagger, opts=ResourceOptions(provider=provider)
    )
    testObject = BucketObject(
        resource_name="test-bucket-file",
        key="data/database_name=test_data/table_name=test/test_dataset.csv",
        bucket=curatedBucket.name,
        source=test_data_file,
        opts=ResourceOptions(provider=provider),
    )
    testObject2 = BucketObject(
        resource_name="test-bucket-file-two",
        key="data/database_name=test_data/table_name=test_two/test_dataset.csv",
        bucket=curatedBucket.name,
        source=test_data_file,
        opts=ResourceOptions(provider=provider),
    )
    curatedToAthenaDBPipeline = CuratedToAthenaDatabasePipeline(
        name=test_run_id,
        curated_bucket=curatedBucket,
        tagger=tagger,
        provider=provider,
        opts=ResourceOptions(depends_on=[curatedBucket, testObject, testObject2]),
    )
    export("curated_bucket", curatedBucket.name)
    export("athena_database", curatedToAthenaDBPipeline._glueDataCrawler._database.name)


def test_raw_curated_to_athena_db():
    with TestInfrastructure(
        test_id=test_run_id, pulumi_program=pulumi_program, delete_on_exit=True
    ) as stack:
        curated_bucket = stack.up_results.outputs["curated_bucket"].value

        waiter = client.get_waiter("object_exists")
        try:
            waiter.wait(
                Bucket=curated_bucket,
                Key="data/database_name=test_data/table_name=test/test_dataset.csv",
                WaiterConfig={"Delay": 2, "MaxAttempts": 10},
            )
        except Exception as e:
            print("Could not find object")
            print(e)
            found = False
        else:
            found = True
        crawler_name = test_run_id + "-crawler"
        crawlerStarter(name=crawler_name)
        time.sleep(360)
        database_name = test_run_id
        response = athena_client.start_query_execution(
            QueryString=f"SHOW TABLES IN {database_name}",
            QueryExecutionContext={"Database": database_name},
            ResultConfiguration={
                "OutputLocation": "s3://" + curated_bucket + "/" + "temp/athena/output"
            },
        )
        query_id = response["QueryExecutionId"]
        athenaCompletionWaiter(client=athena_client, query_id=query_id)
        try:
            response = athena_client.get_query_results(QueryExecutionId=query_id)
            # This abomination is how you retrieve the name of the first table returned.
            # For reference, the first index is the index of the table, alphabetically
            # The second two are just to unlist a [[{Dictionary}]] with only one value
            # In effect, this is a request to go to the second row (skipping header row)
            # And then retrieve the first value of a nested list (the row)
            table_name = list(response["ResultSet"]["Rows"][0].values())[0][0][
                "VarCharValue"
            ]
        except Exception as e:
            print("Athena Query was Unsuccesful! Response is shown below.")
            print(response)
            print(e)
            table_name = "Athena Failure"
        database_bucket = test_run_id + "-athena-query-bucket"
        empty_bucket_with_assumed_role(
            curated_bucket, access_key_id, secret_access_key, session_token
        )
        empty_bucket_with_assumed_role(
            database_bucket, access_key_id, secret_access_key, session_token
        )
        # Destroys a database and all data therein, while the stack destroy
        # will fail if the database still has data, and so can't be relied on.
        response = glue_client.get_tables(DatabaseName=database_name)
        tables = []
        for table in response["TableList"]:
            tables.append(table["Name"])

        glue_client.batch_delete_table(
            DatabaseName=database_name, TablesToDelete=tables
        )
    assert found
    assert table_name == "data"
