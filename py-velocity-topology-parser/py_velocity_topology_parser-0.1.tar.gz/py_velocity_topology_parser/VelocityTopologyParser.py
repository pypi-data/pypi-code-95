"""

    This module will help you parse the topology from .tbml file or the string of tbml format
    :returns object structure
                 - topology_name
                 - resource_list
                 -resource
                    -property_list
                    -port_list
                    -property
                        -value
                    -port
                        -value
                        -property
                            -value
"""


from lxml import etree  # we need it to parse the tbml file


__Version__ = '0.1'
__Author__ = 'Poornima Wari'


"""
    Modification History
    ====================
    0.1 : 9/7/2021 'Poornima Wari'                                                                                                                     /7/2021 'Poornima Wari'
          - Initial Code
"""


import os  # we need it for environ variable


class VelocityTopologyParser:
    """
        topology parser for velocity TBML file:
            you can either get the tbml file from Spirent Velocity environment
            or you can pass the file name
            or you can get the string from topology reservation id and pass it
            kwargs - >
                file_name = 'file_name_with_complete_path'
                string_to_parse = 'string'
    """

    def __init__(self, **kwargs):
        """
            init definition, it will look for environ variable VELOCITY_PARAM_TMBL_FILE, if not passed kwargs
        :param kwargs:
            file_name = 'file_name_with_complete_path'
            OR
            string_to_parse = 'string' # you can get it from VelocityReST API
        """
        # set the name space
        self.ns = {'ns': 'http://www.teslaalliance.org/trs/tbml/1.0'}

        # create parser
        self.parser = etree.XMLParser(remove_blank_text=True)

        # create element tree from environ, if kwargs not passed
        if not len(kwargs) > 0:
            try:
                # check for velocity environ
                file_name = os.environ['VELOCITY_PARAM_TMBL_FILE']

                # create element tree
                self.tree = etree.parse(file_name, self.parser)
            except KeyError:
                # error handling
                raise KeyError('TMBL file name is not passed')

        # check for kwargs and create element for tree
        for key1 in kwargs.keys():
            if 'string_to_parse' in key1:
                # create element tree from string
                self.tree = etree.fromstring(kwargs[key1])
            elif 'file_name' in key1:
                # create element tree from file
                self.tree = etree.parse(kwargs[key1], self.parser)
            else:
                # error handling
                raise KeyError('TBML file is not passed')

        # add topology name to object
        self.topology_name = self.tree.xpath('//ns:header/ns:name', namespaces=self.ns)[0].text

        # add resource list to the object
        self.resource_list = []

    # add resource name
    def add_resource(self, abstract_name):
        """

        :param abstract_name: resource abstract name
        :return: adds resource abstract name
        """
        # add the resource name to the list
        self.resource_list.append(abstract_name)

        # set resource attribute
        setattr(self, abstract_name, VelocityResource(abstract_name))

        # return the velocity resource object
        return getattr(self, abstract_name)

    @property
    def parse_topology(self):
        """
            Parse the topology
        :return: topology object

        """
        try:
            # create resource list
            resource_list = self.tree.xpath('//ns:resource[@type="device"]', namespaces=self.ns)

            # create the topology object notation for every resource
            for resource in resource_list:
                # get the resource abstract name and add it to the object
                resource_name = resource.xpath('ns:property[@name="name"]', namespaces=self.ns)[0].text
                resource_obj = self.add_resource(resource_name)

                # get all property collection (ex :username,password etc) and add them to resource object
                collections = resource.xpath('ns:propertyCollection', namespaces=self.ns)

                # collection from property collections
                for collection in collections:
                    # get the property list
                    property_list = collection.xpath('ns:property', namespaces=self.ns)
                    # check if the property is list
                    if isinstance(property_list, list):
                        # get the individual property and add it to resource object
                        for property1 in property_list:
                            property_name = property1.attrib['name']
                            property_value = property1.text
                            resource_obj.add_property(property_name, property_value)

                # add the remaining property
                property_list = resource.xpath('ns:property', namespaces=self.ns)

                # get the property and add it to resource object
                for property1 in property_list:
                    property_name = property1.attrib['name']
                    property_value = property1.text
                    resource_obj.add_property(property_name, property_value)

                # get the port and add it to port object
                port_list = resource.xpath('ns:resource[@type="port"]', namespaces=self.ns)
                for port in port_list:
                    port_name = port.xpath('ns:property[@name="name"]', namespaces=self.ns)[0].text
                    port_number = port.xpath('ns:propertyCollection[@name="System Identification"]'
                                             '/ns:property[@name="portNumber"]', namespaces=self.ns)[0].text
                    port_obj = resource_obj.add_ports(port_name, port_number)

                    # get the port property and add it to velocity port object
                    port_property_list = port.xpath('ns:property', namespaces=self.ns)
                    for port_property in port_property_list:
                        port_property_name = port_property.attrib['name']
                        port_property_value = port_property.text
                        port_obj.add_property(port_property_name, port_property_value)
        except ValueError:
            raise ValueError('Error getting the value . Check the Object structure ')
        return self


class VelocityResource:
    """
        This will maintain the topology resources
            -Resources
                - resource property list
                - port list
    """

    def __init__(self, abstract_name):
        """

        :param abstract_name: resource abstract name
        """
        self.abstract_name = abstract_name

        # set port name
        self.port_list = []

        # set pro numbers
        self.port_numbers = []

        # set property list
        self.property_list = []

    def add_property(self, property_name, property_value):
        """

        :param property_name: resource property Name
        :param property_value: resource property Value
        :return: adds resource property Name to object
        """
        # update resource property
        self.property_list.append(property_name)

        # set resource property name and value
        setattr(self, property_name, property_value)
        return getattr(self, property_name)

    def add_ports(self, port_name, port_number):
        """

        :param port_name: abstract port name
        :param port_number: abstract port number
        :return: adds abstract port name to the object
        """
        # add port to resource port list
        self.port_list.append(port_name)
        self.port_numbers.append(port_number)

        # set port name add it to Velocity Port object
        setattr(self, port_name, VelocityPort(port_name))
        return getattr(self, port_name)


class VelocityPort:
    """
        This will maintain the port details
            - ports
                -port list
                -port property list
    """

    def __init__(self, port_name):
        self.port_name = port_name
        self.property_list = []

    def add_property(self, port_property_name, port_property_value):
        """

        :param port_property_name: port property name
        :param port_property_value: port property value
        :return: adds port property name to the object
        """
        # add port property to velocity port object
        self.property_list.append(port_property_name)

        # set port property name and port property value
        setattr(self, port_property_name, port_property_value)
        return getattr(self, port_property_name)


def main():
    filename = '/Users/pwari/workspace/velocity_topology_parser/FDK_CFv_FWv_Testing.tbml'
    velocity = VelocityTopologyParser(file_name=filename)
    velocity.parse_topology

    ip_address = velocity.__getattribute__('TG-1').ipAddress
    user_name = velocity.__getattribute__('TG-1').username

    tg_port_numbers = velocity.__getattribute__('TG-1').port_numbers
    fw_port_numbers = velocity.__getattribute__('FW-1').port_numbers

    return tg_port_numbers, fw_port_numbers, ip_address, user_name


if __name__ == "__main__":
    main()
