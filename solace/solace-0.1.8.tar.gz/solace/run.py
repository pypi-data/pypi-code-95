import typer
import os
import sys
import importlib
from solace import DevelopmentServer

typ = typer.Typer()

@typ.command()
def dev(
    host: str = typer.Option("127.0.0.1", help="the interface the development server will bind to"),
    port: int = typer.Option(5000, help="the port the development server will listen on")
):
  """ starts a local development server. Do not use this for production. """
  sys.path.append(os.getcwd())
  if not os.path.isfile("src/index.py"):
        raise Exception("unable to find solace project")
  instance = importlib.import_module("src.index")
  app = instance.app
  DevelopmentServer(app, host=host, port=port).start()
