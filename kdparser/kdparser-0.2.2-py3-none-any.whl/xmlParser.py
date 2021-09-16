"""
This module contains the xmlParserExtensions functions.
"""
import xml.etree.ElementTree as et


def parse_xml_by_tags(xml_object: et.Element, list_of_tags: list, is_recursive: bool = False):
    """
    Parses an xml object into a new one with the given keys.
    :param xml_object: The xml object to be parsed.
    :param list_of_tags: list of wanted keys.
    :param is_recursive: If true the function will search the keys in all sub-tags.
    :return: The new xml object.
    """

    parsed_xml = et.Element(xml_object.tag)

    for child in xml_object:
        if child.tag in list_of_tags:
            parsed_xml.append(child)
        elif is_recursive:
            inner_elements = parse_xml_by_tags(child, list_of_tags, True)
            if len(list(inner_elements)) > 0:
                parsed_xml.append(inner_elements)

    return parsed_xml


def parse_xml_by_attribute(xml_object: et.Element, list_of_attributes: list, is_recursive: bool = False):
    """
    Parses an xml object into a new one with the given attributes.
    :param xml_object: The xml object to be parsed.
    :param list_of_attributes: list of wanted attributes.
    :param is_recursive: If true the function will search the attributes in all sub-tags.
    :return: The new xml object.
    """

    parsed_xml = et.Element(xml_object.tag)

    for child in xml_object:
        child_attributes = child.attrib
        if child_attributes is not None:
            for attribute in child_attributes:
                if attribute in list_of_attributes:
                    parsed_xml.append(child)
                    continue
        if is_recursive:
            inner_elements = parse_xml_by_attribute(child, list_of_attributes, True)
            if len(list(inner_elements)) > 0:
                parsed_xml.append(inner_elements)

    return parsed_xml


def parse_xml_by_values(xml_object: et.Element, list_of_values: list, is_recursive: bool = False):
    """
    Parses an xml object into a new one with the given values.
    :param xml_object: The xml object to be parsed.
    :param list_of_values: list of wanted values.
    :param is_recursive: If true the function will search the values in all sub-tags.
    :return: The new xml object.
    """

    parsed_xml = et.Element(xml_object.tag)

    for child in xml_object:
        if child.text in list_of_values:
            parsed_xml.append(child)
        elif is_recursive:
            inner_elements = parse_xml_by_values(child, list_of_values, True)
            if len(list(inner_elements)) > 0:
                parsed_xml.append(inner_elements)

    return parsed_xml


def parse_xml_by_attributes_values(xml_object: et.Element, list_of_attributes_values: list, is_recursive: bool = False):
    """
      Parses an xml object into a new one with the given attributes values
    :param xml_object: The xml object to be parsed.
    :param list_of_attributes_values: List of wanted attributes values.
    :param is_recursive: If true the function will search the attributes values in all sub-tags.
    :return: The new xml object.
    """

    parsed_xml = et.Element(xml_object.tag)

    for child in xml_object:
        child_attributes = child.attrib
        if child_attributes is not None:
            for attribute in child_attributes:
                if child_attributes[attribute] in list_of_attributes_values:
                    parsed_xml.append(child)
                    continue
        if is_recursive:
            inner_elements = parse_xml_by_attributes_values(child, list_of_attributes_values, True)
            if len(list(inner_elements)) > 0:
                parsed_xml.append(inner_elements)

    return parsed_xml
