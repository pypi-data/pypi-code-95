import pipes
import yaml
from yaml.loader import SafeLoader

def get_orange_pipelines():
	with open('./orange.yml') as orange:
		data = yaml.load(orange, Loader=SafeLoader)
	return data.get('pipelines')

def get_global_envs():
	try:
		pipelines = get_orange_pipelines()
		globalEnvs = pipelines.get('global').get('env')
		return globalEnvs
	except:
		return None

def get_envs_by_name(pipeline: str):
	try:
		pipelines = get_orange_pipelines()
		pipes = pipelines.get(pipeline)
		return pipes.get('env')
	except:
		print('Failed to read "'+pipeline+'" pipeline environment variables in orange.yml')
		raise

def apply_envs(envs):
	for env in envs:
		envsValue = pipes.quote(str(envs.get(env)))
		print('export %s=%s' % (env, envsValue))

def apply_orange_envs(pipeline=None):
	globalEnvs = get_global_envs()
	if (globalEnvs != None):
		apply_envs(globalEnvs)
	if (pipeline != None):
		pipeEnvs = get_envs_by_name(pipeline)
		apply_envs(pipeEnvs)
