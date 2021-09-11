from os import path
import subprocess
from semver import VersionInfo
from typing import List
from swimlane_platform.lib.version_manager import semver_parse
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return
from swimlane_platform.lib.logger import SplitStreamLogger
import re


class DockerComposeManager:

    def __init__(self, logger, *docker_compose_file):
        # type: (SplitStreamLogger, List[str]) -> None
        self.logger = logger
        self.docker_compose_files = docker_compose_file

    @debug_function_return
    @debug_function_args
    def docker_compose_run(self, command, *args):
        # type: (str, str) -> str
        """
        Runs docker compose commands.
        :param command: Docker compose command. (up, down, build etc)
        :param args: Command arguments
        """
        command_args = ['docker-compose']
        dir_name = ''
        for docker_compose_file in self.docker_compose_files:
            dir_name, file_name = path.split(docker_compose_file)
            command_args.extend(['-f', file_name])
        command_args.append(command)
        if args:
            command_args.extend(args)
        std_out = subprocess.check_output(command_args, cwd=dir_name)
        try:
            std_out = std_out.decode()
        except AttributeError:
            pass
        self.logger.verbose(std_out)
        return std_out

    @debug_function_return
    def docker_compose_down(self):
        # type: () -> str
        """
        Spins down services from docker compose.
        """
        return self.docker_compose_run('down')

    @debug_function_return
    def docker_compose_up(self, *services):
        # type: (List[str]) -> str
        """
        Starts services from docker compose.
        """
        return self.docker_compose_run('up', '-d', *services)

    @debug_function_return
    def docker_compose_version(self):
        # type: () -> VersionInfo
        """
        Gets docker-compose version
        :return: semver version of docker-compose
        """
        command_args = ['docker-compose', '--version']
        std_out = subprocess.check_output(command_args)
        try:
            std_out = std_out.decode()
        except AttributeError:
            pass
        self.logger.verbose(std_out)
        match = re.search(r'\b(?:\d+\.)*\d+\b', std_out)
        version = match.group() if match else '0'
        return semver_parse(version)
