import os
import re
import subprocess
import time
from typing import Any, Dict, Optional, Union
import uuid

import yaml

from anyscale.background.const import (
    ANYSCALE_BACKGROUND_JOB_CONTEXT,
    BACKGROUND_ACTOR_NAME,
)
from anyscale.background.job_context import BackgroundJob, BackgroundJobContext


class BackgroundJobRunner:
    """
    This class is an actor that runs a shell command on the head node for an anyscale cluster.
    This class will:
    1. Pass a BackgroundJobContext as an environment variable
    2. execute the command in a subprocess (and stream logs appropriately)
    3. Gracefully exit when the command is complete
    """

    def run_background_job(
        self, command: str, self_handle: Any, context: BackgroundJobContext,
    ) -> None:
        import ray

        # Update the context with the runtime env uris
        uris = [u for u in ray.get_runtime_context().runtime_env["uris"]]
        context.runtime_env_uris = uris
        env_vars = {
            "PYTHONUNBUFFERED": "1",  # Make sure python subprocess streams logs https://docs.python.org/3/using/cmdline.html#cmdoption-u
            "RAY_ADDRESS": "anyscale://",  # Make sure that internal ray.init has an anyscale RAY_ADDRESS
            ANYSCALE_BACKGROUND_JOB_CONTEXT: context.to_json(),
        }
        env = {**os.environ, **env_vars}

        try:
            subprocess.run(command, shell=True, check=True, env=env)  # noqa

        finally:
            # allow time for any logs to propogate before the task exits
            time.sleep(1)

            self_handle.stop.remote()

    def stop(self) -> None:
        import ray

        ray.actor.exit_actor()


def _parse_runtime_env(
    env: Optional[Union[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    If `env` is a string, it represents a YAML file. Load the file and return the dict.
    Otherwise, return the dict that is passed in, or {} if nothing is passed
    """
    if isinstance(env, str):
        with open(env, "r") as stream:
            try:
                return yaml.safe_load(stream)  # type: ignore
            except yaml.YAMLError as e:
                raise ValueError(
                    f"Failed while attempting to load a runtime env yaml spec into a runtime environment dictionary. Please ensure that the file {env} is specified correctly",
                    e,
                )
    else:
        return env or {}


def _generate_job_name(command: str) -> str:
    """
    Escape the command string to get the job name, and replace spaces and periods with _
    """
    return re.sub(r"\W+", "", re.sub(r"[\. ]", "_", command))


def run(
    command: str,
    runtime_env: Optional[Union[str, Dict[str, Any]]] = None,
    address: Optional[str] = None,
) -> BackgroundJob:
    """
    This function lets you execute a shell command in the background on a ray cluster, in a specific environment

    This function returns a BackgroundJobContext object that let's you wait for or kill the scheduled job

    :param command: This is the first param
    @param param2: this is the second param

    Args:
        command: The shell command to run. Eg. "python script.py"
        runtime_env: The OSS Ray runtime environment in which to run the command. Should be a dict or a path.
            Please see the Ray runtime env documentation for the format
        address: The address of the cluster to run the command on. Must start with 'anyscale://'

    Returns:
        BackgroundJob object. You can use this object to wait for the job, or to kill it

    Examples:
        >>> script.py
        >>> # connect as normal
        >>> ray.init("anyscale://")

        >>> runner.py
        >>> ctx = run("python script.py", runtime_env="env.yaml", address="anyscale://")
        >>> ctx.wait() # wait for the job
        >>> ctx.kill() # kill the job
    """
    # lazy imports
    # ray is required to run in the background
    import ray

    from anyscale import ClientBuilder

    # handle optional args
    address = address or os.getenv("RAY_ADDRESS") or "anyscale://"
    runtime_env = _parse_runtime_env(runtime_env)
    namespace = f"bg_{str(uuid.uuid4())}"

    if not address.startswith("anyscale://"):
        raise ValueError(
            "Anyscale run can only be used to connect to anyscale clusters"
        )

    _, inner_address = address.split("://", maxsplit=1)

    # This is just setting a default, and will be overwritten by the inner job name
    outer_job_name = _generate_job_name(command)

    # Connect the outer ray client.
    # Start an outer job that will be used to ship the users file system
    client = ClientBuilder(inner_address)
    client._log.info(
        f"Running in namespace: {namespace}. You can use this namespace as a reference to access this background job in the future."
    )
    # Enable this job's metadata to be overwritten by any children jobs
    client._bg_set_outer_overwritable()
    client.env(runtime_env).job_name(outer_job_name).namespace(namespace).connect()

    # Construct the actor to run the inner job in
    BackgroundJobRunnerActor = ray.remote(BackgroundJobRunner)  # noqa
    actor = BackgroundJobRunnerActor.options(
        lifetime="detached", name=BACKGROUND_ACTOR_NAME
    ).remote()

    # grab the creator id from the job config of the outer job
    creator_db_id = client._job_config.metadata["creator_id"]
    outer_job_id = ray.get_runtime_context().job_id.hex()

    # generate a random cross reference id to identify the created job later
    context = BackgroundJobContext(
        creator_db_id=creator_db_id,
        original_command=command,
        namespace=namespace,
        # This will be populated in the actor
        runtime_env_uris=[],
        parent_ray_job_id=outer_job_id,
    )

    remote_ref = actor.run_background_job.remote(
        command=command, self_handle=actor, context=context
    )
    return BackgroundJob(actor, remote_ref, context)
