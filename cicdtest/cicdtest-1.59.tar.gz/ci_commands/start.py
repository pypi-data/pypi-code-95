"""
    Title: start.py
    Author: Kushagra A.
    Language: Python
    Date Created: 10-09-2021
    Date Modified: 11-09-2021
    Description:
        ###############################################################
        ## Create a cron process   ## 
         ###############################################################
 """


import click
from click.decorators import command
from crontab import CronTab
import os

@click.command()
def start():
    '''
    For initiating the cron process 

    \f
    '''

    cron_job = CronTab(user=True)
    cron_path = os.environ.get("cron_path")
    job = cron_job.new(command=f'{cron_path}buildpan pull')
    job.minute.every(1)
    cron_job.write()
    print("called")