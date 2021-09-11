import os
from pathlib import Path as path


class GCPConfig:
    BUCKET = os.environ.get('BUCKET_NAME', "signals-data")
    WORKER_PREFIX = os.environ.get('WORKER_PREFIX', 'cc-')
    MAX_INSTANCE_RESTART = os.environ.get('MAX_INSTANCE_RESTART', 5)
    IP_BLOCK_SECONDS = os.environ.get('IP_BLOCK_SECONDS', 100000)
    RESTART_KEY = 'restart'
    RESTART_TTL = os.environ.get('RESTART_TTL', 1200)
    MAX_INSTANCE_IP_RESTART = os.environ.get('MAX_INSTANCE_IP_RESTART', 10)
    SECONDS_THRESHOLD = 1


FROM_LOCAL = os.environ.get('FROM_LOCAL', "true") == "true"
TO_LOCAL = os.environ.get('TO_LOCAL', "false") == "true"


if FROM_LOCAL:
    DIR = path(os.path.dirname(os.path.abspath(__file__))).parent
else:
    DIR = f"gs://{GCPConfig.BUCKET}/"


class MemcachedConfig:
    HOST = os.environ.get("MEMCACHE_HOST", "127.0.0.1")
    PORT = "11211"

