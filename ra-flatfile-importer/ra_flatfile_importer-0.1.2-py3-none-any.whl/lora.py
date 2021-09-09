#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import cast
from typing import TextIO
from typing import Type

import click
from pydantic import AnyHttpUrl
from ra_utils.async_to_sync import async_to_sync
from raclients.lora import ModelClient
from ramodels.base import RABase
from tqdm import tqdm

from .lora_flatfile_gen import generate_lora_flatfile
from .lora_flatfile_model import concat_chunk
from .lora_flatfile_model import LoraFlatFileFormatImport
from .util import model_validate_helper
from .util import takes_json_file
from .util import validate_url


LoraObj = Type[RABase]


def lora_validate_helper(json_file: TextIO) -> LoraFlatFileFormatImport:
    return cast(
        LoraFlatFileFormatImport,
        model_validate_helper(LoraFlatFileFormatImport, json_file),
    )


@click.group()
def lora() -> None:
    """Lora Flatfile importer.

    Used to validate and load flatfile data (JSON) into LoRa.
    """
    pass


@lora.command()
@takes_json_file
def validate(json_file: TextIO) -> None:
    """Validate the provided JSON file."""
    lora_validate_helper(json_file)


@lora.command()
@click.option(
    "--indent", help="Pass 'indent' to json serializer", type=click.INT, default=None
)
def schema(indent: int) -> None:
    """Generate JSON schema for valid files."""
    click.echo(LoraFlatFileFormatImport.schema_json(indent=indent))


@lora.command()
@click.option(
    "--mox-url",
    default="http://localhost:8080",
    show_default=True,
    callback=validate_url,
    help="Address of the MOX host",
)
@takes_json_file
@async_to_sync
async def upload(json_file: TextIO, mox_url: AnyHttpUrl) -> None:
    """Validate the provided JSON file and upload its contents."""
    flatfilemodel = lora_validate_helper(json_file)

    client = ModelClient(base_url=mox_url)
    async with client.context():
        for chunk in tqdm(flatfilemodel, desc="Filechunks", unit="chunk"):
            objs = list(concat_chunk(chunk))
            if objs:
                await client.load_lora_objs(objs)


@lora.command()
@click.option(
    "--name",
    help="Name of the root organization",
    required=True,
)
@click.option(
    "--indent", help="Pass 'indent' to json serializer", type=click.INT, default=None
)
def initialize(name: str, indent: int) -> None:
    """Generate LoRa initializer file."""
    flatfile = generate_lora_flatfile(name)
    click.echo(flatfile.json(indent=indent))


@lora.command()
@click.option(
    "--name",
    help="Name of the root organization",
    required=True,
)
@click.option(
    "--indent", help="Pass 'indent' to json serializer", type=click.INT, default=None
)
def generate(name: str, indent: int) -> None:
    """Generate LoRa fixture."""
    flatfile = generate_lora_flatfile(name, dummy_classes=True)
    click.echo(flatfile.json(indent=indent))
