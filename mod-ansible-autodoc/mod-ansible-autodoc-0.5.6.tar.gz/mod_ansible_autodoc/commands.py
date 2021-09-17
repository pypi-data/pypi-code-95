import subprocess
from typing import Optional
from mod_ansible_autodoc.args.args import ARG_NAMES, get_user_arguments
from mod_ansible_autodoc.files.common import (
    check_file_exists,
    move_file,
    read_file,
    save_file,
)
from mod_ansible_autodoc.markdown.parse import parse_section
from mod_ansible_autodoc.markdown.format import (
    format_todo,
    format_actions,
    format_tags,
    format_variables,
    add_title,
    add_description,
    reformat_subheaders
)
from mod_ansible_autodoc import __version__


def run() -> None:
    """Entry point for the script"""
    mod_ansible_doc()


def mod_ansible_doc() -> None:
    # Get cmd args
    user_args = get_user_arguments()

    # Backup current README.md
    file_to_backup, backup_filename = "./README.md", "./README.backup"
    if check_file_exists(file_to_backup):
        move_file(file_to_backup, backup_filename)

    # Run ansible autodoc
    run_ansible_autodoc()

    if check_file_exists("README.md"):
        # Read generated README.md
        generated_file = "README.md"
        content = read_file(generated_file)

        # Parse variables
        todo = try_parse_section(content, "TODO")
        actions = try_parse_section(content, "Actions")
        tags = try_parse_section(content, "Tags")
        variables = try_parse_section(content, "Variables")

        # Format...
        todo = format_todo(todo)
        actions = format_actions(actions)
        tags = format_tags(tags)
        variables, examples = format_variables(
            variables,
            user_args.get(ARG_NAMES[8]),
            user_args.get(ARG_NAMES[9]),
            user_args.get(ARG_NAMES[10])
        )

        # Add descriptions
        todo = add_description(todo, user_args, ARG_NAMES[4])
        actions = add_description(actions, user_args, ARG_NAMES[5])
        tags = add_description(tags, user_args, ARG_NAMES[6])
        examples = add_description(examples, user_args, ARG_NAMES[7])

        # Add titles (if applies)...
        todo = add_title(todo, user_args, ARG_NAMES[0], "## TODO")
        actions = add_title(actions, user_args, ARG_NAMES[1], "## ACTIONS")
        tags = add_title(tags, user_args, ARG_NAMES[2], "## TAGS")
        examples = add_title(examples, user_args, ARG_NAMES[3], "## VARIABLES")

        # Reformat subheaders
        todo = reformat_subheaders(todo)
        actions = reformat_subheaders(actions, True)
        tags = reformat_subheaders(tags)
        examples = examples

        # Save new docs
        save_file("ansible_todo.md", todo)
        save_file("ansible_actions.md", actions)
        save_file("ansible_tags.md", tags)
        save_file("ansible_variables.json", variables, is_json=True)
        save_file("ansible_variables.md", examples)

    # Restore README.md
    if check_file_exists(backup_filename):
        move_file(backup_filename, file_to_backup)


def try_parse_section(text: str, section_name: str) -> str:
    """
    Parse a section. Return an empty string if section not found.

    Args:
        text (str): text
        section_name (str): section's name

    Returns:
        (str): section
    """
    try:
        return parse_section(text, section_name)
    except Exception:
        return ""


def run_ansible_autodoc(verbose: Optional[bool] = True) -> None:
    """
    Runs ansible autodoc.

    Args:
        verbose (bool, optional) = indicates if cmd output should be printed out
    """
    # Build bash command
    bash_command = ["ansible-autodoc-fork", "-y"]
    bash_command = " ".join(bash_command)

    # Open subprocess and run
    proc = subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
    output, _ = proc.communicate()

    # Print the output if necessary
    if verbose:
        print(output.decode("utf-8"))


if __name__ == "__main__":
    run()
