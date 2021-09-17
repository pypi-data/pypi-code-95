import re
from typing import Dict, List, Optional, Tuple
from mod_ansible_autodoc.markdown.todo import get_todo_source_code_link
from mod_ansible_autodoc.markdown.parse import (
    get_all_headings,
    parse_section,
    get_list_items,
    get_examples,
)


def format_todo(todo: str) -> str:
    """
    Format todo.

    Args:
        todo (str): todo section str

    Returns:
        (str) -> formatted todo
    """
    if not todo:
        return ""

    headings = get_all_headings(todo, 4)

    formatted_todo_content = []
    for heading in headings:
        # Get inner text
        section = parse_section(todo, heading, "#", 4, 4)
        section = section.strip()

        # Get TODO items
        todo_items = get_list_items(section)

        for todo_item in todo_items:
            # Format current item
            todo_name = heading.replace(':', '')
            todo_link = get_todo_source_code_link(todo_name)
            formatted_item = (
                f"* **{todo_link}:** "
                f"{todo_item.lstrip('*').strip('-').strip()}"
            )
            formatted_todo_content.append(formatted_item)

    return "\n".join(formatted_todo_content)


def format_actions(actions: str) -> str:
    """
    Format actions.

    Args:
        actions (str): actions section str

    Returns:
        (str) -> formatted actions
    """
    if not actions:
        return ""

    headings = get_all_headings(actions, 4)

    hashes_str = "#" * 4 + " "
    formatted_actions_content = []
    for heading in headings:
        # Get inner text
        section = parse_section(actions, heading, "#", 4, 4)
        section = section.strip()

        # Ensure capitalization
        section_lines = section.split("\n")
        fheading = hashes_str + section_lines[0].replace(hashes_str, "")
        section_lines[0] = fheading
        section = "\n".join(section_lines)

        formatted_actions_content.append(section)

    return "\n".join(formatted_actions_content)


def format_tags(tags: str) -> str:
    """
    Format tags. For now, uses the same formatting as "format_actions".

    Args:
        tags (str): tags section str

    Return:
        (str) -> formatted tags
    """
    return format_actions(tags)


def format_variables(
    variables: str,
    title_prefix: Optional[str] = "#### ",
    title_postfix: Optional[str] = "",
    example_comment_prefix: Optional[str] = "### "
) -> Tuple[Dict[str, List[List[str]]], str]:
    """
    Format variables.

    Args:
        variables (str): variables section str
        title_prefix (str, optional): variable title prefix. Defaults to '#### '
        title_postfix (str, optional): variable title postfix. Defaults to ''
        example_comment_prefix (str, optional): variable example comment prefix.
        Defaults to '### '.

    Return:
        (Tuple[Dict[str, List[List[str]]], str]) -> variables json, example str
    """
    if not variables:
        return {"role_variables": []}, ""

    # Get variable items
    var_items = get_list_items(variables)

    # Get examples
    examples = get_examples(variables)

    # Format variables
    formatted_variables = [["Name", "Default Value", "Description"]]
    for var_item in var_items:
        # Get name
        var_item_data = var_item.split(":", 1)
        name = var_item_data[0].lstrip("*").strip().strip("`")

        # If name is "docker_edition", check if it has an example
        # ... if it does, add hyperlink
        for example in examples:
            if name in example:
                name = f"[`{name}`](#{name})"

        # Get value
        var_item_data = var_item_data[1].split("-", 1)

        default_value = var_item_data[0].strip()

        # Get description
        description = var_item_data[1].strip()

        # Append to the formatted variable list
        formatted_variables.append([name, default_value, description])

    variables_json = {"role_variables": formatted_variables}

    return (
        variables_json,
        format_variable_examples(
            variables, title_prefix, title_postfix, example_comment_prefix)
    )


def format_variable_examples(
    variables: str,
    title_prefix: Optional[str] = "#### ",
    title_postfix: Optional[str] = "",
    example_comment_prefix: Optional[str] = "###"
) -> str:
    """
    Format variable examples.

    Args:
        variables (str): variables section str
        title_prefix (str, optional): variable title prefix. Defaults to '#### '
        title_postfix (str, optional): variable title postfix. Defaults to ''
        example_comment_prefix (str, optional): variable example comment prefix.
        Defaults to '### '.

    Return:
        (str): formatted examples
    """
    if not variables:
        return ""

    if title_prefix is None:
        title_prefix = "#### "

    if title_postfix is None:
        title_postfix = ""

    # Get examples
    examples = get_examples(variables)

    formatted_examples = []
    for example in examples:
        # Take out beginning ``yaml and ending ``
        if example.startswith("``yaml"):
            example = example.replace("``yaml", "")

        if example.endswith("``"):
            example = example[:-2]

        # Remove extra whitespace
        example = example.strip()

        # Extract name
        example_data = example.split(":", 1)
        name = example_data[0]

        # Extract items
        items = example_data[1].replace('"', "`").strip("`")

        # Define which whitespace to use before {items}

        # Build heading
        head = f"{title_prefix}`{name}`{title_postfix}\n\n"
        comment = f"{example_comment_prefix} Example implementation of the " \
                  f"{name} variable"

        whitespace = "" if items.endswith("\n") else "\n"

        formatted_examples.append(
            f"{head}```yaml\n{comment}\n{name}:{items}{whitespace}```")

    return "\n\n".join(formatted_examples)


def reformat_subheaders(
    content: str,
    change_three_hashes: Optional[bool] = False
) -> str:
    """
    Reformats subheaders' #s so they all are one header level below the
    preceding header or subheader.

    Args:
        content (str): text to reformat
        change_three_hashes (bool, optional): changes ### to ** **.

    Returns:
        str: reformatted text
    """
    text = content[:]
    
    # Find all matches
    matches = re.finditer(r"#+(?=[\s])", text)

    current_level = None
    delta = 0

    # Check all sections' header levels
    for match in matches:
        match_header_level = len(match.group())

        # Current level is equal to the number of #s in the topmost header
        if current_level is None or match_header_level <= current_level:
            current_level = match_header_level
        elif match_header_level == current_level + 1:
            current_level = match_header_level

        # Calculate the number of #s that the header being checked should have
        should_change_to = None
        if match_header_level > current_level:
            should_change_to = (current_level + 1) * "#"

        # Modify if necessary
        if should_change_to:
            text = text[:match.start() + delta] + \
                should_change_to + text[match.end() + delta:]
            # the length of the "text" will change, so keep track of the delta
            delta -= match_header_level - len(should_change_to)

    # Change ### subheaders for ** bold text **
    if change_three_hashes:
        text_lines = text.split("\n")
        for i, line in enumerate(text_lines):
            if line.startswith("### "):
                text_lines[i] = "\n" + line.replace("### ", "**") + "**\n"
        text = "\n".join(text_lines)

    return text


def add_title(
    text: str, args: Dict[str, str], arg_name: str, default_title: str
) -> str:
    return add_subsection(text, args, arg_name, default_title)


def add_description(
    text: str, args: Dict[str, str], arg_name: str
) -> str:
    # Default description is just an empty string
    return add_subsection(text, args, arg_name, "") 


def add_subsection(
    text: str, args: Dict[str, str], arg_name: str, default: str
) -> str:
    # If empty, dont add anything
    if not text:
        return text

    element_to_add = args.get(arg_name, default)

    if element_to_add.strip():
        return f"{element_to_add}\n{text}"

    if default:
        return f"{default}\n{text}"

    return text
