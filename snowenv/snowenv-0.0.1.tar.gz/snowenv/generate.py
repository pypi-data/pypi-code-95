import os
from pathlib import Path
from typing import Optional, Tuple

from .utils import shell

DEFAULT_KEY_PATH = Path.home() / ".ssh"


def _key_paths(name: str, target_dir=str(DEFAULT_KEY_PATH)) -> Tuple[Path, Path, Path]:
    path = Path(os.path.expanduser(target_dir))
    prv_path = path / f"{name}.p8"
    pub_path = path / f"{name}.pub"
    return (path, prv_path, pub_path)


def generate_key(name: str, target_dir: Optional[str] = None):
    """Generates private and public key files.

    Args:
        name (str): Name of the key.
        target_dir (str, optional): Target key target_directory. Defaults to ~/.ssh.
    """

    path, prv_path, pub_path = _key_paths(name, target_dir)

    if prv_path.is_file() != pub_path.is_file():
        raise ValueError(
            f"Found private OR public key only for {name} in {target_dir}, delete to re-generate"
        )

    os.makedirs(path, exist_ok=True)

    if not prv_path.is_file() and not pub_path.is_file():
        # Step 1: Generate the Private Key
        # https://docs.snowflake.com/en/user-guide/key-pair-auth.html#step-1-generate-the-private-key
        retcode = shell(
            f'openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out "{prv_path}" -nocrypt'
        )
        if retcode != 0:
            raise ValueError(f"Return code {retcode} received from openssl")

        # Step 2: Generate a Public Key
        # https://docs.snowflake.com/en/user-guide/key-pair-auth.html#step-2-generate-a-public-key
        retcode = shell(f'openssl rsa -in "{prv_path}" -pubout -out "{pub_path}"')
        if retcode != 0:
            raise ValueError(f"Return code {retcode} received from openssl")


def print_key_assign_info(name: str, user: str, target_dir: str = None):
    """Prints instructions on assigning key to your Snowflake account.

    Args:
        name (str): Name of the key.
        user (str): Snowflake user.
        target_dir (str, optional): Target key target_directory. Defaults to ~/.ssh.
    """
    _, _, pub_path = _key_paths(name, target_dir)

    with open(pub_path, "r", encoding="utf8") as f:
        pubkey = "".join(
            filter(
                lambda x: not x.startswith("-----"),
                map(
                    lambda x: x.replace("\n", ""),
                    f.readlines(),
                ),
            )
        )

    # Step 4: Assign the Public Key to a Snowflake User
    # https://docs.snowflake.com/en/user-guide/key-pair-auth.html#step-4-assign-the-public-key-to-a-snowflake-user
    print("Execute the following SQL in Snowflake console:\n")
    print(f"ALTER USER \"{user}\" SET RSA_PUBLIC_KEY='{pubkey}';\n")
