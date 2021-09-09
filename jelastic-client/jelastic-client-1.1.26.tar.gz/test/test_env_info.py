import pytest

from jelastic_client.env_info import EnvInfo
from jelastic_client.env_status import EnvStatus
from jelastic_client.node import Nodes, Node


@pytest.mark.parametrize(
    "input_dict,expected_status",
    [
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 1
                }
            }, EnvStatus.Running
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 2
                }
            }, EnvStatus.Down
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 5
                }
            }, EnvStatus.Unknown
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 8
                }
            }, EnvStatus.NotExists
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 13
                }
            }, EnvStatus.Stopping
        ),
    ]
)
def test_env_info_status(input_dict: str, expected_status: EnvStatus):
    # Arrange
    env_info = EnvInfo(input_dict)

    # Act
    actual_status = env_info.status()

    # Assert
    assert expected_status == actual_status


def test_env_info_env_name():
    # Arrange
    expected_env_name = "the-env-name"
    input_dict = {
        "nodes": [],
        "env": {
            "envName": expected_env_name
        }
    }
    env_info = EnvInfo(input_dict)

    # Act
    actual_env_name = env_info.env_name()

    # Assert
    assert expected_env_name == actual_env_name


@pytest.mark.parametrize(
    "input_dict,expected_running",
    [
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 1
                }
            }, True
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 2
                }
            }, False
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 10
                }
            }, False
        ),
    ]
)
def test_env_info_is_running(input_dict: dict, expected_running: bool):
    # Arrange
    env_info = EnvInfo(input_dict)

    # Act
    actual_running = env_info.is_running()

    # Assert
    assert expected_running == actual_running


@pytest.mark.parametrize(
    "input_dict,expected_exists",
    [
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 1
                }
            }, True
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 2
                }
            }, True
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 10
                }
            }, True
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 8
                }
            }, False
        ),
        pytest.param(
            {
                "nodes": [],
                "env": {
                    "status": 5
                }
            }, False
        ),
    ]
)
def test_env_info_exists(input_dict: dict, expected_exists: bool):
    # Arrange
    env_info = EnvInfo(input_dict)

    # Act
    actual_exists = env_info.exists()

    # Assert
    assert expected_exists == actual_exists


@pytest.mark.parametrize(
    "input_dict,expected_nodes",
    [
        pytest.param(
            {
                "nodes": [],
            }, [], id="empty nodes"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    }
                ],
            }, [Node(int_ip="10.102.15.248", node_type="docker", node_group="cp", url="http://irrelevant.com")], id="single node"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "sqldb",
                        "nodeType": "postgresql",
                        "intIP": "10.102.15.249",
                        "url": "http://irrelevant.com"
                    }
                ],
            }, [Node(int_ip="10.102.15.248", node_type="docker", node_group="cp", url="http://irrelevant.com"),
                Node(int_ip="10.102.15.249", node_type="postgresql", node_group="sqldb", url="http://irrelevant.com")], id="multiple nodes"
        ),
    ]
)
def test_env_info_nodes(input_dict: dict, expected_nodes: Nodes):
    # Arrange
    env_info = EnvInfo(input_dict)

    # Act
    actual_nodes = env_info.nodes()

    # Assert
    assert not set(actual_nodes) ^ set(expected_nodes)


@pytest.mark.parametrize(
    "input_dict,node_group,node_type,expected_ips",
    [
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "cp", None, ["10.102.15.248"], id="filter list of 1 node on existing node group"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, None, "docker", ["10.102.15.248"], id="filter list of 1 node on existing node type"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, None, "vps", [], id="filter list of 1 node on non-existent node type"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "bl", None, [], id="filter list of 1 node on non-existent node group"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "bl",
                        "nodeType": "docker",
                        "intIP": "10.102.15.258",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.249",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.250",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "cp", None, ["10.102.15.248", "10.102.15.249", "10.102.15.250"],
            id="filter list of multiple nodes on existing node group"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.249",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "ubuntu-vps",
                        "intIP": "10.102.15.259",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.250",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, None, "docker", ["10.102.15.248", "10.102.15.249", "10.102.15.250"],
            id="filter list of multiple nodes on existing node type"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.249",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "ubuntu-vps",
                        "intIP": "10.102.15.259",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "ubuntu-vps",
                        "intIP": "10.102.15.260",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.250",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "cp", "ubuntu-vps", ["10.102.15.259", "10.102.15.260"],
            id="filter list of multiple nodes on existing node type and node group"
        ),
    ],
)
def test_env_info_get_node_ips_returns_filtered_ips(input_dict: dict, node_group: str, node_type: str,
                                                    expected_ips: [str]):
    # Arrange
    env_info = EnvInfo(input_dict)

    # Act
    actual_ips = env_info.get_node_ips(
        node_group=node_group, node_type=node_type)

    # Assert
    assert not set(actual_ips) ^ set(expected_ips)


@pytest.mark.parametrize(
    "input_dict,display_name,expected_ip",
    [
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "displayName": "target-node",
                        "url": "http://irrelevant.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "target-node", "10.102.15.248", id="list of 1 node with desired display name"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.249",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "displayName": "target-node",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.250",
                        "displayName": "uninteresting-node",
                        "url": "http://irrelevant.com"
                    },
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "target-node", "10.102.15.248", id="list of multiple nodes containing the desired display name"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.249",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "displayName": "other-name",
                        "url": "http://irrelevant.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.250",
                        "displayName": "uninteresting-node",
                        "url": "http://irrelevant.com"
                    },
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "target-node", None, id="list of multiple nodes not containing the desired display name"
        ),
    ]
)
def test_env_info_get_node_ip_from_name_returns_corresponding_ip(input_dict: dict, display_name: str, expected_ip: str):
    # Arrange
    env_info = EnvInfo(input_dict)

    # Act
    actual_ip = env_info.get_node_ip_from_name(display_name)

    # Assert
    assert actual_ip == expected_ip


@pytest.mark.parametrize(
    "input_dict,display_name,expected_hostname",
    [
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "displayName": "target-node",
                        "url": "http://node89876-local-sha-master-0954606.hidora.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "target-node", "node89876-local-sha-master-0954606.hidora.com",
            id="list of 1 node with desired display name"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "displayName": "irrelevant-node",
                        "url": "http://node89876-local-sha-master-0954606.hidora.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "target-node", None,
            id="list of 1 node without the desired display name"
        ),
        pytest.param(
            {
                "nodes": [
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.248",
                        "displayName": "irrelevant-node",
                        "url": "http://node89876-local-sha-master-0954606.hidora.com"
                    },
                    {
                        "nodeGroup": "cp",
                        "nodeType": "docker",
                        "intIP": "10.102.15.268",
                        "displayName": "target-node",
                        "url": "http://node89886-local-sha-master-0954656.hidora.com"
                    }
                ],
                "env": {
                    "envName": "local-sha-master-0954606",
                    "status": 1
                }
            }, "target-node", "node89886-local-sha-master-0954656.hidora.com",
            id="list of multiple nodes with the desired display name"
        ),
    ]
)
def test_env_info_get_node_hostname_from_name_returns_hostname(input_dict: dict, display_name: str,
                                                               expected_hostname: str):
    # Arrange
    env_info = EnvInfo(input_dict)

    # Act
    actual_hostname = env_info.get_node_hostname_from_name(display_name)

    # Assert
    assert actual_hostname == expected_hostname
