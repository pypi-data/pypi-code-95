"""PyProjectUpVers

Copyright (c) 2021 - GitLab
"""

import re
import poetryupvers.util as util

def get_all_hashes_from_tag(tag):
    """
        Gets all commit message between HEAD and a specified tag
        and returns the messages as a list of strings
    """
    cmd = f"git log --pretty=format:\"%H\" HEAD...{tag}"
    return util.newline_to_list(util.run_cmd(cmd))

def get_all_tags_raw():
    """
        Gets all tags from git repo and returns as list of strings
    """
    cmd = "git for-each-ref --sort=creatordate --format '%(refname:lstrip=2)' refs/tags"
    return util.newline_to_list(util.run_cmd(cmd))
    
def get_all_msg_from_tag(tag):
    """
        Gets all commit message between HEAD and a specified tag
        and returns the messages as a list of strings
    """
    cmd = f"git log --pretty=format:\"%s\" HEAD...{tag}"
    return util.newline_to_list(util.run_cmd(cmd))

def get_all_tags_cleansed():
    """
        Scrubs out all tags with letters in them
    """
    tags = []
    regex = re.compile('.+[A-Za-z].+')
    for t in get_all_tags_raw():
        m = regex.search(t)
        if not m:
            tags.append(t)
    return tags
    
def get_latest_tag():
    """
        Returns latest tag, assuming it's the first in the list
    """
    return get_all_tags_cleansed()[0]

def git_add(file_name):
    """
        Runs `git add <file>`
    """
    return util.run_cmd(f"git add {file_name}")

def git_config(username, email):
    """
        Configures local git repository

        Used within CI pipeline
    """
    util.run_cmd(f"git config user.name '{username}'")
    util.run_cmd(f"git config user.email '{email}'")

def git_commit(commit_msg):
    """
        Creates git commit with message
    """
    return util.run_cmd(f"git+commit+-m+{commit_msg}", split="+")

def git_push(remote, branch):
    """
        Runs git push <remote> <branch>
    """
    return util.run_cmd(f"git push {remote} {branch}")

def git_set_origin(remote, url):
    """
        Sets the git remote URL
    """
    return util.run_cmd(f"git remote set-url {remote} {url}")

def get_current_branch():
    """
        Gets current branch
    """
    cmd = f"git branch --show-current"
    return util.run_cmd(cmd).rstrip("\n")

def get_current_remote():
    """
        Get current remote name
    """
    return util.run_cmd("git remote").rstrip("\n")