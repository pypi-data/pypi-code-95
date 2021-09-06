"""Tests of getting ABI from different sources."""
import os
import pytest

from evmscript_parser.core.decode import decode_function_call
from evmscript_parser.core.ABI import get_cached_combined
from evmscript_parser.core.ABI.storage import CachedStorage

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
INTERFACES = os.path.join(CUR_DIR, 'interfaces')


@pytest.fixture(scope='module')
def abi_storage(api_key: str) -> CachedStorage:
    """Return prepared abi storage."""
    return get_cached_combined(
        api_key, 'goerli', INTERFACES
    )


def test_etherscan_api(abi_storage, abi_positive_example):
    """Run tests for getting ABI from Etherscan API."""
    interface_name, contract, sign, name = abi_positive_example
    assert decode_function_call(
        contract, sign,
        '', abi_storage,
        combined_key=True, interface_name=interface_name
    ).function_name == name
    assert (contract, interface_name) in abi_storage
