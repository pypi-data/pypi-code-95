import os
import functools

from .ffi import track_event


def track_function(
    name="",
    type="",
    include_args=[],
    include_kwargs=[],
    include_return_value=False,
    include_env=[],
    metadata={},
    dispatch=False,
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            raised_exception = None

            event_metadata = metadata.copy()

            # Include specific args
            if include_args:
                # TODO should be {}?
                event_metadata["args"] = []
                for arg_index in include_args:
                    try:
                        event_metadata["args"][arg_index] = args[arg_index]
                    except IndexError as e:
                        pass
                        # logger.error(
                        #     f"Could not include arg {arg_index} in event metadata: {e}"
                        # )

            # Include specific kwargs
            if include_kwargs:
                event_metadata["kwargs"] = {}
                for kwarg_name in include_kwargs:
                    try:
                        event_metadata["kwargs"][kwarg_name] = kwargs[kwarg_name]
                    except KeyError as e:
                        pass
                        # logger.error(
                        #     f"Could not include kwarg {kwarg_name} in event metadata: {e}"
                        # )

            # Inlcude specific environment variables
            if include_env:
                event_metadata["env"] = {}
                for env_name in include_env:
                    if env_name in os.environ:
                        event_metadata["env"][env_name] = os.environ[env_name]

            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                raised_exception = e
                return_value = "Exception"

            if include_return_value:
                event_metadata["return_value"] = return_value

            slug = name or func.__name__

            track_event(
                slug=slug, type=type, metadata=event_metadata, dispatch=dispatch
            )

            if raised_exception:
                raise raised_exception

            return return_value

        return wrapper

    return decorator


def track_command(*args, **kwargs):
    if "dispatch" not in kwargs:
        kwargs["dispatch"] = True
    return track_function(type="command", *args, **kwargs)
