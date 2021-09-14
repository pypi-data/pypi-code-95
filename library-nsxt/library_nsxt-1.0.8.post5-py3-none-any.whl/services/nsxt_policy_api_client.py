import logging, urllib3
from library_nsxt.services.nsxt_api_parser import NSXTAPIParser
from library_nsxt.services.nsxt_api_session import NSXTAPISession
from library_nsxt.exceptions import *
from library_nsxt.models.generic.nsx_group import *
from library_nsxt.models.security.rule import *
from library_nsxt.models.security.policy import *

### Disable Warnings
urllib3.disable_warnings()


# Firewall Constants
URL_GROUPS = "/infra/domains/default/groups"
URL_GROUP = "/infra/domains/default/groups/%s"
URL_POLICIES = "/infra/domains/default/security-policies"
URL_ADD_MEMBER_GROUP = "/infra/domains/default/groups/%s/path-expressions/%s?action=add"
URL_ADD_PATH_EXPRESSION = "/infra/domains/default/groups/%s/path-expressions/%s"
URL_ADD_RULE = "/infra/domains/default/security-policies/%s/rules/%s"
URL_ADD_POLICY = "/infra/domains/default/security-policies/%s"


class NSXTPolicyAPIClient:
    """NSX-T policy API client"""

    def __init__(self, host, user, password, timeout=None, delete_timeout=None):
        """
        Client used to make requests to the NSX-T Policy API.

        :param str host: The host of the NSX-T API
        :param str user: The user of the BasicAuth used to connect to the NSX-T API
        :param str password: The user of the BasicAuth used to connect to the NSX-T API
        :param float or None timeout: The default max time to wait for each request before an error is thrown.
        """
        self.host = host
        self.session = NSXTAPISession(host, user, password, timeout)
        self.parser = NSXTAPIParser
        self._logger = logging.getLogger("%s@%s" % (self.__class__.__name__, host))
        self.__delete_timeout = delete_timeout

    # ------------------------------------------------------------------------------------------
    # FIREWALL METHODS
    # ------------------------------------------------------------------------------------------

    def get_nsx_groups(self, nsx_group_unique_id=None, info=False):
        """
        Get all info of all groups or a single group if 'idgroup' parameter is filled in JSON format
        :param nsx_group_unique_id: grup-id to retrive information
        :param info: flag True / False, output the info about all groups
        :return: List of dictionaries with all NSX groups on the cluster.
        :rtype: list
        """

        url = URL_GROUPS

        logging.debug("get_nsx_groups: %s" % URL_GROUPS)
        if nsx_group_unique_id:
            groups = self.session.get(URL_GROUPS, True)["results"]
            for group in groups:
                if group["unique_id"] == nsx_group_unique_id:
                    r = group
            if not "r" in locals():
                raise APIError("The nsx group unique id \"" + nsx_group_unique_id + "\" not match with any other nsx group unique id in NSX cluster.", None, "Bad nsx group unique id")
        else:
            r = self.session.get(URL_GROUPS, True)["results"]
        if info:
            logging.info("INFO ABOUT GROUPS: %s\n" % r)

        return r

    def check_if_nsgroup_exist(self, group_name):
        """
        Search existing group into the inventory.
        :param group_name: Display name of NSX group.
        :return: True if exists
        :rtype: bool
        """
        for nsx_group in self.get_nsx_groups():
            if nsx_group["display_name"] == group_name:
                exist = True

        if not "exist" in locals():
            exist = False

        return exist

    def post_nsx_group(self, group_name):
        """
        Create a NSX group not existing into the inventory.
        :param group_name: Display name of NSX group.
        """
        if self.check_if_nsgroup_exist(group_name) == True:
            raise NSXTError("The cluster group name \"" + group_name + "\" match with other cluster group name in NSX.",
                            "Group already exist")
        else:
            body = NSX_Policy_Group(group_name).to_json()
            self.session.patch(URL_GROUP %group_name, body, True)

    def get_nsx_group_unique_id(self, group_name):
        """
        Get specific id for a nsx group name.
        :param group_name: Display name of NSX group.
        :return: NSX group id.
        :rtype: str
        """
        for nsx_group in self.get_nsx_groups():
            if nsx_group["display_name"] == group_name:
                id = nsx_group["unique_id"]

        if not "id" in locals():
            raise APIError("The NSX group name supplied not match with any other in NSX cluster.", None, "Bad NSX group name")

        return id

    def put_nsx_member_group(self, master_group_name, member_group_name):
        """
        Add member group to nsx existing group.
        :param str master_group_name: Display name of NSX master group.
        :param str member_group_name: Display name of NSX member group.
        """
        if self.check_if_nsgroup_exist(master_group_name) == False:
            raise APIError("The master group name \"" + master_group_name + "\" not match with any other group name on NSX.", None, "Bad master group name")
        if self.check_if_nsgroup_exist(member_group_name) == False:
            raise APIError("The member group name \"" + member_group_name + "\" not match with any other group name on NSX.", None, "Bad member group name")

        master_group_unique_id = self.get_nsx_group_unique_id(master_group_name)
        master_group = self.get_nsx_groups(master_group_unique_id)
        if len(master_group["expression"]) == 0:
            path_exp_id = "master_exp"
            path_expression = NSX_Policy_Path_Expression(member_group_name, path_exp_id).to_json()
            self.session.patch(URL_ADD_PATH_EXPRESSION %(master_group_name, path_exp_id), path_expression, True)

        else:
            expression = master_group["expression"][0]
            nsx_group_member = NSX_Policy_Member_Group(member_group_name).to_json()
            for expression_path in expression["paths"]:
                if expression_path == nsx_group_member["members"][0]:
                    raise APIError("Group member \"" + member_group_name + "\" is already into the master group \"" + master_group_name + "\".", None, "Group is already into master group")
            self.session.post(URL_ADD_MEMBER_GROUP % (master_group_name, expression["id"]), nsx_group_member, True)

    def put_firewall_rule(self, rule_id, display_name, policy, tenant="default", connect_from=None, connect_to=None, services=["ANY"], description=None, revision=None):
        """
        Add or update existing firewall rule on specific nsx policy.
        :param str rule_id: The internal id of the rule.
        :param str display_name: The name displayed to the user.
        :param str policy: The name of the policy that this rule belongs to.
        :param str tenant: The owner of the rule. Default is "default"
        :param set[str] connect_from: The set of groups that are the source of the connection.
        :param set[str] connect_to: The set of groups that are the destination of the connection.
        :param set[str] services: The set of services that are allowed in the connection.
        :param str description: The optional description of the rule.
        :param int revision: The internal revision number of the rule in the NSX-T API.
        """
        rule = Rule(rule_id, display_name, policy, tenant, connect_from, connect_to, services, description, revision).to_json()
        self.session.put(URL_ADD_RULE % (policy, rule_id), rule, True)

    def put_firewall_policy_section(self, policy_id, display_name, category="Application", tenant="default", description=None, revision=None):
        """
        Add or update existing firewall policy section.
        :param str policy_id: The internal id of the policy.
        :param str display_name: The name displayed to the user.
        :param str category: The category of the Policy. Can be `Application`, `Environment` or `Infrastructure`. The
                             order of application of the firewall configuration depends on the order of categories.
        :param str tenant: The owner of the policy. Default is "default"
        :param str description: The optional description of the policy.
        :param int revision: The internal revision number of the policy in the NSX-T API.
        """
        policy = Policy(policy_id, display_name, category, tenant, description, revision).to_json()
        self.session.put(URL_ADD_POLICY % policy_id, policy, True)

    def get_firewall_policy_sections(self):
        """
        Get all firewall policy sections.
        """
        return self.session.get(URL_POLICIES, True)["results"]

    def check_if_firewall_policy_section_exist(self, policy_id):
        """
        Check if a firewall policy section exists with the specific policy_id
        :param str policy_id: The internal id of the policy.
        """

        policy_list = self.get_firewall_policy_sections()
        for policy in policy_list:
            if policy["id"] == policy_id:
                exist = True

        if not "exist" in locals():
            exist = False

        return exist