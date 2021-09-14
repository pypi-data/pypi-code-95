import os
import sys
import time
from argparse import Namespace
from datetime import datetime, timedelta

import colorama
from git import InvalidGitRepositoryError
from tabulate import tabulate

from dstack.cli.common import get_job, get_jobs, get_user_info, boto3_client
from dstack.config import get_config, ConfigurationError

DAYS = 30


# TODO: Make it show logs as they come
def logs_func(args: Namespace):
    try:
        dstack_config = get_config()
        # TODO: Support non-default profiles
        profile = dstack_config.get_profile("default")
        user_info = get_user_info(profile)

        client = boto3_client(user_info, 'logs')

        job = get_job(args.run_name_or_job_id, profile)
        if job is not None:
            run_name = job["run_name"]
            job_id = args.run_name_or_job_id
        else:
            run_name = args.run_name_or_job_id
            job_id = None

        table_headers = [
            f"{colorama.Fore.LIGHTMAGENTA_EX}RUN{colorama.Fore.RESET}",
            f"{colorama.Fore.LIGHTMAGENTA_EX}JOB{colorama.Fore.RESET}",
            f"{colorama.Fore.LIGHTMAGENTA_EX}TIMESTAMP{colorama.Fore.RESET}",
            f"{colorama.Fore.LIGHTMAGENTA_EX}MESSAGE{colorama.Fore.RESET}"
        ]
        table_rows = []
        start_query_response = client.start_query(
            logGroupName=f"{user_info['user_name']}/{run_name}",
            startTime=int((datetime.today() - timedelta(days=DAYS)).timestamp()),
            endTime=int(datetime.now().timestamp()),
            queryString="fields @logStream, @timestamp, log | sort @timestamp desc" + (
                f" | filter @logStream = \"{job_id}\"" if job_id is not None else "")
        )
        query_id = start_query_response['queryId']
        response = None
        while response is None or response['status'] == 'Running':
            time.sleep(1)
            response = client.get_query_results(queryId=query_id)

        for result_row in sorted(response['results'], key=lambda r: (r[1]['value'])):
            job_id = result_row[0]['value']
            timestamp = result_row[1]['value']
            message = result_row[2]['value']
            table_rows.append([
                run_name,
                job_id,
                timestamp,
                message
            ])
        print(tabulate(table_rows, table_headers, tablefmt="plain"))

    except InvalidGitRepositoryError:
        sys.exit(f"{os.getcwd()} is not a Git repo")
    except ConfigurationError:
        sys.exit(f"Call 'dstack login' or 'dstack register' first")


def register_parsers(main_subparsers):
    parser = main_subparsers.add_parser("logs", help="Fetch the logs of a run or a job")

    parser.add_argument('run_name_or_job_id', metavar='(RUN | JOB)', type=str)

    parser.set_defaults(func=logs_func)
