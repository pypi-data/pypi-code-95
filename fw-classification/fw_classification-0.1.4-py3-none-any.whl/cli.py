"""CLI interface to classification."""
import json
import typing as t
from functools import partial
from pathlib import Path

import typer
from dotty_dict import Dotty

from . import Profile, available_adapters, run_classification
from .adapters import Adapter
from .utils import configure_logging

app = typer.Typer(name="classify", add_completion=False)
red = partial(typer.style, fg=typer.colors.RED)
green = partial(typer.style, fg=typer.colors.GREEN)

path_opts = {"exists": True, "readable": True, "dir_okay": False, "resolve_path": True}
a_choices = "|".join(available_adapters.keys())


@app.callback()
def main(verbose: bool = False):
    """CLI interface to fw-classification."""
    configure_logging(verbose)


@app.command()
def validate(
    profile: Path = typer.Argument(
        ..., help="Path to YAML profile.", **path_opts  # type: ignore
    )
) -> None:
    """Validate the YAML profile at the specified path."""
    try:
        p_obj = Profile(profile, exit_on_error=False)
    except ValueError as e:
        typer.echo(red("Could not load profile:"))
        typer.echo(red(f"\t{e.args[0]}"))
        raise typer.Exit(code=1) from e
    else:
        if p_obj.errors:
            typer.echo(red("Found the following validation errors:"))
            for err in p_obj.errors:
                typer.echo(red(f"\t{err}"))
        else:
            typer.echo(
                green(f"Success! No errors found with the profile at {p_obj.path}")
            )


@app.command()
def run(
    profile: Path = typer.Argument(
        ..., help="Path to YAML profile.", **path_opts  # type: ignore
    ),
    in_file: Path = typer.Argument(
        ..., help="Path to input file.", **path_opts  # type: ignore
    ),
    out_file: t.Optional[Path] = typer.Option(
        None, "-o", "--out", help="Path to output."
    ),
    adapter: t.Optional[str] = typer.Option(
        None,
        "-a",
        "--adapter",
        help=(
            f"Adapter to use, choose from {a_choices} or pass in path to "
            "custom adapter"
        ),
    ),
):
    """Perform classification with the given profile on a file."""
    if adapter:
        if adapter in available_adapters:
            cls: t.Type[Adapter] = available_adapters[adapter]
            classifier = cls(in_file)
            out = classifier.classify(profile)
        else:
            out = Dotty({})
    else:
        i_dict = {}
        typer.echo("Loading input file.")
        with open(in_file, "r", encoding="utf-8") as fp:
            i_dict = json.load(fp)
        typer.echo("Running classification.")
        out = run_classification(profile, i_dict)
    if out_file:
        with open(out_file, "w", encoding="utf-8") as fp:
            json.dump(out.to_dict(), fp, indent=2)
        typer.echo(green(f"Success! Wrote output to {out_file}"))
    else:
        typer.echo(json.dumps(out, indent=2))


if __name__ == "__main__":  # pragma: no cover
    app()
