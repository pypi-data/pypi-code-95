import argparse

from caeops.global_settings import ConfigKeys
from caeops.utilities import json_keys_to_camel_case
import sys
from caeops.configurations import read


class ArgumentParser:
    # Add arguments to the parser based on the received parameters
    def __init__(self):
        pass

    @staticmethod
    def get_reserved_args():
        return ["version", "generate-cli-skeleton", "yaml", "input-file"]

    @staticmethod
    def convert_args_to_payload(args, keep_none=False):
        payload = args.__dict__
        # Collect keys that have value None
        drop_keys = list(
            filter(lambda ky: not payload[ky] and not keep_none, payload.keys())
        )
        for k in drop_keys:
            payload.pop(k, None)
        # Also drop reserved keys
        for k in ArgumentParser.get_reserved_args():
            payload.pop(k.replace("-", "_"), None)
        # Convert payload keys from kebab case to camel case
        payload_camel = json_keys_to_camel_case(payload)
        return payload_camel

    @staticmethod
    def get_payload_from_args(parameters, parser, keep_none=False):
        ArgumentParser.add_required_args(parameters, parser)
        return ArgumentParser.parse_args_and_convert_to_payload(parser, keep_none)

    @staticmethod
    def parse_args_and_convert_to_payload(parser, keep_none=False):
        args = parser.parse_args(sys.argv[3:])
        return ArgumentParser.convert_args_to_payload(args, keep_none=keep_none)

    @staticmethod
    def add_required_args(parameters, parser):
        "email" in parameters and parser.add_argument(
            "--email", help="Email id of the user"
        )
        "email_internal_use" in parameters and parser.add_argument(
            "--email", help="Email id of the user"
        )
        "tenant-id" in parameters and parser.add_argument(
            "--tenant-id", default=read(ConfigKeys.TENANT_ID), help="Enter tenant id"
        )
        "stack-region" in parameters and parser.add_argument(
            "--stack-region", default="us-east-2", help="AWS region"
        )
        "identifier" in parameters and parser.add_argument(
            "--identifier",
            default=read(ConfigKeys.IDENTIFIER),
            help="unique identifier",
        )
        "company" in parameters and parser.add_argument(
            "--company", default="", help="Name of the company"
        )
        "company-phone" in parameters and parser.add_argument(
            "--company-phone", default="", help="Phone number of the company."
        )
        "company-logo" in parameters and parser.add_argument(
            "--company-logo", default="", help="Logo of the company."
        )
        "company-url" in parameters and parser.add_argument(
            "--company-url", default="", help="Company official website url"
        )
        "password" in parameters and parser.add_argument(
            "--password", help="Password to login"
        )
        "new-password" in parameters and parser.add_argument(
            "--new-password", help="New password to be set"
        )
        "given-name" in parameters and parser.add_argument(
            "--given-name", default="", help="First name of the user"
        )
        "family-name" in parameters and parser.add_argument(
            "--family-name", default="", help="Last name of the user"
        )
        "role" in parameters and parser.add_argument(
            "--role", help="Role assigned to the user"
        )
        "phone-number" in parameters and parser.add_argument(
            "--phone-number", default="", help="Phone number of the user"
        )
        "linkedin-url" in parameters and parser.add_argument(
            "--linkedin-url", default="", help="Company LinkedIn url"
        )
        "birthdate" in parameters and parser.add_argument(
            "--birthdate", default="", help="DOB of the user"
        )
        "gender" in parameters and parser.add_argument(
            "--gender", default="", help="Gender of the user", choices=["male", "female", "other"]
        )
        "address" in parameters and parser.add_argument(
            "--address", default="", help="company official address"
        )
        "group-name" in parameters and parser.add_argument(
            "--group-name", help="Enter the name of the service group"
        )
        "group-id" in parameters and parser.add_argument(
            "--group-id", help="Id of the service group"
        )
        "users" in parameters and parser.add_argument(
            "--users", help="Enter the user ids"
        )
        "namespace" in parameters and parser.add_argument(
            "--namespace", help="tenant namespace"
        )
        "domain-name" in parameters and parser.add_argument(
            "--domain-name",
            help="Domain name of the Elastic Search",
        )
        "workspace-id" in parameters and parser.add_argument(
            "--workspace-id",
            help="Workspace id of the DashboaMetrics Service instance",
        )
        "labels" in parameters and parser.add_argument(
            "--labels", help="Labels for the service"
        )
        "name" in parameters and parser.add_argument("--name", help="Name of resource")
        "data-sources" in parameters and parser.add_argument(
            "--data-sources", help="Name of source you want to link"
        )
        "data-source" in parameters and parser.add_argument(
            "--data-source", help="Name of source you want to link"
        )
        "service-name" in parameters and parser.add_argument(
            "--service-name", help="Name of the service"
        )
        "cloud" in parameters and parser.add_argument(
            "--cloud",
            help="The type of cloud service providers. Supported providers : aws",
        )
        "source" in parameters and parser.add_argument(
            "--source",
            help="The type of cloud source that is sending logs. Supported resources : kubernetes | docker",
        )
        "medium" in parameters and parser.add_argument(
            "--medium",
            help="The medium of notification to send on. Supported resources : email | sms",
        )
        "template-name" in parameters and parser.add_argument(
            "--template-name",
            help="The name of notification template.",
        )
        "template-file" in parameters and parser.add_argument(
            "--template-file",
            help="The file containing notification template.",
        )
        "description" in parameters and parser.add_argument(
            "--description", help="Small description about the purpose of the group"
        )
        ArgumentParser.add_agent_params(parameters=parameters, parser=parser)
        ArgumentParser.add_logs_parser_params(parameters=parameters, parser=parser)
        return

    @staticmethod
    def _parse_bool_args(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    @staticmethod
    def add_input_file_args(parser):
        parser.add_argument(
            "--generate-cli-skeleton",
            help="Generate cli skeleton structure for the current command",
            action="store_true",
        )
        parser.add_argument(
            "--yaml", help="Use yaml format for the data. If not provided, defaults to json", action="store_true"
        )
        parser.add_argument(
            "--input-file",
            help="Absolute path to the input file",
        )
        return

    @staticmethod
    def add_agent_params(parameters, parser):
        """
        Adds logs service related command line params
        :param parameters: List of parameters
        :param parser: Command line argument parser
        """
        # Agent related command line arguments
        "kubernetes-cluster-name" in parameters and parser.add_argument(
            "--kubernetes-cluster-name",
            help="Name of the kubernetes cluster where the agent needs to run",
        )
        "enable" in parameters and parser.add_argument(
            "--enable",
            default=True,
            type=ArgumentParser._parse_bool_args,
            help="Determine whether to enable or disable the agent. Defaults to true",
        )
        "app-name" in parameters and parser.add_argument(
            "--app-name",
            help="An identification name to the app for which the agent is being installed or updated",
        )
        "docker-network" in parameters and parser.add_argument(
            "--docker-network",
            help="Name of the docker network on which the docker agent needs to run",
        )
        "metrics-scrape-config" in parameters and parser.add_argument(
            "--metrics-scrape-config",
            help="Path to the config file that contains the scrape target configuration for prometheus",
        )
        "kubernetes-enable-system-logs" in parameters and parser.add_argument(
            "--kubernetes-enable-system-logs",
            help="Determines whether or not to collect system level logs for the cluster",
            type=ArgumentParser._parse_bool_args,
        )
        "generate-default-scrape-config" in parameters and parser.add_argument(
            "--generate-default-scrape-config",
            help="Generates default scrape configuration structure to provide scrape targets while collecting metrics",
            action="store_true",
        )
        return

    @staticmethod
    def add_logs_parser_params(parameters, parser):
        """
        Adds logs parsing related command line params
        :param parameters: List of parameters
        :param parser: Command line argument parser
        """
        # Agent related command line arguments
        "plugin-name" in parameters and parser.add_argument(
            "--plugin-name",
            help="The name of the logstash plugin to use",
        )
        "filter" in parameters and parser.add_argument(
            "--filter",
            help="A parsing filter that specifies the pattern to apply on streaming logs",
        )
        return
