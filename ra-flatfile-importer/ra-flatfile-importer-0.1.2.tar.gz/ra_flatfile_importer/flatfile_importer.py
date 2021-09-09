#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
import click

from ra_flatfile_importer.lora import lora
from ra_flatfile_importer.mo import mo


@click.group()
def cli() -> None:
    """Flatfile importer.

    Used to validate and load flatfile data (JSON) into OS2mo/LoRa.
    """
    pass


cli.add_command(lora)
cli.add_command(mo)


if __name__ == "__main__":
    cli(auto_envvar_prefix="FLATFILE_IMPORTER")
