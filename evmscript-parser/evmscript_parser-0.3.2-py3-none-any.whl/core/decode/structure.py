"""
Description of function calling as structure.
"""
from dataclasses import dataclass
from typing import List, Any, Dict, Optional


@dataclass
class FuncInput:
    """
    Single function input
    """

    name: str
    type: str
    value: Any


@dataclass
class Call:
    """
    Single function call
    """

    contract_address: str
    function_signature: str
    function_name: str
    inputs: List[FuncInput]
    properties: Dict[str, Any]
    outputs: Optional[List[Any]]
