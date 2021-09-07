"""The CLI for snapspam."""
import argparse
import json
import threading
import random
from time import sleep
from typing import Callable

from . import __version__


def start_threads(target: Callable, count: int):
    for i in range(count - 1):
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()

    # Instead of running n threads, run n - 1 and run one in the main thread
    target()


def main():
    """The main function to set up the CLI and run the spammers"""
    parser = argparse.ArgumentParser(description='Spam sendit or LMK messages.')
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f'snapspam {__version__}',
    )

    subparsers = parser.add_subparsers(
        help='The app to spam',
        dest='target_app',
        required=True,
    )

    ##### Parent parser for common args #####
    common_args = argparse.ArgumentParser(add_help=False)

    common_args.add_argument(
        '--msg-count',
        type=int,
        default=-1,
        help='The amount of messages to send. '
        'Set to -1 (default) to spam until stopped',
    )
    common_args.add_argument(
        '--thread-count',
        type=int,
        default=1,
        help='The amount of threads to create. Only valid for --msg-count -1 ',
    )
    common_args.add_argument(
        '--delay',
        type=int,
        default=500,
        help='Milliseconds to wait between message sends',
    )
    common_args.add_argument(
        '--proxy',
        type=str,
        help='Specify a SOCKS proxy to use for HTTPS traffic '
        '(eg. socks5://127.0.0.1:9050). Note that this will almost certainly '
        'be much slower than not using a proxy',
    )

    ##### Sendit Parser #####
    sendit_parser = subparsers.add_parser(
        'sendit',
        help='Spam a sendit sticker',
        parents=[common_args],
    )
    sendit_parser.add_argument(
        'sticker_id',
        type=str,
        help='The sticker ID or URL to spam',
    )
    sendit_parser.add_argument('message', type=str, help='The message to spam')
    sendit_parser.add_argument(
        '--sendit-delay',
        type=int,
        default=0,
        help='Minutes before the recipient gets the message '
        '(Part of sendit; not a custom feature)',
    )

    ##### LMK Parser #####
    lmk_parser = subparsers.add_parser(
        'lmk',
        help='Spam an LMK poll',
        parents=[common_args],
    )

    lmk_parser.add_argument(
        'lmk_id',
        type=str,
        help='The ID or URL of the poll to spam',
    )
    lmk_parser.add_argument(
        'choice',
        type=str,
        help='The choice ID to send to the poll. '
        "To get a list of choices, use 'get_choices'. "
        "To send a random choice each time, use 'all'",
    )

    args = parser.parse_args()
    print(args)

    if args.proxy is None:
        proxies = {}
    else:
        proxies = {'https': args.proxy}

    if args.target_app == 'sendit':
        from .sendit import Sendit

        spammer = Sendit(
            args.sticker_id,
            args.message,
            args.sendit_delay,
            proxies,
        )

        def send():
            r = json.loads(spammer.post().content)
            if r['status'] == 'success':
                print('Sent message.')
            else:
                print(f'Message failed to send. Code: {r.status_code}')
                print(r.content)
            sleep(args.delay / 1000)

        if args.msg_count == -1:
            print('Sending messages until stopped.')
            print('(Stop with Ctrl + C)')
        else:
            print(f'Sending {args.msg_count} messages...')

        if args.msg_count == -1:

            def thread():
                while True:
                    send()

            start_threads(thread, args.thread_count)
        else:
            for _ in range(args.msg_count):
                send()

    elif args.target_app == 'lmk':
        from .lmk import LMK

        spammer = LMK(args.lmk_id, proxies)

        # Scrape page for poll choices and print them
        if args.choice.lower() == 'get_choices':
            choices = spammer.get_choices()
            for choice in choices:
                print(f'ID: {choice.cid}')
                print('~' * (len(choice.cid) + 4))
                print(choice.contents)
                print('-' * 50)
            return

        def send(choice: str):
            r = spammer.post(choice)
            if r.status_code == 200:
                print(f'Sent message (Choice: {choice})')
            else:
                print(f'Message failed to send. Code: {r.status_code}')
                print(r.content)
            sleep(args.delay / 1000)

        if args.choice.lower() == 'all':
            ids = [c.cid for c in spammer.get_choices()]

        if args.msg_count == -1:
            print('Sending messages until stopped.')
            print('(Stop with Ctrl + C)')

            if args.choice.lower() == 'all':

                def thread():
                    while True:
                        send(random.choice(ids))
            else:

                def thread():
                    while True:
                        send(args.choice)

            start_threads(thread, args.thread_count)
        else:
            print(f'Sending {args.msg_count} messages...')
            for _ in range(args.msg_count):
                send()
    else:
        return
