import logging
from SPrompt.api import api 
from SPrompt.web import web 
from SPrompt.android import android 

class SPrompt(api, web, android):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = 0.1

    def __init__(self):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.INFO)
        logger = logging.getLogger(__name__)

