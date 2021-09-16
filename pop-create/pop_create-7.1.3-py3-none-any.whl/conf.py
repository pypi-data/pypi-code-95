import os

CLI_CONFIG = {
    "config": {"options": ["-c"], "subcommands": ["_global_"]},
    "author": {},
    "author_email": {},
    "project_name": {
        "subcommands": ["_global_"],
        "options": ["-n", "--name"],
    },
    "dyne": {"subcommands": ["_global_"], "options": ["-d"]},
    "overwrite_existing": {
        "options": ["--overwrite", "-o"],
        "subcommands": ["_global_"],
        "action": "store_true",
    },
    "directory": {"options": ["-D"], "subcommands": ["_global_"]},
    "ignore": {"options": ["-I"], "subcommands": ["_global_"]},
    "vertical": {
        "subcommands": ["_global_"],
        "action": "store_true",
        "options": ["-tv"],
    },
}
CONFIG = {
    "config": {
        "default": "",
        "help": "Load extra options from a configuration file",
    },
    "author": {
        "default": None,
        "help": "The name of the author, defaults to git global config value",
    },
    "author_email": {
        "default": None,
        "help": "The author email, defaults to git global config value",
    },
    "project_name": {
        "help": "The name of the project that is being created",
        "default": None,
    },
    "vertical": {
        "default": False,
        "help": "Build a vertically app-merged project, it's entrypoint is in another project",
    },
    "overwrite_existing": {
        "default": False,
        "help": "Overwrite files if they already exist",
    },
    "dyne": {
        "default": [],
        "nargs": "*",
        "help": "A space delimited list of additional dynamic names for vertical app-merging",
    },
    "directory": {
        "default": os.getcwd(),
        "help": "The directory to create the project in",
    },
    "ignore": {
        "default": [],
        "nargs": "*",
        "help": "A space delimited list of file paths to ignore, they won't be changed by pop-create under any circumstances",
    },
}

SUBCOMMANDS = {
    "seed": {"help": "Seed a traditional pop project"},
    "tests": {"help": "Create the tests for a traditional pop-project"},
    "docs": {"help": "Create the Sphinx tooling for this project"},
    "cicd": {"help": "Create the cicd tooling for this project"},
}
DYNE = {
    "pop_create": ["pop_create"],
    "tool": ["tool"],
}
