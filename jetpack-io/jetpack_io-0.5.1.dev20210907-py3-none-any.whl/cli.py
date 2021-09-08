import json
import sys

import redis
import schedule
from google.protobuf import json_format
from jetpack import utils
from jetpack._job.job import Job
from jetpack.models.runtime import cronjob_pb2, describe_pb2, job_pb2


def describe_output(app):
    # Should these be the same? The concepts are really similar.
    cron_jobs = []
    jobs = []
    for job in schedule.get_jobs():

        if job.at_time is not None:
            target_time = job.at_time.isoformat()
        else:
            target_time = None

        if job.start_day is not None:
            target_day_of_week = cronjob_pb2.DayOfWeek.Value(job.start_day.upper())
        else:
            target_day_of_week = None

        cron_jobs.append(
            cronjob_pb2.CronJob(
                function=utils.job_name(job),
                target_time=target_time,
                target_day_of_week=target_day_of_week,
                unit=cronjob_pb2.Unit.Value(job.unit.upper()),
                interval=job.interval,
            )
        )

    for job in Job.defined_jobs():
        jobs.append(
            job_pb2.Job(
                qualified_symbol=job.name(),
            )
        )

    try:
        enum_name = app.__class__.__name__.upper() if app is not None else "NONE"
        framework = describe_pb2.Framework.Value(enum_name)
    except ValueError:
        framework = describe_pb2.Framework.Value("UNKNOWN")

    return describe_pb2.DescribeOutput(
        cron_jobs=cron_jobs,
        jobs=jobs,
        framework=framework,
    )


class JobNotFoundError(Exception):
    pass


# TODO(Landau): Use a framework? Like https://click.palletsprojects.com/en/7.x/
def handle(app=None):
    run(app=app, cli_args=sys.argv)


# TODO(Landau): Use a framework? Like https://click.palletsprojects.com/en/7.x/
def run(app=None, cli_args=[]):
    """
    Call individual function: `python jetpack_main.py run func_name`
    With args: `python jetpack_main.py run func_name base_64_args`
    """
    if (len(cli_args) == 3 or len(cli_args) == 4) and cli_args[1] == "run":
        target_job_name = cli_args[2]
        target_job = Job.find_job(target_job_name)
        if target_job:
            if len(cli_args) == 4:
                target_job.exec(cli_args[3])
            else:
                target_job.exec()
            return

        for job in schedule.get_jobs():
            if utils.job_name(job) == target_job_name:
                target_job = job
                job.job_func()

        if not target_job:
            raise JobNotFoundError(f'Target job "{target_job_name}" not found')

    """
    Get all jobs `python jetpack_main.py describe`
    """
    if len(cli_args) == 2 and cli_args[1] == "describe":
        print(json_format.MessageToJson(describe_output(app)))

    """
    Get all jobs `python jetpack_main.py describe-to-redis`
    """
    if len(cli_args) == 4 and cli_args[1] == "describe-to-redis":
        host = cli_args[2]
        key = cli_args[3]
        r = redis.Redis(host=host, port=6379, db=0)
        r.set(key, json_format.MessageToJson(describe_output(app)))
