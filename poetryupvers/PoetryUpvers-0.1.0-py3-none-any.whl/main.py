"""PyProjectUpVers

Copyright (c) 2021 - GitLab

Usage:
    ppuv bump [--messages-file=<path>]
    ppuv generate-release-notes [--save] [--path=<path>]

Options:
    -h, --help      Show Usage.

Commands:
    bump            Bump the version of the pyproject.toml file. 
                    This is based on specific keywords, defined in the messages.json file, 
                    found in commit messages ranging from HEAD to the last numeric tag

Arguments:
    messages-file   Override the messages file JSON (text snippets denoting the version bump), 
                    if not using a local messages.json or installed messages.json
"""
from docopt import docopt
from poetryupvers.upvers import PyProjectUpVers
from poetryupvers.release_notes import GitLabReleaseNoteGenerator

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
            

    
