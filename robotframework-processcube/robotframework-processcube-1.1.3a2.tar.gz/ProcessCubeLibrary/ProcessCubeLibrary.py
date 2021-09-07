
from atlas_engine_client.core.api import Client

from .keywords import DeployKeyword
from .keywords import EmptyTaskKeyword
from .keywords import EngineKeyword
from .keywords import ExternalTaskKeyword
from .keywords import ManualTaskKeyword
from .keywords import ProcessInstanceKeyword
from .keywords import SendKeyword
from .keywords import StartKeyword
from .keywords import UserTaskKeyword

from robot.api import logger

from .docker_handler import DockerHandler


class ProcessCubeLibrary(DeployKeyword, EmptyTaskKeyword, 
    EngineKeyword, ExternalTaskKeyword, ManualTaskKeyword, 
    ProcessInstanceKeyword, SendKeyword, StartKeyword, 
    UserTaskKeyword):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, **kwargs):
        self._engine_url = kwargs.get('engine_url', None)
        self._self_hosted_engine = kwargs.get('self_hosted_engine', None)
        self._docker_options = kwargs.get('docker_options', {})

        self._max_retries = int(kwargs.get('max_retries', 5))
        self._backoff_factor = int(kwargs.get('backoff_factor', 2))
        self._delay = float(kwargs.get('delay', 0.1))
        self._worker_id = kwargs.get('worker_id', "robot_framework")

        self._client = self._create_client(**kwargs)

        super(ProcessCubeLibrary, self).__init__(self._client, **kwargs)

    def _create_client(self, **kwargs):
        engine_url = kwargs.get('engine_url', None)
        self_hosted_engine = kwargs.get('self_hosted_engine', None)

        client = None

        if engine_url:
            logger.console(f"Connecting to engine '{engine_url}'.")
            client = Client(engine_url)
        elif self_hosted_engine == 'docker':
            docker_options = kwargs.get('docker_options', {})

            logger.console(f"Starting engine within a docker container ...")
            self._docker_handler = DockerHandler(**docker_options)
            self._docker_handler.start()
            logger.console(
                f"Starting engine within a docker container ... done")

            engine_url = self._docker_handler.get_engine_url()

            logger.console(f"Connecting to engine '{engine_url}'.")
            client = Client(engine_url)
        else:
            raise TypeError(
                "No 'engine_url' or 'self_hosted_engine' parameter provided.")

        return client

    def engine_shutdown(self):
        if self._docker_handler:
            self._docker_handler.shutown()
