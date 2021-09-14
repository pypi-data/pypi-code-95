from library_nsxt.exceptions import APIError
from library_nsxt.models import Group
from library_nsxt.models import IPSet
from library_nsxt.models import Policy
from library_nsxt.models import Rule
from library_nsxt.models import Service
from library_nsxt.models import VMachine

class NSXTAPIParser:
    """This class contains methods to parse the global api responses into usable python models."""

    def __init__(self):
        """Default initializer that raises an error. Parser should not be instantiated, but used as a static class."""
        raise APIError("Parser class should not be initialized, but used as a static class.")

    @classmethod
    def parse_policies(cls, api_response):
        """
        Obtain the policy object instances from the loaded json config. The applications are located at:
        root > children[] > Domain > children[] > SecurityPolicy

        :param dict api_response: Map with all the security model remote objects.
        :return: A list of application objects and a list of error
        :rtype: dict[type, list[Policy]]
        """
        try:
            domains = [domain["Domain"] for domain in api_response["children"] if "Domain" in domain]
            domain_children = [child for domain in domains for child in domain["children"]]
            apps = [app["SecurityPolicy"] for app in domain_children if "SecurityPolicy" in app]
            return {Policy: cls.__ensure_unique([Policy.from_json(app) for app in apps])}
        except (KeyError, AttributeError, TypeError) as e:
            raise APIError("Policies not found at expected location. (%s): %s" % (e.__class__.__name__, e))

    @classmethod
    def parse_rules(cls, api_response):
        """
        Obtain the rule object instances from the loaded json config. The connections are located at:
        root > children[] > Domain > children[] > SecurityPolicy > children[] > Rule

        :param dict api_response: Map with all the security model remote objects.
        :return: A list of connection objects
        :rtype: dict[type, list[Rule]]
        """
        try:
            domains = [domain["Domain"] for domain in api_response["children"] if "Domain" in domain]
            domain_children = [child for domain in domains for child in domain["children"]]
            apps = [app["SecurityPolicy"] for app in domain_children if "SecurityPolicy" in app]
            app_children = [child for app in apps for child in app["children"]]
            rules = [rule["Rule"] for rule in app_children if "Rule" in rule]
            return {Rule: cls.__ensure_unique([Rule.from_json(rule) for rule in rules])}
        except (AttributeError, TypeError) as e:
            raise APIError("Rules not found at expected location. (%s): %s" % (e.__class__.__name__, e))

    @classmethod
    def parse_groups(cls, api_response):
        """
        Obtain the group object instances from the loaded json config. The groups are located at:
        root > children[] > Domain > children[] > Group

        :param dict api_response: Map with all the security model remote objects.
        :return: A list of service objects
        :rtype: dict[type, list[Group]]
        """
        try:
            domains = [domain["Domain"] for domain in api_response["children"] if "Domain" in domain]
            domain_children = [child for domain in domains for child in domain["children"]]
            raw_groups = [group["Group"] for group in domain_children if "Group" in group]
            groups = [group for group in raw_groups if group["_create_user"] != "system"]
            return {Group: cls.__ensure_unique([Group.from_json(group) for group in groups])}
        except (AttributeError, TypeError) as e:
            raise APIError("Groups not found at expected location. (%s): %s" % (e.__class__.__name__, e))

    @classmethod
    def parse_services(cls, api_response):
        """
        Obtain the service object instances from the loaded json config. The services are located at:
        root > children[] > Service

        :param dict api_response: Map with all the security model remote objects.
        :return: A list of service objects.
        :rtype: dict[type, list[Service]]
        """
        try:
            raw_services = [raw_srv["Service"] for raw_srv in api_response["children"] if "Service" in raw_srv]
            services = [service for service in raw_services if service["_create_user"] != "system"]
            return {Service: cls.__ensure_unique([Service.from_json(service) for service in services])}
        except (AttributeError, TypeError) as e:
            raise APIError("Services not found at expected location. (%s): %s" % (e.__class__.__name__, e))

    @classmethod
    def parse_ipsets(cls, api_response):
        """
        Obtain the ip set object instances from the loaded json config. The ip sets are located at:
        root > results[]

        :param dict api_response: Map with all the ipset model remote objects.
        :return: A list of ipset objects
        :rtype: dict[type, list[Ipset]]
        """
        try:
            raw_ipsets = [ipset for ipset in api_response["results"]]
            ipsets = [ipset for ipset in raw_ipsets if ipset["_create_user"] != "nsx_policy"]
            return {IPSet: cls.__ensure_unique([IPSet.from_json(ipset) for ipset in ipsets])}
        except (AttributeError, TypeError) as e:
            raise APIError("IPSets not found at expected location. (%s): %s" % (e.__class__.__name__, e))

    @classmethod
    def parse_vms(cls, api_response):
        """
        Obtain the virtual machine object instances from the loaded json config. The vms are located at:
        root > results[]

        :param api_response: Map with all the virtual machine model remote objects.
        :return: A list of vm objects
        :rtype: dict[type, list[VMachine]]
        """
        try:
            return {VMachine: [VMachine.from_json(vm) for vm in api_response["results"]]}
        except (AttributeError, TypeError) as e:
            raise APIError("Virtual Machines not found at expected location. (%s): %s" % (e.__class__.__name__, e))

    @classmethod
    def parse_virtual_servers(cls, vserver_type, api_response):
        """
        Obtain the virtual server object instances from the loaded json config. The vs are located at:
        root > results[]

        :param type vserver_type: VServer implementation. Either `VServerImperative` or `VServerDeclarative`
        :param dict api_response: Map with the virtual server model objects.
        :return: A list of virtual server objects.
        :rtype: list[VServer]
        """
        try:
            return [vserver_type.from_json(vs) for vs in api_response["results"]]
        except (AttributeError, TypeError) as e:
            raise APIError("Virtual server not found at expected location. (%s): %s" % (e.__class__.__name__, e))

    @staticmethod
    def __ensure_unique(model_list):
        """
        Filters repeated entries from the list of models. A model is considered repeated if it has the same ID and path
        as another model..

        :param list[NSXTSecurityModel] model_list: The list of models to filter.
        :return: All unique models from the source list.
        :rtype: list[NSXTSecurityModel]
        """
        seen = []
        unique_models = []
        for model in model_list:
            model_check = (model.id, model.get_path())
            if model_check not in seen:
                seen.append(model_check)
                unique_models.append(model)
        return unique_models