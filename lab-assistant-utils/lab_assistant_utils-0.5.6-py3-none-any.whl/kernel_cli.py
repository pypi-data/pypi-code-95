#!/usr/bin/env python


import json
import os
import sys
from collections import namedtuple

from docker import APIClient
import click
from datetime import datetime
from pytz import timezone
from typing import List

from .docker import DockerRunOptionsBuilder


eastern = timezone('US/Eastern')
WORKSPACE = os.environ['WORKSPACE']
PROJECT_NAME = 'meetingfx'
PROJECT_WORKSPACE = os.path.join(WORKSPACE, PROJECT_NAME)
PROJECT_DATA = f'{PROJECT_WORKSPACE}/data'


NETWORK_NAME = os.environ.get('NETWORK_NAME')
DISPLAY = os.environ.get('DISPLAY')
TRACING_HOST = os.environ.get('TRACING_HOST')
TRACING_PORT = os.environ.get('TRACING_PORT')

KernelConnection = namedtuple('KernelConnection', ['key', 'control_port', 'shell_port', 'stdin_port', 'hb_port', 'iopub_port'])


__all__ = ['start_kernel', 'start_kernel_image']


def get_project_name():
    raise NotImplementedError('Implement get_project_name')


def get_project_version():
    raise NotImplementedError('Implement get_project_version')


def build_image_name(image_name_prefix: List):
    image_name_prefix.append(get_project_name())
    return f"{'/'.join(image_name_prefix)}:{get_project_version()}"


def parse_kernel_connection(connection: str) -> KernelConnection:
    with open(connection, 'r') as cxn_fp:
        connection_params = json.load(cxn_fp)

    return KernelConnection(
        key=connection_params['key'],
        control_port=connection_params['control_port'],
        shell_port=connection_params['shell_port'],
        stdin_port=connection_params['stdin_port'],
        hb_port=connection_params['hb_port'],
        iopub_port=connection_params['iopub_port']
    )


    # def with_project_volumes(self, project_name) -> 'DockerRunOptionsBuilder':
    #     self.options.add(f'-v {os.path.join(self.workspace, project_name, "data")}:/data')
    #     self.options.add(f'-v {os.path.join(self.workspace, project_name)}:/{project_name}')
    #     return self

    # def with_user(self, uid: int, gid: int) -> 'DockerRunOptionsBuilder':
    #     self.options.add(f'--user {uid}:{gid}')
    #     return self


def start_kernel_image(ctx, connection, project_name, kernel_image):
    click.echo(f'This is the connection: {connection}')
    options = DockerRunOptionsBuilder()\
        .with_gpu()\
        .with_privileged()\
        .with_add_devices()\
        .with_display(DISPLAY)\
        .with_shared_memory()\
        .build()

    cxn = parse_kernel_connection(connection)

    if TRACING_HOST and TRACING_PORT:
        tracing_options = f'-e OTEL_EXPORTER_JAEGER_AGENT_HOST={TRACING_HOST} \
                            -e OTEL_EXPORTER_JAEGER_AGENT_PORT={TRACING_PORT}'
    else:
        tracing_options = ''

    cmd = f'docker run --rm --init \
            {options} \
            {tracing_options} \
            --network=container:jupyter \
            --name {project_name}-kernel-{ datetime.now(eastern).strftime("%Y-%m-%d__%H-%M-%S") } \
            {kernel_image} \
            python -m ipykernel_launcher \
                --debug \
                --Session.key={cxn.key.encode("utf-8")} \
                --ip=0.0.0.0 \
                --hb={cxn.hb_port} \
                --shell={cxn.shell_port} \
                --iopub={cxn.iopub_port} \
                --stdin={cxn.stdin_port} \
                --control={cxn.control_port}'.split()
    click.echo(f'About to run command: {cmd}')
    os.execvp(cmd[0], cmd)


def start_kernel(ctx, connection, image_name_prefix: List):
    image_name_prefix.append(get_project_name())
    kernel_image = f"{'/'.join(image_name_prefix)}:{get_project_version()}"
    project_name = get_project_name()
    start_kernel_image(ctx, connection, kernel_image, project_name)


