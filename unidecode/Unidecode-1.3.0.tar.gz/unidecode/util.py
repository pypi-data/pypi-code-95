# vim:ts=4 sw=4 expandtab softtabstop=4
import argparse
import locale
import os
import sys

from unidecode import unidecode

def fatal(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(1)

def main():
    default_encoding = locale.getpreferredencoding()

    parser = argparse.ArgumentParser(
            description="Transliterate Unicode text into ASCII. FILE is path to file to transliterate. "
            "Standard input is used if FILE is omitted and -c is not specified.")
    parser.add_argument('-e', '--encoding', metavar='ENCODING', default=default_encoding,
            help='Specify an encoding (default is %s)' % (default_encoding,))
    parser.add_argument('-c', metavar='TEXT', dest='text',
            help='Transliterate TEXT instead of FILE')
    parser.add_argument('path', nargs='?', metavar='FILE')

    args = parser.parse_args()

    encoding = args.encoding

    if args.path:
        if args.text:
            fatal("Can't use both FILE and -c option")
        else:
            with open(args.path, 'rb') as f:
                stream = f.read()
    elif args.text:
        stream = os.fsencode(args.text)
        # add a newline to the string if it comes from the
        # command line so that the result is printed nicely
        # on the console.
        stream += b'\n'
    else:
        stream = sys.stdin.buffer.read()

    try:
        stream = stream.decode(encoding)
    except UnicodeDecodeError as e:
        fatal('Unable to decode input: %s, start: %d, end: %d' % (e.reason, e.start, e.end))

    sys.stdout.write(unidecode(stream))
