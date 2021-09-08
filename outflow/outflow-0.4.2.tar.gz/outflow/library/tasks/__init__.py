# -*- coding: utf-8 -*-
import os
import pathlib
import tempfile
from subprocess import PIPE, STDOUT, Popen
from typing import Dict, Iterable, List, Union

from outflow.core.logging import logger
from outflow.core.pipeline import context
from outflow.core.target import Target
from outflow.core.tasks import Task

from .control_flow_tasks import IdentityTask, IfThenElse, MergeTask  # noqa: F401
from .generic_map_task import MapTask

__all__ = [
    "IfThenElse",
    "IdentityTask",
    "MergeTask",
    "PipelineArgs",
    "PopenTask",
    "ExecuteShellScripts",
    "IPythonTask",
    "MapTask",
]


class PipelineArgs(Task):
    def __init__(self, *args, only: Union[None, Iterable] = None, **kwargs):
        """Task used to extract the pipeline arguments and pass them to the next task

        Args:
            only (Union[None, Iterable], optional): If specified, create targets only for the pipeline arguments listed. Defaults to None.
        """
        self.untracked_task = True
        super().__init__(*args, auto_outputs=False, **kwargs)
        self._update_outputs(only=only)

    def _update_outputs(self, only: Union[None, Iterable] = None):
        """Update target outputs using pipeline arguments

        Args:
            only (Union[None, Iterable], optional): If specified, create targets only for the pipeline arguments listed. Defaults to None.
        """
        self.outputs = {}

        keys = vars(context.args) if only is None else only

        for key in keys:
            self.outputs.update({key: Target(name=key)})

    def run(self):
        """Return the pipeline arguments as task outputs"""
        pipeline_args = {}

        # return value using the pipeline args
        for key in self.outputs:
            pipeline_args[key] = getattr(context.args, key)
        return pipeline_args

    def check_inputs(self, task_inputs):
        pass


@Task.as_task(with_self=False)
def PopenTask(
    command: Union[str, List, pathlib.Path],
    use_system_shell: bool = False,
    env: Dict = {},
):
    """Wrapper task for subprocess.Popen

    With 'use_system_shell=True', if the 'command' argument is:
      - a string, it is executed directly through the system shell.
      - a list, the command element are passed to Popen as follow: Popen(['/bin/sh', '-c', command[0], command[1], ...]) (On a POSIX system)

    Args:
        command (Union[str, List, pathlib.Path]): a list of program arguments, a single string or path-like object
        use_system_shell (bool, optional): specifies whether to use the system shell to execute the command. If True, it is recommended to pass the command as a string rather than as a list. Defaults to False.
        env (Dict, optional): a mapping that defines the environment variables for the command. Defaults to {}.

    """
    current_env = os.environ.copy()
    current_env.update(env)
    process = Popen(command, shell=use_system_shell, env=current_env)
    process.wait()
    return_code = process.returncode
    if return_code:
        msg = f"Command failed with exit code {return_code}"
        raise Exception(msg)


@Task.as_task(with_self=False)
def ExecuteShellScripts(
    shell_scripts: Iterable[str],
    env=None,
    shell: Union[str, None] = None,
    encoding: str = "utf-8",
):
    """Execute a sequence of shell scripts in the same process

    Args:
        shell_scripts (Iterable[str]): sequence of plain text shell scripts
        env (Dict, optional): a mapping that defines the environment variables for the command. Defaults to {}.
        shell (str, optional): the shell used to execute the scripts. Defaults to 'bash'.
        encoding (str, optional): the file encoding. Defaults to 'utf-8'.

    Raises:
        Exception: raise for non-zero return code
    """
    if env is None:
        env = {}
    tmp = tempfile.NamedTemporaryFile(prefix="outflow_", delete=False)

    for script in shell_scripts:
        tmp.write(script.encode(encoding))
        tmp.write("\n".encode(encoding))
    tmp.flush()

    current_env = os.environ.copy()
    current_env.update(env)

    if shell is None:
        use_system_shell = True
        popen_args = tmp.name
    else:
        use_system_shell = False
        popen_args = [shell, tmp.name]

    tmp.close()

    os.chmod(tmp.name, 0o0700)

    with Popen(
        popen_args, stdout=PIPE, stderr=STDOUT, env=current_env, shell=use_system_shell
    ) as process:
        output, error = process.communicate()
        logger.debug(output)
        if error:
            logger.error(error)
        return_code = process.returncode
    os.remove(tmp.name)
    if return_code:
        msg = f"Command failed with exit code {return_code}"
        raise Exception(msg)


@IdentityTask.as_task(with_self=True)
def IPythonTask(self, *args, **kwargs):
    from IPython import start_ipython

    start_ipython(argv=[], user_ns={**locals(), **globals()})

    return kwargs
