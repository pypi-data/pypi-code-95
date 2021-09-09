"""Bayscrape 1.1.3

Browse legal torrents from the safety and comfort of your command-line interface.
"""
from bayscrape.bsutils import get_input, output
from bayscrape.results import Results
from sys import argv

_WELCOME_MESSAGE = "\n".join((
    "bayscrape torrent fetcher",
    "| Enter your search term (optional: include tag to filter results)",
    "| Enter 'q' to quit",
    "| tags: -audio, -video, -apps, -games",
))


def main() -> None:
    """Begin bayscrape application."""
    if len(argv) > 1:
        query = " ".join(argv[1:])
    else:
        query = ""
    while True:
        output(_WELCOME_MESSAGE)
        if query:  # in case loaded from command line arguments
            output(query)
        else:
            query = get_input()
        torrent_results = Results(query)
        if torrent_results.user_quits:
            break
        if torrent_results.is_empty():
            output("No results found. Try your query again.\n\n")
        else:
            torrent_results.open_interface()
        query = ""


if __name__ == "__main__":
    main()
