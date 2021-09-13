from typing import Any

import boto3
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from jwt.algorithms import RSAAlgorithm


class KMSAlgorithm(RSAAlgorithm):
    region = "ap-northeast-1"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.hash_alg = RSAAlgorithm.SHA256

    def get_client(self) -> boto3.session.Session.client:
        client = boto3.client("kms", self.region)
        return client

    def prepare_key(self, key: str) -> str:
        return key

    def sign(self, msg: bytes, key: str) -> bytes:
        client = self.get_client()
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.sign
        # `Message` should be bytes, as well as the `resp["Signature"]`
        resp = client.sign(
            KeyId=key, Message=msg, SigningAlgorithm="RSASSA_PKCS1_V1_5_SHA_256"
        )
        return resp["Signature"]  # type: ignore

    def verify(self, msg: str, key: bytes, sig: str) -> bool:
        real_key = load_pem_public_key(key)
        return super().verify(msg, real_key, sig)  # type: ignore
