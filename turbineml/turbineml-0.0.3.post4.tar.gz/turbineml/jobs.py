import configparser
from genericpath import isdir
from gql import Client, gql, transport
from gql.transport.requests import RequestsHTTPTransport
import requests
import json
from turbineml.configuration import _config
from turbineml.internal.file_wrapper import FileWrapper
from contextlib import contextmanager
from rich.progress import Progress, BarColumn, DownloadColumn, TimeRemainingColumn
import os
import tarfile
import tempfile
import stringcase


class MachineType:
    CPU_S2 = "cpu-s2"

class WaitForExitMode:
    ALL = "all"
    ALL_VALUES=[ALL]

class NodeGroup:
    def __init__(self, name, script, node_count=1, machine_type=MachineType.CPU_S2, container_image="alpine:latest", wait_for_exit=WaitForExitMode.ALL):
        self.name = name
        self.script = script
        self.node_count = node_count
        self.machine_type = machine_type
        self.container_image = container_image
        self.wait_for_exit = wait_for_exit

    def to_object(self):
        values = vars(self)
        return {stringcase.camelcase(k): values[k] for k in values}

    def from_object(obj):
        values = {stringcase.snakecase(k): obj[k] for k in obj}
        return NodeGroup(**values)

class JobConfiguration:
    def __init__(self, node_groups):
        self.node_groups = node_groups

    def to_object(self):
        return {
            "nodeGroups": [x.to_object() for x in self.node_groups]
        }

    @staticmethod
    def from_object(obj):
        return JobConfiguration(NodeGroup.from_object(x) for x in obj['nodeGroups'])


def _enumerate_files_to_archive(src_dir):
    for root, _, files in os.walk(src_dir):
        relative_dir = os.path.relpath(root, src_dir)
        if relative_dir == ".":
            relative_dir = ""
        for file in files:
            src_file = os.path.join(root, file)
            archive_path = os.path.join(relative_dir, file)
            yield (src_file, archive_path)

@contextmanager
def _managed_file(file_or_name):
    if isinstance(file_or_name, str):
        file = open(file_or_name, 'rb')
        close_file = True
    else:
        file = file_or_name
        close_file = False
    
    try:
        yield file
    finally:
        if close_file:
            file.close()


class TurbineClient:
    def __init__(self, api_url, api_key):
        transport = RequestsHTTPTransport(url=f"{api_url}graphql", headers={"Authorization": f"Bearer {api_key}"})
        self.client = Client(transport=transport, fetch_schema_from_transport=False)
    
    def _check_for_errors(result):
        if result['errors']:
            formatted_errors = "; ".join(x['message'] for x in result['errors'])
            raise Exception(formatted_errors)

    def get_job_status(self, job_id):
        query = gql("""
        query($jobId: ID!) {
            job(id: $jobId) {
                id status
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "jobId": job_id
        })
        return result['job']['status']
    
    def get_job_inputs(self, job_id):
        query = gql("""
        query($jobId: ID!) {
            job(id: $jobId) {
                id
                inputs { key value }
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "jobId": job_id
        })
        inputs = result['job']['inputs']
        return { x['key']: x['value'] for x in inputs }
    
    def create_job(self, organization, project, name):
        query = gql("""
        mutation($input: CreateJobInput!) {
            createJob(input: $input) {
                job { id }
                errors { code message }
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "input": {
                "organization": organization,
                "project": project,
                "name": name,
                "parentJobId": None,
            }
        })
        return result['createJob']['job']['id']
        
    def set_job_config(self, job_id, configuration):
        config_json = json.dumps(configuration.to_object())
        query = gql("""
        mutation($input: SetJobConfigurationInput!) {
            setJobConfiguration(input: $input) {
                job { id }
                errors { code message }
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "input": {
                "jobId": job_id,
                "configuration": config_json,
            }
        })
        return result['setJobConfiguration']['job']['id']
    
    def update_job_inputs(self, job_id, inputs):
        query = gql("""
        mutation($input: UpdateJobInputsInput!) {
            updateJobInputs(input: $input) {
                job { id }
                errors { code message }
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "input": {
                "jobId": job_id,
                "newValues": inputs
            }
        })
        return result['updateJobInputs']['job']['id']
    
    def enqueue_job(self, job_id):
        query = gql("""
        mutation($input: EnqueueJobInput!) {
            enqueueJob(input: $input) {
                job { id }
                errors { code message }
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "input": {
                "jobId": job_id,
            }
        })
        return result['enqueueJob']['job']['id']

    def cancel_job(self, job_id):
        query = gql("""
        mutation($input: CancelJobInput!) {
            cancelJob(input: $input) {
                job { id }
                errors { code message }
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "input": {
                "jobId": job_id,
            }
        })
        return result['cancelJob']['job']['id']

    def job_id_for_cluster(self, cluster_id):
        query = gql("""
        query($clusterId: ID!) {
            cluster(id: $clusterId) {
                id
                job { id }
            }
        }
        """)
        result = self.client.execute(query, variable_values={
            "clusterId": cluster_id
        })
        job = result['cluster']['job']
        if job is None:
            return None
        return job['id']

    def upload_code_archive(self, job_id, file):
        headers = {"Authorization": "Bearer " + _config.get_api_key()}
        url = f"{_config.get_api_url()}jobs/{job_id}/codeArchive"
        r = requests.post(url, headers=headers, data=file)
        r.raise_for_status()

def _create_client():
    return TurbineClient(_config.get_api_url(), _config.get_api_key())

def current_job():
    if "TURBINE_CLUSTER_ID" not in os.environ:
        return None
    cluster_id = os.environ["TURBINE_CLUSTER_ID"]
    client = _create_client()
    job_id = client.job_id_for_cluster(cluster_id)
    return Job(job_id) if job_id is not None else None

def create_job(project, name):
    # TODO validate format of project
    organization, proj = project.split('/')

    client = _create_client()
    job_id = client.create_job(organization, proj, name)
    return Job(job_id)

class Job:
    def __init__(self, job_id):
        self.job_id = job_id
        self.client = _create_client()

    def get_status(self):
        return self.client.get_job_status(self.job_id)
    
    def get_inputs(self):
        return self.client.get_job_inputs(self.job_id)

    def set_configuration(self, configuration):
        self.client.set_job_config(self.job_id, configuration)

    def update_inputs(self, inputs):
        new_values = [ {'key': x, 'value': inputs[x] } for x in inputs ]
        self.client.update_job_inputs(self.job_id, new_values)

    def upload_code_archive(self, file_or_directory):
        if os.path.isfile(file_or_directory):
            file = file_or_directory
            delete_file = False
            if not file.endsWith(".tar"):
                raise Exception("File must be a .tar file")
        elif os.path.isdir(file_or_directory):
            fd, file = tempfile.mkstemp(suffix=".tar")
            self._create_archive_file(file, file_or_directory)
            delete_file = True
        else:
            raise Exception(f"{file_or_directory} is not a .tar file or a directory")
        
        self._upload_archive_file(file)

        if delete_file:
            os.close(fd)
            os.remove(file)


    def _create_archive_file(self, output_file, dir):
        files = list(_enumerate_files_to_archive(dir))
        with tarfile.open(output_file, "w") as tar:
            with Progress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    DownloadColumn(),
                    TimeRemainingColumn(),
                ) as progress:
                    task = progress.add_task(f"Archiving {len(files)} files...", total=len(files))

                    def set_permissions(tarinfo):
                        tarinfo.mode = 0o777
                        return tarinfo

                    for src_file, archive_file in files:
                        tar.add(src_file, arcname=archive_file, filter=set_permissions)
                        progress.update(task, advance=1)

    
    def _upload_archive_file(self, file):
        with _managed_file(file) as file_handle:
            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                DownloadColumn(),
                TimeRemainingColumn(),
            ) as progress:
                file_size = os.fstat(file_handle.fileno()).st_size
                task = progress.add_task(f"Uploading code archive...", total=file_size)
                def callback(bytes_read):
                    nonlocal task
                    progress.update(task, advance=bytes_read)
                file_wrapper = FileWrapper(file_handle, callback)

                self.client.upload_code_archive(self.job_id, file_wrapper)

    def enqueue(self):
        self.client.enqueue_job(self.job_id)
    
    def cancel(self):
        self.client.cancel_job(self.job_id)

