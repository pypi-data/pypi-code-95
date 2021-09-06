# coding: utf-8

"""
    AssistedInstall

    Assisted installation  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class HostUpdateParams(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'host_role': 'str',
        'host_name': 'str',
        'disks_selected_config': 'list[DiskConfigParams]',
        'machine_config_pool_name': 'str'
    }

    attribute_map = {
        'host_role': 'host_role',
        'host_name': 'host_name',
        'disks_selected_config': 'disks_selected_config',
        'machine_config_pool_name': 'machine_config_pool_name'
    }

    def __init__(self, host_role=None, host_name=None, disks_selected_config=None, machine_config_pool_name=None):  # noqa: E501
        """HostUpdateParams - a model defined in Swagger"""  # noqa: E501

        self._host_role = None
        self._host_name = None
        self._disks_selected_config = None
        self._machine_config_pool_name = None
        self.discriminator = None

        if host_role is not None:
            self.host_role = host_role
        if host_name is not None:
            self.host_name = host_name
        if disks_selected_config is not None:
            self.disks_selected_config = disks_selected_config
        if machine_config_pool_name is not None:
            self.machine_config_pool_name = machine_config_pool_name

    @property
    def host_role(self):
        """Gets the host_role of this HostUpdateParams.  # noqa: E501


        :return: The host_role of this HostUpdateParams.  # noqa: E501
        :rtype: str
        """
        return self._host_role

    @host_role.setter
    def host_role(self, host_role):
        """Sets the host_role of this HostUpdateParams.


        :param host_role: The host_role of this HostUpdateParams.  # noqa: E501
        :type: str
        """
        allowed_values = ["auto-assign", "master", "worker"]  # noqa: E501
        if host_role not in allowed_values:
            raise ValueError(
                "Invalid value for `host_role` ({0}), must be one of {1}"  # noqa: E501
                .format(host_role, allowed_values)
            )

        self._host_role = host_role

    @property
    def host_name(self):
        """Gets the host_name of this HostUpdateParams.  # noqa: E501


        :return: The host_name of this HostUpdateParams.  # noqa: E501
        :rtype: str
        """
        return self._host_name

    @host_name.setter
    def host_name(self, host_name):
        """Sets the host_name of this HostUpdateParams.


        :param host_name: The host_name of this HostUpdateParams.  # noqa: E501
        :type: str
        """

        self._host_name = host_name

    @property
    def disks_selected_config(self):
        """Gets the disks_selected_config of this HostUpdateParams.  # noqa: E501


        :return: The disks_selected_config of this HostUpdateParams.  # noqa: E501
        :rtype: list[DiskConfigParams]
        """
        return self._disks_selected_config

    @disks_selected_config.setter
    def disks_selected_config(self, disks_selected_config):
        """Sets the disks_selected_config of this HostUpdateParams.


        :param disks_selected_config: The disks_selected_config of this HostUpdateParams.  # noqa: E501
        :type: list[DiskConfigParams]
        """

        self._disks_selected_config = disks_selected_config

    @property
    def machine_config_pool_name(self):
        """Gets the machine_config_pool_name of this HostUpdateParams.  # noqa: E501


        :return: The machine_config_pool_name of this HostUpdateParams.  # noqa: E501
        :rtype: str
        """
        return self._machine_config_pool_name

    @machine_config_pool_name.setter
    def machine_config_pool_name(self, machine_config_pool_name):
        """Sets the machine_config_pool_name of this HostUpdateParams.


        :param machine_config_pool_name: The machine_config_pool_name of this HostUpdateParams.  # noqa: E501
        :type: str
        """

        self._machine_config_pool_name = machine_config_pool_name

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(HostUpdateParams, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, HostUpdateParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
