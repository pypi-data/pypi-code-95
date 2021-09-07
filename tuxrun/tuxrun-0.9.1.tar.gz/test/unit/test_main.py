import pytest
import yaml

import tuxrun.__main__
from tuxrun.__main__ import start, main


def touch(directory, name):
    f = directory / name
    f.touch()
    return f


@pytest.fixture
def device(tmp_path):
    return touch(tmp_path, "device.yaml")


@pytest.fixture
def job(tmp_path):
    return touch(tmp_path, "job.yaml")


@pytest.fixture
def run(mocker):
    return mocker.patch("tuxrun.__main__.run")


@pytest.fixture
def tuxrun_args(monkeypatch, device, job):
    args = ["tuxrun", "--device-dict", str(device), "--definition", str(job)]
    monkeypatch.setattr("sys.argv", args)
    return args


@pytest.fixture
def tuxrun_args_generate(monkeypatch):
    args = [
        "tuxrun",
        "--device",
        "qemu-i386",
        "--kernel",
        "https://storage.tuxboot.com/i386/bzImage",
    ]
    monkeypatch.setattr("sys.argv", args)
    return args


@pytest.fixture
def lava_run_call(mocker):
    return mocker.patch("subprocess.Popen")


@pytest.fixture
def lava_run(lava_run_call, mocker):
    proc = lava_run_call.return_value
    proc.wait.return_value = 0
    proc.communicate.return_value = (mocker.MagicMock(), mocker.MagicMock())
    return proc


def test_start_calls_main(monkeypatch, mocker):
    monkeypatch.setattr(tuxrun.__main__, "__name__", "__main__")
    main = mocker.patch("tuxrun.__main__.main")
    with pytest.raises(SystemExit):
        start()
    main.assert_called()


def test_main_usage(monkeypatch, capsys):
    monkeypatch.setattr("tuxrun.__main__.sys.argv", ["tuxrun"])
    ret = main()
    assert ret != 0
    _, err = capsys.readouterr()
    assert "usage: tuxrun" in err


def test_almost_real_run(tuxrun_args, lava_run, capsys):
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n'
    ]
    exitcode = main()
    assert exitcode == 0
    stdout, _ = capsys.readouterr()
    assert "Hello, world" in stdout


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["--device", "qemu-armv7", "--device-dict", "device.yaml"],
        ["--device", "qemu-armv7", "--dtb", "bla.dtb"],
        ["--device", "qemu-arm64", "--bios", "bios.bin"],
        ["--kernel", "https://storage.tuxboot.com/i386/bzImage"],
        ["--device-dict", "device.yaml"],
        ["--definition", "definition.yaml"],
        ["--device", "fvp-morello-android", "--mcp-fw", "mcp.bin"],
        ["--device", "fvp-morello-android", "--test", "multicore"],
    ],
)
def test_command_line_errors(argv, capsys, monkeypatch):
    monkeypatch.setattr("tuxrun.__main__.sys.argv", ["tuxrun"] + argv)
    exitcode = main()
    assert exitcode == 1
    stdout, stderr = capsys.readouterr()
    assert "usage: tuxrun" in stderr
    assert "tuxrun: error:" in stderr


def test_almost_real_run_generate(tuxrun_args_generate, lava_run, capsys):
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n'
    ]
    exitcode = main()
    assert exitcode == 0
    stdout, _ = capsys.readouterr()
    assert "Hello, world" in stdout


def test_ignores_empty_line_from_lava_run_stdout(tuxrun_args, lava_run):
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n',
        "",
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:26.139513"}\n',
    ]
    exitcode = main()
    assert exitcode == 0


def test_ignores_empty_line_from_lava_run_logfile(tuxrun_args, lava_run, tmp_path):
    log = tmp_path / "log.yaml"
    tuxrun_args += ["--log", str(log)]
    lava_run.stderr = [
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:25.139513"}\n',
        "",
        '{"lvl": "info", "msg": "Hello, world", "dt": "2021-04-08T18:42:26.139513"}\n',
    ]
    exitcode = main()
    assert exitcode == 0
    logdata = yaml.safe_load(log.open())
    assert type(logdata[0]) is dict
    assert type(logdata[1]) is dict


def test_tuxmake_directory(monkeypatch, tmp_path, run):
    tuxmake_build = tmp_path / "build"
    tuxmake_build.mkdir()
    (tuxmake_build / "metadata.json").write_text(
        """
        {
            "results": {
                "artifacts": {"kernel": ["bzImage"], "modules": ["modules.tar.xz"]}
            },
            "build": {"target_arch": "x86_64"}
        }
        """
    )
    monkeypatch.setattr("sys.argv", ["tuxrun", "--tuxmake", str(tuxmake_build)])

    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.kernel == f"file://{tuxmake_build}/bzImage"
    assert options.device == "qemu-x86_64"


def test_no_modules(monkeypatch, tmp_path, run):
    tuxmake_build = tmp_path / "build"
    tuxmake_build.mkdir()
    (tuxmake_build / "metadata.json").write_text(
        """
        {
            "results": {
                "artifacts": {"kernel": ["bzImage"]}
            },
            "build": {"target_arch": "x86_64"}
        }
        """
    )
    monkeypatch.setattr("sys.argv", ["tuxrun", "--tuxmake", str(tuxmake_build)])

    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert options.modules is None


def test_invalid_tuxmake_directory(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr("sys.argv", ["tuxrun", "--tuxmake", str(tmp_path)])
    with pytest.raises(SystemExit) as exit:
        main()
        assert exit.status_code != 0
    _, err = capsys.readouterr()
    assert "metadata.json" in err


def test_modules(monkeypatch, lava_run_call, lava_run):
    monkeypatch.setattr(
        "sys.argv",
        [
            "tuxrun",
            "--kernel=bzImage",
            "--device=qemu-x86_64",
            "--modules=/path/to/foo.tar.gz",
        ],
    )
    assert main() == 0
    lava_run_call.assert_called()
    args = lava_run_call.call_args[0][0]
    assert "/path/to/foo.tar.gz:/path/to/foo.tar.gz:ro" in args


def test_overlays(monkeypatch, lava_run_call, lava_run):
    monkeypatch.setattr(
        "sys.argv",
        [
            "tuxrun",
            "--kernel=bzImage",
            "--device=qemu-x86_64",
            "--overlay=/path/to/stuff.tar.gz",
            "--overlay=/path/to/morestuff.tar.gz",
        ],
    )
    assert main() == 0
    lava_run_call.assert_called()
    args = lava_run_call.call_args[0][0]
    assert "/path/to/stuff.tar.gz:/path/to/stuff.tar.gz:ro" in args
    assert "/path/to/morestuff.tar.gz:/path/to/morestuff.tar.gz:ro" in args


def test_custom_commands(monkeypatch, run):
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--kernel=bzImage", "--device=qemu-x86_64", "cat", "/etc/hostname"],
    )
    main()
    run.assert_called()
    options = run.call_args[0][0]
    assert "command" in options.tests
    assert options.command == ["cat", "/etc/hostname"]


def test_list_devices(mocker, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--list-devices"],
    )
    mocker.patch("argparse.ArgumentParser.exit")
    main()
    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert "qemu-i386" in stderr


def test_list_tests(mocker, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["tuxrun", "--list-tests"],
    )
    mocker.patch("argparse.ArgumentParser.exit")
    main()
    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert "ltp-smoke" in stderr
