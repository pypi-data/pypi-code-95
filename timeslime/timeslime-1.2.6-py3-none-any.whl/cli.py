#!/usr/bin/env python3
from ast import literal_eval
import click
from datetime import date, timedelta
from os.path import expanduser, join

from .handler import DatabaseHandler, SettingsHandler, TimeslimeHandler, TimeslimeServerHandler

DATABASE_PATH = join(expanduser('~'), '.timeslime', 'data.db')

def boot(database_path = DATABASE_PATH) -> TimeslimeHandler:
    database_handler = DatabaseHandler(database_path)
    settings_handler = SettingsHandler(database_handler)
    if not settings_handler.contains('weekly_hours'):
        print('Please run `timeslime init` to configure timeslime')
        exit(1)

    weekly_hours = literal_eval(settings_handler.get('weekly_hours').value)
    daily_working_time_array = weekly_hours[date.today().weekday()].split(':')
    daily_working_time = timedelta(hours=int(daily_working_time_array[0]), minutes=int(daily_working_time_array[1]), seconds=int(daily_working_time_array[2]))

    if settings_handler.contains('timeslime_server'):
        setting = settings_handler.get('timeslime_server')
        timeslime_server_handler = TimeslimeServerHandler(setting.value)
    else:
        timeslime_server_handler = None

    return TimeslimeHandler(daily_working_time, database_handler, timeslime_server_handler)

@click.group()
@click.option('--database', default=DATABASE_PATH, help='Defines path to the database. [ default: ~/.timeslime/data.db ]')
@click.pass_context
def main(ctx, database):
    """It's a tool to track your time."""
    ctx.ensure_object(dict)
    ctx.obj['database'] = database

@main.command('start', short_help='Start your time')
@click.pass_context
def start(ctx):
    timeslime_handler = boot(ctx.obj['database'])
    timeslime_handler.start_time()

@main.command('stop', short_help='Stop your time')
@click.pass_context
def stop(ctx):
    timeslime_handler = boot(ctx.obj['database'])
    timeslime_handler.stop_time()

@main.command('display', short_help='Display your time')
@click.pass_context
def display(ctx):
    timeslime_handler = boot(ctx.obj['database'])
    elapsed_time = str(timeslime_handler.get_elapsed_time())
    print(elapsed_time)

@main.command('settings', short_help='Get or set a setting')
@click.pass_context
@click.option('--key', required=True, help='defines setting key')
@click.option('--value', help='defines setting value')
@click.option('--delete', is_flag=True, help='delete a setting')
def settings(ctx, key, value, delete):
    """Get or set a setting. If value is set it will create or overwrite the setting."""
    database_handler = DatabaseHandler(ctx.obj['database'])
    settings_handler = SettingsHandler(database_handler)

    if delete:
        if settings_handler.contains(key):
            setting = settings_handler.get(key)
            print('Old setting was: "%s" with value: "%s"' % (key, setting.value))
            settings_handler.delete(key)
            print('Deleted setting: "%s"' % (key))
        else:
            print('There is no setting for: "%s"' % key)
        return

    if not value:
        if settings_handler.contains(key):
            setting = settings_handler.get(key)
            print('Setting: "%s" is "%s"' % (key, setting.value))
        else:
            print('There is no setting for: "%s"' % key)
    else:
        if settings_handler.contains(key):
            setting = settings_handler.get(key)
            print('Old setting was: "%s" with value: "%s"' % (key, setting.value))
        settings_handler.set(key, value)
        print('Set setting: "%s" to "%s"' % (key, value))

@main.command('init', short_help='Initialize timeslime')
@click.pass_context
@click.option('--weekly_hours', type=click.INT, prompt='How many hours do you have to work a week?')
def init(ctx, weekly_hours):
    week = timedelta(hours=weekly_hours)
    daily_hours = week / 5
    weekly_hours_setting = [str(daily_hours), str(daily_hours), str(daily_hours), str(daily_hours), str(daily_hours), str(timedelta()), str(timedelta())]

    database_handler = DatabaseHandler(ctx.obj['database'])
    settings_handler = SettingsHandler(database_handler)
    settings_handler.set('weekly_hours', weekly_hours_setting)

if __name__ == "__main__":
    main(obj={})
