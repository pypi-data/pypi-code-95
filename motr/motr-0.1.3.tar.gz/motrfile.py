import pathlib
import re
import sys
import typing

import attr
import trio
import wheel_filename

from motr import api
from motr._api.actions import cmd as cmd_
from motr._api.requirements import action
from motr._api.requirements import target
from motr.core import result as result_


CONSTRAINTS_FILE = api.Input(pathlib.Path(".motr/constraints.txt"))
REQUIREMENTS = api.Input(pathlib.Path(".motr/requirements"))
REQUIREMENTS_FILE = api.Input(REQUIREMENTS.path.with_suffix(".txt"))


@attr.dataclass(frozen=True)
class SinglePythonPackage:
    root: pathlib.Path
    src: bool


@attr.dataclass(frozen=True)
class PythonPackage:
    prefix: pathlib.Path
    suffix: pathlib.Path
    src: bool

    @property
    def requirements_file(self):
        return api.Input((REQUIREMENTS / self.suffix).with_suffix(".txt"))


def make_parent(input_file):
    path = input_file.path.parent
    yield from api.mkdir(api.Input(path))


@attr.dataclass(frozen=True)
class Venv:
    root: pathlib.Path
    name: str

    @property
    def root_path(self):
        return self.root / self.name

    @property
    def bin_dir(self):
        return self.root_path / "bin"

    @property
    def pip(self):
        return api.Input(self.bin_dir / "pip")

    def create(self):
        action = yield from api.cmd(
            [sys.executable, "-m", "venv", "--clear", self.root_path],
        )
        yield from target.target(self.bin_dir, action)

    def update(self):
        yield from api.cmd(
            [self.pip.as_output(), "install", "-U", "pip"],
            self.bin_dir,
        )

    def install(self, *pip_args):
        return (yield from api.cmd((self.pip, "install") + pip_args))

    def command(self, command, install_action):
        command_path = self.bin_dir / command
        yield from target.target(command_path, install_action)
        return api.Input(command_path)


dot_dir = pathlib.Path(".motr")
requirements_dir = pathlib.Path("requirements")
reports_dir = pathlib.Path("reports")


def setup_venv(name, command, *pip_args):
    venv = Venv(dot_dir, name)

    yield from venv.create()
    yield from venv.update()
    install_action = yield from venv.install(*pip_args)

    return (yield from venv.command(command, install_action))


@attr.dataclass(frozen=True)
class PackageRoots:
    common_root: pathlib.Path
    roots: typing.FrozenSet[typing.Tuple[str, ...]]


@attr.dataclass(frozen=True)
class PyprojectBuild:
    pyproject_build: api.Input
    package_roots: PackageRoots

    async def __call__(self):
        dist_dir = pathlib.Path(".motr/dist")
        await trio.Path(dist_dir).mkdir()
        constraints = []
        for root in self.package_roots.roots:
            outdir = nested
            srcdir = self.package_roots.common_root
            for segment in root:
                outdir /= segment
                srcdir /= segment
            result = await cmd_.Cmd(
                (
                    str(self.pyproject_build.path),
                    "--outdir",
                    str(dist_dir),
                    str(srcdir)
                )
            )(outdir)
            if result is not result_.Result.PASSED:
                return result_.Result.ABORTED
            build_log = await trio.Path(outdir / "out.txt").read_text()
            wheel_re = re.compile(
                r"^Successfully built .* (\S+\.whl)$", flags=re.MULTILINE,
            )
            build_match = re.search(wheel_re, build_log)
            if build_match is None:
                return result_.Result.ABORTED
            build_path = dist_dir / build_match.group(1)
            package_name = wheel_filename.parse_wheel_filename(build_path).project


@attr.dataclass(frozen=True)
class FlitToRequirements:
    flit: api.Input
    outfile: api.Input

    async def __call__(self):
        result, data = await cmd_.Cmd(
            (
                str(self.flit.path), "build", "--format", "wheel",
            ),
        )()
        if result is not result_.Result.PASSED:
            return result_.Result.ABORTED, {}
        build_log = data["err"]
        wheel_re = r"Built wheel:\s*(\S*)"
        build_match = re.search(wheel_re, build_log)
        if build_match is None:
            return result_.Result.ABORTED
        build_path = pathlib.Path(build_match.group(1))
        package_name = wheel_filename.parse_wheel_filename(build_path).project
        await trio.Path(self.outfile.path).write_text(
            f"{package_name} @ {build_path.resolve().as_uri()}\n"
        )
        return result_.Result.PASSED, {}


def flit(outfile):
    flit_cmd = yield from setup_venv("flit", "flit", "flit")
    flit_to_requirements = FlitToRequirements(flit_cmd, outfile)
    yield from action.action(flit_to_requirements, flit_cmd.path)
    yield from target.target(outfile.path, flit_to_requirements)
    return outfile


def venv_wrapper(name, command, requirements_file, *pip_args):
    return (
        yield from setup_venv(
            name,
            command,
            "-r",
            (requirements_dir / requirements_file).with_suffix(".txt"),
            *pip_args,
        )
    )


def pytest_suffix(junit_file):
    return (
        "tests",
        "-p",
        "no:cacheprovider",
        "--junitxml",
        junit_file.as_output(),
    )


def run_pytest(
    env_name, requirement_name, runner, report_name, test_extra_inputs=()
):
    command_name = runner[0]
    requirements_file = yield from flit(REQUIREMENTS_FILE)
    command = yield from venv_wrapper(
        env_name, command_name, requirement_name, "-r", requirements_file
    )
    runner = (command,) + runner[1:]
    report_dir = api.Input(reports_dir / report_name)
    yield from api.mkdir(report_dir)
    junit_file = api.Input(report_dir.path / "junit.xml")
    pytest_action = yield from (
        api.cmd(
            runner + pytest_suffix(junit_file),
            report_dir.path,
            *test_extra_inputs,
            allowed_codes=[1],
        )
    )
    junit2html = yield from venv_wrapper(
        "junit-report", "junit2html", "junit-report"
    )
    html_file = api.Input(report_dir.path / "index.html")
    yield from (
        api.cmd(
            [
                junit2html,
                junit_file,
                html_file.as_output(env_name),
            ],
        )
    )
    return pytest_action


def changes():
    flake8_report_dir = api.Input(reports_dir / "flake8")
    flake8_report_file = flake8_report_dir.path / "index.html"
    flake8 = yield from venv_wrapper("check", "flake8", "check")
    yield from api.mkdir(flake8_report_dir)
    check_action = yield from api.cmd(
        [
            flake8,
            "--format=html",
            "--htmldir",
            flake8_report_dir,
            "--isort-show-traceback",
            "src",
            "tests",
        ],
        allowed_codes=[1],
    )
    yield from target.target(flake8_report_file, check_action, "check")

    requirements_file = yield from flit(REQUIREMENTS_FILE)

    mypy_report_dir = reports_dir / "mypy"
    mypy_report_file = api.Input(mypy_report_dir / "junit.xml")
    mypy_coverage_dir = api.Input(reports_dir / "mypy-coverage")
    mypy_coverage_file = mypy_coverage_dir.path / "index.html"
    mypy = yield from venv_wrapper("mypy", "mypy", "mypy", "-r", requirements_file)
    yield from api.mkdir(api.Input(mypy_report_dir))
    yield from api.mkdir(mypy_coverage_dir)
    mypy_action = yield from api.cmd(
        [
            mypy,
            "--html-report",
            mypy_coverage_dir,
            "--junit-xml",
            mypy_report_file.as_output(),
            "src",
        ],
        mypy_report_dir,
        allowed_codes=[1],
    )
    yield from target.target(mypy_coverage_file, mypy_action, "mypy")
    junit2html = yield from venv_wrapper(
        "junit-report", "junit2html", "junit-report"
    )
    mypy_report_html = api.Input(mypy_report_dir / "index.html")
    yield from api.cmd(
        [junit2html, mypy_report_file, mypy_report_html.as_output("mypy")],
    )

    yield from run_pytest(
        "nocov", "pytest", ("python", "-m", "pytest"), "pytest"
    )

    coverage = yield from venv_wrapper("coverage", "coverage", "coverage")
    coverage_deleted = api.deleted(pathlib.Path(".coverage"))
    erase_action = yield from api.cmd([coverage, "erase"])
    yield from target.target(coverage_deleted, erase_action)
    initial_coverage = "initial-coverage"
    updated_coverage_file = pathlib.Path(".coverage")
    pytest_cover_action = yield from run_pytest(
        "cover",
        "cover",
        ("coverage", "run", "-m", "pytest"),
        "pytest-cover",
        (coverage_deleted,),
    )
    yield from target.target(initial_coverage, pytest_cover_action)
    combine_action = yield from api.cmd(
        [coverage, "combine"],
        initial_coverage,
    )
    yield from target.target(updated_coverage_file, combine_action)
    yield from api.cmd(
        [
            coverage,
            "html",
            "--show-contexts",
            "-d",
            api.Input(reports_dir / "coverage").as_output("cover"),
        ],
        updated_coverage_file,
    )
    coverage_report_action = yield from api.cmd(
        [
            coverage,
            "report",
            "--skip-covered",
            "-m",
            "--fail-under=100",
        ],
        updated_coverage_file,
        allowed_codes=[2],
    )

    yield from target.target("coverage-report", coverage_report_action, "cover")

    profile_dir = api.Input(reports_dir / "profile")

    yield from api.mkdir(profile_dir)
    yield from run_pytest(
        "profile",
        "profile",
        (
            "pyinstrument",
            "--renderer",
            "html",
            "--outfile",
            api.Input(profile_dir.path / "index.html").as_output("profile"),
            "-m",
            "pytest",
        ),
        "pytest-profile",
        (profile_dir.path,),
    )


MOTR_CONFIG = api.build(changes())
