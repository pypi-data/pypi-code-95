import typer

app = typer.Typer()


@app.command()
def hello(user_name: str):
    typer.echo(f"Hello: {user_name}")

from widen.basics.animals.Octopus import Octopus

@app.command()
def Animal(name: str):
    oct = Octopus(name, "Red")
    oct.tell_me_about_the_octopus()

# def main(name: str):
#     typer.echo(f"Hello {name}")


# if __name__ == "__main__":
#     typer.run(main)


if __name__ == "__main__":
    app()