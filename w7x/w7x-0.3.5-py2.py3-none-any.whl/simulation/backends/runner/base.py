"""
Local runners tooling.

A local runner may be a local executable, a slurm workload manager or remote runner
interfaced via SSH.

TODO-2(@amerlo): Implement the shh client.
"""

import abc
import dataclasses
import logging
import os
import typing
import subprocess
import time

import rna
from rna.pattern.singleton import Singleton, SingletonMeta
from rna.process import execute
from w7x.config import get_option

LOGGER = logging.getLogger(__name__)


class RunnerBackendMixin:
    def __init__(self):
        self._runner = None
        self.folder = None
        self.exe = None

    @property
    def runner(self):
        return self._runner

    @runner.setter
    def runner(self, runner):
        self._runner = runner

        code = self.__module__.rpartition(".")[-1]
        self.folder = get_option(f"{code}.{runner}", "folder", fallback=True)
        self.exe = get_option(f"{code}.{runner}", "exe")
        assert self.folder is not None
        assert self.exe is not None


def get_sbatch_line(
    key: str, value: str, directive: str = "#SBATCH", new_line: bool = True
):
    """
    Compose a single directive line for a slurm file.
    """

    line = f"{directive} --{key}={value}"

    if new_line:
        line += "\n"

    return line


class AbstractSingleton(abc.ABCMeta, SingletonMeta):
    """
    Abstract singleton metaclass.

    See: http://www.phyast.pitt.edu/~micheles/python/metatype.html
    """

    pass


@dataclasses.dataclass
class Job:
    """
    A generic job.

    Examples:
        >>> from w7x.simulation.backends.runner import Job
        >>> job = Job(name="test", cmd="ll")
        >>> job.to_slurm().startswith("#!/bin/bash -l")
        True

    """

    #: name of the job. This could e.g. be the job name in slurm
    name: str = None
    #: current working directory for the job to be executed. Should be a path.
    cwd: str = None
    #: list of 2-tuples with a storable and the path where to save it.
    files: typing.List[
        typing.Tuple[rna.polymorphism.Storable, str]
    ] = dataclasses.field(default_factory=lambda: [])
    pre: typing.List[str] = dataclasses.field(
        default_factory=lambda: []
    )  # TODO-1(@amerlo) eval to delete
    #: main command to run
    cmd: str = None
    #: overwrite the job folder and file when writing a file to disk
    overwrite: bool = False
    timeout: int = int(get_option("job", "timeout"))  # [s]

    #  Slurm Specific
    #  From: https://slurm.schedmd.com/sbatch.html
    #: instructions over how to use this as executable
    shebang: str = "#!/bin/bash -l"
    #: path to logging.Logger stream handler
    log_path: str = get_option("job", "log_path")  # STDOUT and STDERR
    #: TODO-2(@amerlo): required?
    chdir: str = "./"
    #: batch queue, see https://docs.mpcdf.mpg.de/doc/computing/cobra-user-guide.html
    partition: str = get_option("job", "partition")
    # TODO-2(@amerlo): the three options below: should we put None there and automate the optimum?
    #: the number of MPI processes for the job
    tasks: int = int(get_option("job", "tasks"))
    #: number of computer nodes to use
    nodes: int = int(get_option("job", "nodes"))
    #: the memory required per node
    mem: str = get_option("job", "mem")
    #: a list of modules to load prior to the job execution
    modules: typing.List[str] = dataclasses.field(default_factory=lambda: [])

    def to_slurm(self) -> str:
        """
        Return sbatch script as string.
        """

        slurm = f"{self.shebang}\n"
        slurm += get_sbatch_line("output", self.log_path)  # stdout redirection
        slurm += get_sbatch_line("error", self.log_path)  # stderr redirection
        slurm += get_sbatch_line("chdir", self.chdir)  # initial working directory
        slurm += get_sbatch_line("job-name", self.name)  # job name
        slurm += get_sbatch_line("partition", self.partition)  # Queue ( Partition )
        slurm += get_sbatch_line("nodes", str(self.nodes))  # number of nodes
        slurm += get_sbatch_line(
            "ntasks-per-node", str(self.tasks)
        )  # mpi tasks per node
        slurm += get_sbatch_line("mem", self.mem)  # memory

        str_time = time.gmtime(self.timeout)
        slurm += get_sbatch_line(
            "time", time.strftime("%H:%M:%S", str_time)
        )  # wall clock limit

        slurm += "module purge\n"
        for m in self.modules:
            slurm += f"module load {m}\n"

        for p in self.pre:
            slurm += p + "\n"

        slurm += "srun " + self.cmd

        return slurm

    # TODO-2(@amerlo,@dboe): Consider job.submit instead of submit.
    # TO(@dboe): I understand the idea that a job should know how to run
    #            itself, however, I do not see why a job description should
    #            include the runner information. I downgrade the TODO to "-2",
    #            but we could quickly revert to "-0" and change the interface.
    # def submit(self...):


class RunnerMixin(abc.ABC):
    """
    Runner interface.

    TODO-2(@amerlo, @dboe): consider https://github.com/marian-code/ssh-utilities or similar
    """

    @staticmethod
    @abc.abstractmethod
    def isfile(path: str) -> bool:
        """
        Return True if path is an existing regular file.
        """

    @staticmethod
    @abc.abstractmethod
    def isdir(path: str) -> bool:
        """
        Return True if path is an existing directory.
        """

    @staticmethod
    @abc.abstractmethod
    def makedirs(path: str, mode: int, exist_ok: bool):
        """
        Create directories.
        """

    @staticmethod
    @abc.abstractmethod
    def read_file(path: str) -> bytes:
        """
        Read file.
        """

    @staticmethod
    @abc.abstractmethod
    def write_file(obj, path: str):
        """
        Write object to file.
        """

    @abc.abstractmethod
    def submit(self, job: Job, **kwargs) -> int:
        """
        Submit and execute a job.
        """


@dataclasses.dataclass
class Slurm(RunnerMixin, Singleton, metaclass=AbstractSingleton):
    """
    HPC client.

    Examples:
        >>> import tempfile
        >>> dtemp = tempfile.mkdtemp()
        >>> from w7x.simulation.backends.runner import Slurm, Job
        >>> hpc = Slurm()
        >>> job = Job(name="test", cwd=dtemp, pre=["uname -a"], cmd="ll")
        >>> hpc.submit(job, dry_run=True)
        0

        >>> import shutil
        >>> shutil.rmtree(dtemp)

    """

    @staticmethod
    def isfile(path: str) -> bool:
        """
        Check if path, relative to base folder, is a file.
        """
        return os.path.isfile(path)

    @staticmethod
    def isdir(path: str) -> bool:
        """
        Check if path, relative to base folder, is a directory.
        """
        return os.path.isdir(path)

    @staticmethod
    def makedirs(path, **kwargs):
        """
        Recursive directory creation function.
        """
        return os.makedirs(path, **kwargs)

    @staticmethod
    def read_file(path: str) -> bytes:
        """
        Returns file content in bytes.
        """
        with open(path, "rb") as f:
            return f.read()

    @staticmethod
    def write_file(obj, path: str):
        """
        Read object to file.
        """
        with open(path, "w") as f:
            f.write(obj)

    def submit(self, job: Job, dry_run: bool = False) -> int:
        """
        Submit the job.
        """

        #  Check if job folder exists
        job_dir_path = os.path.join(job.cwd, job.name)
        if not self.isdir(job_dir_path):
            self.makedirs(job_dir_path)

        #  Create job files
        for obj, f in job.files:
            file_path = os.path.join(job_dir_path, f)
            if not self.isfile(file_path) or job.overwrite:
                self.write_file(obj, file_path)

        #  Create slurm file
        slurm_file_path = os.path.join(job_dir_path, "slurm")
        if not self.isfile(slurm_file_path) or job.overwrite:
            self.write_file(job.to_slurm(), slurm_file_path)

        #  Submit job
        cmd = "sbatch slurm"
        if dry_run:
            LOGGER.info(cmd)
            return 0

        #  Submit and retrieve job id
        output = execute(cmd, cwd=job_dir_path, output=True, level=None)[0]
        job_id = output.split(" ")[-1]

        #  Pool to check if job has left the slurm queue
        while job_id in " ".join(
            execute(f"squeue -j {job_id}", output=True, level=None)
        ):
            #  TODO-2(@amerlo): find optimal interval
            time.sleep(10)

        #  TODO-2(@amerlo): if needed, return job state as return code
        return 0


@dataclasses.dataclass
class Local(RunnerMixin, Singleton, metaclass=AbstractSingleton):
    """
    A local client.

    Examples:
        >>> import tempfile
        >>> dtemp = tempfile.mkdtemp()
        >>> from w7x.simulation.backends.runner import Local, Job
        >>> local = Local()
        >>> job = Job(name="test", cwd=dtemp, cmd="touch input")
        >>> local.submit(job)
        0

        >>> import os
        >>> os.path.isfile(os.path.join(dtemp, "test", "input"))
        True

        >>> import shutil
        >>> shutil.rmtree(dtemp)

    """

    @staticmethod
    def isfile(path: str) -> bool:
        """
        Check if path, relative to base folder, is a file.
        """
        return os.path.isfile(path)

    @staticmethod
    def isdir(path: str) -> bool:
        """
        Check if path, relative to base folder, is a directory.
        """
        return os.path.isdir(path)

    @staticmethod
    def makedirs(path, **kwargs):
        """
        Recursive directory creation function.
        """
        return os.makedirs(path, **kwargs)

    @staticmethod
    def read_file(path: str) -> bytes:
        """
        Returns file content in bytes.
        """
        with open(path, "rb") as f:
            return f.read()

    @staticmethod
    def write_file(obj, path: str):
        """
        Read object to file.
        """
        with open(path, "w") as f:
            f.write(obj)

    def submit(self, job: Job, dry_run: bool = False) -> int:
        """
        Submit the job.
        """

        #  Check if job folder exists
        job_dir_path = os.path.join(job.cwd, job.name)
        if not self.isdir(job_dir_path):
            self.makedirs(job_dir_path)

        #  Create job files
        for obj, f in job.files:
            file_path = os.path.join(job_dir_path, f)
            if not self.isfile(file_path) or job.overwrite:
                self.write_file(obj, file_path)

        #  Create job logger
        log = logging.getLogger(job.name)
        log.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.join(job_dir_path, job.log_path))
        log.addHandler(handler)

        #  Execute pre and append output and error to log files
        for pre in job.pre:
            if dry_run:
                LOGGER.info(pre)
            else:
                try:
                    execute(pre, cwd=job_dir_path, logger=log)
                except subprocess.CalledProcessError as e:
                    LOGGER.info(e)
                    return e.returncode

        #  Check if mpirun is available
        if execute("which mpirun", output=True)[0] != "":
            nproc = int(execute("nproc", output=True)[0])
            if job.tasks < nproc:
                nproc = job.tasks
            cmd = f"mpirun -np {nproc} {job.cmd}"

        #  Execute the main command
        if dry_run:
            LOGGER.info(cmd)
            return 0

        try:
            execute(
                cmd,
                cwd=job_dir_path,
                stdin=subprocess.DEVNULL,
                logger=log,
                timeout=job.timeout,
            )
        except subprocess.CalledProcessError as e:
            LOGGER.info(e)
            return e.returncode

        return 0


def get_runner(runner: str):
    """
    Instantiate a runner as singleton.

    Examples:
        >>> from w7x.simulation.backends.runner.base import get_runner
        >>> l1 = get_runner("local")
        >>> l2 = get_runner("local")
        >>> id(l1) == id(l2)
        True

        >>> get_runner("i_am_not_available")
        Traceback (most recent call last):
        ValueError: Requested runner i_am_not_available is not available.

    """

    runners = {"local": Local, "slurm": Slurm}
    if runner in runners:
        return runners[runner]()
    else:
        raise ValueError(f"Requested runner {runner} is not available.")


def submit(runner: str, job: Job, **kwargs) -> int:
    """
    Submit a job to the runner.
    """
    runner = get_runner(runner)
    return runner.submit(job, **kwargs)


def isfile(runner: str, path: str) -> bool:
    runner = get_runner(runner)
    return runner.isfile(path)


def isdir(runner: str, path: str) -> bool:
    runner = get_runner(runner)
    return runner.isdir(path)


def read_file(runner: str, path: str) -> bytes:
    runner = get_runner(runner)
    return runner.read_file(path)


# import paramiko


# def get_ssh_client():
#     """
#     Get a ssh client.
#     """
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
#     return ssh


# @dataclasses.dataclass
# class SSHBackend(SlurmBackend):
#     """
#     A SSH Backend.
#     """

#     host: str = None
#     user: str = None
#     pswd: str = None

#     ssh: paramiko.SSHClient = None

#     def __post_init__(self):
#         if not self.local:
#             self.ssh = get_ssh_client()

#     def connect(self):
#         self.ssh.connect(self.host, username=self.user, password=self.pswd)

#     def exec_command(self, cmd: str):
#         self.ssh.exec_command(cmd)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
