import click
from click.decorators import command
from crontab import CronTab
import os

@click.command()
def start():
    '''
    For initiating the pull operation 

    Please store config.yaml in the directory 
    Please create the clone of the repository  
    \f
    
   
    '''

    cron_job = CronTab(user=True)
    cron_path = os.environ.get("cron_path")
    job = cron_job.new(command=f'{cron_path}buildpan pull')
    job.minute.every(1)
    cron_job.write()
    print("called")