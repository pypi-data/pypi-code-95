import pipes
import yaml
from yaml.loader import SafeLoader
from yaml.reader import ReaderError

def get_orange_pipelines():
	with open('./orange.yml') as orange:
		data = yaml.load(orange, Loader=SafeLoader)
	if (data == None):
		raise ReaderError('"orange.yml" is empty')
	return data.get('pipelines')

def get_envs(pipeline: str):
	pipelines = get_orange_pipelines()
	pipes = pipelines.get(pipeline)
	if (pipes == None):
		print('Fails to read environment variables from "',pipeline,'" pipeline into orange.yml')
		raise ReaderError('Fails to read environment variables from pipeline into orange.yml')
	envs = pipes.get('env')
	if (envs == None):
		print('The "',pipeline,'" env field is empty')	
		raise ReaderError('The pipeline env field is empty')
	return envs

def apply_orange_envs(pipeline: str):
	envs = get_envs(pipeline)
	for env in envs:
		envs_value = pipes.quote(str(envs.get(env)))
		print('export %s=%s' % (env, envs_value))
