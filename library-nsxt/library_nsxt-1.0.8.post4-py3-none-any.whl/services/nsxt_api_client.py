import json, logging, inspect, urllib3
from library_nsxt.services.nsxt_api_parser import NSXTAPIParser
from library_nsxt.services.nsxt_api_session import NSXTAPISession
from library_nsxt.exceptions import *
from library_nsxt.models.generic.nsx_group import *
from library_nsxt.models.generic.nsx_rules_and_sections import *

### Disable Warnings
urllib3.disable_warnings()


_PATH_SECURITY_MODELS = "/infra?filter=Type-"
_PATH_IPSETS = "/ip-sets"
_PATH_VMS = "/fabric/virtual-machines"
_PATH_VMS_UPDATE_TAGS = "/fabric/virtual-machines?action=update_tags"

_PATH_NODE_TUNNELS = "/transport-nodes/%s/tunnels"
_PATH_LOGICAL_PORTS = "/logical-router-ports"
_PATH_LOGICAL_ROUTERS = "/logical-routers"
_PATH_LOGICAL_ROUTERS_STATUS = "/logical-routers/%s/status"
_PATH_LOGICAL_ROUTER_PORTS = "/logical-router-ports?logical_router_id=%s"
_PATH_LOGICAL_ROUTER_PORT_STATS = "/logical-router-ports/%s/statistics?transport_node_id=%s"
_PATH_TRANSPORT_NODES = "/transport-nodes"
_PATH_TRANSPORT_NODE_STATUS = "/transport-nodes/%s/status"
_PATH_ARP_TABLE = "/logical-router-ports/%s/arp-table%s&transport_node_id=%s"
_PATH_VIRTUAL_SERVERS = "/loadbalancer/virtual-servers"
_PATH_NODES = "/fabric/nodes"
_PATH_EDGE_CLUSTERS = "/edge-clusters"
_PATH_EDGE_CLUSTER_STATUS = "/edge-clusters/%s/status%s"
_PATH_LOAD_BALANCER_SERVICES = "/loadbalancer/services"
_PATH_LOAD_BALANCER_STATUS = "/loadbalancer/services/%s/status"
_PATH_LOAD_BALANCER_POOLS = "/loadbalancer/pools"
_PATH_LOAD_BALANCER_SPECIFIC_POOL = "/loadbalancer/pools/%s"
_PATH_LOAD_BALANCER_POOL_STATISTICS = "/loadbalancer/services/%s/pools/%s/statistics%s"
_PATH_LOAD_BALANCER_VIRTUAL_SERVERS_STATISTICS = "/loadbalancer/services/%s/virtual-servers/%s/statistics%s"
_PATH_LOAD_BALANCER_VIRTUAL_SERVERS_DEBUG_INFO = "/loadbalancer/services/%s/debug-info"
_PATH_MANAGER_CLUSTER_INFO = "/cluster"
_PATH_MANAGER_CLUSTER_STATUS = "/cluster/status"
_PATH_MANAGER_NODE_STATUS = "/cluster/nodes/%s/status"
_PATH_MANAGER_NODE_INFO = "/cluster/nodes/%s"
_PATH_MANAGER_NODE_INTERFACES = "/cluster/nodes/%s/network/interfaces"
_PATH_MANAGER_NODE_INTERFACES_STATS = "/cluster/nodes/%s/network/interfaces/%s/stats"
_PATH_MANAGER_SERVICES = "/cluster/%s/node/services"
_PATH_MANAGER_SERVICE_STATUS = "/cluster/%s/node/services/%s/status"

_logger = logging.getLogger("NSX-T API")

# Firewall Constants
URL_LIST_GROUPS = "/ns-groups"
URL_LIST_RULES = "/firewall/rules"
URL_LIST_RULES_IN_SECTION = "/firewall/sections/%s/rules"
URL_UPDATE_SECTION_WITH_RULES = "/firewall/sections/%s?action=update_with_rules"
URL_GET_GROUP = "/ns-groups/%s"
URL_LIST_SECTIONS = "/firewall/sections"
URL_LIST_IPSET = "/ip-sets"
URL_LIST_SERVICES = "/ns-services"
URL_GET_SECTIONS = "/firewall/sections"
URL_GET_RULE_CONFIG = "/firewall/sections/%s/rules/%s"

# URL Parameters
_SOURCE_REALTIME = "?source=realtime"


class NSXTAPIClient:
    """NSX-T API client"""

    def __init__(self, host, user, password, timeout=None, delete_timeout=None):
        """
        Client used to make requests to the NSX-T API.

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

    def get_security_models(self):
        """
        Gathers all security models.

        :return: A dictionary of security model items, keyed by type.
        :rtype: dict[type, list[NSXTSecurityModel]]
        """
        output = {}
        raw_api_response = self.session.get(_PATH_SECURITY_MODELS, security_api=True)
        output.update(self.parser.parse_policies(raw_api_response))
        output.update(self.parser.parse_rules(raw_api_response))
        output.update(self.parser.parse_groups(raw_api_response))
        output.update(self.parser.parse_services(raw_api_response))
        return output

    def get_ipsets(self):
        """
        Gathers all ip set models.

        :return: A dictionary of ip set model items, sorted by class.
        :rtype: dict[type, list[NSXTModel]]
        """
        return self.parser.parse_ipsets(self.session.get(_PATH_IPSETS))

    def get_vms(self):
        """
        Gathers all virtual machine models.

        :return: A dictionary of virtual machine items, sorted by class.
        :rtype: dict[type, list[VMachine]]
        """
        return self.parser.parse_vms(self.session.get(_PATH_VMS))

    def get_node_peers(self, node_id):
        """
        Retrieves the node peers in a NSX-T cluster of a given node id.

        :param str node_id: The target node ID
        :return: The node peers of the given node ID.
        :rtype: dict
        """
        return {tunnel["remote_ip"]: tunnel["remote_node_display_name"].split(".")[0]
                for tunnel in self.session.get(_PATH_NODE_TUNNELS % node_id)["tunnels"]}

    def get_downlink_ports(self, ip_prefix=None):
        """
        Retrieves the DownLink ports from a NSX-T cluster. If ip_prefix is set, only those that match the destination
        IP will be returned.

        :param str ip_prefix: The IP group or subnet prefix that identifies the required subnet.
        :return: The DownLink logical ports of the NSX-T cluster that match.
        :rtype: list[dict]
        """
        logical_ports = self.session.get(_PATH_LOGICAL_PORTS)["results"]
        return [port for port in logical_ports
                if port["resource_type"] == "LogicalRouterDownLinkPort"
                and "dummy" not in port["display_name"]
                and (ip_prefix is None or port["subnets"][0]["ip_addresses"][0].startswith(ip_prefix))]

    def get_arp_table(self, port_id, transport_node_id):
        """
        Retrieves the ARP table from a transport node of a logical router port.

        :param str port_id: The ID of the logical router port to get the ARP table from.
        :param str transport_node_id: The ID of the target transport node to get the ARP table from.
        :return: The ARP table or an empty list if it could not be gathered.
        :rtype: list[dict]
        """
        raw_response = self.session.get(_PATH_ARP_TABLE % (port_id, _SOURCE_REALTIME, transport_node_id))
        return raw_response["results"] if "results" in raw_response else []

    # ------------------------------------------------------------------------------------------
    # FIREWALL METHODS
    # ------------------------------------------------------------------------------------------
    def get_nsx_groups(self, nsx_group_id=None, info=False):
        """
        Get all info of all groups or a single group if 'idgroup' parameter is filled in JSON format
        :param nsx_group_id: grup-id to retrive information
        :param info: flag True / False, output the info about all groups
        :return: List of dictionaries with all NSX groups on the cluster.
        :rtype: list
        """
        url = ""
        if not nsx_group_id:
            url += URL_LIST_GROUPS
        else:
            url += URL_GET_GROUP % nsx_group_id

        logging.debug("get_nsx_groups: %s" % url)
        if nsx_group_id:
            r = self.session.get(url)
        else:
            r = self.session.get(url)["results"]
        if info:
            logging.info("INFO ABOUT GROUPS: %s\n" % r)

        return r

    def get_nsx_group_id(self, group_name):
        """
        Get specific id for a nsx group name.
        :param group_name: Display name of NSX group.
        :return: NSX group id.
        :rtype: str
        """
        for nsx_group in self.get_nsx_groups():
            if nsx_group["display_name"] == group_name:
                id = nsx_group["id"]

        if not "id" in locals():
            raise APIError("The NSX group name supplied not match with any other in NSX cluster.", None, "Bad NSX group name")

        return id

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
            raise NSXTError("The cluster group name \"" + group_name + "\" match with other cluster group name in NSX.", "Group already exist")
        else:
            body = NSX_Group(group_name).to_json()
            self.session.post(URL_LIST_GROUPS, body, False)

    def put_nsx_member_group(self, master_group_name, member_group_name):
        """
        Add member group to nsx existing group.
        :param str master_group_name: Display name of NSX master group.
        :param str member_group_name: Display name of NSX member group.
        """
        nsx_group_id = self.get_nsx_group_id(master_group_name)
        nsx_member_group_id = self.get_nsx_group_id(member_group_name)
        nsx_group = self.get_nsx_groups(nsx_group_id)
        nsx_group["members"].append(NSX_Member_Group(nsx_member_group_id).to_json())
        self.session.put(URL_GET_GROUP % nsx_group_id, nsx_group)

    def get_group_id_from_device(self, group_name):
        """
        Obtain the ID asociated to the group name from device
        :param group_name: group name to search
        :return: ID's group
        """
        json_group = self.get_nsx_groups()

        list_json_group = json_group[1]
        work_list = json.loads(list_json_group)
        results = work_list["results"]
        i = [i for i in results if i["display_name"] == group_name]

        return i[0]["id"]

    def get_id_from_group(self, groupname):
        """
        Auxiliary function to extract ID code from json schema
        :param groupname: group name to search
        :return: the ID group
        """
        result, content = self.get_nsx_groups()
        idcontent = ""
        if result == 200:
            json_content = json.loads(content)
            sources_list = json_content["results"]
            for i in sources_list:
                if i["display_name"] == groupname:
                    idcontent = i["id"]

        return idcontent

    def get_firewall_inventory_sections(self, idsection=None, info=None):
        """
        Return all the sections existing into de inventory or the information about one section
        :param idsection: the ID of the section to consult
        :param info: True = print info in console
        :return: the infor in json format
        """
        if not idsection:
            url = URL_LIST_SECTIONS
        else:
            url = URL_LIST_SECTIONS + "/" + idsection

        logging.debug("Get Section: " + url)
        r = self.session.get(path=url)
        if info:
            logging.info("INFO ABOUT SECTIONS:%s\n" % r)

        return r

    def get_firewallsection_rules(self, id_section, identificator=None, info=None):
        """
        Return Json with all rules in one firewall section.
        :param id_section: id of the section to search.
        :param info: True=prints info about rule.
        :return: Json with info.
        """
        url = URL_LIST_RULES
        if id_section:
            url = URL_LIST_RULES_IN_SECTION % id_section
        logging.debug("Getting Rules: " + url)
        r = self.session.get(url)
        if info:
            logging.info("INFO ABOUT RULES:%s\n" % r)
        if identificator:
            # search by rule identificator id
            for i in r['results']:
                if i['id'] == identificator:
                    r = i

        return r

    def get_id_rule_from_firewall(self, section_name, rule_name):
        """
        Obtain the ID of the rule name
        :param section_name: the name of the section
        :param rule_name: the name of the
        :return: ID of the rule indicated
        """
        url = URL_LIST_SECTIONS
        sections = self.session.get(url)
        rv = None
        for s in sections['results']:
            if s['display_name'] == section_name:
                section_id = s['id']
        if section_id:
            url = URL_LIST_RULES_IN_SECTION % section_id

        rules = self.session.get(url)
        for r in rules['results']:
            if r['display_name'] == rule_name:
                rv = r['id']

        return rv

    def get_id_from_firewallsection_rule(self, section_id, rule_name):
        """
        Search the ID of one rule
        :param section_id: ID where the rule exists
        :param rule_name: the name of the rule
        :return: ID of the rule / None if not exist
        """
        rv = None
        logging.debug("Get ID from Rule: %s in section: %s" % (rule_name, section_id))
        json_rules = self.get_firewallsection_rules(section_id)

        for rule in json_rules["results"]:
            if rule["display_name"] == rule_name:
                rv = rule["id"]

        return rv

    def get_id_from_firewall_inventory_section(self, section_name):
        """
        Return the ID of an existing section
        :param section_name: the name of the section (human friendly)
        :return: ID of specific section.
        :rtype: str
        """
        content = self.get_firewall_inventory_sections()["results"]
        for i in content:
            if i["display_name"] == section_name:
                idcontent = i["id"]

        if not "idcontent" in locals():
            raise APIError("The specific section name \"" + section_name + "\" not match with any other section in NSX cluster.", None, "Bad Section Name")
        else:
            return idcontent

    def check_if_firewall_inventory_section_exist(self, section_name):
        """
        Return the ID of an existing section
        :param section_name: the name of the section (human friendly)
        :return: True if exist or False if not exist.
        :rtype: bool
        """
        for section in self.get_firewall_inventory_sections()["results"]:
            if section["display_name"] == section_name:
                r = True
                break
            else:
                r = False

        return r

    def post_firewall_inventory_section(self, section_name, operation=None):
        """
        Create a firewall inventory section into the NSX.
        :param section_name: the name of the section (human friendly)
        :param operation: The operation type to append the section, (optional).
                          Operation types: insert_top, insert_bottom, insert_after, insert_before
                          Default: "insert_top"
        """
        if self.check_if_firewall_inventory_section_exist(section_name) == True:
            raise APIError("The section name \"" + section_name + "\" already exists.", None, "Section already exists")
        if operation == None:
            url = URL_LIST_SECTIONS
        else:
            url = URL_LIST_SECTIONS + "?operation=" + operation
        section = NSX_Sections(section_name).to_json()
        self.session.post(url, section)

    def post_firewallsection_rules(self, section_name, section_id, rules, revision):
        """
        Post specific section with specific rules in body.
        :param section_name: The inventory section name.
        :param section_id: id of the section to search.
        :param rules: The rules to append to specific section.
        :param revision: The revision number of the specific section.
        """
        rules = NSX_Rules(section_name, section_id, rules, revision).to_json()
        self.session.post(URL_UPDATE_SECTION_WITH_RULES %section_id, rules)

    def list_firewall_sections(self, info=False):
        """
        Helper function, used to list all sections in firewall option
        :param user: the user to connect
        :param password: his password
        :param iphost: the ip host
        :return: the code status & json with all content
        """
        url = URL_GET_SECTIONS
        rv = self.session.get(url)
        if info:
            print(rv)

        return rv

    def get_firewall_section_name(self, section_id):
        """
        Get the name of the firewall section, searching by ID
        :param section_id: id to search
        :return: the name of the section
        """
        rescode, json_group = self.get_firewall_inventory_sections()
        if rescode == 200:
            work_list = json.loads(json_group)
            results = work_list["results"]
            i = [i for i in results if i["id"] == section_id]
            if len(i) > 0:
                return i[0]["display_name"]
            else:
                return None
        else:
            return None

    def get_firewall_rule_body(self, rule_name, section_name):
        """
        Returns the body of the rule mentioned by parameter
        :param rule_name: the rule to search
        :param section_name: the section where the rule exist
        :return: json with the rule definition
        """
        rv = {}
        id_section = self.get_id_from_firewall_inventory_section(section_name)
        rules = self.get_firewallsection_rules(id_section)
        rules_list = rules

        for rule in rules_list["results"]:

            if rule["display_name"] == rule_name:
                rv = rule
        return rv

    @staticmethod
    def get_firewall_rule_name(localization, name):
        """
        Performs firewall rule name
        :param localization: localization code string
        :param name: name code string
        :return: string with the firewall rule name
        """
        return "rl-%s-cbs-cl-%s" % (localization, name)

    def get_ipsets_imperative(self, idipset=None, info=False):
        """
        Returns IPSet List or only one IPSet if the parameter is filled
        :param idipset: if you need a particular ipset, indicate in this parameter his ID
        :param info: True=prints info about the ipset
        :return: status code & content in json format
        """
        url = ""
        if not idipset:
            url += URL_LIST_IPSET
        else:
            url += URL_LIST_IPSET + "/" + idipset

        r = self.session.get(url)

        if info:
            logging.info("INFO ABOUT IPSets:%s\n" % r)

        rv = None
        if r:
            rv = r
        return 200, rv

    def get_id_from_ipset_imperative(self, ipset_name):
        """
        Return the ID of the IPSet name item passed by parameter
        :param ipset_name: IPSet name to search
        :return: ID of the ipset or none
        """
        result, content = self.get_ipsets_imperative()
        idcontent = None
        if content:
            lista = content['results']
            for i in lista:
                if i["display_name"] == ipset_name:
                    idcontent = i["id"]

        return idcontent

    def get_ipset_name_imperative(self, ipset_id):
        """
        Get the name of the IPSET, searching by ID
        :param ipset_id: the ID to search
        :return: his name or None
        """
        result, json_group = self.get_ipsets_imperative()

        results = json_group["results"]
        i = [i for i in results if i["id"] == ipset_id]
        if i:
            return i[0]["id"]
        else:
            return None

    def get_ip_set_service_body_imperative(self, ipset_name, field_name=None):
        """
        Return the body of a service searched by name, optionaly, you can indicate "field", and then, this method
        will search by this field, the content
        By default, this method search by 'display_name' field, but you can indicate other field in the 2nd. parameter
        :param ipset_name: service's name to search
        :param field: field name by that you want to search. [optional]
        :return: info in json format or none
        """
        _, all_ipsets = self.get_ipsets_imperative()
        rv = None
        json_services = all_ipsets
        if not field_name:
            for service in json_services["results"]:
                if service["display_name"] == ipset_name:
                    rv = service
                    break
        else:
            for service in json_services["results"]:
                if service["display_name"] == ipset_name:
                    if field_name in service:
                        rv = service[field_name]
                    else:
                        rv = None
                    break
        return rv

    # ---------------SERVICE METHODS
    # ------------------------------
    def get_services_imperative(self, idservice=None):
        """
        Obtain all de services available in inventory
        :param idservice: indicate the is of the service to search
        :return: result in json format or none
        """
        if not idservice:
            url = URL_LIST_SERVICES
        else:
            url = URL_LIST_SERVICES + "/%s" % idservice

        data = self.session.get(url)

        return data

    def get_service_body_imperative(self, service_name, field_name=None):
        """
        Return the body of a service searched by name, optionaly, you can indicate "field", and then, this method
        will search by this field, the content
        By default, this method search by 'display_name' field, but you can indicate other field in the 2nd. parameter
        :param service_name: service's name to search
        :param field_name: field name by that you want to search. [optional]
        :return: info in json format
        """
        all_services = self.get_services_imperative()

        if all_services:
            if not field_name:
                for service in all_services["results"]:
                    if service["display_name"] == service_name:
                        return service
            else:
                for service in all_services["results"]:
                    if service["display_name"] == service_name:
                        return service[field_name]

        else:
            return None

    # -------------------- UTILS METHODS
    # ----------------------------------

    def get_transport_node_uuid(self, display_name):
        """
        Get transport node UUID for an specific transport node.
        :param str display_name: NSX-T transport node display name.
        :return: Dictionary with transport node id.
        :rtype: str
        """
        for node in self.get_transport_nodes():
            if display_name == node["display_name"]:
                result = node["id"]
                break

        if not "result" in locals():
            raise APIError("The node name supplied not match with any host in NSX", None, "Bad Name")

        return result

    def get_transport_nodes(self):
        """
        Get all nodes in a list of dictionaries.
        :return: List of dictionaries with all nodes of NSX-T.
        :rtype: list
        """
        nodes = self.session.get(_PATH_TRANSPORT_NODES, False)["results"]
        return nodes

    def get_esx_nodes(self):
        """
        Get all ESX nodes in a list of dictionaries.
        :return: List of dictionaries with all ESX nodes of NSX-T.
        :rtype: list
        """
        esx_nodes = []
        nodes = self.get_transport_nodes()
        for node in nodes:
            if "os_type" in node["node_deployment_info"]:
                if node["node_deployment_info"]["os_type"] == "ESXI":
                    esx_nodes.append(node)

        if not "esx_nodes" in locals():
            raise APIError("No ESX nodes matched in NSX-T system", False, "No ESX nodes matched")
        return esx_nodes

    def get_edge_cluster_node_status(self, display_name):
        """
        Returns the status of the edge cluster for the NSX-T edge transport node.
        :param str display_name: NSX-T node display name.
        :return: Status of the edge cluster for the NSX node.
        :rtype: str
        """
        for edge_node in self.get_edge_clusters_member_list():
            if edge_node["uuid"] == self.get_transport_node_uuid(display_name):
                status = self.session.get(_PATH_EDGE_CLUSTER_STATUS %(edge_node["edge_cluster_id"], _SOURCE_REALTIME), False)["edge_cluster_status"]
                break

        if not "status" in locals():
            raise APIError("The node name supplied not match with any host in NSX", None, "Bad Name")

        return status

    def get_edge_clusters_member_list(self):
        """
        Get a list with all members of all edge clusters in NSX.
        :return: List of dictionaries for all member of all edge clusters.
        :rtype: list
        """
        edge_clusters = self.get_edge_clusters()
        member_list = []
        for edge_cluster in edge_clusters:
            for member in edge_cluster["members"]:
                member_list.append({"uuid": member["transport_node_id"], "edge_cluster_id": edge_cluster["id"]})
        return member_list

    def get_edge_clusters(self):
        """
        Get all edge clusters of NSX.
        :return: List of dictionaries with all edge clusters of NSX.
        :rtype: list
        """
        raw_edge_clusters = self.session.get(_PATH_EDGE_CLUSTERS, False)["results"]
        return raw_edge_clusters

    def get_logical_routers(self):
        """
        Get all logical_routers of NSX-T.
        :return: List of dictionaries for all logical routers in NSX.
        :rtype: list
        """
        logical_routers = self.session.get(_PATH_LOGICAL_ROUTERS, False)["results"]
        return logical_routers

    def get_node_logical_routers(self, display_name):
        """
        Get all logical_routers for NSX transport node and node status of connection with the logical router.
        :param str display_name: NSX-T transport node display name.
        :return: List of dictionaries for the logical_routers of the given transport node display name.
        :rtype: list
        """
        edge_cluster_status = self.get_edge_cluster_node_status(display_name)
        logical_router_list = []
        transport_node_uuid = self.get_transport_node_uuid(display_name)

        for edge_node in self.get_edge_clusters_member_list():
            if edge_node["uuid"] == transport_node_uuid:
                edge_cluster_id = edge_node["edge_cluster_id"]
                break

        if not "edge_cluster_id" in locals():
            raise APIError("The node name supplied not match with any host in NSX", None, "Bad Name")

        for logical_router in self.get_logical_routers():
            if not "edge_cluster_id" in logical_router:
                break
            else:
                if edge_cluster_id == logical_router["edge_cluster_id"]:
                    logical_router_list.append({"logical_router_id": logical_router["id"],
                                                "edge_cluster_id": logical_router["edge_cluster_id"],
                                                "display_name": logical_router["display_name"],
                                                "router_type": logical_router["router_type"],
                                                "high_availability_mode": logical_router["high_availability_mode"],
                                                "edge_cluster_status": edge_cluster_status,
                                                "per_node_status": []
                                                })
                    if logical_router["edge_cluster_id"] == edge_cluster_id:
                        for logical_router_per_node_status in self.get_logical_router_per_node_status(logical_router["id"])["per_node_status"]:
                            if logical_router_per_node_status["transport_node_id"] == transport_node_uuid:
                                logical_router_list[-1]["per_node_status"].append({"transport_node_id": logical_router_per_node_status["transport_node_id"],
                                                                                   "service_router_id": logical_router_per_node_status["service_router_id"],
                                                                                   "high_availability_status": logical_router_per_node_status["high_availability_status"]
                                                                                   })

        if not logical_router_list:
            raise APIError("The edge cluster id supplied not match with any other edge cluster id in the logical routers list", None, "Bad Edge Cluster ID")

        return logical_router_list

    def get_logical_router_per_node_status(self, logical_router_id):
        """
        Returns the status of specific logical router per node connected.
        :param str logical_router_id: The logical router id.
        :return: Dict with all nodes connected to specific logical router and their status on the same logical router.
        :rtype: dict
        """
        per_node_status = self.session.get(_PATH_LOGICAL_ROUTERS_STATUS %logical_router_id, False)
        return per_node_status

    def get_logical_router_transport_node_status(self, logical_router_id, display_name):
        """
        Returns the status of specific logical router on the specific connected transport node .
        :param str logical_router_id: The logical router id.
        :param str display_name: NSX-T node display name.
        :return: String with the status of specific node on the specific logical router.
        :rtype: str
        """
        logical_routers = self.get_node_logical_routers(display_name)
        for logical_router in logical_routers:
            if logical_router["logical_router_id"] == logical_router_id:
                return logical_router["per_node_status"][0]["high_availability_status"]

    def get_tier0_logical_router(self, display_name):
        """
        Returns the Tier 0 logical router for the given NSX-T Edge Node.
        :param str display_name: NSX-T node display name.
        :return: The Tier 0 logical router of the Edge Node.
        :rtype: dict
        """
        logical_routers = self.get_node_logical_routers(display_name)

        for logical_router in logical_routers:
            if logical_router["router_type"] == "TIER0":
                return logical_router
            else:
                raise NSXTError("The method " + inspect.currentframe().f_code.co_name + " not work", "UNKNOWN")

    def get_logical_router_status(self, logical_router_id):
        """
        Returns the status for the given logical router on the especific node of NSX.
        :param str logical_router_id: The logical router id.
        :return: The status of the logical router.
        :rtype: dict
        """
        logical_routers = self.get_logical_routers()

        for logical_router in logical_routers:
            if logical_router_id == logical_router["id"]:
                return logical_router["high_availability_mode"]

    def get_logical_router_ports(self, logical_router_id):
        """
        Returns all logical router ports of specific logical router.
        :param str logical_router_id: The logical router id.
        :return: List of dictionaries with all logical router ports of specific logical router.
        :rtype: list
        """
        logical_router_ports = list(self.session.get(_PATH_LOGICAL_ROUTER_PORTS %logical_router_id, False)["results"])
        return logical_router_ports

    def get_logical_router_port_stats(self, logical_router_port_id, display_name):
        """
        Returns all logical router ports of specific logical router.
        :param str logical_router_port_id: The logical router port id.
        :param str display_name: Transport node display name.
        :return: List of dictionaries with all logical router ports of specific logical router.
        :rtype: list
        """
        transport_node_id = self.get_transport_node_uuid(display_name)
        logical_router_port_stats = self.session.get(_PATH_LOGICAL_ROUTER_PORT_STATS %(logical_router_port_id, transport_node_id))["per_node_statistics"][0]
        return logical_router_port_stats

    def get_node_logical_router_port_stats(self, display_name):
        """
        Returns all logical router ports of all logical routers on the same edge cluster of specific transport node.
        :param str display_name: Transport node display name.
        :return: List of dictionaries with all logical router ports of all logical routers of specific transport node.
        :rtype: list
        """
        logical_routers = self.get_node_logical_routers(display_name)
        logical_router_ports_list = []
        for logical_router in logical_routers:
            logical_router_ports_list.append({"logical_router_id": logical_router["logical_router_id"],
                                              "display_name": logical_router["display_name"],
                                               "logical_router_ports": []
                                               })
            logical_router_ports = self.get_logical_router_ports(logical_router["logical_router_id"])
            for logical_router_port in logical_router_ports:
                logical_router_port_stats = self.get_logical_router_port_stats(logical_router_port["id"], display_name)
                logical_router_ports_list[-1]["logical_router_ports"].append({"logical_router_port_id": logical_router_port["id"],
                                                                              "display_name": logical_router_port["display_name"],
                                                                              "stats": logical_router_port_stats
                                                                              })

        return logical_router_ports_list

    def get_load_balancer_services(self):
        """
        Returns all load balancer services with their virtual servers.
        :return: List of dictionaries with all load balancer services and their virtual servers.
        :rtype: list
        """
        lb_services = self.session.get(_PATH_LOAD_BALANCER_SERVICES, False)["results"]
        return lb_services

    def get_load_balancer_status(self, lb_service_id):
        """
        Returns the specific load balancer service status with their virtual servers and pools status information.
        :param str load_balancer_id: Load balancer identifier.
        :return: Dictionary with all status information of specific load balancer and their virtual servers.
        :rtype: dict
        """
        lb_status = self.session.get(_PATH_LOAD_BALANCER_STATUS %lb_service_id, False)
        return lb_status

    def get_load_balancer_pools(self):
        """
        Returns all load balancer pools with their information members.
        :return: List of dictionaries with all load balancer pools and their members information.
        :rtype: list
        """
        lb_pools = self.session.get(_PATH_LOAD_BALANCER_POOLS, False)["results"]
        return lb_pools

    def get_load_balancer_specific_pool(self, lb_pool_id):
        """
        Returns a specific load balancer pool with their information members.
        :param str lb_pool_id: The load balancer pool id.
        :return: Dictionary with specific load balancer pool and their members information.
        :rtype: dict
        """

        pool = self.session.get(_PATH_LOAD_BALANCER_SPECIFIC_POOL %lb_pool_id, False)
        return pool

    def get_load_balancer_pool_statistics(self, lb_service_id, lb_pool_id ):
        """
        Returns the statistics list of load balancer specific pool in given load balancer service.
        :param str lb_service_id: The load balancer service id.
        :param str lb_pool_id: The load balancer pool id.
        :return: List of dictionaries with all load balancer pools statistics of the given load balancer service.
        :rtype: list
        """
        lb_pool = self.session.get(_PATH_LOAD_BALANCER_POOL_STATISTICS %(lb_service_id, lb_pool_id, _SOURCE_REALTIME), False)
        return lb_pool

    def get_load_balancer_virtual_servers(self):
        """
        Retrieve a paginated list of load balancer virtual servers.
        :return: List of dictionaries with all load balancer pools statistics of the given load balancer service.
        :rtype: list
        """
        lb_virtual_servers = self.session.get(_PATH_VIRTUAL_SERVERS, False)["results"]
        return lb_virtual_servers

    def get_load_balancer_virtual_server_statistics(self, lb_service_id, virtual_server_id):
        """
        Returns the statistics of specific virtual server in given load balancer service.
        :param str lb_service_id: The load balancer service id.
        :param str virtual_server_id: The virtual server id.
        :return: Dictionary with all statistics of specific virtual server on the given load balancer service.
        :rtype: dict
        """
        lb_virtual_server_stats = self.session.get(_PATH_LOAD_BALANCER_VIRTUAL_SERVERS_STATISTICS % (lb_service_id, virtual_server_id, _SOURCE_REALTIME), False)["statistics"]
        return lb_virtual_server_stats

    def get_load_balancers(self):
        """
        Returns all load balancers and all virtual servers on each load balancer with their statistics, too return all pools of each load balancer with members information and their statistics.
        :return: List of dictionaries with all load balancers and their virtual servers with their pools and their members with their statistics.
        :rtype: list
        """
        load_balancer_services = self.get_load_balancer_services()
        load_balancers_list = []
        vs_num_up = 0
        pool_num_up = 0
        for lb in load_balancer_services:
            lb_status = {"lb_status": self.get_load_balancer_status(lb["id"])}
            if "virtual_servers" in lb_status["lb_status"] and "pools" in lb_status["lb_status"]:
                del lb_status["lb_status"]["service_id"], lb["_create_user"], lb["_create_time"], lb["_last_modified_user"], \
                    lb["_last_modified_time"], lb["_system_owned"], lb["_protection"], lb["_revision"]
                for virtual_server in lb_status["lb_status"]["virtual_servers"]:
                    if virtual_server["status"] == "UP":
                        vs_num_up += 1
                    virtual_server_debug_info = self.get_load_balancers_virtual_servers_debug_info(lb["id"], virtual_server["virtual_server_id"])
                    virtual_server["ip_address"] = virtual_server_debug_info["ip_address"]
                    virtual_server["display_name"] = virtual_server_debug_info["display_name"]
                    virtual_server["port"] = virtual_server_debug_info["port"]
                    virtual_server_statistics = self.get_load_balancer_virtual_server_statistics(lb["id"], virtual_server["virtual_server_id"])
                    virtual_server["statistics"] = virtual_server_statistics

                for pool in lb_status["lb_status"]["pools"]:
                    lb_pool_stats = self.get_load_balancer_pool_statistics(lb["id"], pool["pool_id"])
                    if "statistics" and "members" in lb_pool_stats:
                        if pool["status"] == "UP":
                            pool_num_up += 1
                        lb_pool = self.get_load_balancer_specific_pool(pool["pool_id"])
                        pool["display_name"] = lb_pool["display_name"]
                        pool["statistics"] = lb_pool_stats["statistics"]
                        pool["members"] = lb_pool_stats["members"]
                        for member in pool["members"]:
                            for pool_member in lb_pool["members"]:
                                if member["ip_address"] == pool_member["ip_address"]:
                                    member["display_name"] = pool_member["display_name"]
                                    member["backup_member"] = pool_member["backup_member"]
                                    member["admin_state"] = pool_member["admin_state"]
                                    member["weight"] = pool_member["weight"]

                for index, pool in enumerate(lb_status["lb_status"]["pools"]):
                    if not "statistics" in pool:
                        del lb_status["lb_status"]["pools"][index]

                lb_status["lb_status"]["vs_num"] = len(lb_status["lb_status"]["virtual_servers"])
                lb_status["lb_status"]["vs_num_up"] = vs_num_up
                lb_status["lb_status"]["pool_num"] = len(lb_status["lb_status"]["pools"])
                lb_status["lb_status"]["pool_num_up"] = pool_num_up
                lb.update(lb_status)
                load_balancers_list.append(lb)
            else:
                continue
        return load_balancers_list

    def get_load_balancers_virtual_servers_debug_info(self, lb_service_id, virtual_server_id):
        """
        Get debug info for specific virtual server on the given load balanser service.
        :param str lb_service_id: The load balancer service id.
        :param str virtual_server_id: The virtual server id.
        :return: Dicctionary with debug info of specific virtual server on the given load balancer service.
        :rtype: dict
        """
        virtual_servers_debug_info = \
        self.session.get(_PATH_LOAD_BALANCER_VIRTUAL_SERVERS_DEBUG_INFO % lb_service_id, False)["virtual_servers"]
        for virtual_server_debug_info in virtual_servers_debug_info:
            if virtual_server_debug_info["id"] == virtual_server_id:
                return virtual_server_debug_info

        if not "virtual_server_debug_info" in locals():
            raise APIError("The virtual server id supplied not match whit any virtual server id on load balancer \"" + lb_service_id + "\"", None, "Bad ID")

    def get_manager_node_uuid(self, display_name):
        """
        Returns the uuid of specific node manager
        :param str display_name: Node manager display name.
        :return: UUID of node manager.
        :rtype: str
        """
        for node in self.get_manager_cluster_info():
            if node["display_name"] == display_name:
                node_uuid = node["uuid"]
                return node_uuid
        if not "node_uuid" in locals():
            raise APIError("The node name supplied not match with any host in NSX", None, "Bad Name")

    def get_manager_cluster_info(self):
        """
        Returns all node managers info of cluster.
        :return: List of dictionaries with all node managers and their information.
        :rtype: list
        """
        manager_nodes = []
        for node in self.session.get(_PATH_MANAGER_CLUSTER_INFO, False)["nodes"]:
            manager_nodes.append(
                {
                    "uuid": node["node_uuid"],
                    "display_name": node["fqdn"],
                    "status": node["status"]
                }
            )
        return manager_nodes

    def get_node_type(self, display_name):
        """
        Returns the uuid of specific node manager
        :param str display_name: Node manager display name.
        :return: UUID of node manager.
        :rtype: str
        """
        for node in self.get_manager_cluster_info():
            if node["display_name"] == display_name:
                node_type = "MNG-CTRL"
                return node_type

        for node in self.get_transport_nodes():
            if node["display_name"] == display_name:
                node_type = "EDGE"
                return node_type

        if not "node_type" in locals():
            raise APIError("The node name supplied not match with any host in NSX", None, "Bad Name")

    def get_transport_node_status(self, display_name):
        """
        Returns the information status of specific transport node.
        :param str display_name: Transport node display name.
        :return: UUID of node manager.
        :rtype: str
        """
        transport_node_status = self.session.get(_PATH_TRANSPORT_NODE_STATUS %self.get_transport_node_uuid(display_name), False)
        return transport_node_status

    def get_manager_cluster_status(self):
        """
        Returns the information status of cluster management.
        :return: Status of cluster management.
        :rtype: dict
        """
        cluster_status = self.session.get(_PATH_MANAGER_CLUSTER_STATUS, False)
        return cluster_status

    def get_manager_node_status(self, display_name):
        """
        Returns the information status of specific manager node.
        :param str display_name: The manager node display name.
        :return: Status of manager node.
        :rtype: dict
        """
        manager_node_uuid = self.get_manager_node_uuid(display_name)
        manager_status = self.session.get(_PATH_MANAGER_NODE_STATUS %manager_node_uuid, False)
        return manager_status

    def get_manager_node_filesystems(self, display_name):
        """
        Returns each filesystem use percentage of specific manager node.
        :param str display_name: The manager node display name.
        :return: All filesystems use percentage of specific manager node.
        :rtype: dict
        """
        filesystems = self.get_manager_node_status(display_name)["system_status"]["file_systems"]
        for filesystem in filesystems:
            filesystem["use_percentage"] = (filesystem["used"] * 100) / filesystem["total"]

        return filesystems

    def get_manager_node_mem_use(self, display_name):
        """
        Returns memeory use percentage of specific manager node.
        :param str display_name: The manager node display name.
        :return: Memory use percentage of specific manager node.
        :rtype: dict
        """
        system_status = self.get_manager_node_status(display_name)["system_status"]
        mem_use_percentage = {"mem_use_percentage": (system_status["mem_used"] * 100) / system_status["mem_total"]}
        return mem_use_percentage

    def get_manager_node_ip_address(self, display_name):
        """
        Returns the ip address and port of specific manager/controller node.
        :param str display_name: The manager node display name.
        :return: IP address and port of manager node.
        :rtype: dict
        """
        manager_id = self.get_manager_node_uuid(display_name)
        manager_info = self.session.get(_PATH_MANAGER_NODE_INFO %manager_id, False)
        manager_info_addr = {"ip_address": manager_info["manager_role"]["api_listen_addr"]["ip_address"], "port": manager_info["manager_role"]["api_listen_addr"]["port"]}
        return manager_info_addr

    def get_manager_node_interfaces(self, display_name):
        """
        Returns the information of all interfaces on specific manager node.
        :param str display_name: The manager node display name.
        :return: All interfaces for specific manager node.
        :rtype: dict
        """
        manager_node_uuid = self.get_manager_node_uuid(display_name)
        interfaces = self.session.get(_PATH_MANAGER_NODE_INTERFACES %manager_node_uuid, False)["results"]
        for interface in interfaces:
            interface["statistics"] = self.session.get(_PATH_MANAGER_NODE_INTERFACES_STATS %(manager_node_uuid, interface["interface_id"]), False)
            del interface["statistics"]["interface_id"]
        return interfaces

    def get_manager_services(self, display_name):
        """
        Returns the information of all interfaces on specific manager node.
        :param str display_name: The manager node display name.
        :return: All interfaces for specific manager node.
        :rtype: dict
        """
        manager_node_uuid = self.get_manager_node_uuid(display_name)
        services = self.session.get(_PATH_MANAGER_SERVICES %(manager_node_uuid), False)["results"]
        for service in services:
            service["status"] = self.session.get(_PATH_MANAGER_SERVICE_STATUS %(manager_node_uuid, service["service_name"]), False)["runtime_state"]
        return services