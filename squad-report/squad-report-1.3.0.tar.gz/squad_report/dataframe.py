def filter_isin(df, key, values):
    if df.empty:
        return df

    filtered = df.copy(deep=True)
    filtered = filtered[filtered[key].isin(values)]

    return filtered


def filter_startswith(df, key, values):
    if df.empty:
        return df

    filtered = df.copy(deep=True)
    filtered = filtered[filtered[key].str.startswith(values)]

    return filtered


def regressions(changes):
    try:
        data = changes.loc[changes["change"] == "regressions"].to_dict("records")
    except KeyError:
        return []

    regressions = {}
    for regression in data:
        key = (regression["environment"], regression["suite"])

        if key not in regressions:
            regressions[key] = []

        regressions[key].append(regression["test"])

    return regressions


def fixes(changes):

    try:
        data = changes.loc[changes["change"] == "fixes"].to_dict("records")
    except KeyError:
        return []

    fixes = {}
    for fix in data:
        key = (fix["environment"], fix["suite"])

        if key not in fixes:
            fixes[key] = []

        fixes[key].append(fix["test"])

    return fixes


def summary(results):
    data = results.to_dict("records")

    summary = {}
    for result in data:
        key = (result["environment"], result["suite"])

        if key not in summary:
            summary[key] = {"pass": 0, "fail": 0, "skip": 0, "xfail": 0}

        status = result["status"]
        summary[key][status] += 1

    return summary


def environments(results):
    return sorted(results.environment.unique().tolist())


def suites(results):
    return sorted(results.suite.unique().tolist())


def fails(results):
    data = results.loc[results["status"] == "fail"].to_dict("records")

    fails = {}
    for fail in data:
        key = (fail["environment"], fail["suite"])

        if key not in fails:
            fails[key] = []

        fails[key].append(fail["test"])

    return fails


def skips(results):
    data = results.loc[results["status"] == "skip"].to_dict("records")

    skips = {}
    for skip in data:
        key = (skip["environment"], skip["suite"])

        if key not in skips:
            skips[key] = []

        skips[key].append(skip["test"])

    return skips
