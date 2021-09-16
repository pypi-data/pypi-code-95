"""PyProjectUpVers

Copyright (c) 2021 - GitLab

Usage:
    ppuv bump [--messages-file=<path>]
    ppuv push-bump [--config-user=<user>] [--config-email=<email>] [--remote=<remote>] [--url=<url>] [--branch=<branch>]
    ppuv generate-release-notes [--save] [--path=<path>]

Options:
    -h, --help      Show Usage.

Commands:
    bump                    Bump the version of the pyproject.toml file. 
                            This is based on specific keywords, defined in the messages.json file, 
                            found in commit messages ranging from HEAD to the last numeric tag
    
    push-bump               Commits the pyproject.toml file to the git repository.
                            Contains multiple options to run this command in a CI pipeline

    generate-release-notes  Generates release notes based on commits and related MRs in GitLab

Arguments:
    messages-file   Override the messages file JSON (text snippets denoting the version bump), 
                    if not using a local messages.json or installed messages.json
    save            Writes release notes to file (default path = ./release_notes.md)
    path            Override release notes file path
    config-user     Sets git user
    config-email    Sets git user email
    remote          Sets git remote name (ex: origin)
    url             Set remote URL
    branch          Sets git push branch
"""
from docopt import docopt
from poetryupvers.upvers import PyProjectUpVers
from poetryupvers.release_notes import GitLabReleaseNoteGenerator
import poetryupvers.git as git

def run():
    arguments = docopt(__doc__)
    if arguments['bump']:
        if msg_file := arguments['--messages-file']:
            ppuv = PyProjectUpVers(messages_file=msg_file)
        else:
            ppuv = PyProjectUpVers()
        ppuv.bump_version()
        ppuv.write_version_file()
    if arguments['generate-release-notes']:
        notes = GitLabReleaseNoteGenerator()
        notes.generate_mr_map()
        notes.generate_release_notes()
        if arguments['--save']:
            if path := arguments['--path']:
                notes.save_release_notes(path=path)
            else:
                notes.save_release_notes()
    if arguments['push-bump']:
        user = arguments['--config-user']
        email = arguments['--config-email']
        remote = arguments['--remote']
        url = arguments['--url']
        branch = arguments['--branch']
        if user and email:
            print("Setting git config")
            git.git_config(user, email)
        if remote and url:
            git.git_set_origin(remote, url)
        else:
            remote = git.get_current_remote()
        git.git_add("pyproject.toml")
        git.git_commit("Bump version")
        if branch:
            git.git_push(remote, branch)
        else:
            git.git_push(remote, git.get_current_branch())
            

    
