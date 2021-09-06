from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
import sys
from awsglue.job import Job
import boto3


class InvalidFileType(Exception):
    pass


def key_splitter(key: str):
    """
    Takes standard AWS Key, as outputted by boto3.client.list_objects_v2(),
    and splits the key into the filename + extension, and the file path.

    Arguments:
    key: str
        A key of the format path/to/file/filename.ext
    """
    key_list = key.split("/")
    filename = key_list.pop()
    key_list.pop()  # Drop extraction timestamp
    table_key = [s for s in key_list if "table_name=" in s]
    filetype = filename.split(".")[-1]
    filepath = "/".join(key_list) + "/"
    table_name = table_key[0].split("=")[-1]
    if filetype not in ["csv", "json", "jsonl"]:
        raise InvalidFileType(
            f"The filetype, {filetype} is not supported by this operation"
        )
    return filepath, table_name, filetype


def destination_cleaner(key: str, bucket: str, role_arn: str = None):
    """
    Takes standard AWS Key, as outputted by boto3.client.list_objects_v2(),
    and cleans any exact matches existing in another, separate bucket.

    Arguments:
    key: str
        A key of the format path/to/file/filename.ext
    bucket: str
        An AWS Bucket name
    role_arn:
        An optional ARN, if the bucket being cleared requires an assumed role.
    """
    if role_arn is not None:
        sts_client = boto3.client("sts")
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName="AssumedRoleSession1"
        )
        assume_creds = assumed_role_object["Credentials"]
        access_key_id = assume_creds["AccessKeyId"]
        secret_access_key = assume_creds["SecretAccessKey"]
        session_token = assume_creds["SessionToken"]
        s3 = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
        )
    else:
        s3 = boto3.client("s3")
    existence_check = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=key,
    )

    if existence_check["KeyCount"]:
        print(key + " already exists at destination, flushing...")
        s3.delete_object(Bucket=bucket, Key=key)
    else:
        print(key + " does not exist in destination!")


def dynamic_frame_to_glue_catalog(
    path: str,
    table_name: str,
    database_name: str,
    dynamic_frame: DynamicFrame,
    glue_context: GlueContext,
):
    """
    Adds a given Glue DynamicFrame to the Glue Catalog,
    by writing it out to the supplied path

    Arguments:
    path: str
        A S3 path of the format s3://path/to/file/
    table_name: str
        The desired name of the table
    database name: str
        The name of the database which the table is to appear in.
    dynamic_frame: DynamicFrame
        A Glue DynamicFrame, including partitioning info, to be written out.
    glue_context:
        An AWS GlueContext
    """
    print("Attempting to register to Glue Catalogue")
    try:
        sink = glue_context.getSink(
            connection_type="s3",
            path=path,
            enableUpdateCatalog=True,
            updateBehavior="UPDATE_IN_DATABASE",
            partitionKeys=["extraction_timestamp"],
        )
        sink.setFormat("glueparquet")
        sink.setCatalogInfo(catalogDatabase=database_name, catalogTableName=table_name)
        sink.writeFrame(dynamic_frame)
        print("Write out of file succeeded!")
    except Exception as e:
        print(f"Could not convert {path} to glue table, due to an error!")
        print(e)


def files_to_dynamic_frame(
    path: str,
    filetype: str,
    source_bucket: str,
    table_name: str,
    spark: SparkSession,
    glue_context: GlueContext,
):
    """
    Reads in files at a filepath, and transforms them into
    a partitioned DynamicFrame using Spark and Glue.

    Arguments:
    path: str
        A S3 path of the format path/to/file/, not including any "s3://" prefixes
    filetype: str
        A filetype, currently only of the format "csv" or "json/jsonl"
    source_bucket: str
        The name of AWS bucket in which the files are contained.
    table_name: str
        The name of the table to be constructed.
    spark: SparkSession
        A SparkSession to be used to construct a Dataframe,
        containing the partitioned data.
    glue_context:
        An AWS GlueContext
    """
    try:
        file_location = "s3://" + source_bucket + "/" + path
        if filetype == "csv":
            datasource = spark.read.load(
                path=file_location,
                format="csv",
                header="true",
            )
        else:
            datasource = spark.read.load(path=file_location, format="json")
        print(f"Successfully read files at {path} to Spark")

        dynamic_frame = DynamicFrame.fromDF(datasource, glue_context, table_name)
        return dynamic_frame
    except Exception as e:
        print(f"Could not convert {path} to dynamic_frame, due to an error!")
        print(e)


if __name__ == "__main__":
    args = getResolvedOptions(
        sys.argv, ["JOB_NAME", "source_bucket", "destination_bucket", "database_name"]
    )

    sc = SparkContext()
    glueContext = GlueContext(sc)
    job = Job(glueContext)
    job.init(args["JOB_NAME"], args)
    glueContext._jsc.hadoopConfiguration().set(
        "fs.s3.enableServerSideEncryption", "true"
    )
    glueContext._jsc.hadoopConfiguration().set(
        "fs.s3.canned.acl", "BucketOwnerFullControl"
    )
    spark = glueContext.spark_session

    print(
        f"Job name: {args['JOB_NAME']},",
        f"source_bucket: {args['source_bucket']},",
        f"destination_bucket: {args['destination_bucket']},",
        f"database_name: {args['database_name']},",
    )

    client = boto3.client("s3")
    print("Listing Objects")
    response = client.list_objects_v2(
        Bucket=args["source_bucket"],
        Prefix="data/",
    )
    if response["KeyCount"]:

        paths = {}

        for item in response["Contents"]:
            print(f"Found Key {item['Key']}, logging...")
            key = item["Key"]
            input_path, table_name, filetype = key_splitter(key=key)
            if input_path not in paths:
                paths[input_path] = {}
            paths[input_path]["filetype"] = filetype
            paths[input_path]["table_name"] = table_name
            destination_cleaner(key=key, bucket=args["destination_bucket"])

        for path in paths:
            desired_path = "s3://" + args["destination_bucket"] + "/" + path
            dynamic_frame = files_to_dynamic_frame(
                path=path,
                filetype=paths[path]["filetype"],
                source_bucket=args["source_bucket"],
                table_name=paths[path]["table_name"],
                glue_context=glueContext,
                spark=spark,
            )
            dynamic_frame_to_glue_catalog(
                path=desired_path,
                table_name=paths[path]["table_name"],
                database_name=args["database_name"],
                dynamic_frame=dynamic_frame,
                glue_context=glueContext,
            )
