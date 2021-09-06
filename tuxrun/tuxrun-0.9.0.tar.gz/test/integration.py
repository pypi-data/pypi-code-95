#!/usr/bin/python3
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from typing import Dict
from tuxrun.__main__ import KERNELS
from tuxrun.yaml import yaml_load


###########
# Helpers #
###########
def get_results(tmpdir: Path) -> Dict:
    required_keys = set(["msg", "lvl", "dt"])
    res = {}
    data = yaml_load((tmpdir / "logs.yaml").read_text(encoding="utf-8"))

    if data is None:
        return {}

    for line in data:
        if not isinstance(line, dict):
            continue
        if not required_keys.issubset(set(line.keys())):
            continue
        if line["lvl"] != "results":
            continue
        definition = line["msg"]["definition"]
        case = line["msg"]["case"]
        del line["msg"]["definition"]
        del line["msg"]["case"]
        res.setdefault(definition, {})[case] = line["msg"]

    return res


def get_simple_results(res: Dict) -> Dict:
    results = {
        "boot": res.get("lava", {}).get("login-action", {}).get("result", "fail")
    }
    for name in res:
        if name == "lava":
            continue
        key = "_".join(name.split("_")[1:])
        if all([res[name][case]["result"] in ["skip", "pass"] for case in res[name]]):
            results[key] = "pass"
        else:
            results[key] = "fail"
    return results


def get_job_result(results: Dict, simple_results: Dict) -> str:
    # lava.job is missing: error
    lava = results.get("lava", {}).get("job")
    if lava is None:
        return "error"

    if lava["result"] == "fail":
        if lava.get("error_type") == "Job":
            return "fail"
        return "error"

    if all([v == "pass" for (k, v) in simple_results.items()]):
        return "pass"
    return "fail"


def run(device, test, runtime, debug):
    tmpdir = Path(tempfile.mkdtemp(prefix="tuxrun-"))

    args = [
        "python3",
        "-m",
        "tuxrun",
        "--device",
        device,
        "--runtime",
        runtime,
        "--log-file",
        str(tmpdir / "logs.yaml"),
    ]
    if test:
        args.extend(["--tests", test])

    try:
        ret = subprocess.call(args)
        if ret != 0:
            print(f"Command return non-zero exist status {ret}")
            print((tmpdir / "logs.yaml").read_text(encoding="utf-8"))
            return ret

        results = get_results(tmpdir)
        simple_results = get_simple_results(results)
        result = get_job_result(results, simple_results)

        if debug:
            print("Results:")
            for res in results:
                print(f"* {res}: {results[res]}")

            print("\nSimple results:")
            for res in simple_results:
                print(f"* {res}: {simple_results[res]}")
            print(f"Result {result}")
        else:
            print(f"{result}")
        assert result == "pass"
    finally:
        shutil.rmtree(tmpdir)


##############
# Entrypoint #
##############
def main():
    parser = argparse.ArgumentParser(description="Integration tests")
    parser.add_argument(
        "--devices", default=list(KERNELS.keys()), nargs="+", help="devices"
    )
    parser.add_argument(
        "--tests",
        default=[
            "boot",
            "ltp-fcntl-locktests",
            "ltp-fs_bind",
            "ltp-fs_perms_simple",
            "ltp-fsx",
            "ltp-nptl",
            "ltp-smoke",
        ],
        nargs="+",
        help="tests",
    )
    parser.add_argument("--debug", default=False, action="store_true", help="debug")
    parser.add_argument(
        "--runtime",
        default="podman",
        choices=["docker", "null", "podman"],
        help="Runtime",
    )
    options = parser.parse_args()

    for device in options.devices:
        for test in options.tests:
            print(f"=> {device} x {test}")
            if run(
                device, "" if test == "boot" else test, options.runtime, options.debug
            ):
                return 1
            print("")


if __name__ == "__main__":
    sys.exit(main())
