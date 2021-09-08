import pathlib

import nox


def install_from_requirements(session, filename, project=None):
    args = ["-r", f"requirements/{filename}.txt"]
    if project is not None:
        args.append(project)
    session.install(*args)


REPORTS = pathlib.Path("reports")
PYTEST = "pytest"
COVER = "pytest-cover"
PROFILE = "pytest-profile"
PYSPY = "pytest-py-spy"


def junit_xml_root(name):
    return REPORTS / name


@nox.session
def clean(session):
    install_from_requirements(session, "coverage")
    session.run("coverage", "erase")


@nox.session
def check(session):
    install_from_requirements(session, "check")
    report_dir = REPORTS / "flake8"
    report_dir.mkdir(parents=True, exist_ok=True)
    session.run(
        "flake8",
        "--format=html",
        f"--htmldir={report_dir}",
        "--isort-show-traceback",
        "src",
        "tests",
    )


@nox.session
def mypy(session):
    install_from_requirements(session, "mypy", ".")
    report_dir = REPORTS / "mypy"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "junit.xml"
    coverage_report_dir = REPORTS / "mypy-coverage"
    coverage_report_dir.mkdir(parents=True, exist_ok=True)
    session.run(
        "mypy",
        f"--html-report={coverage_report_dir}",
        f"--junit-xml={report_file}",
        "src",
    )


@nox.session
def mypy_report(session):
    install_from_requirements(session, "junit-report")
    report_dir = REPORTS / "mypy"
    xml = str(report_dir / "junit.xml")
    html = str(report_dir / "index.html")
    session.run("junit2html", xml, html)


@nox.session
def nocov(session):
    install_from_requirements(session, "pytest", ".")
    report_dir = junit_xml_root(PYTEST)
    report_dir.mkdir(parents=True, exist_ok=True)
    junit_xml = report_dir / "junit.xml"
    session.run(
        "python",
        "-m",
        "pytest",
        "tests",
        "-p",
        "no:cacheprovider",
        f"--junitxml={junit_xml}",
    )


@nox.session
def cover(session):
    install_from_requirements(session, "cover", ".")
    report_dir = junit_xml_root(COVER)
    report_dir.mkdir(parents=True, exist_ok=True)
    junit_xml = report_dir / "junit.xml"
    session.run(
        "coverage",
        "run",
        "-m",
        "pytest",
        "tests",
        "-p",
        "no:cacheprovider",
        f"--junitxml={junit_xml}",
    )


@nox.session
def report(session):
    install_from_requirements(session, "report")
    session.run("coverage", "combine")
    # I am skeptical of the organization; do not rely on it.
    # session.run("limit-coverage")
    session.run(
        "coverage", "html", "--show-contexts", "-d", "reports/coverage"
    )
    session.run(
        "coverage", "report", "--skip-covered", "-m", "--fail-under=100"
    )


@nox.session
def profile(session):
    install_from_requirements(session, "profile", ".")
    report_dir = junit_xml_root(PROFILE)
    report_dir.mkdir(parents=True, exist_ok=True)
    junit_xml = report_dir / "junit.xml"
    html_dir = REPORTS / "profile"
    html_dir.mkdir(parents=True, exist_ok=True)
    outfile = html_dir / "index.html"
    session.run(
        "pyinstrument",
        "--renderer",
        "html",
        f"--outfile={outfile}",
        "-m",
        "pytest",
        "tests",
        "-p",
        "no:cacheprovider",
        f"--junitxml={junit_xml}",
    )


@nox.session
def pyspy(session):
    install_from_requirements(session, "pyspy", ".")
    report_dir = junit_xml_root(PYSPY)
    report_dir.mkdir(parents=True, exist_ok=True)
    junit_xml = report_dir / "junit.xml"
    svg_dir = REPORTS / "py-spy"
    svg_dir.mkdir(parents=True, exist_ok=True)
    outfile = svg_dir / "profile.svg"
    session.run(
        "py-spy",
        "record",
        "-o",
        str(outfile),
        "--",
        "python",
        "-m",
        "pytest",
        "tests",
        "-p",
        "no:cacheprovider",
        f"--junitxml={junit_xml}",
    )


@nox.session
@nox.parametrize("pytest_kind", [PYTEST, COVER, PROFILE, PYSPY])
def pyest_report(session, pytest_kind):
    install_from_requirements(session, "junit-report")
    junit_xml_dir = junit_xml_root(pytest_kind)
    junit_xml = str(junit_xml_dir / "junit.xml")
    html = str(REPORTS / pytest_kind / "index.html")
    session.run("junit2html", junit_xml, html)
