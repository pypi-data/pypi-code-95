import os
import subprocess
import sys
from importlib.machinery import ModuleSpec, PathFinder
from inspect import getattr_static, getcomments, getdoc, getmembers, isfunction
from typing import Callable, Dict, List, Optional, Union


class _UnsupportedCommand(Exception):
    pass


class _TaskError(Exception):
    pass


class _InternalError(Exception):
    pass


class _CustomFinder(PathFinder):
    """
    Allows us to import a file in the current diectory, that is
    the directory the file is run in. the tasks.py file should
    always be run from it's own dir, for now

    https://stackoverflow.com/a/44788410
    """

    _path = [os.getcwd()]

    @classmethod
    def find_spec(cls, fullname, path=None, target=None) -> Optional[ModuleSpec]:
        return super().find_spec(fullname, cls._path, target)


sys.meta_path.append(_CustomFinder)  # type: ignore


class Output:
    def __init__(self):
        self.stdout: str
        self.stderr: str
        self.status: int


class _Taskr:
    def __init__(self, module) -> None:
        self.module = module
        self.funcs: Dict[str, Callable] = {}
        self._default = ""
        self._get_tasks()
        self._check_default()

    def _check_default(self) -> None:
        """
        Runs a simple check for the efault keyword, and it a user sets it
        then mark it
        """

        try:
            self._default = getattr_static(self.module, "DEFAULT")
        except AttributeError:
            self._default = ""

    def _get_tasks(self) -> None:
        """
        Internal function that pulls every function from a module
        and matches it with a name, basically the core
        """
        funcs = getmembers(self.module, isfunction)
        transformed = dict(
            (name, method) for name, method in funcs if not name.startswith("_")
        )

        self.funcs = transformed

    @staticmethod
    def init() -> None:
        """
        Generates a default task file
        """
        from taskr.template import template

        filename = "tasks.py"

        if os.path.exists(filename):
            print("Task file already exists, skipping generation")
            return

        with open(filename, "w") as file:
            file.write(template)

        print(f"Generated sample task file {filename}")

    def list(self) -> None:
        """
        Lists available tasks

        On initialization we get a dictionary of names to functions
        This will loop through the names, and try to grab the docstrings
        of the functions and display them

        If there is a default function defines, we mark it
        """

        if len(self.funcs) == 0:
            raise _InternalError("No functions defined or found")

        longest = len(max(self.funcs.keys(), key=len))
        print("\nTasks:")

        for name, func in self.funcs.items():
            if name == self._default:
                name = "*" + name

            # Try to find documentation for the function
            doc = None
            docString = getdoc(func)
            docPreceed = getcomments(func)
            if docPreceed:
                doc = docPreceed.replace("#", "").strip()
            if docString:
                doc = docString.replace("\n", "").strip()
            if not doc:
                doc = "No comment"

            print(f" {name:<{longest+1}}: {doc}")
        print("\n* = default")

    def process(self, task: str) -> None:
        """
        Given a task name, runs the function if it exists
        """
        if known := self.funcs.get(task):
            try:
                known()
            except Exception as e:
                print(f"Error running task {task}: {e}")
        else:
            print(f"Unknown task: {task}")

    def hasDefault(self) -> bool:
        """
        Let's the CLI know if we can run a default command
        """
        return self._default != ""

    def default(self) -> bool:
        """
        Runs the default task, if it's defined
        """
        if self._default:
            if self._default not in self.funcs:
                raise _TaskError(f"Task {self._default} is not defined")

            self.funcs.get(self._default)()  # type: ignore
            return True
        else:
            print("No default defined")
            return False


def _transform_cmd(cmd: Union[str, List[str]]) -> str:
    runCmd = ""
    if type(cmd) == list:
        runCmd = " ".join(cmd)
    elif type(cmd) == str:
        runCmd = str(cmd)
    else:
        raise _UnsupportedCommand(f"Unsupported command type: {type(cmd)}")

    return runCmd


def _get_env(env: Optional[dict]) -> dict:
    if env:
        env = {**env, **os.environ.copy()}
    else:
        env = os.environ.copy()

    return env


def run(cmd: Union[str, List[str]]) -> bool:
    """
    Runs a simple command, takes a list or string
    Returns whether the command has a normal exit (True), or not (False)
    """
    runCmd = _transform_cmd(cmd)
    return run_env(runCmd)


def run_env(cmd: Union[str, List[str]], env: Optional[dict] = None) -> bool:
    """
    Runs a command, with optional environment variables passed

    This also attaches a copy of the users environment variables for every run
    This makes tasks work in a virtual env too, if the task calls a module only installed
    in one (e.g. python -m my_module_I_installed_in_this_venv)

    Returns whether the command has a normal exit (True), or not (False)

    """

    runCmd = _transform_cmd(cmd)
    env = _get_env(env)

    return subprocess.Popen(runCmd, shell=True, env=env).wait() == 0


def run_output(cmd: Union[str, List[str]], env: Optional[dict] = None) -> Output:
    """
    Returns the status of the call, as well as the output
    TODO - combine this with run_env. Will be a bit weird
    """

    runCmd = _transform_cmd(cmd)
    env = _get_env(env)

    res = subprocess.run(runCmd, shell=True, capture_output=True, env=env)

    data = Output()
    data.stdout = res.stdout.decode("utf-8").rstrip()
    data.stderr = res.stderr.decode("utf-8").rstrip()
    data.status = res.returncode == 0

    return data


def run_conditional(*args: Callable) -> bool:
    """
    Runs functions in orders, on the condition the previous passes
    Functions must return a status, (True or False)

    Returns whether the command has a normal exit (True), or not (False)

    """
    for f in args:
        if not callable(f):
            print(f"{f} is not callable")
            return False
        print(f"▸ Running {f.__name__}")
        ret = f()
        # Support void functions
        if ret is None:
            return True
        if not ret:
            print(f"Task {f.__name__} failed, bailing")
            return False
    return True
