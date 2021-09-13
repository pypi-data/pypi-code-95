#!/usr/bin/python

import sys
import getopt

def get(english_digit):
    if 0 > english_digit or english_digit > 9:
        raise Exception('Digit range is between 0 and 9.')

    return (english_digit, chr(0x06f0 + english_digit), hex(0x6f0 + english_digit))

def view(english_digit):
    conv = get(int(english_digit))
    #print({english_digit}, {conv[1]}, {conv[2]})
    print(conv)

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'h',['help'])
    for opt in opts:
        if opt[0] in ['-h', '--help']:
            print('Usage: urdu_digit <english_digit>')
            print('Example Output: {}'.format(get(2)))
            sys.exit(0)

    if len(args) != 1:
        raise Exception('Please specify a single English digit.')
    view(args[0])
