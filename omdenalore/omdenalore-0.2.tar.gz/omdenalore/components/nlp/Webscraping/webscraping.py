import requests
from bs4 import BeautifulSoup


def getWebPage(topic_url):
    """
    Get the content of the page you want to scrape
    :param arg1: The URL of the page you want to scrape
    :type arg1: str
    :return : the status code of the response, content from this url or an assertion error
    """

    response = requests.get(topic_url)

    try:
        assert response.status_code in [200, 201, 202, 203, 204, 205, 207, 208, 226]
        return response.status_code, response.text
    except AssertionError:
        print(
            f"Problem with your url or your request. Try to check it.status_code: {response.status_code}"
        )
        return None, None


def putContentFile(filename, contents, encoding="utf-8"):
    """
    Get a new html file where the content of a web page is written
    :param arg1: name of the html file in which you want to put the content
    :param arg2: the contents we will write in the file
    :param arg3: the encoding of the file
    :type arg1: str
    :type arg2: object get from response object
    :type arg3: str
    """
    with open(filename, mode="w", encoding=encoding) as file:
        file.write(contents)


def openFile(filename):
    """
    Open the content scraped from a website
    :param arg1: the name of an existing file
    :return: the content of the file
    """
    with open(filename, "r") as f:
        html_source = f.read()
        return html_source


def get_tag(doc, tag_name):
    """
    Get a tag and it's the content.
    :param arg1: the reference for the BeautifulSoup object created
    :param arg2: the name of the tag
    :type arg1: BeautifulSoup object
    :type arg2: str
    :return : the tag and it's content
    """
    return doc.find(tag_name)


def get_groups_of_tag(doc, tag_name):
    """
    Get groups of same tag in the page.
    :param arg1: the reference for the BeautifulSoup object created
    :param arg2: the name of the tag
    :type arg1: BeautifulSoup object
    :type arg2: str
    :return : a list of same tag and their content
    """
    return doc.findAll(tag_name)


def find_tag_with_attributes(doc, tag_name, attr_dict):
    """
    Get groups of same tag in the page.
    :param arg1: the reference for the BeautifulSoup object created
    :param arg2: the name of the tag
    :param arg3: A dictionnary of attribute-values
    :type arg1: BeautifulSoup object
    :type arg2: str
    :type arg3: dictionnary
    :return : a list of same tag having the same attributes defined in the attr_dict
    """
    return doc.findAll(tag_name, attr_dict)


def findChildren(beautyobject, tagvalue, childvalue, classname, deeper=False):
    """
    Get for a tag and its child and little child.
    :param arg1: the beautifulsoup object linked to the data scraped
    :param arg2: the tag for which you search for its child
    :param arg3: the tag for child you are searching for
    :param arg4: the class for father tag
    :param arg5: the deeper you want to go in the tree
    :type arg1: BeautifulSoup object
    :type arg2: str
    :type arg3: str
    :type arg4: str
    :type arg5: boolean
    :return: a list of children of the tag
    """
    return beautyobject.find(tagvalue, class_=classname).find_all(
        childvalue, recursive=deeper
    )


def findTagAttr(doc, tagname, classname, *attributes):
    """
    Get a list of dictionnaries representing for each tag of class classname theirs attributes and their values
      :param arg1: the reference for the BeautifulSoup object created
      :param arg2: the name of the  tag
      :param arg3: the name of the class of the tag
      :param arg4: the list of attributes we need
      :type arg1: BeautifulSoup object
      :type arg2: str
      :type arg3: str
      :type arg4: list of variables arguments
      :return : a list of  dictionnaries where the attributes names are the keys and their values the corresponding values
    """
    attrList = []
    tags = find_tag_with_attributes(doc, tagname, {"class": classname})
    for tag in tags:

        listval = []
        for attr in attributes:
            listval.append(tag[attr])
            # Add the text of the tag

        dictattr = dict(zip(list(attributes), listval))
        # Add the text of the tag if it exists
        if tag.text != "":
            dictattr["text"] = tag.text.strip()
        attrList.append(dictattr)
    return attrList


def write_csv(items, path):
    """
    Write a lits of dictionnary of attributes values pairs in a CSV file
    :arg1: the list of dictionnaries
    :arg2: the path to the data
    :type arg1: list
    :type arg2: str
    :return : a csv file containing the data
    """
    # Open the file in write mode
    with open(path, "w") as f:
        # Return if there's nothing to write
        if len(items) == 0:
            return

        # Write the headers in the first line
        headers = list(items[0].keys())
        f.write(",".join(headers) + "\n")

        # Write one item per line
        for item in items:
            values = []
            for header in headers:
                values.append(item.get(header, ""))
            f.write(",".join(values) + "\n")
