from argparse import ArgumentParser

def read_pipe_args():
	parser = ArgumentParser()
	parser.add_argument("-p", "--pipeline", dest="pipeline", help="enter the pipeline name")
	args = vars(parser.parse_args())
	pipeline = args['pipeline']
	if (pipeline == None):
		raise RuntimeError('you must pass the pipeline name')
	return pipeline