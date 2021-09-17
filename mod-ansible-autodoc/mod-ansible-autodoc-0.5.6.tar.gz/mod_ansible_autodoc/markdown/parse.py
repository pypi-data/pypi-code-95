import re
from typing import List, Optional


def parse_section(
    text: str,
    name: str,
    by: Optional[str] = "#",
    by_num: Optional[int] = 2,
    by_num_end: Optional[int] = 2,
) -> str:
    """
    Returns a specific section from a markdown file.

    Args:
        text (str): text
        name (str): name of the section
        by (Optional[str]): items will be filtered using this str

    Returns:
        (str): section
    """
    hashes = by * by_num + " "
    section_start = hashes + name

    section_start_index = text.index(section_start)

    if section_start_index == -1:
        return ""

    sub_txt = text[section_start_index:]

    hashes_end = by * by_num_end + " "

    section_end_match = re.search(
        r"(?<!{0}){1}".format(by, hashes_end), sub_txt[len(section_start):]
    )
    if section_end_match:
        section_end_index = section_end_match.span()[0]
    else:
        section_end_index = -1

    if section_end_index == -1:
        return sub_txt[:]
    return sub_txt[: len(section_start) + section_end_index]


def get_all_headings(text: str, num_hashes: int) -> List[str]:
    """
    Returns headings from a markdown file.

    Args:
        text (str): text
        num_hashes (int): indicates the heading "level" to look for

    Returns:
        (List[str]): headers
    """
    hashes_str = "#" * num_hashes + " "

    headings = []
    for line in text.splitlines():
        if hashes_str in line:
            headings.append(line.strip().replace(hashes_str, ""))

    return headings


def get_list_items(text: str, by: Optional[str] = "*") -> List[str]:
    """
    Gets list of 'items' from a string of text, by default, lines starting w/ *

    Args:
        text (str): text
        by (Optional[str]): items will be filtered using this str

    Returns:
        (List[str]): items
    """
    by_str = by + " "

    items = []
    for line in text.splitlines():
        if line.startswith(by_str):
            items.append(line.strip())

    return items


def get_examples(text: str) -> List[str]:
    """
    Returns yaml examples from a string of text.

    Args:
        text (str): text

    Returns:
        (List[str]): examples
    """
    # can use (``yaml)([^*]*)(``) or \**(example:)([^*]*)(\*|)
    matches = re.findall(r"(``yaml)([^*]*)(``)", text)

    examples = []
    for match in matches:
        examples.append("\n".join(match))

    return examples
