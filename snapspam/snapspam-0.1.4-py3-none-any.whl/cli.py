"""The CLI for snapspam."""
import argparse
import json
import threading
import random
from datetime import datetime
from time import sleep
from typing import Callable

from . import __version__


def start_threads(target: Callable, count: int):
    """Start threads to spam

    Args:
        target (Callable): The function to run
        count (int): The amount of threads to start
    """
    for i in range(count - 1):
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()

    # Instead of running n threads, run n - 1 and run one in the main thread
    target()


def get_time() -> str:
    """Get the current time with milliseconds

    Returns:
        str: The formatted time
    """
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def main():
    """The main function to set up the CLI and run the spammers"""
    parser = argparse.ArgumentParser(
        prog='snapspam',
        description='spam sendit or LMK messages.',
    )
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )

    subparsers = parser.add_subparsers(
        help='the app to spam',
        dest='target_app',
        required=True,
    )

    ##### Parent parser for common args #####
    common_args = argparse.ArgumentParser(add_help=False)

    common_args.add_argument(
        '--msg-count',
        type=int,
        default=-1,
        help='the amount of messages to send. '
        'set to -1 (default) to spam until stopped',
    )
    common_args.add_argument(
        '--thread-count',
        type=int,
        default=1,
        help='the amount of threads to create. only valid for --msg-count -1',
    )
    common_args.add_argument(
        '--delay',
        type=int,
        default=500,
        help='milliseconds to wait between message sends',
    )
    common_args.add_argument(
        '--proxy',
        type=str,
        help='specify a SOCKS proxy to use for HTTPS traffic '
        '(eg. socks5://127.0.0.1:9050). note that this will almost certainly '
        'be much slower than not using a proxy',
    )

    ##### Sendit Parser #####
    sendit_parser = subparsers.add_parser(
        'sendit',
        help='spam a sendit sticker',
        parents=[common_args],
    )
    sendit_parser.add_argument(
        'sticker_id',
        type=str,
        help='the sticker ID or URL to spam',
    )
    sendit_parser.add_argument('message', type=str, help='the message to spam')
    sendit_parser.add_argument(
        '--sendit-delay',
        type=int,
        default=0,
        help='minutes before the recipient gets the message '
        '(part of sendit; not a custom feature)',
    )

    ##### LMK Parser #####
    lmk_parser = subparsers.add_parser(
        'lmk',
        help='spam an LMK poll',
        parents=[common_args],
    )

    lmk_parser.add_argument(
        'lmk_id',
        type=str,
        help='the ID or URL of the poll to spam',
    )
    lmk_parser.add_argument(
        'choice',
        type=str,
        help='the choice ID to send to the poll. '
        "to get a list of choices, use 'get_choices'. "
        "to send a random choice each time, use 'all'",
    )
    lmk_parser.add_argument(
        '--no-choice-lookup',
        action='store_true',
        help="don't get a list of choices from the poll "
        "while sending messages. this just means that the value "
        "of the choice won't be printed out, just the ID will. "
        "this parameter doesn't apply if 'all' is passed for the choice, "
        "since the list of choices will have to be requested any way.",
    )

    args = parser.parse_args()

    if args.proxy is None:
        proxies = {}
    else:
        proxies = {'https': args.proxy}

    # Arguments to pass to later-defined send() function, if any
    send_args = []

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
                print(f'Sent message. ({get_time()})',)
            else:
                r_json = json.loads(r.content)
                print(f'Message failed to send. Code: {r.status_code}')
                print(r_json)
            sleep(args.delay / 1000)

        if args.msg_count == -1:

            def thread():
                while True:
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

        if args.choice.lower() == 'all' or not args.no_choice_lookup:
            choices = {}
            for c in spammer.get_choices():
                choices[c.cid] = c.contents
            ids = list(choices.keys())
        else:
            choices = ids = None

        def send(choice: str):
            r = spammer.post(choice)
            if r.status_code == 200:
                print(f'Sent message ({get_time()} - '
                      f'{choice if choices is None else choices[choice]})')
            else:
                # This error is misleading, so print our own output
                r_json = json.loads(r.content)
                if 'reason' in r_json and r_json[
                        'reason'] == "Argument 'question' required":
                    print('Invalid choice ID provided.')
                    exit(1)
                else:
                    print(f'Message failed to send. Code: {r.status_code}')
                    print(r_json)
            sleep(args.delay / 1000)

        if args.msg_count == -1:
            if args.choice.lower() == 'all':

                def thread():
                    while True:
                        send(random.choice(ids))
            else:

                def thread():
                    while True:
                        send(args.choice)
        else:
            send_args = [args.choice]
    else:
        return

    # Spam
    if args.msg_count == -1:
        print('Sending messages until stopped.')
        print('(Stop with Ctrl + C)')
        start_threads(thread, args.thread_count)
    else:
        print(f'Sending {args.msg_count} messages...')
        for _ in range(args.msg_count):
            send(*send_args)
