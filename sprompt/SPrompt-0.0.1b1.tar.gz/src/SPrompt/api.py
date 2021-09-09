import json
import shlex
import logging
import subprocess
from robot.api.deco import keyword

class api(object):

    def __init__(self):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.INFO)
        logger = logging.getLogger(__name__)

    @keyword('Request cURL')
    def cURL(curl_command):
        args = shlex.split(curl_command)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        parsed = json.loads(stdout)
        return parsed