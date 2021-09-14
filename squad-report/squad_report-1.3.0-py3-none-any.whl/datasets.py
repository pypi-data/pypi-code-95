import pandas as pd
from squad_report.logging import getLogger
from squad_client.core.models import Environment, Suite
from squad_client.utils import getid

logger = getLogger(__name__)


def changes(group, project, build, base_build, unfinished):
    logger.debug("Fetching changes...")
    changes = project.compare_builds(base_build.id, build.id, unfinished)

    change_data = []
    for change in changes.keys():
        for environment in changes[change].keys():
            for suite, tests in changes[change][environment].items():
                for test in tests:
                    change_data.append(
                        {
                            "group": group.slug,
                            "project": project.slug,
                            "build": build.version,
                            "base_build": base_build.version,
                            "environment": environment,
                            "suite": suite,
                            "test": test,
                            "change": change,
                        }
                    )

    data = pd.DataFrame(change_data)

    if not data.empty:
        data.sort_values(by=["environment", "suite", "test"], inplace=True)

    return data


def results(group, project, build, base_build, unfinished):
    logger.debug("Fetching results...")
    tests = build.tests(fields="build,environment,short_name,status,suite").values()

    result_data = []
    environments = {}
    suites = {}
    for test in tests:
        if test.environment not in environments:
            environments[test.environment] = Environment().get(
                _id=getid(test.environment)
            )
        if test.suite not in suites:
            suites[test.suite] = Suite().get(_id=getid(test.suite))

        environment = environments[test.environment]
        suite = suites[test.suite]
        result_data.append(
            {
                "group": group.slug,
                "project": project.slug,
                "build": build.version,
                "base_build": base_build.version,
                "environment": environment.slug,
                "suite": suite.slug,
                "test": test.short_name,
                "status": test.status,
            }
        )

    data = pd.DataFrame(result_data)
    data.sort_values(by=["environment", "suite", "test"], inplace=True)

    return data
