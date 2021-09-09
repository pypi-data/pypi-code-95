import click
from click.decorators import command
from crontab import CronTab

@click.command()
def start():
    '''
    For initiating the pull operation 

    Please store config.yaml in the directory 
    Please create the clone of the repository  
    \f
    
   
    '''

    cron_job = CronTab(user=True)
    job = cron_job.new(command='/home/kush/.local/bin/buildpan init')
    job.minute.every(1)
    print("called")