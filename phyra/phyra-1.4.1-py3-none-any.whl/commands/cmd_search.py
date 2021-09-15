import click
from googlesearch import search

@click.command()
@click.option('--now', '-n', help='Search Google', required=True)
def cli(now):
    '''Phyra Search'''
    to_search = now

    print(f'============== Searching {now} ==============')
    for j in search(to_search, tld='com', num=12, stop=12, pause=2):
        print(j)
    print(f'================================================')