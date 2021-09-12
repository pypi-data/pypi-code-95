# Eli Fulkerson
# http://www.elifulkerson.com

import random
import sys


def double(digit):
    "Double digit, add its digits together if they are >= 10"
    digit = int(digit) * 2
    return digit if digit < 10 else digit - 9


def check(cc):
    "Given a cc number (string), will return True if it passes mod10 check, False otherwise"
    cc = cc[::-1]
    total = 0
    for i, n in enumerate(cc):
        n = int(n)
        total += double(n) if i % 2 else n

    return (total % 10) == 0


def make_number(prefix, length):
    "Generate a random number that starts with prefix and is length long that passes mod10"
    while True:
        cc = list(prefix)
        for i in range(len(cc)):
            if cc[i].lower() == 'x':
                cc[i] = str(random.randint(0, 9))

        while len(cc) < length:
            cc.append(str(random.randint(0, 9)))

        cc = ''.join(cc)
        if check(cc):
            return cc


def generate_random_date():
    m = random.randint(1, 12).__str__()
    m = '0' + m if len(m) == 1 else m
    y = random.randint(2022, 2028).__str__()
    return (m, y)


def create_cc_numbers(prefix='537630', count=10, ccnumber_length=16):
    "Print count numbers that pass mod10 - example function"
    for _ in range(count):
        cc = make_number(prefix, ccnumber_length)
        m, y = generate_random_date()
        yield cc + "|{}|{}|{}".format(m, y, str(random.randint(100, 999)))


if __name__ == '__main__':
    prefix = sys.argv[1] if len(sys.argv) > 1 else '537630'
    ccnumber_length = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    numbers = create_cc_numbers(prefix, 10, ccnumber_length)
    for n in numbers:
        print(n)
