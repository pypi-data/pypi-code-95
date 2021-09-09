import logging
from time import sleep
from infiniguard_health.jobs.monitor_jobs import monitor_job
from infiniguard_health.data_collection.loaders import LOADER_IDS

_logger = logging.getLogger(__name__)

capacity_loaders = [LOADER_IDS.snapshots_capacity_loader, LOADER_IDS.dde_capacity_loader]  # To be run every cycle

snapshot_loaders = [LOADER_IDS.snapshots_loader, LOADER_IDS.snapshot_suspend_delete_loader]

policy_loader = LOADER_IDS.policies_loader

network_loaders = [LOADER_IDS.ethtool_loader,
                   LOADER_IDS.fcports_gc_loader,
                   LOADER_IDS.fcports_sysfs_loader,
                   LOADER_IDS.fcports_lspci_loader,
                   LOADER_IDS.fcports_driver_version_loader,
                   LOADER_IDS.fcports_sfp_info_loader,
                   LOADER_IDS.syscli_ethernet_loader,
                   LOADER_IDS.bonds_loader,
                   ]

lshw_loader = LOADER_IDS.lshw_loader

failover_loaders = [
    LOADER_IDS.volumes_loader,
    LOADER_IDS.role_loader,
    LOADER_IDS.ibox_connectivity_loader,
    LOADER_IDS.remote_ddes_loader,
    LOADER_IDS.remote_idracs_loader,
    LOADER_IDS.services_loader,
]

# The data from these loaders set the state of the ports
state_loaders = [LOADER_IDS.fcports_sysfs_loader, LOADER_IDS.ethtool_loader,
                 LOADER_IDS.syscli_ethernet_loader]


class JobRunner:
    """
    Defines a health job, with a certain type of source collectors.
    Holds the amount of consecutive times this Job should be run, and the amount of sleep in between.
    when run_job() is called, runs the defined job x times in a row, with sleep in between (when x is consecutive_runs)
    """

    def __init__(self, source_loader_ids, composite_job_runners=None, consecutive_runs=1, sleep_in_between_jobs=0):
        """
        :param source_loader_ids: A list of source collection ids (as strings). Eliminates duplicates.
        :param composite_job_runners: An optional list of JobRunner objects.
        These will be run before the source loaders are run, allowing constructing a JobRunner in a recursive way.
        :param consecutive_runs: Number of times in a row that this JobRunner should be run
        :param sleep_in_between_jobs: Sleep amount in between each consecutive run, given in seconds
        """
        self.source_loaders_ids = list(set(source_loader_ids))
        self.composite_job_runners = composite_job_runners or []
        self.consecutive_runs = consecutive_runs
        self.sleep_in_between_jobs = sleep_in_between_jobs

    def run_monitor_jobs(self, current_system_state, message_queue):
        """
        Runs the current job, several times consecutively (according to the given field).
        if there are composite job runners, runs these first, before running the current job.

        :param current_system_state: SystemState object holding the current state. To be used for comparison.
        :param message_queue: MessageQueue object for dispatching messages following
        :return: The new system state as created by the monitor jobs
        """
        _logger.info(f"Running {self} {self.consecutive_runs} times in a row")
        for _ in range(self.consecutive_runs):
            for job_runner in self.composite_job_runners:
                current_system_state = job_runner.run_monitor_jobs(current_system_state, message_queue)

            _logger.info(f"Running health monitor job with sources: {self.source_loaders_ids}")
            current_system_state = monitor_job(current_system_state, self.source_loaders_ids, message_queue)

            _logger.debug(f"Sleeping for {self.sleep_in_between_jobs} seconds in between iterations of {self}")
            sleep(self.sleep_in_between_jobs)

        return current_system_state

    def get_loaders(self):
        """
        Returns all loaders contained in this JobRunner, and all loaders contained in all the JobRunners held
        recursively. Returns a set, thus eliminating duplicates.
        """
        loaders = set(self.source_loaders_ids)

        for job_runner in self.composite_job_runners:
            loaders |= job_runner.get_loaders()

        return loaders

    def __str__(self):
        return f"<JobRunner of {self.source_loaders_ids}>"


class SleepJobRunner:
    """
    A dummy job runner that sleeps the given amount of seconds
    """

    def __init__(self, sleep_in_between_jobs):
        self.sleep_in_between_jobs = sleep_in_between_jobs

    def run_monitor_jobs(self, system_state, *_):
        """
        Performs sleep of the set amount of seconds.
        Receives a system state and returns the same system state. This allows this job to be used in the
        same way as a JobRunner.
        """
        _logger.debug(f"Sleeping for {self.sleep_in_between_jobs} seconds in between different JobRunners")
        sleep(self.sleep_in_between_jobs)

        return system_state

    def get_loaders(self):
        return set()
