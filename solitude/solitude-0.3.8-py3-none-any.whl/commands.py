import hashlib
import logging
from typing import Any, Dict, List, Optional

from solitude import TOOL_NAME
from solitude.slurmjob import SlurmJob, query_all_slurmjobs
from solitude.cache import Cache
from solitude import hookimpl
from solitude.utils.ssh import SSHClient


def md5(s) -> str:
    return hashlib.md5(s.encode()).hexdigest()


class CommandBase(object):
    def __init__(
        self, cmd: str, plugin: hookimpl, cache: Optional[Cache] = None
    ):
        self.logger: logging.Logger = logging.getLogger(type(self).__name__)
        self._plugin: hookimpl = plugin
        self.cmd: str = cmd.strip()
        self.cache: Optional[Cache] = cache
        self.hash: str = md5(
            self.get_plugin_short_name()
            + self._plugin.get_command_hash(self.cmd)
        )
        self.job_info: Optional[SlurmJob] = None
        self._set_basic_job_info_from_cache()
        self._state: Dict[str, Any] = {}
        self.errors: List[str] = []

    def get_plugin_short_name(self) -> str:
        return self._plugin.__name__.rsplit(".", 2)[-1].replace(
            f"{TOOL_NAME}_", ""
        )

    def update(self, ssh_client: SSHClient):
        self.update_job_info(ssh_client=ssh_client)
        self.update_state()
        self.update_errors()

    def update_state(self):
        self._state = self._plugin.retrieve_state(self.cmd)

    def update_errors(self):
        self.errors = self._update_errors()

    def _set_basic_job_info_from_cache(self):
        self.job_info = None
        if self.cache is not None and self.hash in self.cache:
            entry = self.cache[self.hash]
            self.job_info = entry

    def update_job_info(self, ssh_client: SSHClient):
        if self.cache is not None and self.hash in self.cache:
            try:
                cached_job = self.cache[self.hash]
                if not isinstance(cached_job, SlurmJob):
                    raise ValueError(
                        f"Unexpected Cached object found! Should be of type SlurmJob! Found: {type(cached_job)}"
                    )
                job_info = SlurmJob(ssh_client=ssh_client, jobid=cached_job.id)
                job_info.update()
                self.job_info = job_info
            except ValueError:
                self.job_info = None
            except Exception as e:
                self.logger.warning(
                    "Job with id: {} has no job_info: {}".format(self.hash, e)
                )
                raise e

    def _update_errors(self):
        if (
            self.has_job_link()
            and not self.job_info.is_running()
            and not self.is_finished()
        ):
            try:
                joblog = self.job_info.get_log_text()
                errors = self._plugin.get_errors_from_log(log=joblog)
                return errors
            except Exception as e:
                self.logger.error(
                    f"Exception while fetching errors from log: {e}"
                )
        return []

    def has_job_link(self) -> bool:
        return self.job_info is not None

    def get_job_status_str(self) -> str:
        if self.job_info is not None:
            if self.job_info.is_pending():
                return "PEND"
            elif self.job_info.is_timeout():
                return "TIME"
            elif self.is_running():
                return "RUN"
        if self.is_erroneous():
            return "ERR!"
        elif self.is_finished():
            return "."
        return "IDLE"

    def __str__(self) -> str:
        self._errors: List[str] = []
        priority = ""
        if self.job_info is not None:
            if self.is_running() and self.job_info.priority == "high":
                priority = "H*"
        return "{status:4}{priority:2} {plugin:10} {tag} {errors}".format(
            plugin=self.get_plugin_short_name(),
            tag=self.get_job_info_str(),
            status=self.get_job_status_str(),
            priority=priority,
            errors=f'!!ERRORS: {" ".join(self.errors)}!!'
            if self.is_erroneous()
            else "",
        )

    @staticmethod
    def header_str() -> str:
        return (
            "id  {status:6} {plugin:10} {info}".format(
                plugin="plugin", info="job_info", status="status"
            )
            + "\n"
            + "--  {status:6} {plugin:10} {info}".format(
                plugin="------", info="--------", status="------",
            )
        )

    def is_running(self) -> bool:
        return self.job_info is not None and self.job_info.is_running()

    def is_finished(self) -> bool:
        return self._plugin.is_command_job_done(
            cmd=self.cmd, state=self._state
        )

    def is_erroneous(self) -> bool:
        return any(self.errors)

    def get_job_info_str(self) -> str:
        return self._plugin.get_command_status_str(
            cmd=self.cmd, state=self._state
        )


def update_jobinfo_for_multiple_commands(
    commands: List[CommandBase], ssh_client: SSHClient
):
    commands_with_joblinks = [
        e.job_info for e in commands if e.job_info is not None
    ]
    status_info = query_all_slurmjobs(
        job_ids=[job_info.id for job_info in commands_with_joblinks],
        ssh_client=ssh_client,
    )
    for job_info in commands_with_joblinks:
        job_info._set_state_from_dict(dic=status_info.get(job_info.id, None))
        job_info._ssh_client = ssh_client
