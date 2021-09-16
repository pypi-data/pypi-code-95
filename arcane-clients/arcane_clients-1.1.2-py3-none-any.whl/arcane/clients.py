import requests
import backoff
import json

from arcane.requests import call_get_route, request_service
from arcane.core import UserRightsEnum, RightsLevelEnum, Account, Campaign
from typing import List, Union


def get_client(
    client_id: str,
    CLIENTS_URL: str,
    firebase_api_key: str,
    auth_enabled=True,
    credentials_path: str = None,
    uid: str = None
):
    url = f"{CLIENTS_URL}/api/clients?client_id={client_id}"
    client_list = call_get_route(
        url,
        firebase_api_key,
        claims={'features_rights': {UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
        auth_enabled=auth_enabled,
        credentials_path=credentials_path,
        uid=uid
    )
    return client_list[0] if len(client_list) > 0 else None


def get_client_old(
    client_id: str,
    CLIENTS_URL: str,
    firebase_api_key: str,
    auth_enabled=True,
    credentials_path: str = None,
    uid: str = None
):
    url = f"{CLIENTS_URL}/api/clients/old?client_id={client_id}"
    old_client_list = call_get_route(
        url,
        firebase_api_key,
        claims={'features_rights': {UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
        auth_enabled=auth_enabled,
        credentials_path=credentials_path,
        uid=uid
    )
    return old_client_list[0] if len(old_client_list) > 0 else None


def get_user(
    user_id: str,
    UTILS_SERVICES_URL: str,
    firebase_api_key: str,
    auth_enabled=True,
    credentials_path: str = None,
    uid: str = None
):
    response = request_service('GET',
                               url=f"{UTILS_SERVICES_URL}/api/users?user_id={user_id}",
                               firebase_api_key=firebase_api_key,
                               claims={'features_rights': {UserRightsEnum.USERS: RightsLevelEnum.VIEWER}},
                               uid=uid,
                               auth_enabled=auth_enabled,
                               retry_decorator=backoff.on_exception(
                                        backoff.expo,
                                        (ConnectionError, requests.HTTPError, requests.Timeout),
                                        3
                                    ),
                               credentials_path=credentials_path)
    response.raise_for_status()
    user_list = json.loads(response.content.decode("utf8"))
    return user_list[0] if len(user_list) > 0 else None


def get_user_list_by_client_right(
    client_right_id: str, UTILS_SERVICES_URL: str,
    firebase_api_key: str,
    auth_enabled=True,
    credentials_path: str = None,
    uid: str = None
):
    """ get list of users by client right """
    url = f"{UTILS_SERVICES_URL}/api/users"
    users = call_get_route(
        url,
        firebase_api_key,
        claims={
            'features_rights': {
                UserRightsEnum.USERS: RightsLevelEnum.VIEWER,
                UserRightsEnum.AMS_GTP: RightsLevelEnum.EDITOR
            }
        },
        auth_enabled=auth_enabled,
        credentials_path=credentials_path,
        uid=uid
    )

    return [
        user for user in users
        if (
            user.authorized_clients and
            len(user.authorized_clients) != 0 and
            (client_right_id in user.authorized_clients or user.authorized_clients[0] == 'all')
        )
    ]


def get_scope_content(
    scope_definition_id: Union[int, str],
    client_id: str,
    CLIENTS_URL: str,
    firebase_api_key: str,
    auth_enabled=True,
    credentials_path: str = None,
    uid: str = None
) -> List[Account]:
    if scope_definition_id is not None:
        url = f"{CLIENTS_URL}/api/scopes/{scope_definition_id}"
        scope = call_get_route(
            url,
            firebase_api_key,
            claims={'features_rights': {
                UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
            auth_enabled=auth_enabled,
            credentials_path=credentials_path,
            uid=uid
        )
    scope_content = scope['scope_content']
    return [
        Account(
            account_id=account['account_id'],
            account_type=account['account_type'],
            account_name=account['account_name'],
            campaigns=[Campaign(**campaign)
                       for campaign in account['campaigns']]
        ) for account in scope_content]


def get_recipients_from_scope(
    scope_definition_id: Union[int, str],
    client_id: str,
    CLIENTS_URL: str,
    UTILS_SERVICES_URL: str,
    firebase_api_key: str,
    auth_enabled=True,
    credentials_path: str = None,
    uid: str = None
) -> List[str]:
    url = f"{CLIENTS_URL}/api/scopes?scope_id={scope_definition_id}"
    scope = call_get_route(
        url,
        firebase_api_key,
        claims={'features_rights': {
            UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
        auth_enabled=auth_enabled,
        credentials_path=credentials_path,
        uid=uid
    )
    recipients = scope[0].get('owners', [])
    return recipients


def get_name_from_scope(
    scope_definition_id: Union[int, str],
    CLIENTS_URL: str,
    firebase_api_key: str,
    auth_enabled=True,
    credentials_path: str = None,
    uid: str = None
) -> str:
    url = f"{CLIENTS_URL}/api/scopes?scope_id={scope_definition_id}"
    scope = call_get_route(
        url,
        firebase_api_key,
        claims={'features_rights': {
            UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
        auth_enabled=auth_enabled,
        credentials_path=credentials_path,
        uid=uid
    )
    name = scope[0].get('name', '')
    return name
