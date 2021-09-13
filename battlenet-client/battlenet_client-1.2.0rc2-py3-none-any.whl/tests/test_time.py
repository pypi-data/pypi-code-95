import cProfile
import pstats
from decouple import config
from battlenet_client.client import BattleNetClient


def main():
    # set up the client, url and params, before starting run
    client = BattleNetClient('us', 'wow', 'enus', config('CLIENT_ID'), config('CLIENT_SECRET'))

    with cProfile.Profile() as pr:
        client.get(f'{client.api_host}/data/wow/achievement-category/81', locale='en_US', namespace='static-us')

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


if __name__ == '__main__':
    main()
