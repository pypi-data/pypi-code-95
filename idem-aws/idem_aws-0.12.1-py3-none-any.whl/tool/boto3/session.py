import boto3.session
import botocore.session


USE_SHARED_BOTOCORE_SESSION = object()


def __init__(hub):
    # Create a single session for everything else to be run from
    hub.tool.boto3.SESSION = botocore.session.Session()


def get(
    hub, botocore_session: botocore.session.Session = USE_SHARED_BOTOCORE_SESSION
) -> boto3.session.Session:
    """
    Get a boto3 session that uses the universal botocore session
    """
    if botocore_session == USE_SHARED_BOTOCORE_SESSION:
        return boto3.session.Session(botocore_session=hub.tool.boto3.SESSION)
    else:
        return boto3.session.Session(botocore_session=botocore_session)
