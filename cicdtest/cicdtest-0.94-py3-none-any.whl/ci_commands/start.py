from crontab import CronTab


def start():
    '''
    For initiating the pull operation in background
   
    '''

    my_cron = CronTab(user=True)
    job = my_cron.new(command='/home/kush/.local/bin/buildpan pull')
    job.minute.every(1)
