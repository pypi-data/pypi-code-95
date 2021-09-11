from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from tests.test_connect import _make_test_builder

from anyscale.background.const import (
    ANYSCALE_BACKGROUND_JOB_CONTEXT,
    BACKGROUND_ACTOR_NAME,
)
from anyscale.background.job_context import BackgroundJobContext
from anyscale.background.job_runner import _generate_job_name, BackgroundJobRunner, run
from anyscale.connect import ClientBuilder


def test_job_runner_actor():
    """
    Test that the job runner actor is passing the correct args to the subprocess
    """
    mock_runtime_env = {"uris": ["a", "b", "c"]}
    mock_ray = Mock()
    mock_ray.get_runtime_context.return_value.runtime_env = mock_runtime_env

    mock_subprocess = Mock()
    mock_subprocess.run = Mock()

    mock_actor_handle = Mock()
    mock_actor_handle.stop.remote = Mock()

    mock_os = Mock()
    mock_os.environ = {}

    context = BackgroundJobContext("creator", "cmd", "ns", [], "par_job_id")

    with patch.dict("sys.modules", ray=mock_ray, os=mock_os), patch.multiple(
        "anyscale.background.job_runner", os=mock_os, subprocess=mock_subprocess
    ):
        runner = BackgroundJobRunner()
        runner.run_background_job("cmd", mock_actor_handle, context)

        context.runtime_env_uris = mock_runtime_env["uris"]

        mock_subprocess.run.assert_called_once_with(
            "cmd",
            shell=True,
            check=True,
            env={
                "PYTHONUNBUFFERED": "1",  # Make sure python subprocess streams logs https://docs.python.org/3/using/cmdline.html#cmdoption-u
                "RAY_ADDRESS": "anyscale://",  # Make sure that internal ray.init has an anyscale RAY_ADDRESS
                ANYSCALE_BACKGROUND_JOB_CONTEXT: context.to_json(),
            },
        )

        mock_actor_handle.stop.remote.assert_called_once()


def test_generate_command_name_default() -> None:
    """
    Test generation of job name default from command
    """

    assert _generate_job_name("python abc.py") == "python_abc_py"
    assert _generate_job_name("rllib train -f train.py") == "rllib_train_f_train_py"
    assert _generate_job_name("./my_script.sh") == "_my_script_sh"


def test_non_anyscale_address() -> None:
    """
    Test that anyscale.background.run fails for non anyscale addresses
    """
    try:
        run("cmd", {"pip": "r"}, "ray://")
    except ValueError:
        pass
    except Exception:
        pytest.fail("ray:// address should not be accepted")


def test_run_job(tmp_path: Path):
    """
    Tests the anyscale.background.run function
    Ensure that data is passed into ray correctly
    Ensure the context is set correctly
    """
    builder, _, _, _ = _make_test_builder(tmp_path)
    mock_background_job_runner = Mock()
    builder.connect = Mock()
    builder._job_config.metadata["creator_id"] = "cid"
    mock_client_builder = Mock(return_value=builder)
    mock_uuid = Mock(return_value="ns")
    mock_get_runtime_ctx = Mock()
    mock_get_runtime_ctx.return_value.job_id.hex.return_value = "par_job_id"

    with patch.multiple("anyscale", ClientBuilder=mock_client_builder), patch(
        "ray.remote", new=Mock(return_value=mock_background_job_runner),
    ), patch("uuid.uuid4", new=mock_uuid), patch(
        "ray.get_runtime_context", new=mock_get_runtime_ctx
    ):

        address = "anyscale://cluster"
        job = run("cmd", {"pip": "r"}, address)
        mock_client_builder.assert_called_once_with("cluster")
        mock_uuid.assert_called_once()

        b: ClientBuilder = builder
        b._job_config.set_ray_namespace.assert_called_once_with("bg_ns")
        b._job_config.set_metadata.assert_called_with("job_name", "cmd")
        b._job_config.set_metadata.has_call("inherit_from_child", "1")

        mock_background_job_runner.options.assert_called_once_with(
            lifetime="detached", name=BACKGROUND_ACTOR_NAME
        )
        context = BackgroundJobContext(
            "cid",
            "cmd",
            namespace="bg_ns",
            runtime_env_uris=[],
            parent_ray_job_id="par_job_id",
        )
        actor = mock_background_job_runner.options.return_value.remote.return_value
        mock_background_job_runner.options.return_value.remote.return_value.run_background_job.remote.assert_called_once_with(
            command="cmd", context=context, self_handle=actor,
        )

        assert job.context == context

        # Check the private variables and make sure they are correct
        assert job._BackgroundJob__actor == actor  # type: ignore
        assert job.ref == actor.run_background_job.remote.return_value  # type: ignore
