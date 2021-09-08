import logging

logging.basicConfig()
LOG = logging.getLogger("AclBindApi")
LOG.setLevel(logging.DEBUG)


def get_credentials_for(environment, credential_type):
    from dbaas_credentials.models import Credential
    cred = Credential.objects.filter(
        integration_type__type=credential_type, environments=environment
    )

    if not cred.exists():
        return None
    
    return cred[0]


def get_description_from_tupple(status_tuple, status):
    return {_tuple[0]: _tuple[1] for _tuple in status_tuple}.get(status, None)

def oi():
    print("ok")
