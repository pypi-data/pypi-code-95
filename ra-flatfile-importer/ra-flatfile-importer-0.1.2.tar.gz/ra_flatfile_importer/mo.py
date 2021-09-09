#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import cast
from typing import TextIO

import click
from pydantic import AnyHttpUrl
from ra_utils.async_to_sync import async_to_sync
from ra_utils.headers import TokenSettings
from raclients.mo import ModelClient
from raclients.modelclientbase import common_session_factory
from tqdm import tqdm

from ra_flatfile_importer.mo_flatfile_gen import generate_mo_flatfile
from ra_flatfile_importer.mo_flatfile_model import concat_chunk
from ra_flatfile_importer.mo_flatfile_model import MOFlatFileFormatImport
from ra_flatfile_importer.util import model_validate_helper
from ra_flatfile_importer.util import takes_json_file
from ra_flatfile_importer.util import validate_url


def mo_validate_helper(json_file: TextIO) -> MOFlatFileFormatImport:
    return cast(
        MOFlatFileFormatImport, model_validate_helper(MOFlatFileFormatImport, json_file)
    )


@click.group()
def mo() -> None:
    """OS2mo Flatfile importer.

    Used to validate and load flatfile data (JSON) into OS2mo.
    """
    pass


@mo.command()
@takes_json_file
def validate(json_file: TextIO) -> None:
    """Validate the provided JSON file."""
    mo_validate_helper(json_file)


@mo.command()
@click.option(
    "--indent", help="Pass 'indent' to json serializer", type=click.INT, default=None
)
def schema(indent: int) -> None:
    """Generate JSON schema for valid files."""
    click.echo(MOFlatFileFormatImport.schema_json(indent=indent))


@mo.command()
@click.option(
    "--mo-url",
    default="http://localhost:5000",
    show_default=True,
    callback=validate_url,
    help="Address of the OS2mo host",
)
@takes_json_file
@async_to_sync
async def upload(json_file: TextIO, mo_url: AnyHttpUrl) -> None:
    """Validate the provided JSON file and upload its contents."""
    flatfilemodel = mo_validate_helper(json_file)

    client = ModelClient(
        base_url=mo_url,
        session_factory=common_session_factory(token_settings=TokenSettings()),
    )
    async with client.context():
        for chunk in tqdm(flatfilemodel, desc="Filechunks", unit="chunk"):
            objs = list(concat_chunk(chunk))
            if objs:
                await client.load_mo_objs(objs)


@mo.command()
@click.option(
    "--name",
    help="Name of the root organization",
    required=True,
)
@click.option(
    "--indent", help="Pass 'indent' to json serializer", type=click.INT, default=None
)
def generate(name: str, indent: int) -> None:
    """Generate OS2mo fixture."""
    flatfile = generate_mo_flatfile(name)
    click.echo(flatfile.json(indent=indent))
