from typing import Callable, NamedTuple, Optional

import jsonpickle
from jetpack.proto.runtime.v1alpha1 import remote_pb2


def encode_result(result) -> remote_pb2.RemoteCallResponse:
    response = remote_pb2.RemoteCallResponse()
    response.json_results = jsonpickle.encode(result)
    return response


def decode_result(response: remote_pb2.RemoteCallResponse):
    return jsonpickle.decode(response.json_results)


# FuncArgs is used by jsonpickle to capture the arguments to an RPC
# TODO: Consider using inspect.BoundArguments instead of defining our own type.
FuncArgs = NamedTuple(
    "FuncArgs", [("args", Optional[tuple]), ("kwargs", Optional[dict])]
)


def encode_args(args, kwargs) -> str:
    return jsonpickle.encode(FuncArgs(args=args, kwargs=kwargs))


def decode_args(encoded_args: str):
    func_args: FuncArgs = jsonpickle.decode(encoded_args)
    return func_args.args, func_args.kwargs
