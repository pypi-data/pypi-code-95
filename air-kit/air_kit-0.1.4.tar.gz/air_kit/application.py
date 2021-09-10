from asyncio import gather, get_event_loop, sleep
from asyncio.runners import _cancel_all_tasks
from dataclasses import dataclass
from logging import getLogger
from os import environ
from signal import SIGHUP, SIGINT, SIGTERM, SIGUSR1, SIGUSR2
from time import time

from dotenv import load_dotenv
from yaml import dump, load

from .environment import Environment
from .errors import ConfigurationValidationError

logger = getLogger(__name__)


def read_yaml(directory, file):
    with open(f"{directory}/{file}", "rt") as handle:
        return load(handle.read())


def write_yaml(directory, file, data):
    with open(f"{directory}/{file}", "wt") as handle:
        handle.write(dump(data, indent=2))


@dataclass
class EnvironmentVariable:
    key: str
    cast: type
    default: object
    is_required: bool


class BaseConfiguration:
    def __init__(self):
        self.environment = environ.get(
            "ENVIRONMENT",
            Environment.DEVELOPMENT,
        ).lower()
        self.configuration = self._merge_configuration(
            self._load_features(),
            self._load_options(),
            self._load_environment(),
        )
        if not self._validate_configuration(self.configuration):
            raise ConfigurationValidationError()

    def _load_features(self):
        # fmt: off
        return {
            name: read_yaml("configuration/features", value)
            for name, value in self._feature_files().items()
        }
        # fmt: on

    def _load_options(self):
        # fmt: off
        return {
            name: read_yaml("configuration/options", value)
            for name, value in self._option_files().items()
        }
        # fmt: on

    def _load_environment(self):
        # fmt: off
        load_dotenv("configuration/environments/.env_{}".format(self.environment))
        variables = {}

        for environment_variable in self._environment_variables():
            key_upper = environment_variable.key.upper()

            if key_upper in environ:
                value = environment_variable.cast(environ[key_upper])
            else:
                if environment_variable.is_required:
                    raise Exception("Value is required.")  # TODO: error type

                value = environment_variable.default

            variables[environment_variable.key] = value

        return variables
        # fmt: on

    def _feature_files(self):
        return {}

    def _option_files(self):
        return {}

    def _environment_variables(self):
        return ()

    def _merge_configuration(self, features, options, environment):
        return {}

    def _validate_configuration(self, configuration) -> bool:
        return True


class Runner:
    def __init__(self, applications):
        self.applications = applications

        for application in self.applications:
            application.runner = self

    def start(self):
        event_loop = get_event_loop()

        try:
            return event_loop.run_until_complete(self.run())
        except BaseException:
            logger.exception("Exception in runner loop.")
            pass

        try:
            _cancel_all_tasks(event_loop)
            event_loop.run_until_complete(event_loop.shutdown_asyncgens())
        except BaseException:
            logger.exception("Exception in runner shutdown.")
            pass

    def stop(self):
        for application in self.applications:
            application.stop()

    async def run(self):
        await gather(*[application.run() for application in self.applications])


class BaseApplication:
    def __init__(self, name, *, period=1.0):
        self.name = name
        self.period = period
        self.tasks = []
        self.runner = None
        self.is_active = True

    def start(self):
        event_loop = get_event_loop()

        try:
            event_loop.run_until_complete(self.run())
        except BaseException:
            logger.exception(f"Exception in application {self.name} loop.")
            pass

        try:
            _cancel_all_tasks(event_loop)
            event_loop.run_until_complete(event_loop.shutdown_asyncgens())
        except BaseException:
            logger.exception(f"Exception in application {self.name} shutdown.")
            pass

    def stop(self):
        self.is_active = False

    async def run(self):
        # Signal handlers.
        def _on_exit_signal():
            if self.runner is None:
                self.stop()
                return

            self.runner.stop()

        event_loop = get_event_loop()
        event_loop.add_signal_handler(SIGINT, _on_exit_signal)
        event_loop.add_signal_handler(SIGTERM, _on_exit_signal)
        event_loop.add_signal_handler(SIGUSR1, self._on_usr_1)
        event_loop.add_signal_handler(SIGUSR2, self._on_usr_2)
        event_loop.add_signal_handler(SIGHUP, self._on_hup)

        # Start.
        await self._on_start()
        logger.debug(f"Application {self.name} started.")

        # Workers.
        async def _worker(worker):
            while True:
                await sleep(worker.period - time() % worker.period)

                event_loop = get_event_loop()
                event_loop.create_task(worker.function())

        for worker in self._workers():
            task = event_loop.create_task(_worker(worker))
            self.tasks.append(task)

        # Loop.
        while self.is_active:
            try:
                await self._activity()
                await sleep(self.period)
            except BaseException:
                logger.exception(f"Exception while running application {self.name}.")
                await sleep(1)

        # Stop.
        await self._on_stop()
        logger.debug(f"Application {self.name} stopped.")

    async def _on_start(self):
        pass

    async def _on_stop(self):
        pass

    async def _activity(self):
        pass

    def _on_usr_1(self):
        pass

    def _on_usr_2(self):
        pass

    def _on_hup(self):
        pass

    def _workers(self):
        return []
