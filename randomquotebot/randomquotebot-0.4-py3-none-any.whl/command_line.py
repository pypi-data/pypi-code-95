import argparse
from colr import color
from quotebot.randomquotes import enlightme


def coloredquote():
    parser = argparse.ArgumentParser(description='Citations en couleur')
    parser.add_argument('color', metavar='C', type=str, help='Indiquer une couleur')
    args = parser.parse_args()
    quote = enlightme()
    print(color("%s once said : %s"%tuple(quote), args.color))

