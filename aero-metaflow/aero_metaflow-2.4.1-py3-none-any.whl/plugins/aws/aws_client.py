# File modified under the Apache Licence 2.0 spec. Modified by Aero Technologies.
# Altered how profile is set based on local/remote execution
import logging
import os
from pathlib import Path
from metaflow.metaflow_config import AERO_ID_TOKEN, AERO_IDENTITY_POOL, AERO_PROVIDER

def get_credentials():
    import boto3

    client = boto3.client('cognito-identity', region_name='eu-west-1')

    try:
        identity_response = client.get_id(
                                IdentityPoolId=AERO_IDENTITY_POOL, 
                                Logins = {AERO_PROVIDER: AERO_ID_TOKEN})
    except Exception as e:
        raise Exception("Credentials have expired, please run 'aero account login' again")

    identity_id = identity_response['IdentityId']

    resp = client.get_credentials_for_identity(
                    IdentityId=identity_id,
                    Logins={AERO_PROVIDER: AERO_ID_TOKEN})

    secret_key = resp['Credentials']['SecretKey']
    access_key = resp['Credentials']['AccessKeyId']
    session_token = resp['Credentials']['SessionToken']
    expiry = resp['Credentials']['Expiration']

    return {
        "access_key": access_key,
        "secret_key": secret_key,
        "token": session_token,
        "expiry_time": expiry.isoformat()
    }

def create_client_credentials():
    import boto3
    from botocore.credentials import RefreshableCredentials
    from botocore.session import get_session

    # Catch if running on Batch
    if 'METAFLOW_INPUT_PATHS_0' in os.environ or 'MANAGED_BY_AWS' in os.environ:
        return boto3.session.Session(
            region_name='eu-west-1'
        )

    session_credentials = RefreshableCredentials.create_from_metadata(
        metadata = get_credentials(),
        refresh_using = get_credentials,
        method = 'sts-assume-role'
    )

    session = get_session()
    session._credentials = session_credentials
    autorefresh_session = boto3.Session(
        botocore_session=session,
        region_name='eu-west-1'
    )

    try:
        sts = autorefresh_session.client('sts')
        sts.get_caller_identity()
    except:
        raise Exception("Credentials have expired, please run 'aero account login' again")

    return autorefresh_session

AWS_SESSION = create_client_credentials()

def get_aws_client(module, with_error=False, params={}):
    from metaflow.exception import MetaflowException  

    try:
        import boto3
        from botocore.exceptions import ClientError
    except (NameError, ImportError):
        raise MetaflowException(
            "Could not import module 'boto3'. Install boto3 first.")

    if with_error:
        return AWS_SESSION.client(module, **params), ClientError
    return AWS_SESSION.client(module, **params)
