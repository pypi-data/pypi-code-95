from octadocs.cli import sparql, context
from typer import Typer

app = Typer()

app.add_typer(sparql.app)
app.add_typer(context.app)
