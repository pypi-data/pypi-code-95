# -*- coding: utf-8 -*-
import argparse
import datetime
import importlib
import json
import logging.config
import os
import pathlib
import sys
import traceback
from hashlib import sha256
from uuid import uuid4

from outflow import __version__ as outflow_version
from outflow.core.logging import logger, set_plugins_loggers_config
from outflow.core.pipeline import config, context, settings
from outflow.core.pipeline.context_manager import PipelineContextManager
from outflow.core.plugin import Plugin
from outflow.core.workflow import WorkflowManager


class Pipeline:
    system_arguments = {
        "config": (
            ["--config"],
            {"help": "The path to the config file."},
        ),
        "settings": (
            ["--settings"],
            {
                "help": 'The Python path to a settings module, e.g. "my_project.my_settings". If this isn\'t provided, the OUTFLOW_SETTINGS_MODULE environment variable will be used.'
            },
        ),
        "version": (
            ["--version"],
            {"help": "Show program's version number and exit.", "action": "store_true"},
        ),
        "python_path": (
            ["--python_path"],
            {
                "help": 'A directory to add to the Python path, e.g. "/home/pipeline_projects/my_project".',
                "action": "append",
                "default": [],
            },
        ),
        "traceback": (
            ["--traceback"],
            {"help": "Display exception tracebacks."},
        ),
        "no_color": (
            ["--no_color"],
            {"help": "Don't colorize the command output."},
        ),
        "log_level": (
            ["-ll", "--log-level"],
            {
                "help": "Specifies the amount information that the pipeline should print to the console ",
                "choices": ("DEBUG", "INFO", "WARNING", "ERROR"),
            },
        ),
        "local_mode": (
            ["-L", "--local-mode"],
            {"help": "Force local mode", "action": "store_true"},
        ),
        "backend": (
            ["--backend", "-b"],
            {
                "help": "Force backend",
            },
        ),
    }

    base_arguments = (
        {  # TODO test underscore (just for information) and switch to caret
            "dry_run": (
                ["--dry-run"],
                {
                    "help": "Run the pipeline without the database",
                    "action": "store_true",
                },
            ),
        }
    )

    def __init__(self, **kwargs):
        self.result = []
        self._kwargs = kwargs

    def _init(
        self,
        *,
        root_directory: str = None,
        settings_module: str = "settings",
        argv=None,
        force_dry_run: bool = False,
    ):
        """Init the pipeline instance with the settings, config, descriptor, etc.

        Args:
            root_directory (str, optional): The pipeline directory where the 'manage.py' file is usually located. Defaults to None.
            settings_module (str, optional): The pipeline directory where the 'manage.py' file is usually located. Defaults to 'settings'.
        """
        from outflow.core.pipeline import config as pipeline_config

        self._root_command = None
        self.force_dry_run = force_dry_run

        if root_directory is not None:
            # ensure both manage.py and settings.py are in the python path
            root_directory_abs_path = pathlib.Path(root_directory).resolve().as_posix()
            os.environ.setdefault("PIPELINE_ROOT_DIRECTORY", root_directory_abs_path)
            sys.path.append(root_directory_abs_path)

        if settings_module is not None:
            os.environ.setdefault("OUTFLOW_SETTINGS_MODULE", settings_module)

        # check pipeline level command line args
        system_args, self.command_argv = self.parse_system_args(argv=argv)

        if system_args.settings is not None:
            os.environ["OUTFLOW_SETTINGS_MODULE"] = system_args.settings

        if system_args.config is not None:
            os.environ["OUTFLOW_CONFIG_PATH"] = (
                pathlib.Path(system_args.config).resolve().as_posix()
            )

        for dir_path in system_args.python_path:
            sys.path.append(pathlib.Path(dir_path).resolve().as_posix())

        # If true, show program's version number and exit.
        self.display_version = system_args.version

        # setup the logger and force the verbose level if needed
        if system_args.log_level is not None:
            pipeline_config["logging"]["loggers"]["outflow"][
                "level"
            ] = system_args.log_level

        set_plugins_loggers_config()

        logging.config.dictConfig(pipeline_config["logging"])

        logger.debug(f"Config loaded: {pipeline_config}")

        pipeline_config["local_mode"] = system_args.local_mode
        if system_args.backend:
            pipeline_config["backend"] = system_args.backend

        self.load_plugins()
        self.load_backends()

    def _dispose(self):
        # close database connections, clear Model metadata and bubble up the exception if any
        context.databases.close()

    def load_plugins(self):
        from outflow.core.pipeline import context, settings

        for plugin_name in settings.PLUGINS:
            Plugin.load(plugin_name)

        # ensure table metadata correspond to the loaded models
        for model in context._models:
            model.register()

    def load_backends(self):
        from outflow.core.backends.backend import Backend as DefaultBackend
        from outflow.core.pipeline import settings

        self.backends = {"default": DefaultBackend}

        for key, value in settings.BACKENDS.items():
            try:
                module = importlib.import_module(value)
                self.backends[key] = module.Backend
                logger.debug(f"Backend {key} successfully imported")
            except ImportError as ie:
                logger.warning(f"Cannot import module {value} for backend {key}")
                logger.debug(ie)

    @property
    def root_command(self):
        if self._root_command is None:
            try:
                from outflow.core.pipeline import settings
            except ImportError as exc:
                raise ImportError(
                    "Couldn't import the pipeline root command from the settings. Are you sure outflow is installed and "
                    "available on your PYTHONPATH environment variable? Did you "
                    "forget to activate a virtual environment?"
                ) from exc
            # get the instance of the root command singleton
            self._root_command = settings.ROOT_COMMAND_CLASS()

            # loop over the system and base args and add them to the parser to be able to display the full help message
            # if the system arguments have already been added, pass
            base_root_command_args = {**self.system_arguments, **self.base_arguments}
            self.add_args(base_root_command_args, self._root_command.parser)

        return self._root_command

    def add_args(self, args_dict, parser):
        if not getattr(parser, "_args_already_setup", False):

            for argument in args_dict.values():
                parser.add_argument(*argument[0], **argument[1])
            parser._args_already_setup = True

    def parse_system_args(self, argv=None):
        """
        Parse the system args
        """
        parser = argparse.ArgumentParser(
            description="Preprocess system arguments.",
            add_help=False,
            allow_abbrev=False,
        )

        self.add_args(self.system_arguments, parser)

        return parser.parse_known_args(argv)

    def setup_backend(self, backend_name=None):
        from outflow.core.pipeline import config

        if not backend_name:
            backend_name = config.get("backend", "default")

        Backend = self.backends.get(backend_name)
        if Backend is None:
            raise ModuleNotFoundError(
                f"Could not find backend {backend_name}, "
                "please check that it is correctly imported"
            )
        return Backend()

    def run(self):
        """Run the pipeline"""
        if self.display_version:
            print(f"Outflow version '{outflow_version}'")
            return 0

        context.force_dry_run = self.force_dry_run

        command = self.root_command.parse_command_tree(self.command_argv)

        # if no argument is supplied, the help message is triggered
        # and command tree parser returns 0
        if command == 0:
            return command

        context.db_untracked = command.db_untracked

        backend = self.setup_backend(command.backend)

        context.backend_name = backend.name

        if command.db_untracked:
            logger.debug(
                "db_untracked=True passed to command init, this run will not be stored in the database"
            )

        db_config = self.create_config_in_db()
        db_run = self.create_run_in_db(db_config)

        return_code = 1

        try:
            db_run.start()
            with WorkflowManager():
                task_list = command._setup_tasks()
            if task_list:
                backend.check_task_io(task_list)
                self.result = backend.run(task_list=task_list)
            db_run.success()
            return_code = 0
        except Exception as e:
            db_run.fail()
            from outflow.management.models.runtime_exception import RuntimeException

            RuntimeException.create(
                task=getattr(e, "db_task", None),
                exception_type=e.__class__.__name__,
                exception_msg=str(e.args),
                traceback="".join(traceback.format_tb(e.__traceback__)),
                time=datetime.datetime.now(),
            )

            # logger.print_exception() # TODO add this for file_handler but find a way to not duplicate exception in terminal
            raise
        finally:
            backend.clean()

        return return_code

    @staticmethod
    def create_config_in_db():
        from outflow.core.pipeline import config, settings
        from outflow.management.models.configuration import Configuration

        cfg = config.sanitize(config.to_serializable_dict())
        del cfg["logging"]
        cfg_json = json.dumps(cfg)
        settings_json = json.dumps(settings.to_serializable_dict())
        hash = sha256(bytes(cfg_json + settings_json, encoding="utf-8")).hexdigest()
        return Configuration.get_or_create(
            hash=hash,
            create_method_kwargs={"config": cfg_json, "settings": settings_json},
        )

    @staticmethod
    def create_run_in_db(db_config):
        from outflow.management.models.run import Run

        run_uuid = str(uuid4())
        db_run = Run.create(uuid=run_uuid, configuration=db_config, state="pending")

        context.db_run = db_run
        return db_run

    @staticmethod
    def get_parent_directory_posix_path(module_path):
        """Return the posix path of the parent directory of the given module

        Args:
            module_path (str): The module path. Usually the one of 'manage.py'

        Returns:
            str: The posix path of the parent directory of the given module
        """
        return pathlib.Path(module_path).parent.resolve().as_posix()

    def __enter__(self):
        self.pipeline_context_manager = PipelineContextManager().__enter__()
        self._init(**self._kwargs)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context, resetting parent_context and context to None"""
        self._dispose()
        self.pipeline_context_manager.__exit__(exc_type, exc_val, exc_tb)


def get_pipeline_states():
    states = {
        "context_state": context.getstate(),
        "settings_state": settings.getstate(),
        "config_state": config.getstate(),
    }
    return states
