import argparse
import os
from caeops.services.service_groups.update import service_groups_update
from caeops.services.logs.remove_from_group import logs_remove_from_group
from caeops.services.logs.add_to_group import logs_add_to_group
from caeops.services.metrics.remove_from_group import metrics_remove_from_group
from caeops.services.metrics.add_to_group import metrics_add_to_group
from caeops.services.logs.describe_elastic_domain import logs_get
from caeops.services.metrics_analyzer.delete import metrics_analyzer_delete
from caeops.services.metrics_analyzer.create import metrics_analyzer_create
from caeops.services.metrics_analyzer.get import metrics_analyzer_get
from caeops.services.metrics_analyzer.list import metrics_analyzer_list
from caeops.services.metrics_analyzer.update import metrics_analyzer_update
from caeops.services.dashboards.get import dashboards_get
from caeops.services.dashboards.get_labels import dashboards_get_labels
from caeops.services.dashboards.delete_labels import dashboards_delete_labels
from caeops.services.dashboards.add_labels import dashboards_add_labels
from caeops.services.logs.install_agent import logs_install_agent
from caeops.services.logs.update_agent import logs_update_agent
from caeops.services.logs_analyzers.delete import logs_analyzer_delete
from caeops.services.logs_analyzers.update import logs_analyzer_update
from caeops.services.logs_analyzers.list import logs_analyzer_list
from caeops.services.logs_analyzers.get import logs_analyzer_get
from caeops.services.metrics.install_agent import metrics_install_agent
from caeops.services.metrics.update_agent import metrics_update_agent
from caeops.services.others.get_services import get_services
from caeops.services.service_groups.list import service_groups_list
from caeops.services.service_groups.list_services import service_groups_list_services
from caeops.services.service_groups.get import service_groups_get
from caeops.services.service_groups.create import service_groups_create
from caeops.services.logs.add_labels import logs_add_labels
from caeops.services.logs.delete_labels import logs_delete_labels
from caeops.services.logs.get_labels import logs_get_labels
from caeops.services.metrics.get_labels import metrics_get_labels
from caeops.services.metrics.delete_labels import metrics_delete_labels
from caeops.services.metrics.add_labels import metrics_add_labels
from caeops.common.parser import ArgumentParser
from caeops.services.metrics.get import metrics_get
from caeops.services.tenants.update import tenants_update
from caeops.services.users.get import users_get
from caeops.services.dashboards.create import dashboards_create
from caeops.services.dashboards.delete import dashboards_delete
from caeops.services.dashboards.list import dashboards_list
from caeops.services.metrics.list import metrics_list
from caeops.services.groups.remove_users import groups_remove_users
from caeops.services.groups.add_users import groups_add_users
from caeops.services.groups.list import groups_list
from caeops.services.metrics.delete import metrics_delete
from caeops.services.metrics.create import metrics_create
from caeops.services.others.configure import configure
from caeops.services.groups.list_users import groups_list_users
from caeops.services.tenants.register import tenants_register
from caeops.services.users.login import users_login
from caeops.services.users.delete import users_delete
from caeops.services.users.list_groups import users_list_groups
from caeops.services.users.list import users_list
from caeops.services.users.register import users_register
from caeops.services.users.update import users_update
from caeops.services.logs.create_elastic_domain import logs_create
from caeops.services.logs.delete_elastic_domain import logs_delete
from caeops.services.logs.list_elastic_domain import logs_list
from caeops.services.logs_analyzers.create import logs_analyzer_create
from caeops.services.notifications.list import templates_list
from caeops.services.notifications.get import templates_get
from caeops.services.notifications.delete import templates_delete
from caeops.services.notifications.create import templates_create
from caeops.services.logs.create_parsing_rule import create_parsing_rule
from caeops.services.logs.list_parsing_rules import list_parsing_rules
from caeops.services.logs.get_parsing_rule import get_parsing_rule
from caeops.services.logs.update_parsing_rule import update_parsing_rule
from caeops.services.logs.delete_parsing_rule import delete_parsing_rule
from caeops.services.logs.enable_parsing_rule import enable_parsing_rule
from caeops.services.logs.disable_parsing_rule import disable_parsing_rule
import sys
from caeops import __version__
from caeops.common.file_input_helper import (
    check_for_generate_cli_skeleton_argument,
    load_input_from_file,
)

if os.environ.get("LC_CTYPE", "") == "UTF-8":
    os.environ["LC_CTYPE"] = "en_US.UTF-8"


class LoadFromFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        with values as f:
            # parse arguments in the file and store them in the target namespace
            parser.parse_args(f.read().split(), namespace)


class Main:
    def __init__(self):
        help = """caeops <service> <command> [<args>]

AVAILABLE SERVICES
   - tenants
   - users
   - groups
   - service-groups
   - metrics
   - dashboards
   - logs
   - notifications

To see help, you can run: caeops <service> --help
"""
        parser = argparse.ArgumentParser(
            description="CloudAEye command line utility", usage=help
        )
        parser.add_argument(
            "arg_service", help="service to select", type=str, nargs="?", default=""
        )
        parser.add_argument(
            "arg_command",
            help="commands for the selected service",
            nargs="?",
            type=str,
            default="",
        )
        parser.add_argument(
            "--version",
            help="Version of the current package",
            action="store_const",
            const=__version__,
        )
        namespace = parser.parse_args(sys.argv[1:3])
        arg_service = namespace.arg_service.replace("-", "_")
        arg_command = namespace.arg_command.replace("-", "_")
        if not arg_service and not namespace.version:
            print(help)
        elif not arg_service and namespace.version:
            print(f"caeops {namespace.version}")
        elif arg_service and not hasattr(self, arg_service):
            print("Unrecognized service")
            print(help)
            exit(1)
        else:
            # use dispatch pattern to invoke method with same name
            getattr(self, arg_service)(arg_command or "")

    @staticmethod
    def configure(command=""):
        # Used to write identifier and email to the config.ini file
        configure()

    def get(self, command):
        cmd_help = """caeops tenants <command> [<args>]

AVAILABLE COMMANDS
   - services
"""
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "get_{}".format(command.replace("-", "_")).strip("_")
        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, service_command)()

    @staticmethod
    def get_services():
        # Get a list of all services supported by CloudAEye
        get_services()

    def tenants(self, command):
        cmd_help = """caeops tenants <command> [<args>]

AVAILABLE COMMANDS
   - register
   - update
"""
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "tenants_{}".format(command.replace("-", "_")).strip("_")

        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, service_command)()

    @staticmethod
    def tenants_register():
        """
        Command to register an account with CloudAEye
        """
        parser = argparse.ArgumentParser(
            prog="caeops tenants register",
            description="Register an account with CloudAEye",
        )
        supported_args = [
            "email",
            "given-name",
            "family-name",
            "company",
            "company-phone",
            "company-logo",
            "company-url",
            "linkedin-url",
            "phone-number",
            "birthdate",
            "address",
            "gender",
        ]
        # Add supported args for the current command
        ArgumentParser.add_required_args(supported_args, parser)
        # Add additional commands supported for generating / reading input file
        ArgumentParser.add_input_file_args(parser)

        # Check if the input is being provided in an external file => if no read the input from the CLI args
        payload = load_input_from_file(parser)
        if not payload:
            # Check if --generate-cli-skeleton arguments is passed => yes then generate the skeleton and exit
            check_for_generate_cli_skeleton_argument(parser)
            # Parse the command line args passed in the current in the current command and convert it into a dict
            payload = ArgumentParser.parse_args_and_convert_to_payload(parser)
        # Validate and register the account with the given payload
        tenants_register(payload)

    @staticmethod
    def tenants_update():
        # Update the details of a registered user
        parser = argparse.ArgumentParser(
            prog="caeops users update", description="Update a tenant user"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            [
                "email",
                "given-name",
                "family-name",
                "company",
                "company-phone",
                "company-logo",
                "company-url",
                "linkedin-url",
                "phone-number",
                "birthdate",
                "address",
                "gender",
            ],
            parser,
        )
        tenants_update(payload)

    # Users Commands
    def users(self, command):
        cmd_help = """caeops users <command> [<args>]

AVAILABLE COMMANDS
- register
- login
- update
- delete
- list
- get
- list-group
"""
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "users_{}".format(command.replace("-", "_")).strip("_")

        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name

        getattr(self, service_command)()

    @staticmethod
    def users_register():
        # Register a user to the CloudAEye platform
        parser = argparse.ArgumentParser(
            prog="caeops users register",
            description="Create a new tenant user in CloudAEye SAAS",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            [
                "email",
                "given-name",
                "family-name",
                "phone-number",
                "picture",
                "birthdate",
                "gender",
                "address",
                "linkedin-url",
            ],
            parser,
        )
        payload["role"] = "tenantUser"
        users_register(payload)

    @staticmethod
    def users_login():
        # Login for user
        parser = argparse.ArgumentParser(
            prog="caeops users login", description="Login to CloudAEye SAAS"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["email", "password"], parser)
        users_login(payload)

    @staticmethod
    def users_delete():
        # Delete a user
        parser = argparse.ArgumentParser(
            prog="caeops users delete", description="Delete tenant user"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["email_internal_use"], parser)
        users_delete(payload)

    @staticmethod
    def users_list():
        # Get a list of users
        parser = argparse.ArgumentParser(
            prog="caeops users list", description="List tenant users"
        )
        # Read tenantid from config.ini and add it to the request if it is not null
        users_list()

    @staticmethod
    def users_list_groups():
        # List groups that user is part of
        parser = argparse.ArgumentParser(
            prog="caeops users list_groups",
            description="list the groups that the user is part of",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["email_internal_use"], parser)
        users_list_groups(payload)

    @staticmethod
    def users_update():
        # Update the details of a registered user
        parser = argparse.ArgumentParser(
            prog="caeops users update", description="Update a tenant user"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            [
                "given-name",
                "family-name",
                "linkedin-url",
                "birthdate",
                "gender",
                "address",
                "email_internal_use",
            ],
            parser,
        )
        users_update(payload)

    @staticmethod
    def users_get():
        # Get a list of users
        parser = argparse.ArgumentParser(
            prog="caeops users get", description="Get user details"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["email"], parser)
        users_get(payload)

    # Groups Commands
    def groups(self, command):
        cmd_help = """caeops groups <command> [<args>]

AVAILABLE COMMANDS
   - add-users
   - list
   - list-users
   - remove-users
"""
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "groups_{}".format(command.replace("-", "_")).strip("_")

        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name

        getattr(self, service_command)()

    @staticmethod
    def groups_add_users():
        # Add users to the group
        parser = argparse.ArgumentParser(
            prog="caeops groups add-user", description="add user to a group"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["group-name", "email_internal_use"], parser
        )
        groups_add_users(payload)

    @staticmethod
    def groups_list():
        # List groups of the tenant
        parser = argparse.ArgumentParser(
            prog="caeops groups-list", description="list users in a group"
        )
        groups_list()

    @staticmethod
    def groups_list_users():
        # List the users in the group
        parser = argparse.ArgumentParser(
            prog="caeops groups list-users", description="list users in a group"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["group-name"], parser)
        groups_list_users(payload)

    @staticmethod
    def groups_remove_users():
        # Remove users from a group
        parser = argparse.ArgumentParser(
            prog="caeops groups removeuser", description="add user to a group"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["group-name", "email_internal_use"], parser
        )
        groups_remove_users(payload)

    # Service Groups   Commands
    def service_groups(self, command):
        cmd_help = """caeops users <command> [<args>]

AVAILABLE COMMANDS
- create
- list
- get
- list-services
"""
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "service_groups_{}".format(command.replace("-", "_")).strip(
            "_"
        )

        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name

        getattr(self, service_command)()

    @staticmethod
    def service_groups_create():
        # Create a group
        parser = argparse.ArgumentParser(
            prog="caeops service-groups create", description="Create a new group"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["group-name", "description"], parser
        )
        service_groups_create(payload)

    @staticmethod
    def service_groups_get():
        # Get details of a group
        parser = argparse.ArgumentParser(
            prog="caeops service-groups get", description="Get details of a group"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["group-name"], parser)
        service_groups_get(payload)

    @staticmethod
    def service_groups_list():
        # List all the groups
        parser = argparse.ArgumentParser(
            prog="caeops service-groups list", description="List all the groups"
        )
        service_groups_list()

    @staticmethod
    def service_groups_list_services():
        # List services in a group
        parser = argparse.ArgumentParser(
            prog="caeops service-groups list-services",
            description="List services in the group",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["group-name"], parser)
        service_groups_list_services(payload)

    @staticmethod
    def service_groups_update():
        # Get details of a group
        parser = argparse.ArgumentParser(
            prog="caeops service-groups get", description="Get details of a group"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["group-name", "description"], parser
        )
        service_groups_update(payload)

    # Metrics Commands
    def metrics(self, command):
        cmd_help = """caeops metrics <command> [<args>]

    AVAILABLE COMMANDS
       - create
       - delete
       - list
       - get
       - add-labels
       - delete-labels
       - get-labels
       - add-to-group
       - remove-from-group
    """
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "metrics_{}".format(command.replace("-", "_")).strip("_")

        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name

        getattr(self, service_command)()

    @staticmethod
    def metrics_create():
        # Create a Metrics Service instance
        parser = argparse.ArgumentParser(
            prog="caeops metrics create",
            description="Create a Metrics Service instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["name", "labels", "group-name"], parser
        )
        metrics_create(payload)

    @staticmethod
    def metrics_delete():
        # Delete a Metrics Service instance
        parser = argparse.ArgumentParser(
            prog="caeops metrics delete",
            description="Delete a Metrics Service instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        metrics_delete(payload)

    @staticmethod
    def metrics_list():
        # Get Metrics Service instances
        parser = argparse.ArgumentParser(
            prog="caeops metrics list", description="List Metrics Service instances"
        )
        metrics_list()

    @staticmethod
    def metrics_get():
        # Get Metrics Service instances
        parser = argparse.ArgumentParser(
            prog="caeops metrics get", description="Get a Metrics Service instance"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        metrics_get(payload)

    @staticmethod
    def metrics_add_labels():
        # Add labels to a Metrics Service instance
        parser = argparse.ArgumentParser(
            prog="caeops metrics create",
            description="Create a Metrics Service instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "labels"], parser)
        metrics_add_labels(payload)

    @staticmethod
    def metrics_delete_labels():
        # Delete labels from a Metrics Service instance
        parser = argparse.ArgumentParser(
            prog="caeops metrics create",
            description="Create a Metrics Service instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "labels"], parser)
        metrics_delete_labels(payload)

    @staticmethod
    def metrics_get_labels():
        # Get labels of Metrics Service instance
        parser = argparse.ArgumentParser(
            prog="caeops metrics create",
            description="Create a Metrics Service instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        metrics_get_labels(payload)

    @staticmethod
    def metrics_install_agent():
        # Fetches agent installation instruction for given logs source
        parser = argparse.ArgumentParser(
            prog="caeops metrics install-agent",
            description="Fetches instructions to install an agent for a given metrics source",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            [
                "service-name",
                "cloud",
                "source",
                "app-name",
                "kubernetes-cluster-name",
                "kubernetes-metrics-scrape-config",
                "docker-network",
                "metrics-scrape-config",
                "generate-default-scrape-config"
            ],
            parser,
        )
        metrics_install_agent(payload)

    @staticmethod
    def metrics_update_agent():
        # Fetches agent installation instruction for given logs source
        parser = argparse.ArgumentParser(
            prog="caeops metrics update-agent",
            description="Fetches instructions to update a running agent for a given metrics source",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            [
                "service-name",
                "enable",
                "cloud",
                "source",
                "app-name",
                "kubernetes-cluster-name",
            ],
            parser,
        )
        metrics_update_agent(payload)

    @staticmethod
    def metrics_add_to_group():
        parser = argparse.ArgumentParser(
            prog="caeops metrics-service add-to-group",
            description="Add Metrics Service to a group",
        )
        payload = ArgumentParser.get_payload_from_args(
            ["name", "group-name"],
            parser,
        )
        metrics_add_to_group(payload)

    @staticmethod
    def metrics_remove_from_group():
        parser = argparse.ArgumentParser(
            prog="caeops metrics-service get",
            description="Remove Metrics Service from a group",
        )
        payload = ArgumentParser.get_payload_from_args(
            ["name", "group-name"],
            parser,
        )
        metrics_remove_from_group(payload)

    # Dashboard Commands
    def dashboards(self, command):
        cmd_help = """caeops dashboards <command> [<args>]

AVAILABLE COMMANDS
   - provision
   - create
   - list
   - delete
"""
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "dashboards_{}".format(command.replace("-", "_")).strip("_")

        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name

        getattr(self, service_command)()

    @staticmethod
    def dashboards_create():
        # Create a Dashboards Service
        parser = argparse.ArgumentParser(
            prog="caeops dashboards create", description="Create Dashboards Service"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["name", "labels", "data-source"], parser
        )
        dashboards_create(payload)

    @staticmethod
    def dashboards_delete():
        # Delete a Dashboards Service
        parser = argparse.ArgumentParser(
            prog="caeops dashboards delete", description="Delete Dashboards Service"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        dashboards_delete(payload)

    @staticmethod
    def dashboards_list():
        # List Dashboards Services
        parser = argparse.ArgumentParser(
            prog="caeops dashboards list", description="List Dashboards Services"
        )
        dashboards_list()

    @staticmethod
    def dashboards_get():
        # List Dashboards Services
        parser = argparse.ArgumentParser(
            prog="caeops dashboards get", description="Get Dashboards Service"
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        dashboards_get(payload)

    @staticmethod
    def dashboards_add_labels():
        # Get a list of all services supported by cloudaeye
        parser = argparse.ArgumentParser(
            prog="caeops dashboards add-labels",
            description="Add labels to Dashboards Service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "labels"], parser)
        dashboards_add_labels(payload)

    @staticmethod
    def dashboards_delete_labels():
        # Get a list of all services supported by cloudaeye
        parser = argparse.ArgumentParser(
            prog="caeops dashboards delete-labels",
            description="Delete labels of Dashboards Service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "labels"], parser)
        dashboards_delete_labels(payload)

    @staticmethod
    def dashboards_get_labels():
        # Get a list of all services supported by cloudaeye
        parser = argparse.ArgumentParser(
            prog="caeops dashboards get-labels",
            description="Add labels of Dashboards Service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        dashboards_get_labels(payload)

    # Log Services
    #
    def logs(self, command):
        cmd_help = """caeops logs <command> [<args>]

    AVAILABLE COMMANDS
       - create
       - list
       - delete
       - get
       - add-labels
       - get-labels
       - add-to-group
       - remove-from-group
       - delete-labels
       - install-agent
       - update-agent
    """
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "logs_{}".format(command.replace("-", "_")).strip("_")
        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, service_command)()

    @staticmethod
    def logs_create():
        parser = argparse.ArgumentParser(
            prog="caeops logs create",
            description="Provisions a logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["name", "labels", "group-name"],
            parser,
        )
        logs_create(payload)

    @staticmethod
    def logs_list():
        parser = argparse.ArgumentParser(
            prog="caeops logs-service list",
            description="Lists all ES instance created by the tenant",
        )
        logs_list()

    @staticmethod
    def logs_get():
        parser = argparse.ArgumentParser(
            prog="caeops logs-service get",
            description="Gets the given ES instance",
        )
        payload = ArgumentParser.get_payload_from_args(
            ["name"],
            parser,
        )
        logs_get(payload)

    @staticmethod
    def logs_delete():
        parser = argparse.ArgumentParser(
            prog="caeops logs-service delete",
            description="Deletes the given ES instance created by the tenant",
        )
        payload = ArgumentParser.get_payload_from_args(
            ["name"],
            parser,
        )
        logs_delete(payload)

    @staticmethod
    def logs_add_labels():
        # Create labels for Dashboards Service
        parser = argparse.ArgumentParser(
            prog="caeops logs-service add-labels",
            description="Add labels to ES instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "labels"], parser)
        logs_add_labels(payload)

    @staticmethod
    def logs_delete_labels():
        # Delete labels for Dashboards Service
        parser = argparse.ArgumentParser(
            prog="caeops logs-service delete-labels",
            description="Delete labels from ES instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "labels"], parser)
        logs_delete_labels(payload)

    @staticmethod
    def logs_get_labels():
        # Get labels from Es
        parser = argparse.ArgumentParser(
            prog="caeops logs-service get-labels",
            description="Get labels from ES instance",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        logs_get_labels(payload)

    @staticmethod
    def logs_install_agent():
        # Fetches agent installation instruction for given logs source
        parser = argparse.ArgumentParser(
            prog="caeops logs install-agent",
            description="Fetches instructions to install an agent for a given logs source",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            [
                "service-name",
                "cloud",
                "source",
                "app-name",
                "kubernetes-cluster-name",
                "kubernetes-enable-system-logs",
                "docker-network"
            ],
            parser,
        )
        logs_install_agent(payload)

    @staticmethod
    def logs_update_agent():
        # Fetches agent installation instruction for given logs source
        parser = argparse.ArgumentParser(
            prog="caeops logs update-agent",
            description="Fetches instructions to update a running agent for a given logs source",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            [
                "service-name",
                "cloud",
                "source",
                "enable",
                "app-name",
                "kubernetes-cluster-name",
                "kubernetes-enable-system-logs",
            ],
            parser,
        )
        logs_update_agent(payload)

    @staticmethod
    def logs_add_to_group():
        parser = argparse.ArgumentParser(
            prog="caeops logs-service add-to-group",
            description="Add Dashboards Service to a group",
        )
        payload = ArgumentParser.get_payload_from_args(
            ["name", "group-name"],
            parser,
        )
        logs_add_to_group(payload)

    @staticmethod
    def logs_remove_from_group():
        parser = argparse.ArgumentParser(
            prog="caeops logs-service get",
            description="Remove Dashboards Service from a group",
        )
        payload = ArgumentParser.get_payload_from_args(
            ["name", "group-name"],
            parser,
        )
        logs_remove_from_group(payload)

    # Log Analyzer Services
    #
    def logs_analyzers(self, command):
        cmd_help = """caeops logs-analyzers <command> [<args>]

    AVAILABLE COMMANDS
       - create
       - list
       - get
       - update
       - delete
    """
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "logs_analyzers_{}".format(command.replace("-", "_")).strip(
            "_"
        )
        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, service_command)()

    @staticmethod
    def logs_analyzers_create():
        parser = argparse.ArgumentParser(
            prog="caeops logs-analyzers create",
            description="Creates a logs analyzer service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "data-sources"], parser)
        logs_analyzer_create(payload)

    @staticmethod
    def logs_analyzers_get():
        parser = argparse.ArgumentParser(
            prog="caeops logs-analyzers get",
            description="Fetches a single instance of the logs analyzer service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        logs_analyzer_get(payload)

    @staticmethod
    def logs_analyzers_list():
        parser = argparse.ArgumentParser(
            prog="caeops logs-analyzers list",
            description="Lists all instances of logs analyzer service",
        )
        logs_analyzer_list()

    @staticmethod
    def logs_analyzers_update():
        parser = argparse.ArgumentParser(
            prog="caeops logs-analyzers update",
            description="Update a given logs analyzer service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "data-sources"], parser)
        logs_analyzer_update(payload)

    @staticmethod
    def logs_analyzers_delete():
        parser = argparse.ArgumentParser(
            prog="caeops logs-analyzers delete",
            description="Deletes a given logs analyzer service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        logs_analyzer_delete(payload)

    @staticmethod
    def logs_create_parsing_rule():
        parser = argparse.ArgumentParser(
            prog="caeops logs create-parsing-rule",
            description="Creates a parsing rule for the given logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["name", "service-name", "plugin-name", "filter"],
            parser,
        )
        create_parsing_rule(payload)

    @staticmethod
    def logs_list_parsing_rules():
        parser = argparse.ArgumentParser(
            prog="caeops logs list-parsing-rules",
            description="Lists parsing rules for the given logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["service-name"],
            parser,
        )
        list_parsing_rules(payload)

    @staticmethod
    def logs_get_parsing_rule():
        parser = argparse.ArgumentParser(
            prog="caeops logs get-parsing-rule",
            description="Fetches a parsing rule with the given name for the given logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["service-name", "name"],
            parser,
        )
        get_parsing_rule(payload)

    @staticmethod
    def logs_update_parsing_rule():
        parser = argparse.ArgumentParser(
            prog="caeops logs update-parsing-rule",
            description="Updates a parsing rule with the given name for the given logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["service-name", "name", "filter"],
            parser,
        )
        update_parsing_rule(payload)

    @staticmethod
    def logs_delete_parsing_rule():
        parser = argparse.ArgumentParser(
            prog="caeops logs delete-parsing-rule",
            description="Deletes a parsing rule with the given name for the given logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["service-name", "name"],
            parser,
        )
        delete_parsing_rule(payload)

    @staticmethod
    def logs_enable_parsing_rule():
        parser = argparse.ArgumentParser(
            prog="caeops logs enable-parsing-rule",
            description="Enables a parsing rule with the given name for the given logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["service-name", "name"],
            parser,
        )
        enable_parsing_rule(payload)

    @staticmethod
    def logs_disable_parsing_rule():
        parser = argparse.ArgumentParser(
            prog="caeops logs disable-parsing-rule",
            description="Disables a parsing rule with the given name for the given logs service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["service-name", "name"],
            parser,
        )
        disable_parsing_rule(payload)

    # Metrics Analyzer Services
    #
    def metrics_analyzers(self, command):
        cmd_help = """caeops metrics-analyzers <command> [<args>]

    AVAILABLE COMMANDS
       - create
       - list
       - get
       - update
       - delete
    """
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "metrics_analyzers_{}".format(
            command.replace("-", "_")
        ).strip("_")
        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, service_command)()

    @staticmethod
    def metrics_analyzers_create():
        parser = argparse.ArgumentParser(
            prog="caeops metrics-analyzers create",
            description="Creates a metrics analyzer service",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "data-sources"], parser)
        metrics_analyzer_create(payload)

    @staticmethod
    def metrics_analyzers_get():
        parser = argparse.ArgumentParser(
            prog="caeops metrics-analyzers get",
            description="Fetches metrics analyzer with the given name",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        metrics_analyzer_get(payload)

    @staticmethod
    def metrics_analyzers_list():
        parser = argparse.ArgumentParser(
            prog="caeops metrics-analyzers list",
            description="Lists all the metrics analyzers created by the tenant",
        )
        metrics_analyzer_list()

    @staticmethod
    def metrics_analyzers_update():
        parser = argparse.ArgumentParser(
            prog="caeops metrics-analyzers update",
            description="Updates the given metrics analyzer",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name", "data-sources"], parser)
        metrics_analyzer_update(payload)

    @staticmethod
    def metrics_analyzers_delete():
        parser = argparse.ArgumentParser(
            prog="caeops metrics-analyzers delete",
            description="Deletes the given metrics analyzer",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["name"], parser)
        metrics_analyzer_delete(payload)

    # Notification Services
    #
    def notifications(self, command):
        cmd_help = """caeops notifications <command> [<args>]
    AVAILABLE COMMANDS
       - create-template
       - list-templates
       - get-template
       - update-template
       - delete-template
 
    """
        if command == "":
            print(cmd_help)
            exit(1)
        service_command = "notifications_{}".format(command.replace("-", "_")).strip(
            "_"
        )
        if not hasattr(self, service_command):
            print("Unrecognized command")
            print(cmd_help)
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, service_command)()

    @staticmethod
    def notifications_list_templates():
        parser = argparse.ArgumentParser(
            prog="caeops notifications list-templates",
            description="List notification templates",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(["medium"], parser)
        templates_list(payload)

    @staticmethod
    def notifications_get_template():
        parser = argparse.ArgumentParser(
            prog="caeops notifications get-template",
            description="Get a  notification template by name and medium",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["template-name", "medium"], parser
        )
        templates_get(payload)

    @staticmethod
    def notifications_delete_template():
        parser = argparse.ArgumentParser(
            prog="caeops notifications delete-template",
            description="Delete a notification template by name and medium",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["template-name", "medium"], parser
        )
        templates_delete(payload)

    @staticmethod
    def notifications_create_template():
        parser = argparse.ArgumentParser(
            prog="caeops notifications delete-template",
            description="Delete a notification template by name and medium",
        )
        # Take the input and add to parser and return it in camel case
        payload = ArgumentParser.get_payload_from_args(
            ["template-name", "medium", "template-file"], parser
        )
        templates_create(payload)


def run_main():
    Main()
    sys.exit()
