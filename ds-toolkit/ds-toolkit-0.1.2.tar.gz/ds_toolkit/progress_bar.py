import sys
import pyprind
from time import sleep


def progress_bar(items, title=''):
    """
    Progress bar for iterating

    Args:
        items (list or int): Item count or list of items.
        title (str):
    Returns:
        pyprind.ProgBar:
    """
    if type(items) == list:
        items = len(items)

    bar = pyprind.ProgBar(
        items + 1,
        stream=sys.stdout,
        title=title,
        width=100,
        monitor=True,
        update_interval=1
    )
    bar.update()
    return bar


def sleep_for(seconds, title=''):
    """Progress bar for sleeping"""
    bar = progress_bar(seconds, title=title)
    for second in range(0, seconds, 1):
        sleep(1)
        bar.update()
