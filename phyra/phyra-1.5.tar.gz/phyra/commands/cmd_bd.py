import click
from datetime import datetime

@click.command()
def cli():
    '''Phyra Birthday Countdown'''
    bd = datetime(2022, 9, 12)
    now = datetime.today().replace(microsecond=0)

    x = bd -now

    print('=========== PHYRA BIRTHDAY ===========')
    print()
    print(f"Phyra's birthday in {x}")
    print()
    print('======================================')
