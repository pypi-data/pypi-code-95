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
import os
import shlex
from pathlib import Path
from pprint import pformat

import typer

from .models import read_jobspec


def run_job(spec_file: Path, dry_run=False, verbose=False):
    job_spec = read_jobspec(spec_file)
    if verbose:
        typer.secho("Expanded spec file as:", fg=typer.colors.GREEN)
        typer.secho(pformat(job_spec.dict()))
    prod_conf_fn = Path(f"prodConf_{job_spec.output.prefix}.py")
    write_prod_conf_options(job_spec, prod_conf_fn, verbose=verbose)
    execute(job_spec, prod_conf_fn, dry_run=dry_run)


def write_prod_conf_options(job_spec, path: Path, verbose=False):
    """Write an options file for the ProdConf data package"""
    data = {
        "Application": job_spec.application.name,
        "AppVersion": job_spec.application.version,
        "OptionFormat": job_spec.options.format,
        "InputFiles": job_spec.input.files,
        "OutputFilePrefix": job_spec.output.prefix,
        "OutputFileTypes": job_spec.output.types,
        "XMLSummaryFile": job_spec.input.xml_summary_file,
        "XMLFileCatalog": job_spec.input.xml_file_catalog,
        "HistogramFile": job_spec.output.histogram_file,
        "DDDBTag": job_spec.db_tags.dddb_tag,
        "CondDBTag": job_spec.db_tags.conddb_tag,
        "DQTag": job_spec.db_tags.dq_tag,
        "NOfEvents": job_spec.input.n_of_events,
        "RunNumber": job_spec.input.run_number,
        "FirstEventNumber": job_spec.input.first_event_number,
        "TCK": job_spec.input.tck,
        "ProcessingPass": job_spec.options.processing_pass,
    }

    lines = ["from ProdConf import ProdConf", ""]
    lines += ["ProdConf("]
    lines += [f"    {k}={v!r}," for k, v in data.items() if v is not None]
    lines += [")"]
    string = "\n".join(lines)

    if verbose:
        typer.secho(f"Going to write in {path}", fg=typer.colors.GREEN)
        typer.secho(string)
    path.write_text(string)


def execute(job_spec, prod_conf_fn, dry_run=False):
    typer.secho(
        f"Executing application {job_spec.application.name} "
        f"{job_spec.application.version} for binary tag configuration "
        f"{job_spec.application.binary_tag}"
    )

    command = ["lb-run"]
    command += ["--siteroot=/cvmfs/lhcb.cern.ch/lib/"]
    command += ["-c", f"{job_spec.application.binary_tag}"]

    for ep in job_spec.application.data_pkgs:
        command += [f"--use={ep}"]
    command += ["--use=ProdConf"]

    app = job_spec.application.name
    if job_spec.application.version:
        app += "/" + job_spec.application.version
    command += [app]
    command += _make_gaudirun_command(job_spec, prod_conf_fn)

    typer.secho("Executing command:", fg="green")
    typer.secho(shlex.join(command))
    if not dry_run:
        os.execvpe(command[0], command, _prepare_env(job_spec))


def _make_gaudirun_command(job_spec, prod_conf_fn):
    command = ["gaudirun.py", "-T"]
    if job_spec.application.number_of_processors > 1:
        command += ["--ncpus", f"{job_spec.application.number_of_processors}"]
    command += job_spec.options.files
    command += [str(prod_conf_fn)]
    if job_spec.options.gaudi_extra_options:
        extra_options_path = Path("gaudi_extra_options.py")
        extra_options_path.write_text(job_spec.options.gaudi_extra_options)
        command += [extra_options_path]
    return command


def _prepare_env(job_spec):
    """Get a dictionary containing the environment that should be used for the job"""
    env = os.environ.copy()
    # Versions of Brunel used for 2018 data use XGBoost which uses OpenMP to
    # provide parallelism and automatically spawns one thread for each CPU.
    # Use OMP_NUM_THREADS to force it to only use one thread
    env["OMP_NUM_THREADS"] = str(job_spec.application.number_of_processors)
    return env
