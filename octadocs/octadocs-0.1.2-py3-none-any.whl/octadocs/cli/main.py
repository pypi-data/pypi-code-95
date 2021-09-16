from octadocs.cli import sparql
from typer import Typer

app = Typer()

app.add_typer(sparql.app)
