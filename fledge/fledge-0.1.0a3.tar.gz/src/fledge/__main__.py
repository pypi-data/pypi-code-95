"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Fledge."""


if __name__ == "__main__":
    main(prog_name="fledge")  # pragma: no cover
