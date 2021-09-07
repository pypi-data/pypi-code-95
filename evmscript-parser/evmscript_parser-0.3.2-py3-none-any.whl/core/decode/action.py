"""
Decoding functions callings to human-readable format.
"""
import web3

from typing import Union, Tuple, Optional

from ..script_specification import HEX_PREFIX

from .structure import Call, FuncInput

from evmscript_parser.core.ABI.storage import (
    CachedStorage, ABI, ABIKey
)

# ============================================================================
# ================================= Decoding =================================
# ============================================================================

_CacheT = CachedStorage[Union[ABIKey, Tuple[ABIKey, ABIKey]], ABI]


def decode_function_call(
        contract_address: str, function_signature: str, call_data: str,
        abi_storage: _CacheT, combined_key: bool = False,
        interface_name: Optional[str] = None
) -> Optional[Call]:
    """
    Decode function call.

    :param contract_address: str, contract addres.
    :param function_signature: str, the first fourth bytes
                                    of function signature
    :param call_data: str, encoded call data.
    :param abi_storage: CachedStorage, storage of contracts ABI.
    :param combined_key: bool, use address and interface-name as tuple
                               or only address or name.
    :param interface_name: Optional[str],
    :return: Call, decoded description of function calling.
    """
    key = contract_address
    if combined_key:
        key = (key, interface_name)
    else:
        if interface_name is not None:
            key = interface_name

    abi = abi_storage[key]
    function_description = abi.func_storage.get(function_signature, None)

    if function_description is None:
        return function_description

    address = web3.Web3.toChecksumAddress(contract_address)
    contract = web3.Web3().eth.contract(
        address=address, abi=abi.raw
    )

    inputs_spec = function_description['inputs']

    if call_data.startswith(HEX_PREFIX):
        call_data = call_data[len(HEX_PREFIX):]

    _, decoded_inputs = contract.decode_function_input(
        f'{function_signature}{call_data}'
    )

    inputs = [
        FuncInput(
            inp['name'],
            inp['type'],
            decoded_inputs[inp['name']]
        )
        for inp in inputs_spec
    ]

    properties = {
        'constant': function_description.get(
            'constant', 'unknown'
        ),
        'payable': function_description.get(
            'payable', 'unknown'
        ),
        'stateMutability': function_description.get(
            'stateMutability', 'unknown'
        ),
        'type': function_description.get(
            'type', 'unknown'
        )
    }

    return Call(
        contract_address, function_signature,
        function_description.get('name', 'unknown'), inputs,
        properties, function_description['outputs']
    )
