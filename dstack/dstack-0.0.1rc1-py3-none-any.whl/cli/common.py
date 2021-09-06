import collections
import hashlib
import os
import typing as ty
from itertools import groupby
from pathlib import Path

import boto3
import colorama
import yaml
from boto3.s3 import transfer
from git import Repo, InvalidGitRepositoryError
from requests import request
from tabulate import tabulate
from tqdm import tqdm


def load_variables():
    root_folder = Path(os.getcwd()) / ".dstack"
    if root_folder.exists():
        variable_file = root_folder / "variables.yaml"
        if variable_file.exists():
            variable_root = yaml.load(variable_file.open(), Loader=yaml.FullLoader)
            variables = variable_root.get("variables")
            return variables
        else:
            return []
    else:
        return []


def load_repo_data():
    # TODO: Allow to override the current working directory, e.g. via --dir
    cwd = os.getcwd()
    # TODO: Handle if git repo is not available
    repo = Repo(cwd)
    # TODO: Doesn't support private repos
    # TODO: Doesn't support custom SSH certificates
    # TODO: Doesn't support custom SSH hostnames
    repo_branch = repo.active_branch.name
    repo_hash = repo.head.object.hexsha
    # TODO: Doesn't support if no remote is configured or branch is untracked
    remote_name = repo.active_branch.tracking_branch().remote_name
    repo_url = repo.remote(remote_name).url

    # TODO: Doesn't support untracked changes
    repo_diff = repo.git.diff("--staged")
    return repo_url, repo_branch, repo_hash, repo_diff


def load_workflows():
    root_folder = Path(os.getcwd()) / ".dstack"
    if root_folder.exists():
        workflows_file = root_folder / "workflows.yaml"
        if workflows_file.exists():
            workflows_root = yaml.load(workflows_file.open(), Loader=yaml.FullLoader)
            workflows = workflows_root.get("workflows")
            return workflows
        else:
            return []
    else:
        return []


def pretty_date(time: ty.Any = False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "now"
        if second_diff < 60:
            return str(second_diff) + " sec ago"
        if second_diff < 120:
            return "1 min ago"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + " mins ago"
        if second_diff < 7200:
            return "1 hour ago"
        if second_diff < 86400:
            return str(round(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def headers_and_params(profile, run_name, require_repo=True):
    headers = {}
    if profile.token is not None:
        headers["Authorization"] = f"Bearer {profile.token}"
    params = {
    }
    try:
        repo_url, _, _, _ = load_repo_data()
        params["repo_url"] = repo_url
    except InvalidGitRepositoryError as e:
        if require_repo:
            raise e
    if run_name is not None:
        params["run_name"] = run_name
    return headers, params


# TODO: Add a parameter repo_url
def get_jobs(run_name: ty.Optional[str], profile):
    headers, params = headers_and_params(profile, run_name, False)
    response = request(method="GET", url=f"{profile.server}/jobs/query", params=params, headers=headers,
                       verify=profile.verify)
    response.raise_for_status()
    jobs = sorted(response.json()["jobs"], key=lambda job: (job["updated_at"]))
    return jobs


def get_runs(args, profile):
    headers, params = headers_and_params(profile, args.run_name, False)
    if args.n is not None:
        params["n"] = args.n
    response = request(method="GET", url=f"{profile.server}/runs/query", params=params, headers=headers,
                       verify=profile.verify)
    response.raise_for_status()
    runs = sorted(response.json()["runs"], key=lambda job: (job["updated_at"]))
    return runs


def get_runners(profile):
    headers, params = headers_and_params(profile, None, require_repo=False)
    response = request(method="GET", url=f"{profile.server}/runners/query", params=params, headers=headers,
                       verify=profile.verify)
    response.raise_for_status()
    runs = sorted(response.json()["runners"], key=lambda job: (job["updated_at"]))
    return runs


def get_job(job_id, profile):
    headers, params = headers_and_params(profile, None)
    response = request(method="GET", url=f"{profile.server}/jobs/{job_id}", params=params, headers=headers,
                       verify=profile.verify)
    if response.status_code == 200:
        return response.json()["job"]
    elif response.status_code == 404:
        return None
    else:
        response.raise_for_status()


def print_runs(profile):
    runs = get_runs({}, profile)
    table_headers = [
        f"{colorama.Fore.LIGHTMAGENTA_EX}RUN{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}WORKFLOW{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}RUNNER{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}STATUS{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}STARTED{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}DURATION{colorama.Fore.RESET}"
    ]
    table_rows = []
    for run in runs:
        duration, started_at = pretty_duration_and_started_at(run)
        status = run["status"].upper()
        table_rows.append([
            colored(status, run["run_name"]),
            colored(status, run["workflow_name"]),
            colored(status, run["runner_name"] or "-"),
            colored(status, status),
            colored(status, started_at),
            colored(status, duration)
        ])
    print(tabulate(table_rows, headers=table_headers, tablefmt="plain",
                   colalign=("left", "left", "center", "center", "center", "center")))


def print_jobs(run_name: ty.Optional[str], profile):
    jobs = get_jobs(run_name, profile)
    table_headers = [
        f"{colorama.Fore.LIGHTMAGENTA_EX}JOB{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}RUN{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}WORKFLOW{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}RUNNER{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}STATUS{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}STARTED{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}DURATION{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}ARTIFACTS{colorama.Fore.RESET}"
    ]
    table_rows = []
    for job in jobs:
        duration, started_at = pretty_duration_and_started_at(job)
        status = job["status"].upper() if job["previous_job_ids"] is None or job[
            "status"].upper() != "SUBMITTED" else "PENDING"
        table_rows.append([
            colored(status, job["job_id"]),
            colored(status, job["run_name"]),
            colored(status, job["workflow_name"]),
            colored(status, job["runner_name"] or "-"),
            colored(status, status),
            colored(status, started_at),
            colored(status, duration),
            colored(status, __job_artifacts(job["artifact_paths"]))
        ])
    print(tabulate(table_rows, headers=table_headers, tablefmt="plain",
                   colalign=("left", "left", "left", "center", "center", "center", "center", "left")))


def print_runs_and_jobs(profile, args):
    runs = get_runs(args, profile)
    runs_by_name = dict([(run_name, list(run)[0]) for run_name, run in groupby(runs, lambda run: run["run_name"])])
    jobs_by_run_name = dict(
        [(run["run_name"], get_jobs(run["run_name"], profile)) for run in runs])
    sorted_jobs_by_run_name = sorted(
        [(run_name, sorted(run_jobs, key=lambda job: job["updated_at"])) for run_name, run_jobs in
         jobs_by_run_name.items()],
        key=lambda run_name_and_jobs: run_name_and_jobs[1][-1]["updated_at"] if len(run_name_and_jobs[1]) > 0 else
        runs_by_name[run_name_and_jobs[0]]["updated_at"])
    table_headers = [
        f"{colorama.Fore.LIGHTMAGENTA_EX}RUN{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}JOB{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}WORKFLOW{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}VARIABLES{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}RUNNER{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}STATUS{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}STARTED{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}DURATION{colorama.Fore.RESET}",
        f"{colorama.Fore.LIGHTMAGENTA_EX}ARTIFACTS{colorama.Fore.RESET}"
    ]
    table_rows = []
    for run_name, run_jobs in sorted_jobs_by_run_name:
        run = runs_by_name[run_name]

        run_duration, run_started_at = pretty_duration_and_started_at(run)
        run_status = run["status"].upper()
        table_rows.append([
            colored(run_status, run["run_name"], not args.no_jobs),
            "",
            colored(run_status, run["workflow_name"], not args.no_jobs),
            colored(run_status, pretty_variables(run["variables"]), not args.no_jobs),
            colored(run_status, run["runner_name"] or "-", not args.no_jobs),
            colored(run_status, run_status, not args.no_jobs),
            colored(run_status, run_started_at, not args.no_jobs),
            colored(run_status, run_duration, not args.no_jobs),
            ""
        ])
        if not args.no_jobs:
            for job in run_jobs:
                duration, started_at = pretty_duration_and_started_at(job)
                status = job["status"].upper() if job["previous_job_ids"] is None or job[
                    "status"].upper() != "SUBMITTED" else "PENDING"
                table_rows.append([
                    "",
                    colored(status, job["job_id"]),
                    colored(status, job["workflow_name"]),
                    colored(status, pretty_variables(job["variables"])),
                    colored(status, job["runner_name"] or "-"),
                    colored(status, status),
                    colored(status, started_at),
                    colored(status, duration),
                    colored(status, __job_artifacts(job["artifact_paths"]))
                ])

    print(tabulate(table_rows, headers=table_headers, tablefmt="plain"))


def __flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(__flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def pretty_variables(variables):
    if len(variables) > 0:
        variables_str = ""
        for k, v in __flatten(variables).items():
            if len(variables_str) > 0:
                variables_str += "\n"
            variables_str = variables_str + "--" + k + " " + v
        return variables_str
    else:
        return "-"


colors = {
    "SUBMITTED": colorama.Fore.YELLOW,
    "PENDING": colorama.Fore.BLUE,
    "RUNNING": colorama.Fore.GREEN,
    # "DONE": colorama.Fore.WHITE,
    "FAILED": colorama.Fore.RED,
    # "STOPPED": colorama.Fore.WHITE,
    "STOPPING": colorama.Fore.GREEN,
    "ABORTED": colorama.Fore.RED,
    "ABORTING": colorama.Fore.RED
}


def colored(status: str, val: str, bright: bool = False):
    color = colors.get(status)
    c = f"{color}{val}{colorama.Fore.RESET}" if color is not None else val
    return f"{colorama.Style.BRIGHT}{c}{colorama.Style.RESET_ALL}" if bright else c


def pretty_duration_and_started_at(job):
    started_at = job.get("started_at")
    if started_at is not None and job.get("finished_at") is not None:
        _finished_at_milli = round(job.get("finished_at") / 1000)
        duration_milli = _finished_at_milli - round(started_at / 1000)
        hours, remainder = divmod(duration_milli, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = ""
        if int(hours) > 0:
            duration_str += "{} hours".format(int(hours))
        if int(minutes) > 0:
            if int(hours) > 0:
                duration_str += " "
            duration_str += "{} mins".format(int(minutes))
        if int(hours) == 0 and int(minutes) == 0:
            duration_str = "{} secs".format(int(seconds))
    else:
        duration_str = "-"
    started_at_str = pretty_date(round(started_at / 1000)) if started_at is not None else "-"
    return duration_str, started_at_str


def print_runners(profile):
    runners = get_runners(profile)
    table_headers = [f"{colorama.Fore.LIGHTMAGENTA_EX}RUNNER{colorama.Fore.RESET}",
                     f"{colorama.Fore.LIGHTMAGENTA_EX}HOST{colorama.Fore.RESET}",
                     f"{colorama.Fore.LIGHTMAGENTA_EX}STATUS{colorama.Fore.RESET}",
                     f"{colorama.Fore.LIGHTMAGENTA_EX}UPDATED{colorama.Fore.RESET}"
                     ]
    table_rows = []
    for runner in runners:
        updated_at_str = pretty_date(round(runner["updated_at"] / 1000))
        table_rows.append([runner["runner_name"], runner["host_name"], runner["status"].upper(), updated_at_str])
    print(tabulate(table_rows, headers=table_headers, tablefmt="plain"))


def __job_ids(ids):
    if ids is not None:
        return ", ".join(ids)
    else:
        return "-"


def __job_artifacts(paths):
    if paths is not None:
        return "\n".join(map(lambda path: short_artifact_path(path), paths))
    else:
        return "-"


def short_artifact_path(path):
    # The format of the path is <user_name>/<run_name>/<job_id>/<internal_artifact_path>
    return '/'.join(path.split('/')[3:])


artifacts_bucket = "dstack-artifacts-stgn"


def list_artifact(client, artifact_path):
    response = client.list_objects(Bucket=artifacts_bucket, Prefix=artifact_path)

    keys_count = 0
    total_size = 0
    for obj in response.get("Contents") or []:
        keys_count += 1
        total_size += obj["Size"]
    return keys_count, total_size


def list_artifact_files(client, artifact_path):
    response = client.list_objects(Bucket=artifacts_bucket, Prefix=artifact_path)

    return [(obj["Key"][len(artifact_path):].lstrip("/"), obj["Size"]) for obj in
            (response.get("Contents") or [])]


def download_artifact(client, artifact_path, output_dir=None):
    output_path = Path(output_dir if output_dir is not None else os.getcwd())

    response = client.list_objects(Bucket=artifacts_bucket, Prefix=artifact_path)

    total_size = 0
    keys = []
    etags = []
    for obj in response.get("Contents") or []:
        key = obj["Key"]
        etag = obj["ETag"]
        dest_path = dest_file_path(key, output_path)
        if dest_path.exists():
            etag_path = etag_file_path(key, output_path)
            if etag_path.exists():
                if etag_path.read_text() != etag:
                    os.remove(etag_path)
                    os.remove(dest_path)
                else:
                    continue

        total_size += obj["Size"]
        keys.append(key)
        etags.append(etag)

    downloader = transfer.S3Transfer(client, transfer.TransferConfig(), transfer.OSUtils())

    # TODO: Make download files in parallel
    with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
              desc=f"Downloading artifact '{short_artifact_path(artifact_path)}'") as pbar:
        for i in range(len(keys)):
            key = keys[i]
            etag = etags[i]

            def callback(size):
                pbar.update(size)

            file_path = dest_file_path(key, output_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            downloader.download_file(artifacts_bucket, key, str(file_path), callback=callback)

            etag_path = Path(etag_file_path(key, output_path))
            etag_path.parent.mkdir(parents=True, exist_ok=True)
            etag_path.write_text(etag)


def dest_file_path(key, output_path):
    return output_path / Path(short_artifact_path(key))


def etag_file_path(key, output_path):
    return cache_dir() / Path(str(hashlib.md5(str(Path(output_path).absolute()).encode('utf-8')).hexdigest())) / Path(
        key + ".etag")


def cache_dir():
    return Path.home() / Path(".dstack/.cache")


def get_user_info(profile):
    headers = {}
    if profile.token is not None:
        headers["Authorization"] = f"Bearer {profile.token}"
    params = {}
    response = request(method="POST", url=f"{profile.server}/users/info", params=params, headers=headers,
                       verify=profile.verify)
    response.raise_for_status()
    return response.json()


def boto3_client(user_info, service_name):
    if user_info["credentials"].get("aws_session_token") is not None:
        client = boto3.client(service_name, aws_access_key_id=user_info["credentials"]["aws_access_key_id"],
                              aws_secret_access_key=user_info["credentials"]["aws_security_access_key"],
                              aws_session_token=user_info["credentials"]["aws_session_token"],
                              region_name=user_info["credentials"]["aws_region"])
    else:
        client = boto3.client(service_name, aws_access_key_id=user_info["credentials"]["aws_access_key_id"],
                              aws_secret_access_key=user_info["credentials"]["aws_security_access_key"],
                              region_name=user_info["credentials"]["aws_region"])
    return client
