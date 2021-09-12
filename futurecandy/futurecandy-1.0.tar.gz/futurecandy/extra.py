"""Script for adding futurecandy to RC file."""

import enquiries
from os.path import join, expanduser

KEY = {
    "Bash (~/.bashrc)": lambda: join(expanduser("~"), ".bashrc"),
    "ZSH (~/.zshrc)": lambda: join(expanduser("~"), ".zshrc"),
    "Use ~/.profile": lambda: join(expanduser("~"), ".profile"),
    "Custom": lambda: enquiries.freetext("Specify path to file: ")
}

with open(KEY[enquiries.choose(
        "Pick RC file for command alias to be written to: ", KEY.keys())](),
          "a") as export_handle:
    export_handle.write("\nalias futurecandy='python -m futurecandy'")
    export_handle.write("\nalias futurecandyrc='python -m futurecandy.extra'")
