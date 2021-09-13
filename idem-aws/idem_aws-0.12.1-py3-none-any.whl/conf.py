CLI_CONFIG = {
    "region": {
        "subcommands": ["aws"],
        "dyne": "pop_create",
    },
    "services": {
        "subcommands": ["aws"],
        "dyne": "pop_create",
    },
}
CONFIG = {
    "region": {
        "default": "us-west-2",
        "help": "The cloud region to target",
        "dyne": "pop_create",
    },
    "services": {
        "default": [],
        "nargs": "*",
        "help": "The cloud services to target, defaults to all",
        "dyne": "pop_create",
    },
}
SUBCOMMANDS = {
    "aws": {
        "help": "Create idem_aws state modules by parsing boto3",
        "dyne": "pop_create",
    },
}
DYNE = {
    "acct": ["acct"],
    "exec": ["exec"],
    "pop_create": ["pop_create_idem"],
    "states": ["states"],
    "tool": ["tool"],
}
