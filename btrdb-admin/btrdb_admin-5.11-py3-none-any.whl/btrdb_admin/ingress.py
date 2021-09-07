# btrdb_admin.ingress
# API interactions for working ingresses
#
# Author:   PingThings
# Created:  Tue May 3 14:22:15 2021 -0500
#
# For license information, see LICENSE.txt
# ID: ingress.py [] allen@pingthings.io $

"""
API interactions for working with ingresses
"""

##########################################################################
## Imports
##########################################################################

from collections import namedtuple

from btrdb_admin.grpcinterface import admin_pb2
from btrdb_admin.exceptions import AdminAPIError, NotFoundError


##########################################################################
## Helpers
##########################################################################

# message IngressClass {
#   string class = 1;
#   bool enabled = 2;
#   map<string, string> requiredParameters = 3;
#   map<string, string> optionalParameters = 4;
# }
_ingress_class_fields = ['class_name', 'enabled', 'required_parameters', 'optional_parameters']
IngressClass = namedtuple('IngressClass', _ingress_class_fields)

def ingressclass_from_grpc(obj):
    return IngressClass(
        getattr(obj, 'class'), obj.enabled, dict(obj.requiredParameters), dict(obj.optionalParameters)
    )
IngressClass.from_grpc = ingressclass_from_grpc

# message Ingress {
#   string name = 1;
#   string class = 2;
#   bool enabled = 3;
#   string collectionPrefix = 4;
#   string comment = 5;
#   map<string, string> parameters = 6;
# }
_ingress_fields = ['name', 'class_name', 'enabled', 'collection', 'comment', 'parameters']
Ingress = namedtuple('Ingress', _ingress_fields)

def ingress_from_grpc(obj):
    return Ingress(
        obj.name, getattr(obj, 'class'), obj.enabled, obj.collectionPrefix,
        obj.comment, dict(obj.parameters)
    )
Ingress.from_grpc = ingress_from_grpc


##########################################################################
## Classes
##########################################################################

# The following calls have not been implemented but could be included in
# a future ticket if needed.
#   rpc AddOrUpdateIngressClass(AddOrUpdateIngressClassParams) returns (AddOrUpdateIngressClassResponse);
#   rpc UpdateIngressClassEnabled(UpdateIngressClassEnabledParams) returns (UpdateIngressClassEnabledResponse);
#   rpc RemoveIngressClass(RemoveIngressClassParams) returns (RemoveIngressClassResponse);
#   rpc UpdateIngress(UpdateIngressParams) returns (UpdateIngressResponse);

class IngressAPI(object):
    """
    API interactions for working with ingresses
    """

    def get_ingress_classes(self):
        """
        Returns all registered ingress classes

        gRPC call:
            rpc GetIngressClasses(GetIngressClassesParams) returns (GetIngressClassesResponse)

        Returns
        -------
        list(IngressClass)
            a list of IngressClass instances
        """
        params = admin_pb2.GetIngressClassesParams()
        response = self.client.GetIngressClasses(params)
        AdminAPIError.check_error(response)
        return [IngressClass.from_grpc(i) for i in response.classes]

    def get_ingress_class(self, ingress_class_name):
        """
        Returns the name of the identity provider currently set

        gRPC call:
            GetIngressClass(GetIngressClassParams) returns (GetIngressClassResponse);

        Parameters
        ----------
        ingress_class_name : str
            the name of the ingress class to retrieve

        Returns
        -------
        IngressClass
            an instance of class IngressClass

        """
        # `class` is a reserved word in Python so we work around the issue
        params = admin_pb2.GetIngressClassParams(**{'class': ingress_class_name})
        response = self.client.GetIngressClass(params)
        AdminAPIError.check_error(response)
        return IngressClass.from_grpc(getattr(response, 'class'))

    def get_all_ingresses(self):
        """
        Returns all registered ingresses

        gRPC call:
            rpc GetAllIngresses(GetAllIngressesParams) returns (GetAllIngressesResponse);

        Returns
        -------
        list(Ingress)
            a list of Ingress instances
        """
        params = admin_pb2.GetAllIngressesParams()
        response = self.client.GetAllIngresses(params)
        AdminAPIError.check_error(response)
        return [Ingress.from_grpc(i) for i in response.ingresses]

    def get_ingresses(self, ingress_class_name):
        """
        Returns all registered ingresses for a given class

        gRPC call:
            rpc GetIngresses(GetIngressesParams) returns (GetIngressesResponse)

        Returns
        -------
        list(Ingress)
            a list of Ingress instances
        """
        # `class` is a reserved word in Python so we work around the issue
        params = admin_pb2.GetIngressesParams(**{'class': ingress_class_name})
        response = self.client.GetIngresses(params)
        AdminAPIError.check_error(response)
        return [Ingress.from_grpc(i) for i in response.ingresses]

    def get_ingress(self, ingress_name):
        """
        Returns requested ingress by name

        gRPC call:
            rpc GetIngress(GetIngressParams) returns (GetIngressResponse)

        Returns
        -------
        IngressClass
            an instance of Ingress
        """
        params = admin_pb2.GetIngressParams(name=ingress_name)
        response = self.client.GetIngress(params)
        AdminAPIError.check_error(response)
        return Ingress.from_grpc(response.ingress)

    def add_ingress(self, ingress_name, ingress_class_name, enabled, collection, comment, parameters):
        """
        Adds a new ingress

        gRPC call:
            rpc AddIngress(AddIngressParams) returns (AddIngressResponse)

        Parameters
        ----------
        ingress_name : str
            the name of the ingress to remove

        ingress_class_name : str
            the type/class of ingress to create

        enabled : bool
            true/false whether new ingress should be active

        collection : str
            collection path to put new streams into

        comment : str
            extra information about the ingress

        parameters : dict
            configuration specific to the ingress class

        """
        # `class` is a reserved word in Python so we work around the issue
        ingress = admin_pb2.Ingress(**{
            'name': ingress_name,
            'class': ingress_class_name,
            'enabled': enabled,
            'collectionPrefix': collection,
            'comment': comment,
            'parameters': parameters
        })
        params = admin_pb2.AddIngressParams(ingress=ingress)
        response = self.client.AddIngress(params)
        AdminAPIError.check_error(response)

    def remove_ingress(self, ingress_name):
        """
        Deletes an existing ingress

        gRPC call:
            rpc RemoveIngress(RemoveIngressParams) returns (RemoveIngressResponse)

        Parameters
        ----------
        ingress_name : str
            the name of the ingress to remove
        """
        params = admin_pb2.RemoveIngressParams(name=ingress_name)
        response = self.client.RemoveIngress(params)
        AdminAPIError.check_error(response)

    def update_ingress_enabled(self, ingress_name, enabled):
        """
        Modifies enabled state of named ingress

        gRPC call:
            rpc UpdateIngressEnabled(UpdateIngressEnabledParams) returns (UpdateIngressEnabledResponse)

        Parameters
        ----------
        ingress_name : str
            the name of the ingress to enable/disable

        enabled : bool
            new state of the specified ingress
        """
        params = admin_pb2.UpdateIngressEnabledParams(name=ingress_name, enabled=enabled)
        response = self.client.UpdateIngressEnabled(params)
        AdminAPIError.check_error(response)
