"""Wait for Docker to be active."""
import sys
import time
from contextlib import contextmanager

import docker
from docker.errors import DockerException
from yaspin import yaspin


def main():
    with exit_with_interrupt():
        with yaspin():
            while not check_docker():
                time.sleep(0.5)

        print("Docker is active now.")


def check_docker() -> bool:
    try:
        docker.from_env()
    except DockerException:
        return False

    return True


@contextmanager
def exit_with_interrupt():
    try:
        yield
    except KeyboardInterrupt:
        sys.exit(1)
