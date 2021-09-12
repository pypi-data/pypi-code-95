"""Python script for git.hook.futurecandy."""

from os import system
from sys import argv
import enquiries

system("git init " + argv[1])

if enquiries.confirm("Specify remotes?"):
    while True:
        system("git " + " --git-dir=" + argv[1] + ".git" + " remote add " +
               enquiries.freetext("Name: ") + " " + enquiries.freetext(
                   "URL: "))
        if not enquiries.confirm("Specify another remote?"):
            break
