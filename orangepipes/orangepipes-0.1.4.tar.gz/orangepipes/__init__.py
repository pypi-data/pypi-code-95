import pipeline
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-p", "--pipeline", dest="pipeline",
                    help="enter the pipeline name")

args = vars(parser.parse_args())

if (args['pipeline'] == None):
	raise RuntimeError('you must pass the pipeline name')

def apply_orange_envs():
	pipeline.apply_orange_envs(args['pipeline'])
