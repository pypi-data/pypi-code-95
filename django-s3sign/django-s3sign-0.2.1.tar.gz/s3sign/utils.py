import logging
from botocore.config import Config
from botocore.exceptions import ClientError


s3_config = Config(
    signature_version='s3v4',
    s3={'addressing_style': 'path'},
)


def create_presigned_url(s3_client, bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    From: https://boto3.amazonaws.com/v1/documentation/api/latest/
                             guide/s3-presigned-urls.html

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to
      remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name,
                    'Key': object_name},
            ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def create_presigned_url_expanded(
        s3_client, client_method_name, method_parameters=None,
        expiration=3600, http_method=None):
    """Generate a presigned URL to invoke an S3.Client method

    Not all the client methods provided in the AWS Python SDK are
    supported.

    :param client_method_name: Name of the S3.Client method, e.g.,
    'list_buckets'

    :param method_parameters: Dictionary of parameters to send to
    the method

    :param expiration: Time in seconds for the presigned URL to
    remain valid

    :param http_method: HTTP method to use (GET, etc.)
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 client method

    try:
        response = s3_client.generate_presigned_url(
            ClientMethod=client_method_name,
            Params=method_parameters,
            ExpiresIn=expiration,
            HttpMethod=http_method)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
