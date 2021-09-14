import argparse
import redis
import traceback


def main(args=None):
    """
    The main method for parsing command-line arguments and running the application.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    parser = argparse.ArgumentParser(
        prog="simple_redis_helper-listen",
        description="Listens to the specified channel for messages to come through and outputs them on stdout.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-H', '--host', metavar='HOST', required=False, default="localhost", help='The redis server to connect to')
    parser.add_argument('-p', '--port', metavar='PORT', required=False, default=6379, type=int, help='The port the redis server is listening on')
    parser.add_argument('-d', '--database', metavar='DB', required=False, default=0, type=int, help='The redis database to use')
    parser.add_argument('-c', '--channel', metavar='CHANNEL', required=True, default=None, help='The channel to broadcast the content on')
    parser.add_argument('-D', '--data_only', action='store_true', help='Whether to output only the message data')
    parser.add_argument('-s', '--convert_to_string', action='store_true', help='Whether to convert the message data to string (requires --data_only)')
    parsed = parser.parse_args(args=args)

    r = redis.Redis(host=parsed.host, port=parsed.port, db=parsed.database)

    def anon_handler(message):
        data = message
        if parsed.data_only:
            data = message['data']
            if parsed.convert_to_string:
                data = data.decode()
        print(data)

    p = r.pubsub()
    p.psubscribe(**{parsed.channel: anon_handler})
    p.run_in_thread(sleep_time=0.001)


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.
    :return: 0 for success, 1 for failure.
    :rtype: int
    """
    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == '__main__':
    main()

