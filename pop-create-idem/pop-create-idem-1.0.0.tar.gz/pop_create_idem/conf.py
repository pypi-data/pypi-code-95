BOTOCORE_CLI = {
    "api_version": {
        "subcommands": ["botocore"],
        "dyne": "pop_create",
    },
    "region": {
        "subcommands": ["botocore"],
        "dyne": "pop_create",
    },
    "services": {
        "subcommands": ["botocore"],
        "dyne": "pop_create",
    },
}
BOTOCORE_CONFIG = {
    "api_version": {
        "default": None,
        "help": "The cloud api version to target",
        "dyne": "pop_create",
    },
    "region": {
        "default": "us-west-1",
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
CLI_CONFIG = {
    "simple_service_name": {
        "options": ["--cloud", "--cloud-name"],
        "subcommands": ["idem-cloud", "openapi3", "swagger"],
        "dyne": "pop_create",
    },
    "acct_plugin": {
        "subcommands": ["idem-cloud", "openapi3", "swagger"],
        "dyne": "pop_create",
    },
    "specification": {
        "options": ["--spec", "--file", "--url"],
        "subcommands": ["openapi3", "swagger"],
        "dyne": "pop_create",
    },
    **BOTOCORE_CLI,
}
CONFIG = {
    "acct_plugin": {
        "default": None,
        "help": "The acct plugin to use for authentication -- default is to create a new plugin",
        "dyne": "pop_create",
    },
    "simple_service_name": {
        "default": None,
        "help": "Short name of the cloud being bootstrapped",
        "dyne": "pop_create",
    },
    "specification": {
        "default": None,
        "help": "The url or file path to a spec",
        "dyne": "pop_create",
    },
    **BOTOCORE_CONFIG,
}
SUBCOMMANDS = {
    # https://openapi.tools/#converters
    "idem-cloud": {"help": "Boostrap an idem cloud project", "dyne": "pop_create"},
    "openapi3": {
        "help": "Create idem_cloud modules based off of an openapi3 spec",
        "dyne": "pop_create",
    },
    "botocore": {
        "help": "Create idem_cloud modules based off of google's protobuffer spec",
        "dyne": "pop_create",
    },
    "protobuffer": {
        "help": "Create idem_cloud modules based off of google's protobuffer spec",
        "dyne": "pop_create",
    },
    "smithy": {
        "help": "Create idem_cloud modules based off of aws smithy",
        "dyne": "pop_create",
    },
    "swagger": {
        "help": "Create idem_cloud modules based off of a swagger spec",
        "dyne": "pop_create",
    },
}
DYNE = {
    "pop_create": ["pop_create"],
    "cloudspec": ["cloudspec"],
    "tool": ["tool"],
    "jinja": ["jinja"],
}
