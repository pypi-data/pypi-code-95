"""Console script for magento_client."""
import sys
import click

from magento_client.magento_client import Magento

@click.command()
def main(args=None):
    """Console script for magento_client."""
    url = input('Enter url: ')
    consumer_key = input('Enter Consumer Key: ')
    consumer_secret = input('Enter Consumer secret: ')
    access_token = input('Enter Access Token: ')
    access_token_secret = input('Enter Access Token Secret: ')

    session = Magento(
        url=url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    try:
        response = session.get(path='/store/websites')
        if response:
            website = response[0]['name']
            print(f'we have contact with {website}')
        else:
            print('Connection failed')
    except KeyError:
        print('Connection failed')


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
