# btrdb_admin.core
# API interactions for working with BTrDB core state
#
# Author:   PingThings
# Created:  Mon Oct 07 13:46:16 2019 -0400
#
# For license information, see LICENSE.txt
# ID: core.py [] benjamin@pingthings.io $

"""
API interactions for working with BTrDB core state
"""

##########################################################################
## Imports
##########################################################################

from btrdb_admin.grpcinterface import admin_pb2
from btrdb_admin.exceptions import AdminAPIError


##########################################################################
## API Object
##########################################################################

class CoreAPI(object):
    """
    API interactions for working with the BTrDB core state
    """

    def info(self):
        """
        Returns the current version of the BTrDB allocation.

        gRPC call:
            rpc Info(InfoParams) returns (InfoResponse)

        Returns
        -------
        dict : version
            A version dictionary containing current info
        """
        params = admin_pb2.InfoParams()
        response = self.client.Info(params)
        AdminAPIError.check_error(response)

        return {
            "build": response.build,
            "major_version": response.majorVersion,
            "minor_version": response.minorVersion,
        }


    def get_cluster_status(self):
        """
        Returns the current status of the allocation.

        gRPC call:
            rpc GetClusterStatus(GetClusterStatusParams) returns (GetClusterStatusResponse)

        Returns
        -------
        dict : status
            Returns a dictionary with the cluster status
        """
        params = admin_pb2.GetClusterStatusParams()
        response = self.client.GetClusterStatus(params)
        AdminAPIError.check_error(response)

        return {
            "state": response.stateString,
            "cluster": {
                "revision": response.state.revision,
                "members": response.state.members,
                "mashes": response.state.mashes,
                "leader": response.state.leader,
                "leader_revision": response.state.leaderRevision,
            }
        }

    def node_disable(self, node):
        """
        Disable a node in the cluster.

        gRPC call:
            rpc NodeDisable(NodeDisableParams) returns (NodeDisableResponse)

        Parameters
        ----------
        node : str
            The name of the node to disable
        """
        params = admin_pb2.NodeDisableParams(node=node)
        response = self.client.NodeDisable(params)
        AdminAPIError.check_error(response)

    def node_out(self, node):
        """
        Take a node out of the cluster.

        gRPC call:
            rpc NodeOut(NodeOutParams) returns (NodeOutResponse)

        Parameters
        ----------
        node : str
            The name of the node to out
        """
        params = admin_pb2.NodeOutParams(node=node)
        response = self.client.NodeOut(params)
        AdminAPIError.check_error(response)

    def node_enable(self, node):
        """
        Enable a node in the cluster.

        gRPC call:
            rpc NodeEnable(NodeEnableParams) returns (NodeEnableResponse)

        Parameters
        ----------
        node : str
            The name of the node to enable
        """
        params = admin_pb2.NodeEnableParams(node=node)
        response = self.client.NodeEnable(params)
        AdminAPIError.check_error(response)

    def node_in(self, node):
        """
        Place a node into the cluster.

        gRPC call:
            rpc NodeIn(NodeInParams) returns (NodeInResponse)

        Parameters
        ----------
        node : str
            The name of the node to in
        """
        params = admin_pb2.NodeInParams(node=node)
        response = self.client.NodeIn(params)
        AdminAPIError.check_error(response)

    def node_remove(self, node):
        """
        Remove a node from the cluster.

        gRPC call:
            rpc NodeRemove(NodeRemoveParams) returns (NodeRemoveResponse)

        Parameters
        ----------
        node : str
            The name of the node to remove
        """
        params = admin_pb2.NodeRemoveParams(node=node)
        response = self.client.NodeRemove(params)
        AdminAPIError.check_error(response)

    def autoprune(self):
        """
        Initiate an autoprune on the cluster.

        gRPC call:
            rpc Autoprune(AutopruneParams) returns (AutopruneResponse)
        """
        params = admin_pb2.AutopruneParams()
        response = self.client.Autoprune(params)
        AdminAPIError.check_error(response)

    def node_weight(self, node, weight):
        """
        Assign the specified node the specified weight.

        gRPC call:
            rpc NodeWeight(NodeWeightParams) returns (NodeWeightResponse)

        Parameters
        ----------
        node : str
            The name of the node to set the weight for

        weight : int
            The weight to assign the node
        """
        params = admin_pb2.NodeWeightParams(node=node, weight=weight)
        response = self.client.NodeWeight(params)
        AdminAPIError.check_error(response)

    def node_read_preference(self, node, rpref):
        """
        Set the node read preference.

        gRPC call:
            rpc NodeReadPreference(NodeReadPreferenceParams) returns (NodeReadPreferenceResponse)

        Parameters
        ----------
        node : str
            The name of the node to set the read preference of

        rpref : float
            The read preference to assign the node
        """
        params = admin_pb2.NodeReadPreferenceParams(node=node, rpref=rpref)
        response = self.client.NodeReadPreference(params)
        AdminAPIError.check_error(response)

    def list_throttles(self):
        """
        List the throttles set on the database.

        gRPC call:
            rpc ListThrottles(ListThrottlesParams) returns (ListThrottlesResponse)

        Returns
        -------
        throttles : list(dict)
            A description of all throttles in the database
        """
        params = admin_pb2.ListThrottlesParams()
        response = self.client.ListThrottles(params)
        AdminAPIError.check_error(response)

        return [
            {"name": throttle.name, "pool": throttle.pool, "queue": throttle.queue}
            for throttle in response.throttles
        ]

    def set_throttle(self, name, pool=100, queue=10000):
        """
        Create throttle or update throttle parameters.

        gRPC call:
            rpc SetThrottle(SetThrottleParams) returns (SetThrottleResponse)

        Parameters
        ----------
        name : str
            The name of the throttle

        pool : int, default: 100
            Limit the size of the pool

        queue : int, default: 10000
            Limit the size of the queue
        """
        throttle = admin_pb2.Throttle(name=name, pool=pool, queue=queue)
        params = admin_pb2.SetThrottleParams(throttle=throttle)
        response = self.client.SetThrottle(params)
        AdminAPIError.check_error(response)
