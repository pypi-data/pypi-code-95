# encoding: utf-8
"""
This module allow to launch tests using behave application while using specific
projects modules.

Steps are:
- List features to launch
- For each feature
    - Set up feature
    - Launching tests
    - Tear down feature
- Generate a report
"""

import argparse
import datetime
import os
import re
import shutil
import time
from multiprocessing import Process

import yaml
from jinja2 import Template

HOME = os.path.dirname(os.path.abspath(__file__))
MAX_PROCESSES = 1
SCENARIO_TITLE = {
    "fr": "scénario:",
    "en": "scenario:",
}


configuration = {
    "behave": {"lang": "fr",},
    "databases": {},
    "variables": {},
    "reporting": {},
    "options": {
        "headless": False,
        "timeout": 10,
    },
}

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    VERSION = version_file.read().strip()


def generate_report(features, title=None, template=None, destination=None):
    """
    Generating test report:
        1. Listing files to use (baesd on features tested)
        2. Parsing each file to extract data
        3. Report creation
        4. Report save
    """
    data = {
        "title": title or configuration["reporting"].get("title", "Default title"),
        "total": 0,
        "danger": 0,
        "warning": 0,
        "success": 0,
        "passed": 0,
        "failed": 0,
        "time": 0,
        "time_elapsed": "",
        "features": [],
        "generation": time.strftime("%H:%M le %d/%m/%Y", time.localtime()),
    }

    # Listing files to use based on features listed
    for feature in features:
        result_file = ".".join(os.path.basename(feature).split(".")[:-1]) + ".result"
        result = parse_result(result_file)
        if result is not None:
            data["features"].append(result)
            data["total"] += data["features"][-1]["total"]
            data["passed"] += data["features"][-1]["passed"]
            data["failed"] += data["features"][-1]["failed"]
            data["time"] += data["features"][-1]["time"]

    # Global statistics
    data["time_elapsed"] = str(datetime.timedelta(seconds=int(data["time"])))
    for state in ("success", "warning", "danger"):
        data[state] = len(
            [feature for feature in data["features"] if feature["state"] == state]
        )

    # Loading template for report generation
    template_name = template or configuration["reporting"].get("template", "default")
    template_path = os.path.join("templates", template_name)
    if os.path.isdir(os.path.join(HOME, template_path)):
        template_path = os.path.join(HOME, template_path)
    elif not os.path.isdir(template_path):
        print(f"Template folder {template_name} not found")
        return
    with open(os.path.join(template_path, "index.html"), encoding="utf-8") as file_handler:
        template_file = file_handler.read()
    template = Template(template_file)

    # Report destination
    report_destination = destination or configuration["reporting"].get("destination", "report")
    os.makedirs(report_destination, exist_ok=True)
    with open(os.path.join(report_destination, "index.html"), "w", encoding="utf-8") as file_handler:
        file_handler.write(template.render(data=data))

    # Copying static files
    try:
        shutil.rmtree(os.path.join(report_destination, "static"))
    except FileNotFoundError:
        # Folder is not present
        pass
    try:
        shutil.copytree(
            os.path.join(template_path, "static"),
            os.path.join(report_destination, "static")
        )
    except FileNotFoundError:
        # No folder to copy
        pass
    except shutil.Error:
        # Folder is already present
        pass


def parse_result(result_file):
    """
    Parse result file in order to extract stats
    """
    feature = {
        "name": "",
        "scenarios": [],
        "passed": 0,
        "failed": 0,
        "state": "success",
        "total": 0,
        "time": 0,
        "time_elapsed": "",
    }
    # File does not exist
    if not os.path.isfile(os.path.join("results", result_file)):
        return
    with open(os.path.join("results", result_file)) as f:
        results = f.read().splitlines()
    # Get feature name
    feature["name"] = ":".join(results[0].split(":")[1:]).strip()
    if feature["name"] != "":
        # Listing all scenarios
        in_scenario = False
        scenario = None
        for line in results:
            if SCENARIO_TITLE[configuration["behave"]["lang"]] in line.lower():
                scenario_name = ":".join(line.split(":")[1:]).strip().split("--")[0].strip()
                in_scenario = True
                scenario = {"name": scenario_name, "passed": True, "logs": []}
            if line.strip() == "" and scenario is not None:
                for subscenario in feature["scenarios"]:
                    if scenario_name == subscenario["name"]:
                        subscenario["logs"].extend(scenario["logs"])
                        break
                else:
                    feature["scenarios"].append(scenario)
                in_scenario = False
                scenario = None
            if in_scenario:
                scenario["logs"].append(line)
        # Looking for failed scenarios
        failing_flag = False
        for line in results:
            if not failing_flag:
                if line.startswith("Failing scenarios:"):
                    failing_flag = True
            else:
                for scenario in feature["scenarios"]:
                    scenario_name = line.split("--")[0].strip()
                    if scenario_name.endswith(scenario["name"]):
                        scenario["passed"] = False
        # Computing time elapsed for this feature
        result = re.search("^Took ([0-9]+)m([0-9.]+)s$", results[-1])
        if result:
            minutes = int(result.group(1))
            secondes = float(result.group(2))
            feature["time"] = minutes * 60 + secondes
            if minutes > 59:
                code = "%H:%M:%S"
            elif minutes > 0:
                code = "%M:%S"
            else:
                code = "%Ss"
            feature["time_elapsed"] = time.strftime(code, time.gmtime(feature["time"]))
        # Computing feature's statistics
        total = 0
        failed = 0
        passed = 0
        for scenario in feature["scenarios"]:
            total += 1
            if scenario["passed"]:
                passed += 1
            else:
                failed += 1
        feature["total"] = total
        feature["failed"] = failed
        feature["passed"] = passed
        if feature["total"] > 0:
            if feature["passed"] / feature["total"] < 0.4:
                feature["state"] = "danger"
            elif feature["passed"] / feature["total"] < 1:
                feature["state"] = "warning"
            return feature


def list_features(folder, filtres):
    """
    This method returns list of features based on filter given in parameters.
    """
    features = []
    files = os.listdir(folder)
    for file_name in files:
        file_path = os.path.join(folder, file_name)
        if os.path.isdir(file_path) and file_name != "__pycache__":
            features += list_features(file_path, filtres)
        elif file_name.endswith(".feature"):
            if filtres is not None:
                for filtre in filtres:
                    found = True
                    for file_part in filtre:
                        if file_part not in file_path:
                            found = False
                            break
                    if found:
                        features.append(file_path)
                        break
            else:
                features.append(file_path)
    return features


def execute_steps(feature_path, feature_name, position):
    """
    Executing one particular feature file with behave.
    """
    setup_name = f"{feature_name}.{position}"
    setup_feature_name = f"{setup_name}.feature"
    setup_filename = os.path.join(feature_path, setup_name)
    setup_feature_filename = os.path.join(feature_path, setup_feature_name)
    clean_feature_filename = setup_feature_filename.replace("\\", "/")
    if not os.path.exists(setup_filename):
        return
    # Executing steps
    print(f"  Executing {position} steps")
    os.rename(setup_filename, setup_feature_filename)
    try:
        # TODO: Problem when using "quiet mode" with setup/teardown files
        # command = 'behave --lang %s --no-summary -i "%s" > nul 2>&1.' % (
        result_file = os.path.join("results", setup_feature_name + ".result",)
        command = f'behave --lang {configuration["behave"]["lang"]} -s -k -i "{clean_feature_filename}"'
        os.system(f'{command} > "{result_file}" 2>&1')
    except:
        # Something gone wrong
        pass
    os.rename(setup_feature_filename, setup_filename)


def setup_steps(feature_path, feature_name):
    execute_steps(feature_path, feature_name, "setup")


def teardown_steps(feature_path, feature_name):
    execute_steps(feature_path, feature_name, "teardown")


def test_steps(feature, feature_name, args_name, config):
    print("  Executing tests")
    result_file = os.path.join("results", feature_name + ".result",)
    command = 'behave --lang %s -s -k -i "%s"' % (
        config["behave"]["lang"],
        feature.replace("\\", "/"),
    )
    if args_name is not None:
        for name in args_name:
            command += ' -n "%s"' % name
    os.system('%s > "%s" 2>&1' % (command, result_file))


def execute_test(feature, verbose, dry_run, args_name, config):
    feature_path = os.path.dirname(feature)
    feature_name = ".".join(os.path.basename(feature).split(".")[:-1])
    print(feature_name)

    if not dry_run:
        # 2.1: Setup steps
        setup_steps(feature_path, feature_name)
        # 2.2: Feature steps
        test_steps(feature, feature_name, args_name, config)
        # 2.3: Teardown steps
        teardown_steps(feature_path, feature_name)


def main():
    """
    Steps:
    1. Listing features based on filter
    2. Launching tests
        2.1 Setup steps
        2.2 Feature steps
        2.3 Teardown steps
    3. Report generation
    """
    # Arguments management
    parser = argparse.ArgumentParser()
    # Features filter argument for file names
    parser.add_argument(
        "-f",
        "--filename",
        nargs="*",
        action="append",
        help="Only run feature files matching PATTERN with AND operator."
        " If this option is given more than once, it will match against"
        " all the given names independently.",
        metavar="PATTERN",
    )
    # Scenario filter argument for scenario names
    parser.add_argument(
        "-n",
        "--name",
        action="append",
        help="Only execute the feature elements which match part of"
        " the given names. If this option is given more than once, "
        "it will match against all the given names independently.",
    )
    # Cleaning old results flag
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Flag indicating if old results have to be deleted.",
    )
    # Not launching tests flag
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Flag indicating if tests should not be run.",
    )
    # No report generation flag
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Flag indicating if reporting should not be done.",
    )
    # Verbose flag
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Flag for verbosity.",
    )
    # Argument for specifying report's title
    parser.add_argument(
        "--title",
        help="Title to be used for report generation.",
    )
    # Argument for specifying template to use for report generation
    parser.add_argument(
        "--template",
        help="Template to be used for report generation.",
    )
    # Argument for specifying destination of report generation
    parser.add_argument(
        "--destination",
        help="Folder to use for report generation.",
    )
    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    # Argument for specifying k-lity config file
    parser.add_argument(
        "-c",
        "--configuration-file",
        help="File to use as configuration.",
    )
    args = parser.parse_args()

    # Loading configuration
    configuration_file = args.configuration_file or "configuration.yml"
    os.environ["KLITY_CONFIG_FILE"] = configuration_file
    try:
        with open(configuration_file) as f:
            configuration.update(yaml.load(f, Loader=yaml.SafeLoader))
    except FileNotFoundError:
        print(
            "Aucun fichier local de configuration trouvé, "
            "utilisation de la configuration par défaut."
        )

    # Step 0 : Init necessary folders
    if args.clean and os.path.exists("results"):
        shutil.rmtree("results")
    os.makedirs("results", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)

    # Step 1: Listing features
    features = list_features(os.getcwd(), args.filename)

    # Step 2: For each feature
    processes = []
    started = 0
    finished = 0

    for feature in features:
        p = Process(
            target=execute_test,
            name=".".join(os.path.basename(feature).split(".")[:-1]),
            args=(feature, args.verbose, args.dry_run, args.name, configuration),
        )
        processes.append(p)

    while finished < len(processes):
        if started < MAX_PROCESSES:
            for process in processes:
                if process.exitcode is None and not process.is_alive():
                    try:
                        process.start()
                        started += 1
                    except AssertionError:
                        # Process finished elsewhere, forget it
                        pass
                if started >= MAX_PROCESSES:
                    break
        # Refresh state
        started = 0
        finished = 0
        for process in processes:
            if process.is_alive():
                started += 1
            elif process.exitcode is not None:
                finished += 1

    for process in processes:
        process.join()

    if not args.no_report:
        # Step 3: Report generation
        generate_report(features, args.title, args.template, args.destination)


def newproject():
    """
    Create a new project folder.

    Usage :
        klity-newproject project_folder_name
    """
    # Arguments management
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Name of new folder project.")
    args = parser.parse_args()

    if args.name is not None:
        if os.path.exists(args.name):
            print(f"Folder '{args.name}' already exists, please choose another name.")
            return
        try:
            os.makedirs(args.name, exist_ok=True)
            with open(os.path.join(args.name, "configuration.yml"), "w") as f:
                f.write("behave:\n    lang: fr")
            with open(os.path.join(args.name, "environment.py"), "w") as f:
                f.write(
                    "# encoding: utf-8\n\nfrom klity.features.environment "
                    "import before_all, after_all, before_feature, after_feature, "
                    "before_scenario, after_scenario, before_step"
                )
            os.mkdir(os.path.join(args.name, "steps"))
            with open(os.path.join(args.name, "steps", "project_steps.py"), "w") as f:
                f.write(
                    "# encoding: utf-8\n\nfrom behave import *\n"
                    "\nfrom klity.features.steps.steps_web import *"
                    "\nfrom klity.features.steps.steps_utils import *"
                )
            print(f"Project {args.name} created!")
        except Exception as exception:
            print(f"Error while trying to create project {args.name} :")
            print(exception)
