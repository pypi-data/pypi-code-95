import typer
from .new import typ as new
from .run import typ as run

app = typer.Typer(add_completion=False)
app.add_typer(new, name="new")
app.add_typer(run, name="run")

def cli():
  app()
