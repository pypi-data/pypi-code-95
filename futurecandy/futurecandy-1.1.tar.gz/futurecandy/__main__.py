"""futurecandy: a project initialization utility for Linux."""

import configparser
import os.path as path
from os import mkdir, system, scandir
from shutil import copy2 as copy
from copy import deepcopy
from ast import literal_eval
from subprocess import Popen
import enquiries

__version__ = "1.1"

print("><=><")
print("futurecandy, v" + __version__)

home = path.join(path.expanduser("~"), ".futurecandy/")

if not path.isfile(home + "candy.cfg"):
    print("Missing user configurations, creating...")
    mkdir(home)
    mkdir(home + "hooks")
    copy(path.join(path.abspath(path.dirname(__file__)), "candy.cfg"), home)
    for hook in [x for x in scandir(path.join(path.abspath(
            path.dirname(__file__)), "hooks")) if x.path.endswith(
                ".hook.futurecandy")]:
        copy(hook.path, home + "hooks/")
    print("Done, created directory ~/.futurecandy with base configurations.")

config = configparser.ConfigParser()
config.read(home + "candy.cfg")

parent_path = ""

if not enquiries.confirm("Use configured default directory for projects?"):
    parent_path = enquiries.freetext("Specify path for custom directory: ")
else:
    parent_path = literal_eval(config["paths"]["projects"])

parent_path = parent_path.replace("~/", path.join(path.expanduser("~"), ""))

if not path.isdir(parent_path):
    raise Exception("Path to directory is not valid.")

name = enquiries.freetext("Specify project name: ")

project_path = path.join(parent_path, name)

try:
    mkdir(project_path)
except FileExistsError:
    if not enquiries.confirm("Project path \"" + project_path + "\" already "
                             "exists, continue?"):
        exit(1)

# probably needs more error handling
hook_files = list(scandir(home + "hooks"))
hooks = {}
for file in hook_files:
    if not file.path.endswith(".hook.futurecandy"):
        continue
    hook_config = configparser.ConfigParser()
    hook_config.read(file.path)
    hooks.update({literal_eval(hook_config["meta"]["name"]) + " - " +
                  literal_eval(hook_config["meta"]["description"]):
                      deepcopy(hook_config)})

hooks_to_run = enquiries.choose("Specify hooks to run: ", hooks.keys(), True)

for queued in hooks_to_run:
    print("Running hook:", queued)
    command = literal_eval(hooks[queued]["exec"]["script"])
    if literal_eval(hooks[queued]["exec"]["want_path"]):
        command = command.format(path.join(project_path, ""))
    system(command)
    print("Hook complete.")

if literal_eval(config["editors"]["auto"]):
    Popen(literal_eval(config["editors"]["main"]) + " " + project_path,
          shell=True)
else:
    Popen(enquiries.choose("Select editor to open project with: ",
                           literal_eval(config["editors"]["all"])) + " " +
          project_path, shell=True)

print("Done.")
exit(0)
