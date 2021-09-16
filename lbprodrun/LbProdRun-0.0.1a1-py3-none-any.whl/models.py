###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json
from pathlib import Path
from typing import Optional

import typer
from pydantic import BaseModel, ValidationError
from typer import colors as c


class JobSpecV1(BaseModel):
    class Application(BaseModel):
        name: str
        version: str
        data_pkgs: list[str] = []
        binary_tag: str = "best"
        event_timeout: Optional[float]
        number_of_processors: int = 1

    application: Application

    class Options(BaseModel):
        files: list[str]
        format: Optional[str]
        gaudi_extra_options: Optional[str]
        processing_pass: Optional[str]

    options: Options

    class Input(BaseModel):
        files: Optional[list[str]]
        xml_summary_file: Optional[str]
        xml_file_catalog: Optional[str]
        run_number: Optional[int]
        tck: Optional[str]
        n_of_events: int = -1
        first_event_number: Optional[int]

    input: Input = Input()

    class Output(BaseModel):
        prefix: str
        types: list[str]
        histogram_file: Optional[str]

    output: Output

    class DBTags(BaseModel):
        dddb_tag: Optional[str]
        conddb_tag: Optional[str]
        dq_tag: Optional[str]

    db_tags: DBTags = DBTags()


KNOWN_SPECS = {
    1: JobSpecV1,
}


def read_jobspec(spec_file: Path):
    try:
        data = json.loads(spec_file.read_text())
    except json.JSONDecodeError as e:
        typer.secho(f"Failed to parse {spec_file} as JSON with error {e}", fg=c.RED)
        raise typer.Exit(101) from e

    try:
        spec_version = data.pop("spec_version")
    except KeyError as e:
        typer.secho(f"'spec_version' is not specified in {spec_file}", fg=c.RED)
        raise typer.Exit(101) from e

    try:
        JobSpecClass = KNOWN_SPECS[spec_version]
    except KeyError as e:
        typer.secho(f"Unknown spec_version {spec_version!r}", fg=c.RED)
        raise typer.Exit(101) from e

    try:
        return JobSpecClass.parse_obj(data)
    except ValidationError as e:
        errors = e.errors()
        typer.secho(
            f"Found {len(errors)} error{'s' if len(errors) > 1 else ''} "
            f"when validating {spec_file}:",
            fg=c.RED,
        )
        for error in e.errors():
            if error["type"] == "value_error.missing":
                message = f"Field {'.'.join(error['loc'])!r} is required"
            else:
                message = error["msg"]
            typer.secho(f"  * {message}", fg=c.RED)
        raise typer.Exit(101) from e
