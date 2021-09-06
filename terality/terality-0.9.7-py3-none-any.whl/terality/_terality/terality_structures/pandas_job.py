from functools import partial
from typing import Optional, Any

from terality_serde import apply_func_on_object_recursively
from common_client_scheduler import (
    ComputationResponse,
    PandasFunctionRequest,
    TeralityInternalError,
)

# from terality.exceptions import TeralityNotFoundError
from .. import global_client, encode, decode
from ..awscredshelper import AwsCredentialsFetcher


def call_pandas_function(
    function_type: str,
    function_prefix: Optional[str],
    function_name: str,
    *args,
    **kwargs,
) -> Any:
    fetcher = AwsCredentialsFetcher()
    args = [] if args is None else args
    args_encoded = apply_func_on_object_recursively(args, partial(encode, fetcher, function_name))
    kwargs = {} if kwargs is None else kwargs
    kwargs_encoded = apply_func_on_object_recursively(
        kwargs, partial(encode, fetcher, function_name)
    )
    job = PandasFunctionRequest(
        function_type=function_type,
        function_accessor=function_prefix,
        function_name=function_name,
        args=args_encoded,
        kwargs=kwargs_encoded,
    )

    response = global_client().poll_for_answer("compute", job)

    if isinstance(response, ComputationResponse):
        result = response.result
        result = apply_func_on_object_recursively(result, partial(decode, fetcher))

        # Handle in-place modification of data structures.
        # NOTE: Because `inplace` is only available on methods, the first argument is guaranteed to be positional
        # (`self`).
        if response.inplace:
            from terality._terality.terality_structures.structure import (
                Struct,
            )  # break cyclic import

            if not isinstance(args[0], Struct):
                raise TeralityInternalError(
                    "Received in-place response but the target is not a data structure"
                )
            target = args[0]
            if not isinstance(result, Struct):
                raise TeralityInternalError(
                    "Received in-place response but the result is not a data structure"
                )
            # noinspection PyProtectedMember
            target._mutate(result)
            result = None
        return result

    raise TeralityInternalError(f"Received unexpected response {response}")
