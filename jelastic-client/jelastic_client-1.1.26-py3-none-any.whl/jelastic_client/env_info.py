from jelastic_client.env_status import EnvStatus
from jelastic_client.node import Node, Nodes


def get_nodes_from_env_info(env_info: dict) -> Nodes:
    if "nodes" not in env_info or env_info["nodes"] is None:
        return []

    nodes = []
    raw_nodes = env_info["nodes"]
    for raw_node in raw_nodes:
        node = Node(
            int_ip=raw_node["intIP"],
            node_type=raw_node["nodeType"],
            node_group=raw_node["nodeGroup"],
            url=raw_node["url"],
            display_name=raw_node["displayName"] if "displayName" in raw_node else None)
        nodes.append(node)
    return nodes


class EnvInfo:

    def __init__(self, env_info: dict):
        self._info = env_info
        self._nodes = get_nodes_from_env_info(env_info)

    def status(self) -> EnvStatus:
        return EnvStatus(self._info["env"]["status"])

    def env_name(self) -> str:
        return self._info["env"]["envName"]

    def nodes(self) -> Nodes:
        return self._nodes

    def is_running(self) -> bool:
        return self.status() is EnvStatus.Running

    def exists(self) -> bool:
        return self.status() is not EnvStatus.NotExists and self.status() is not EnvStatus.Unknown

    def get_nodes(self, node_group: str = None, node_type: str = None) -> Nodes:
        env_nodes = self._nodes

        nodes_with_node_group = []
        if node_group is not None:
            nodes_with_node_group = [env_node for env_node in env_nodes if
                                     env_node.node_group == node_group]
            if node_type is None:
                return nodes_with_node_group

        nodes_with_node_type = []
        if node_type is not None:
            nodes_with_node_type = [
                env_node for env_node in env_nodes if env_node.node_type == node_type]
            if node_group is None:
                return nodes_with_node_type

        return list(set(nodes_with_node_type)
                    .intersection(nodes_with_node_group))

    def get_node_from_name(self, display_name: str) -> Node:
        nodes_with_display_name = [
            env_node for env_node in self._nodes if env_node.display_name == display_name]
        return nodes_with_display_name[0] if len(nodes_with_display_name) == 1 else None

    def get_node_ips(self, node_group: str = None, node_type: str = None) -> [str]:
        nodes = self.get_nodes(node_group, node_type)
        return [node.int_ip for node in nodes]

    def get_node_ip_from_name(self, display_name: str) -> str:
        node = self.get_node_from_name(display_name)
        return node.int_ip if node is not None else None

    def get_node_hostname_from_name(self, display_name: str) -> str:
        node = self.get_node_from_name(display_name)
        if node is None:
            return None
        url = node.url
        hostname = url.split('://')[1]
        return hostname
