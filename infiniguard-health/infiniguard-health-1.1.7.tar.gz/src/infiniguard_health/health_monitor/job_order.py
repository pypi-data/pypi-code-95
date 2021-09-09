from .job_runners import (
    JobRunner,
    SleepJobRunner,
    failover_loaders,
    network_loaders,
    state_loaders,
    capacity_loaders,
    lshw_loader,
    snapshot_loaders,
    policy_loader
)

# The jobs are build recursively - so the networking job runs the core job, and the lshw runs the networking job and
# so on.

core_job = JobRunner(failover_loaders + state_loaders + [policy_loader],
                     consecutive_runs=3, sleep_in_between_jobs=10)
networking_job = JobRunner(network_loaders, composite_job_runners=[core_job, SleepJobRunner(5)],
                           consecutive_runs=3, sleep_in_between_jobs=2)
final_composite_job = JobRunner(snapshot_loaders + [lshw_loader] + capacity_loaders,
                                composite_job_runners=[networking_job, SleepJobRunner(5)],
                                consecutive_runs=1, sleep_in_between_jobs=10)

job_order = [final_composite_job]

all_loaders = set()
for job in job_order:
    all_loaders |= job.get_loaders()
