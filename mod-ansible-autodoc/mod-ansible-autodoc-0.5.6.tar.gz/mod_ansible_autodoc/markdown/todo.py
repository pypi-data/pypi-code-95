import re
import json
import subprocess
from mod_ansible_autodoc.files.common import (
    read_file, check_file_exists, read_lines
)


GIT_REPO_PATTERN = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(\/\/)?)" \
                   r"([\w\.@\:/\-~]+)(\.git)(\/)?"


def get_todo_source_code_link(todo_name: str) -> str:
    """
    Returns link to the location of the todo item in the role's
    defaults/main.yml file.

    Args:
        todo_name (str): todo name

    Returns:
        str: link
    """
    repo_url = get_repo_url()
    if repo_url is None:
        return todo_name
    repo_url = parse_repo_url(repo_url)

    line_number = get_todo_line(todo_name)
    if line_number is None:
        return todo_name

    repo_url += f"defaults/main.yml#L{line_number}"
    return f"[{todo_name}]({repo_url})"


def get_repo_url() -> str:
    """
    Returns the git repo url.

    Returns:
        str: repo url
    """
    repo_url = None

    # Get the repo URL first. Check if there's a package.json in the current dir
    package_json_path = "./package.json"
    if check_file_exists(package_json_path):
        # Attempt to get repo url from .repository.url
        repo_url = get_repo_url_from_package_json(package_json_path)

    if repo_url is None:
        # Else, get repo url by running git config --get remote.origin.url
        repo_url = get_repo_url_from_git_config()

    return repo_url


def get_repo_url_from_package_json(package_json_path: str) -> str:
    """
    Get repo url from package json

    Args:
        package_json_path (str): package.json path

    Returns:
        str: repo url
    """
    package_json = read_file(package_json_path)

    try:
        package_json = json.loads(package_json)
        repo = package_json.get("repository", {})
        repo_url = repo.get("url", None)
    except:
        repo_url = None

    return repo_url


def get_repo_url_from_git_config() -> str:
    """
    Get repo url from git config

    Returns:
        str: repo url
    """
    # Build command
    bash_cmd = "git config --get remote.origin.url"

    # Open subprocess and run
    proc = subprocess.Popen(bash_cmd, stdout=subprocess.PIPE, shell=True)
    output, _ = proc.communicate()
    output = output.decode("utf-8")

    # Check if there's a git repo in the output
    match = re.search(GIT_REPO_PATTERN, output)
    if not match:
        return None

    return match.group()


def parse_repo_url(repo_url: str) -> str:
    """
    Parses repo url and returns it in the form 'https://domain.com/user/repo'

    Args:
        repo_url (str): unformatted repo url

    Returns:
        str: parsed repo url
    """
    repo = repo_url.lstrip("git+") if repo_url.startswith("git+") else repo_url
    repo = repo.rstrip(".git") if repo.endswith(".git") else repo

    if repo.startswith("http"):
        return f"{repo}/-/blob/master/"
    else:
        repo_data = repo.split(":", 1)
        domain = repo_data[0].split("@")[-1]
        return f"https://{domain}/{repo_data[1]}/blob/master/"


def get_todo_line(todo_name: str) -> str:
    """
    Returns the location of a todo item in the defaults/main.yml file.

    Args:
        todo_name (str): todo name

    Returns:
        str: line number
    """
    defaults_main = "./defaults/main.yml"
    if not check_file_exists(defaults_main):
        return None

    lines = read_lines(defaults_main)
    for line_number, line in enumerate(lines):
        try:
            if line.lower().index(f"@todo {todo_name.lower()}") != -1:
                return str(line_number + 2)
        except ValueError:
            pass

    return None
