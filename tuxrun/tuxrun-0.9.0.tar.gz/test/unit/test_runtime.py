from pathlib import Path
import os
import subprocess

import pytest

from tuxrun.runtimes import DockerRuntime, NullRuntime, PodmanRuntime, Runtime


def test_select():
    assert Runtime.select("docker") == DockerRuntime
    assert Runtime.select("null") == NullRuntime
    assert Runtime.select("podman") == PodmanRuntime


def test_cmd_null():
    runtime = Runtime.select("null")()
    assert runtime.cmd(["hello", "world"]) == ["hello", "world"]

    runtime.bind("/hello/world")
    assert runtime.cmd(["hello", "world"]) == ["hello", "world"]


def test_cmd_podman():
    runtime = Runtime.select("podman")()
    runtime.name("name")
    runtime.image("image")
    args = [
        "podman",
        "run",
        "--rm",
        "--quiet",
        "--hostname",
        "tuxrun",
        "-v",
        "/boot:/boot:ro",
        "-v",
        "/lib/modules:/lib/modules:ro",
    ]
    if Path("/dev/kvm").exists():
        args.extend(
            [
                "-v",
                "/dev/kvm:/dev/kvm:rw",
            ]
        )
    if Path(f"/var/tmp/.guestfs-{os.getuid()}").exists():
        args.extend(
            [
                "-v",
                f"/var/tmp/.guestfs-{os.getuid()}:/var/tmp/.guestfs-0:rw",
            ]
        )
    assert runtime.cmd(["hello", "world"]) == args + [
        "--name",
        "name",
        "image",
        "hello",
        "world",
    ]

    runtime.bind("/hello/world") == args + [
        "-v",
        "/hello/world:/hello/world:rw",
        "--name",
        "name",
        "image",
        "hello",
        "world",
    ]


def test_kill_null(mocker):
    runtime = Runtime.select("null")()
    runtime.__proc__ = None
    runtime.kill()

    runtime.__proc__ = mocker.MagicMock()
    runtime.kill()
    runtime.__proc__.kill.assert_called_once_with()


def test_kill_podman(mocker):
    popen = mocker.patch("subprocess.Popen")
    runtime = Runtime.select("podman")()
    runtime.kill()
    popen.assert_called_once_with(
        ["podman", "stop", "--time", "60", None],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        preexec_fn=os.setpgrp,
    )
    assert len(runtime.__sub_procs__) == 1


def test_kill_podman_raise(mocker):
    popen = mocker.patch("subprocess.Popen", side_effect=FileNotFoundError)
    runtime = Runtime.select("podman")()
    runtime.kill()
    popen.assert_called_once_with(
        ["podman", "stop", "--time", "60", None],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        preexec_fn=os.setpgrp,
    )
    assert len(runtime.__sub_procs__) == 0


def test_pre_run_docker():
    runtime = Runtime.select("docker")()
    runtime.pre_run(None)
    runtime.__bindings__[-1] == "/var/run/docker.sock"


def test_pre_run_null():
    runtime = Runtime.select("null")()
    runtime.pre_run(None)


def test_pre_run_podman(mocker, tmp_path):
    (tmp_path / "podman.sock").touch()
    popen = mocker.patch("subprocess.Popen")

    runtime = Runtime.select("podman")()
    runtime.pre_run(tmp_path)
    assert runtime.__pre_proc__ is not None
    popen.assert_called_once()


def test_pre_run_podman_errors(mocker, tmp_path):
    popen = mocker.patch("subprocess.Popen")
    sleep = mocker.patch("time.sleep")

    runtime = Runtime.select("podman")()
    with pytest.raises(Exception) as exc:
        runtime.pre_run(tmp_path)
    assert exc.match("Unable to create podman socket at ")
    assert exc.match("podman.sock")
    popen.assert_called_once()
    sleep.assert_called()


def test_post_run_null():
    runtime = Runtime.select("null")()
    runtime.post_run()


def test_post_run_podman(mocker):
    runtime = Runtime.select("podman")()
    runtime.post_run()

    runtime.__pre_proc__ = mocker.MagicMock()
    runtime.post_run()
    runtime.__pre_proc__.kill.assert_called_once_with()
    runtime.__pre_proc__.wait.assert_called_once_with()


def test_run(mocker):
    popen = mocker.patch("subprocess.Popen")

    runtime = Runtime.select("podman")()
    runtime.name("name")
    runtime.image("image")
    with runtime.run(["hello", "world"]):
        popen.assert_called_once()
        assert runtime.__proc__ is not None
        assert runtime.__ret__ is None
    runtime.__proc__.wait.assert_called_once()


def test_run_errors(mocker):
    popen = mocker.patch("subprocess.Popen", side_effect=FileNotFoundError)

    runtime = Runtime.select("podman")()
    runtime.name("name")
    runtime.image("image")
    with pytest.raises(FileNotFoundError):
        with runtime.run(["hello", "world"]):
            pass
    popen.assert_called_once()

    popen = mocker.patch("subprocess.Popen", side_effect=Exception)
    runtime = Runtime.select("podman")()
    runtime.name("name")
    runtime.image("image")
    with pytest.raises(Exception):
        with runtime.run(["hello", "world"]):
            pass
    popen.assert_called_once()
