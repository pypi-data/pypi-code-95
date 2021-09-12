from django.conf import settings
from fido2.client import ClientData
from fido2.ctap2 import AttestedCredentialData, AttestationObject, AuthenticatorData
from fido2.server import Fido2Server, PublicKeyCredentialRpEntity
from fido2.utils import websafe_decode, websafe_encode


def get_server():
    rp = PublicKeyCredentialRpEntity(settings.FIDO_SERVER_ID, settings.MFA_SERVER_NAME)
    return Fido2Server(rp)


def get_user_credentials(user):
    credentials = []
    for uk in user.userkey_set.filter(key_type="FIDO2"):
        credentials.append(
            AttestedCredentialData(websafe_decode(uk.properties.get("device")))
        )
    return credentials


def generate_fido2_registration(user):
    """Returns registration_data, state"""
    server = get_server()
    return server.register_begin(
        {
            "id": str(user.pk).encode(),
            "name": user.get_full_name(),
            "displayName": user.get_username(),
        },
        get_user_credentials(user),
    )


def fido2_complete_registration(client_data_json, attestation_object, fido_state):
    """Returns properties"""
    client_data = ClientData(client_data_json)
    att_obj = AttestationObject(attestation_object)
    server = get_server()
    auth_data = server.register_complete(
        fido_state,
        client_data,
        att_obj,
    )
    encoded = websafe_encode(auth_data.credential_data)
    return {
        "device": encoded,
        "type": att_obj.fmt,
    }


def fido2_begin_authenticate(user):
    """Returns auth_data, fido_state"""
    server = get_server()
    credentials = get_user_credentials(user)
    return server.authenticate_begin(credentials)


def fido2_complete_authenticate(
    user, credential_id, client_data_json, authenticator_data, signature, fido_state
):
    server = get_server()
    credentials = get_user_credentials(user)

    client_data = ClientData(client_data_json)
    auth_data = AuthenticatorData(authenticator_data)

    cred = server.authenticate_complete(
        fido_state,
        credentials,
        credential_id,
        client_data,
        auth_data,
        signature,
    )

    keys = user.userkey_set.filter(key_type="FIDO2")
    for key in keys:
        if (
            AttestedCredentialData(
                websafe_decode(key.properties["device"])
            ).credential_id
            == cred.credential_id
        ):
            return key