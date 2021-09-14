import os
import sys
import json

#########################################################

from general_utility import utils as us
from general_utility.appbase import ab

__version__ = "2.3.1"
def get_ver():
    return __version__

#########################################################
# 插件框架相关

def load_plugin_runner(url):

    from plugin_utility.plugin_object import Plugin_Runner, Plugin_Object, default_params

    return Plugin_Runner(url, local_params = default_params)

#########################################################

class Global(object):

    def __init__(self, envfile = None):

        self.env = os.environ.copy()
        if (envfile is not None):
            f = open(envfile)
            for line in f.readlines() :
                if line.startswith('#') or line.startswith('\n'):
                    continue
                try:
                    k, v = line.split("=", 1)
                    v = v.replace('\n', '').replace('\r', '')
                    self.set(k, v)
                except Exception as e:
                    continue
            f.close()

        pass

    def __call__(self, key, default=''):
        return self.get(key, default)

    def set(self, k, v):
        try:
            self.env[k] = v
        except Exception as e:
            print(e)

    def get(self, key, default=''):
        try:
            return self.env[key]
        except Exception as e:
            return default

#########################################################

search_path_list = []
def add_search_path(path):
    search_path = None
    if os.path.isdir(path):
        search_path = path
    elif (os.path.isfile(path)):
        search_path = os.path.dirname(path)

    if (search_path is not None) and (search_path not in search_path_list):
        search_path_list.append(search_path)
        
cwd = os.getcwd()

add_search_path(__file__) # apputility dir
add_search_path(cwd)
add_search_path(os.path.join(cwd, 'config'))

def check_params(args):
    if not isinstance(args, dict):
        return args

    if 'from_file' in args.keys():
        filepath = us.get_first_exists_path(args['from_file'], search_path_list = search_path_list)
        args = json.load(open(filepath, 'r'))
        pass
    elif 'from_url' in args.keys():
        pass

    return args

#########################################################

import pickle

USE_POOL = False
redis_channel = {}

def get_redis(host, port, password):
    import redis
    r_conn = redis.ConnectionPool(host=host, port=port, password=password,
                                    max_connections=10, decode_responses=True)
    return r_conn

def get_redis_url(redis_url = None, db = 0):
    if (redis_url is None):
        redis_url = os.getenv('REDIS_URL', None)
        if redis_url is None:
            return None
        return redis_url

    if (redis_url[-1] != "/"):
        redis_url = redis_url + "/"

    if isinstance(db, str):
        try:
            db = int(os.getenv(db, 0))
        except e:
            db = 0        

    return ('%s%d' % (redis_url, db))

def get_redis_db(redis_url, name, db = -1):
    if redis_url is None:
        redis_url = os.getenv('REDIS_URL', None)
        if redis_url is None:
            return None
        
    if us.check_attribute(redis_conns, name) is None:
        from urllib import parse
        url_obj = parse.urlparse(redis_url)
        scheme = url_obj.scheme
        if (scheme.lower() != 'redis'):
            return None

        if (USE_POOL):
            redis_conn_pool = us.check_attribute(redis_conns, 'ConnectionPool') # 连接池
            if (redis_conn_pool is None):
                redis_conns['ConnectionPool'] = get_redis(host=url_obj.hostname, port=url_obj.port, password=url_obj.password)
            redis_conns[name] = redis.Redis(connection_pool=us.check_attribute(redis_conns, 'ConnectionPool'))
        else:
            if (db < 0):
                db = us.check_attribute(redis_channel, name)
            redis_conns[name] = redis.Redis(host=url_obj.hostname, port=url_obj.port, password=url_obj.password, db=db)
        return us.check_attribute(redis_conns, name)

    return us.check_attribute(redis_conns, name)

def save_to_redis(redis_url, db_name, key, data, ex=30):
    conn = get_redis_db(db_name)
    if (conn is None) or (key is None) or (data is None):
        return
    conn.set(key, pickle.dumps(data), ex)

def load_from_redis(redis_url, db_name, key):
    conn = get_redis_db(db_name)        
    if (conn is None) or (key is None):
        return
    data = conn.get(key)
    if (data is None):
        return None
    return pickle.loads(data)