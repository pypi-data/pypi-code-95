import os
from typing import List

from sshpubkeys import SSHKey as SSHPubKey

from openapi_client.models import ResponseSSHKeyInfo
from openapi_client.models.ssh_key_create_api_payload import SSHKeyCreateAPIPayload
from savvihub import vessl_api


def list_ssh_keys() -> List[ResponseSSHKeyInfo]:
    return vessl_api.s_sh_key_list_api().ssh_keys


def create_ssh_key(key_path: str, key_name: str) -> ResponseSSHKeyInfo:
    with open(key_path, "r") as f:
        public_key = f.read()

    ssh_key = SSHPubKey(public_key, strict=True)
    ssh_key.parse()  # May raise InvalidKeyError, NotImplementedError

    return vessl_api.s_sh_key_create_api(
        ssh_key_create_api_payload=SSHKeyCreateAPIPayload(
            filename=os.path.basename(key_path),
            name=key_name,
            public_key=public_key,
        )
    )


def delete_ssh_key(key_id: int) -> object:
    return vessl_api.s_sh_key_delete_api(ssh_key_id=key_id)
