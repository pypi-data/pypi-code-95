from datetime import datetime
import logging
import os
import re
import shutil
from string import Template
import tempita
import yaml

WORKFLOW = ".github/workflows/main.yml"
WORKFLOW_VERSION = "1.0"
APP = ".mobiledgex/app.yml"
APPINSTS = ".mobiledgex/appinsts.yml"
GITHUB_DEPLOY_ACTION = "mobiledgex/deploy-app-action@v1.2"

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def load_tmpl(tmpl, data):
    t = tempita.Template(tmpl,
                         namespace=dict(lower=lambda s: s.lower()))

    for key in data:
        if isinstance(data[key], list):
            ndata = []
            for elem in data[key]:
                ndata.append(tempita.bunch(**elem))
            data[key] = ndata

    return t.substitute(data)

def load_github_action_file(file, tmpl, data):
    try:
        with open(file) as f:
            contents = f.read()
    except FileNotFoundError:
        with open(tmpl) as f:
            tmpl = f.read()
        contents = load_tmpl(tmpl, data)

    d = load(contents, Loader=Loader)
    if True in d:
        d["on"] = d.pop(True)   # Weird issue with YAML truth values

    return d

def load_workflow(data, repo="."):
    data["github_deploy_action"] = GITHUB_DEPLOY_ACTION
    d = load_github_action_file(
        os.path.join(repo, WORKFLOW),
        os.path.join(os.path.dirname(__file__), "workflow.tmpl"),
        data)

    steps = {}
    for job in d["jobs"]:
        for step in d["jobs"][job]["steps"]:
            step_id = step.get("id")
            if not step_id:
                logging.debug("No ID for step: {}".format(step))
            else:
                steps[step.get("id")] = step

    param_steps = ("push", "deploy")
    missing = [ x for x in param_steps if x not in steps ]
    if missing:
        logging.error("Failed to load workflow; missing step(s): "
                      + ", ".join(missing))
    else:
        data["appname"] = os.path.basename(steps["push"]["with"]["repository"])

    return d, data

def load_app(data, repo="."):
    d = load_github_action_file(
        os.path.join(repo, APP),
        os.path.join(os.path.dirname(__file__), "app.yml.tmpl"),
        data)

    try:
        data["appname"] = d["app"]["key"]["name"]
        data["appvers"] = d["app"]["key"]["version"]
        data["apporg"] = d["app"]["key"]["organization"]
        data["flavor"] = d["app"]["default_flavor"]["name"]
        data["ports"] = d["app"]["access_ports"]
        data["deployment"] = d["app"]["deployment"]
    except KeyError as e:
        logging.error("Parameter not found: {}".format(e))

    return d, data

def load_appinst(data, repo="."):
    d = load_github_action_file(
        os.path.join(repo, APPINSTS),
        os.path.join(os.path.dirname(__file__), "appinsts.yml.tmpl"),
        data)

    try:
        data["cluster"] = d[0]["appinst"]["key"]["cluster_inst_key"]["cluster_key"]["name"]
    except KeyError as e:
        logging.error("Parameter not found: {}".format(e))

    return d, data

def dump(data, file, comment=None):
    try:
        with open(file) as f:
            curr_data = f.read()
    except FileNotFoundError:
        curr_data = None
    new_data = yaml.dump(data)
    if comment:
        comment = [ "# " + x for x in comment.splitlines() ]
        new_data = "\n".join(comment) + "\n" + new_data
    if curr_data and new_data != curr_data:
        bakfile = file + "." + datetime.now().strftime("%Y-%m-%d-%H%M%S")
        shutil.copy(file, bakfile)

    with open(file, "w") as f:
        f.write(new_data)

def dump_workflow(workflow, data, repo="."):
    for job in workflow["jobs"]:
        for step in workflow["jobs"][job]["steps"]:
            step_id = step.get("id")
            if step_id == "push":
                step["with"]["registry"] = data["docker"]
                step["with"]["repository"] = "{}/images/{}".format(
                    data["devorg"].lower(), data["appname"])
            elif step_id == "deploy":
                step["with"]["setup"] = data["deployenv"]
                step["uses"] = GITHUB_DEPLOY_ACTION

    return dump(workflow, os.path.join(repo, WORKFLOW),
                comment="WORKFLOW-VERSION:{}".format(WORKFLOW_VERSION))

def dump_app(app, data, repo="."):
    app["region"] = data["region"]
    app["app"]["key"]["name"] = data["appname"]
    app["app"]["key"]["version"] = data["appvers"]
    app["app"]["key"]["organization"] = data["apporg"]
    app["app"]["default_flavor"]["name"] = data["flavor"]
    app["app"]["deployment"] = data["deployment"]
    app["app"]["access_ports"] = data["ports"]
    return dump(app, os.path.join(repo, APP))

def dump_appinst(appinst, data, repo="."):
    # Ignore existing app inst and compute a fresh one
    appinst = [{
        "appinst": {
            "key": {
                "cluster_inst_key": {
                    "cloudlet_key": {
                        "name": data["cloudlet"],
                        "organization": data["cloudletorg"],
                    },
                    "cluster_key": {
                        "name": data["cluster"],
                    },
                    "organization": data["devorg"],
                },
            },
        },
    }]
    return dump(appinst, os.path.join(repo, APPINSTS))

if __name__ == "__main__":
    data = {
        "appname": "foo",
        "devorg": "Dev1",
        "docker": "docker.mobiledgex.net",
        "region": "EU",
        "deployenv": "main",
        "flavor": "m4.small",
        "deployment": "kubernetes",
        "ports": "tcp:5678",
        "cluster": "my-cluster",
        "cloudlet": "foo",
        "cloudletorg": "bar",
    }

    print("\n== Workflow ==")
    workflow, data = load_workflow(data)
    print(yaml.dump(workflow))
    print(data)

    print("\n== App ==")
    app, data = load_app(data)
    print(yaml.dump(app))
    print(data)

    print("\n== App Instances ==")
    appinst, data = load_appinst(data)
    print(yaml.dump(appinst))
    print(data)
