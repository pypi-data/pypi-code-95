import wikipedia
import click

@click.command()
@click.option('--search', '-s', help='Search Wikipedia', required=True)

def cli(search):
	"""Search Wikipedia"""
	results = wikipedia.summary(search)
	print()
	print()
	print(results)
	print()
	print()  
