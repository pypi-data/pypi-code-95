from urllib.parse import urlparse

import click
from requests import PreparedRequest, RequestException

from . import utils
from .docker_utils import convert_host_abs_path_to_container, is_docker


def validate_target_url(
    ctx: click.core.Context, param: click.core.Parameter, raw_value: str
) -> str:
    try:
        netloc = urlparse(raw_value).netloc
    except ValueError as exc:
        raise click.UsageError("Invalid target URL") from exc
    if raw_value and not netloc:
        raise click.UsageError("Invalid target URL")
    return raw_value


def validate_schema(
    ctx: click.core.Context, param: click.core.Parameter, raw_value: str
) -> str:
    if "app" not in ctx.params:
        try:
            netloc = urlparse(raw_value).netloc
        except ValueError as exc:
            raise click.UsageError(
                "Invalid schema, must be a valid URL or file path."
            ) from exc
        if not netloc:
            mapped_file = _check_and_map_schema_file(raw_value)
            if not mapped_file:
                raise click.UsageError(_get_env_specific_schema_file_usage_error())
                # Click ends execution here
            return mapped_file
        else:
            _validate_url(raw_value)
    return raw_value


def _check_and_map_schema_file(filename: str) -> str:
    """Check if the schema file exists accounting for Docker volume mounts.
    Returns mapped schema file on success, AND empty string on error
    """
    if "\x00" in filename:
        return ""

    mapped_filename = convert_host_abs_path_to_container(filename)
    if not mapped_filename or not utils.file_exists(mapped_filename):
        return ""

    return mapped_filename


def _validate_url(value: str) -> None:
    try:
        PreparedRequest().prepare_url(value, {})  # type: ignore
    except RequestException as exc:
        raise click.UsageError(
            "Invalid schema, must be a valid URL or file path."
        ) from exc


def _get_env_specific_schema_file_usage_error() -> str:
    """Return an appropriate message based on the env - Docker or no Docker"""
    if is_docker():
        return "Invalid path for schema file. Please provide the absolute path on the Docker host."
    else:
        return "Invalid path for schema file."
