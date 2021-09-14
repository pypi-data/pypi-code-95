from typing import Dict, Optional, Type, List

import logging
import time
import re

from solitude.cache import CacheData
from solitude.utils.ssh import SSHClient


SLURM_JOBINFO_QUERY = '/opt/slurm/bin/squeue --jobs={jobid} --format="%.18i %.9P %.8j %.10T %.10M %R" -h'
SLURM_JOBINFO_PATTERN = re.compile(
    r"\s+(?P<jobid>\d+)\s+dlc-(?P<priority>\S+)\s+(?P<user>\S+)-(?P<ticket>\S*)"
    r"\s+(?P<status>\S+)\s+(?P<runtime>\S+)\s+(?P<machine>[\S()-]+)"
)
logger = logging.getLogger("SlurmJob")


class SlurmJob(CacheData):
    def __init__(
        self,
        jobid: int,
        user: Optional[str] = None,
        priority: Optional[str] = None,
        timestamp: Optional[int] = None,
        ssh_client: Optional[SSHClient] = None,
    ):
        super(SlurmJob, self).__init__(timestamp=timestamp)
        self.id: int = jobid
        self.user: Optional[str] = user
        self.priority: Optional[str] = priority
        self._status: Optional[str] = None
        self._ssh_client: Optional[SSHClient] = ssh_client

    def update(self):
        if self._ssh_client is None:
            raise ValueError("update - ssh_client was not set")
        result, _ = self._ssh_client.exec_command(
            cmd_to_execute=SLURM_JOBINFO_QUERY.format(jobid=self.id)
        )
        match_result = re.match(SLURM_JOBINFO_PATTERN, result)
        info_dict = None if match_result is None else match_result.groupdict()
        self._set_state_from_dict(dic=info_dict)

    def is_running(self) -> bool:
        return self._status in ("RUNNING", "PENDING")

    def is_pending(self) -> bool:
        return self._status == "PENDING"

    def is_timeout(self) -> bool:
        return self._status == "TIMEOUT"

    def get_log_text(self, active_polling: bool = False) -> str:
        if self._ssh_client is None:
            raise ValueError("get_log_text - ssh_client was not set")
        result = self._ssh_client.exec_command(
            cmd_to_execute=f"{'cat' if not active_polling else 'tail -f'} /mnt/cluster_storage/logfiles/slurm-{self.id}.out",
            active_polling=active_polling,
        )
        assert result is not None
        return result[0]

    def _set_state_from_dict(self, dic: Optional[Dict] = None):
        if dic is None:
            self.__set_idle_status()
        else:
            assert self.id == int(dic["jobid"])
            self.id = int(dic["jobid"])
            self.user = dic["user"]
            self.priority = dic["priority"]
            self._status = dic["status"]

    def to_dict(self) -> Dict:
        return dict(
            id=self.id,
            user=self.user,
            priority=self.priority,
            timestamp=self.timestamp,
        )

    def __set_idle_status(self):
        self._status = "IDLE"
        self.user = None
        self.priority = None

    def exists(self) -> bool:
        if self._ssh_client is None:
            raise ValueError("exists - ssh_client was not set")
        return SlurmJob.check_if_job_exists(
            ssh_client=self._ssh_client, jobid=self.id
        )

    @staticmethod
    def check_if_job_exists(ssh_client: SSHClient, jobid: int) -> bool:
        result = ssh_client.exec_command(
            cmd_to_execute=SLURM_JOBINFO_QUERY.format(jobid=jobid)
        )
        assert result is not None
        return re.match(SLURM_JOBINFO_PATTERN, result[0]) is not None

    @classmethod
    def from_dict(cls: Type, dic: Dict) -> "SlurmJob":
        return SlurmJob(
            jobid=dic["id"],
            user=dic["user"],
            priority=dic["priority"],
            timestamp=dic.get("timestamp", int(time.time())),
        )


def query_all_slurmjobs(
    job_ids: List[int], ssh_client: SSHClient
) -> Dict[int, Dict]:
    query = SLURM_JOBINFO_QUERY.format(jobid=",".join(map(str, job_ids)))
    result = ssh_client.exec_command(cmd_to_execute=query)
    if result is None or not isinstance(result[0], str):
        raise ValueError(
            f"SSH query for {len(job_ids)} slurmjobs returned an unexpected value '{result}'"
        )
    stdout_result = result[0]
    match_results = re.findall(SLURM_JOBINFO_PATTERN, stdout_result)
    if any(match_results):
        return {
            int(r[0]): dict(jobid=r[0], priority=r[1], user=r[2], status=r[4])
            for r in match_results
        }
    else:
        return {}
