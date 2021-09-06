"""
Base class for ABI hierarchy.
"""
import logging
from abc import ABC, abstractmethod

from typing import Tuple

from evmscript_parser.core.exceptions import (
    ABILocalFileNotExisted, ABIEtherscanNetworkError, ABIEtherscanStatusCode
)

from .storage import (
    ABIKey, ABI, ABI_T,
    CachedStorage
)
from .utilities.etherscan import (
    get_abi, get_implementation_address, DEFAULT_NET
)
from .utilities.local import (
    get_all_files, read_abi_from_json
)
from .utilities.processing import (
    index_function_description
)


# ============================================================================
# ============================== ABI =========================================
# ============================================================================


class ABIProvider(ABC):
    """
    Base class for ABI providers.
    """

    def __call__(self, key: ABIKey) -> ABI_T:
        """Return ABI for key."""
        return self.get_abi(key)

    @abstractmethod
    def get_abi(self, key: ABIKey) -> ABI_T:
        """Return ABI."""
        pass


class ABIProviderEtherscanAPI(ABIProvider):
    """
    Getting ABI from Etherscan API.
    """

    def __init__(self, api_key: str, net: str = DEFAULT_NET):
        """Prepare provider with concrete APi key and net."""
        self._api_key = api_key
        self._net = net

        self._retries = 3

    def get_abi(self, key: ABIKey) -> ABI_T:
        """
        Return ABI from Etherscan API.

        :param key: str, address of contract.
        :return: abi
        :exception ABIEtherscanNetworkError in case of error at network layer.
        :exception ABIEtherscanStatusCode in case of error in api calls.
        """
        abi = get_abi(
            self._api_key, key, self._net, self._retries
        )

        proxy_type_code = 1
        implementation_code = 2

        status = 0
        for entry in abi:
            name = entry.get('name', 'unknown')

            if name == 'proxyType':
                status |= proxy_type_code
            elif name == 'implementation':
                status |= implementation_code

            if status == 3:
                logging.debug(
                    f'Proxy punching for {key} '
                    f'in {self._net}'
                )
                key = get_implementation_address(
                    key, abi, self._net
                )
                abi = get_abi(
                    self._api_key, key, self._net, self._retries
                )
                break

        return abi


class ABIProviderLocalDirectory(ABIProvider):
    """
    Getting ABI from local files of interfaces.
    """

    def __init__(self, interfaces_directory: str):
        """Prepare mapping from files names to paths."""
        self._interfaces = get_all_files(
            interfaces_directory, '*.json'
        )

    def get_abi(self, key: ABIKey) -> ABI_T:
        """
        Return ABI from interface file.

        :param key: str, name of interface file.
        :return: abi
        :exception ABILocalFileNotExisted in case of interface file does not
                   exist.
        """
        if key in self._interfaces:
            return read_abi_from_json(self._interfaces[key])

        raise ABILocalFileNotExisted(key)


class ABIProviderCombined(
    ABIProviderEtherscanAPI, ABIProviderLocalDirectory
):
    """
    Combined getting ABI.

    Try to get ABI from Etherscan API.
    In case of failure, read ABI from local file.
    """

    def __init__(self, api_key: str, net: str, interfaces_directory: str):
        """Prepare instances of API and local files providers."""
        ABIProviderEtherscanAPI.__init__(self, api_key, net)
        ABIProviderLocalDirectory.__init__(self, interfaces_directory)

    def get_abi(self, key: Tuple[ABIKey, ABIKey]) -> ABI_T:
        """
        Return ABI.

        :param key: Tuple[str, str], pair of address of contract
                                     and interface file.
        :return: abi
        :exception ABILocalFileNotExisted in case of interface file does not
                   exist.
        """
        address, interface_name = key
        try:
            return ABIProviderEtherscanAPI.get_abi(self, address)
        except (ABIEtherscanNetworkError, ABIEtherscanStatusCode) as err:
            logging.debug(f'Fail with getting ABI from API: {str(err)}')
            return ABIProviderLocalDirectory.get_abi(self, interface_name)


class ABIProcessing:
    """
    Convert ABI to mapping from functions signatures to their descriptions.
    """

    def __call__(self, abi: ABI_T) -> ABI:
        """Convert ABI to mapping."""
        return ABI(raw=abi, func_storage=index_function_description(abi))


def get_cached_etherscan_api(
        api_key: str, net: str
) -> CachedStorage[ABIKey, ABI]:
    """Return prepared instance of CachedStorage with API provider."""
    provider = ABIProviderEtherscanAPI(api_key, net)
    processing = ABIProcessing()

    return CachedStorage(lambda x: processing(provider(x)))


def get_cached_local_interfaces(
        interfaces_directory: str
) -> CachedStorage[ABIKey, ABI]:
    """Return prepared instance of CachedStorage with local files provider."""
    provider = ABIProviderLocalDirectory(interfaces_directory)
    processing = ABIProcessing()

    return CachedStorage(lambda x: processing(provider(x)))


def get_cached_combined(
        api_key: str, net: str,
        interfaces_directory: str
) -> CachedStorage[Tuple[ABIKey, ABIKey], ABI]:
    """Return prepared instance of CachedStorage with combined provider."""
    provider = ABIProviderCombined(
        api_key, net, interfaces_directory
    )
    processing = ABIProcessing()

    return CachedStorage(lambda x: processing(provider(x)))
