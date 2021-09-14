import jinja2
import requests.compat
import squad_report.dataframe
from squad_client.core.api import SquadApi
from os.path import expanduser, dirname, join

te = jinja2.Environment(
    extensions=["jinja2.ext.loopcontrols"],
    loader=jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader(join(dirname(__file__), "templates")),
            jinja2.FileSystemLoader(expanduser("~/.config/squad_report/templates")),
        ]
    ),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=jinja2.StrictUndefined,
)


def test_results(results):
    summary = squad_report.dataframe.summary(results)
    passing = failing = skiping = xfailing = 0
    for key in summary:
        if key[1] != "build":
            passing = passing + summary[key].get("pass")
            failing = failing + summary[key].get("fail")
            skiping = skiping + summary[key].get("skip")
            xfailing = xfailing + summary[key].get("xfail")
    total = passing + failing + skiping + xfailing
    test_result = {
        "total": total,
        "pass": passing,
        "fail": failing,
        "skip": skiping,
        "xfail": xfailing,
    }
    return test_result


def create_report(config, group, project, build, base_build, changes, results):
    args = {
        "build": build,
        "build_url": squad_build_url(group, project, build),
        "base_build": base_build,
        "regressions": squad_report.dataframe.regressions(changes),
        "fixes": squad_report.dataframe.fixes(changes),
        "test_result": test_results(results),
        "summary": squad_report.dataframe.summary(results),
        "environments": squad_report.dataframe.environments(results),
        "suites": squad_report.dataframe.suites(results),
        "fails": squad_report.dataframe.fails(results),
        "skips": squad_report.dataframe.skips(results),
        "total_tests": len(results),
        "config": config,
    }

    if config.email_subject:
        config.email_subject = te.from_string(config.email_subject).render(**args)

    # generate = True means always generate the report.
    generate = True
    if config.email_subject and config.send_on:
        if "FAIL" in config.send_on and len(args["fails"]) == 0:
            generate = False
        if "REG" in config.send_on and len(args["regressions"]) == 0:
            generate = False
    # all
    if generate:
        return te.get_template(config.template + ".txt.jinja").render(**args)

    return None


def squad_build_url(group, project, build):
    return requests.compat.urljoin(
        SquadApi.url, "/".join([group.slug, project.slug, "build", build.version])
    )
