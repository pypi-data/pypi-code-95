import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '-k',
    '--kind',
    help='Pass the kind of animal you want to talk',
    type=str,
    dest='kind',
    default='dog'
)
args = parser.parse_args()