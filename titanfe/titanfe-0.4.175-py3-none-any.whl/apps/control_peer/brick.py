#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""A Brick"""

import re
import shutil
from collections import namedtuple
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import venv
import os
import subprocess

from titanfe.constants import GET_PIP
from titanfe import log as logging
from .services import package_manager
from ...config import configuration

Flow = namedtuple("Flow", ("uid", "name", "schema"))
Connections = namedtuple("Connections", ("input", "output"))
Ports = namedtuple("Ports", ("input", "output"))

RuntimeParameters = namedtuple(
    "RuntimeParameters",
    ("autoscale_max_instances", "autoscale_queue_level", "exit_after_idle_seconds"),
)

REQUIREMENTS = "requirements.txt"


def get_venv_exe(directory):
    if os.name == "nt":
        return os.path.join(directory, "Scripts", "python.exe")
    return os.path.join(directory, "bin", "python")


class EnvBuilder(venv.EnvBuilder):
    """Builder for the virtual enviroments for each brick
    """

    def __init__(self, logger, *args, **kwargs):
        self.log = logger
        self.pip_failed = False
        self.exe = None
        super().__init__(*args, **kwargs)

    def post_setup(self, context):
        """ install platforma and brick requirements during
        setup of the virtual environment
        """
        self.exe = context.env_exe
        if self.pip_failed:
            self.install_pip(context)
        self.install_requirements(context)

    def install_pip(self, context):
        """install pip manually"""
        self.log.info("installing pip")
        binpath = context.bin_path
        pip = [context.env_exe, GET_PIP]
        process = subprocess.Popen(
            pip, cwd=binpath, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        with process.stdout:
            self.log_stdout(process.stdout)
        exitcode = process.wait()
        if exitcode > 0:
            raise RuntimeError(f"Failed to install pip. ({exitcode})")

    def log_stdout(self, pipe):
        for line in pipe.readlines():
            if line:
                self.log.info(line.decode())

    def install_requirements(self, context):
        """install requirements in virtual environment"""
        requirements = os.path.join(context.env_dir, "..", REQUIREMENTS)

        if not os.path.exists(requirements):
            return

        self.log.info("installing brick requirements")
        binpath = context.bin_path
        get_requirements = [context.env_exe, "-m", "pip", "install", "-r", requirements]
        process = subprocess.Popen(
            get_requirements, cwd=binpath, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        with process.stdout:
            self.log_stdout(process.stdout)
        exitcode = process.wait()
        if exitcode > 0:
            raise RuntimeError(f"Failed to install requirements. ({exitcode})")


class BrickBaseDefinition:
    """
    The general definition of a brick contains it's name and id, as well as the module itself
    and possibly a set of default parameters for that module read from the annexed config.yaml
    """

    def __init__(self, uid, name=None, family=None, logger=None, last_modified=None):
        self.uid = uid
        self.name = name
        self.family = family
        self.last_modified = last_modified or None

        self.log = logger

        self.module_path = None
        self.guess_module_path()

        module_parent = Path(configuration.brick_folder)
        destination = module_parent / self.uid
        self.exe = get_venv_exe(os.path.join(destination, "venv"))

    def __getstate__(self):
        _dict = dict(self.__dict__)
        del _dict["log"]
        return _dict

    @property
    def venv_path(self):
        if self.module_path:
            return os.path.join(self.module_path.parent, "venv")
        return ""

    def guess_module_path(self):
        """
        The module is expected to be found in the configured brick_folder extended with the brick-ID
        and should be either a folder or python file having the same name as the brick.
        """

        module_parent = Path(configuration.brick_folder) / self.uid
        try:
            self.module_path = next(
                path
                for path in module_parent.iterdir()
                if re.match(f"^{self.name}(?:\\.py)?$", path.name, re.IGNORECASE)
            )
        except (FileNotFoundError, StopIteration):
            self.log.warning(
                "Missing module `%s/` or `%s.py` in %s", self.name, self.name, module_parent
            )

    def create_virtual_env(self):
        """ create a virtual enviroment for the brick"""
        environment = EnvBuilder(
            logger=self.log,
            system_site_packages=True,
            clear=False,
            symlinks=True,
            upgrade=False,
            with_pip=True,
            prompt=None,
        )
        try:
            environment.create(self.venv_path)
        except subprocess.CalledProcessError:
            environment.with_pip = False
            environment.pip_failed = True
            environment.create(self.venv_path)
        self.exe = environment.exe

    def __repr__(self):
        return f"Base({self.uid}, {self.name}, " f"module_path={self.module_path})"

    async def install_or_update(self, update=True, force_update=False):
        """ Get a brick from the package manager and install it"""
        module_parent = Path(configuration.brick_folder)
        destination = module_parent / self.uid

        if destination.exists():
            self.log.debug("Brick %s is already present", self.uid)
            if not update:
                return

            if not force_update:
                last_modified_local = destination.stat().st_mtime
                if datetime.utcfromtimestamp(last_modified_local) >= datetime.utcfromtimestamp(
                    self.last_modified
                ):
                    return

            shutil.rmtree(destination)

        destination.mkdir(parents=True, exist_ok=True)

        source = await package_manager.get_source_files(self.uid)

        if not source:
            return

        with ZipFile(BytesIO(source), "r") as compressed:
            self.log.debug("compressed brick content: %s", compressed.printdir())
            compressed.extractall(path=destination)

        self.log.info(
            "installed/updated source files for brick %s into %s",
            self.uid,
            list(destination.iterdir()),
        )
        self.guess_module_path()
        self.create_virtual_env()


class BrickInstanceDefinition:
    """
    The Brick Instance Definition is a fully configured brick in a flow context.
    It should have it's own name and uid within the flow, precise parameters
    and possibly connections to other bricks.
    """

    def __init__(  # pylint:disable= too-many-arguments
        self,
        uid,
        name,
        ports: Ports,
        flow: Flow,
        base: BrickBaseDefinition,
        processing_parameters: dict,
        runtime_parameters: RuntimeParameters,
        connections: Connections,
    ):
        self.flow = flow
        self.uid = uid
        self.name = name
        self.base = base
        self.ports = ports

        self.processing_parameters = processing_parameters
        self.runtime_parameters = runtime_parameters
        self.connections = connections

    def __repr__(self):
        return (
            f"Brick({self.uid}, {self.name}, flow={self.flow}, "
            f"base={self.base}, "
            f"processing_parameters={self.processing_parameters}, "
            f"runtime_parameters={self.runtime_parameters}, "
            f")"
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if isinstance(other, BrickInstanceDefinition):
            return other.uid == self.uid
        return False

    @classmethod
    def from_gridmanager(cls, brick_description):
        """Add brick configuration using default and flow-specific parameters if available"""
        config = brick_description["Configuration"]
        instance_uid = config["instanceId"]
        instance_name = config["name"]
        ports = Ports(config["inputPorts"], config["outputPorts"])
        flow = Flow(
            brick_description["FlowID"],
            brick_description["FlowName"],
            brick_description["FlowSchema"],
        )

        logger = logging.TitanPlatformLogger(
            __name__, context=logging.FlowContext(flow.uid, flow.name, instance_uid, instance_name)
        )

        base = BrickBaseDefinition(
            uid=config["id"], name=config["brick"], family=config["family"], logger=logger
        )
        runtime_params = RuntimeParameters(*[config[f] for f in RuntimeParameters._fields])
        processing_params = config["parameters"]
        connections = Connections(brick_description["Inbound"], brick_description["Outbound"])

        instance = cls(
            instance_uid,
            instance_name,
            ports,
            flow,
            base,
            processing_params,
            runtime_params,
            connections,
        )
        return instance
