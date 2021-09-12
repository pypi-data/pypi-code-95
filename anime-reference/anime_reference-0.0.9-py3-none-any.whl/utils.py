from re import search, findall
from bs4 import BeautifulSoup
from typing import List

def clean_str_list(list_str: List[str], search_str: str = '"(.*)"') -> List[str]:
    """
    Description: "Cleans" a list of strings using regex based on
                 on a search string.

    Parameters:
    -----------
    list_str (List[str]): list of strings
    search_str (str): regex search string

    Returns:
    --------
    List[str]: the "cleaned" str
    """
    clean_list = []
    for string in list_str:
        result = search(search_str, string)
        try:
            clean_list.append(result.group(1).strip())
        except AttributeError:
            continue
    return clean_list

def format_episode_links(prefix_url: str, links: List[str]) -> List[str]:
    """
    Description: Formats the episode links from Ex: "/wiki/Plot_of_Naruto"
                 to "https://naruto.fandom.com/wiki/Plot_of_Naruto"

    Parameters:
    -----------
    prefix_url (str): prefix string url
    links (List[str]): unformatted list of string links

    Returns:
    --------
    List[str]: list of formatted string links
    """
    return [prefix_url+search('a href="(.*)" ', string).group(1) for string in links]

def clean_text(text: str) -> str:
    """
    Description: Cleans the test information of links and other unecessary
                 html tags and characters

    Parameters:
    -----------
    text (str): a string 

    Returns:
    --------
    str: a "cleaned" string
    """
    text = findall("<p>(.*)\n</p>", text)
    text = str(text)
    text = text.replace("<p>", "")
    text = text.replace("</p>", "")
    text = text.replace("  ", " ")
    text = text.replace(".,", ".")
    text = text.replace("['", "")
    text = text.replace("']", "")
    text = text.replace(".',", ".")
    text = text.replace('<p class="mw-empty-elt">', "")
    # text = text.replace(', ', "")
    text = text.replace("\\", "")
    text = text.replace(" '", " ")
    soup = BeautifulSoup(text, "html.parser")
    tags = list(map(str, soup.find_all("a")))
    for tag in tags:
        try:
            result = search('title="(.*)"', tag)
            text = text.replace(tag, result.group(1))
        except AttributeError:
            continue
    return text
