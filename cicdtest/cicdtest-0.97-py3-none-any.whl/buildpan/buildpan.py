"""
    Title: buildpan
    Module Name: buildpan
    Author: Akash D.
    Modified By: Kushagra A.
    Language: Python
    Date Created: 26-07-2021
    Date Modified: 03-09-2021
    Description:
        ###############################################################
        ##  Main operating file for all the cli commands             ## 
         ###############################################################
 """

import click
from pyfiglet import Figlet

'''
This contains the code snippet for the cli header.
'''
f = Figlet(font='slant')
print (f.renderText('Buildpan'))


# cli_commands for the buildpan 

from ci_commands import init
from ci_commands import version

@click.group(help="CLI tool to manage CI- CD of projects")
def buildpan():
    pass

'''
 This containes all the commands for the buildpan cli
'''
buildpan.add_command(init.init)
buildpan.add_command(version.version)

if __name__ == '__main__':
    buildpan()