import os
from test.conftest import USE_MOCK
from test.util import random_string

import pytest
from Crypto.PublicKey import RSA

import savvihub


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestSshKey:
    @pytest.mark.order(index=1)
    def test_create_ssh_key(self):
        key_path = "test/fixture/pubkey"
        key = RSA.generate(1024).publickey()
        with open(key_path, "wb") as f:
            f.write(key.exportKey("OpenSSH"))

        key_name = random_string()
        pytest.key = savvihub.create_ssh_key(key_path, key_name)
        os.remove(key_path)

    def test_list_ssh_keys(self):
        savvihub.list_ssh_keys()

    def test_delete_ssh_key(self):
        savvihub.delete_ssh_key(pytest.key.id)
