#!/usr/bin/env python3
from datetime import timedelta
from os.path import expanduser, join
from threading import Timer
from time import sleep
from threading import Timer

from gpiozero import Button, LED
import tm1637

from timeslime.handler import DatabaseHandler, TimespanHandler
from timeslime_rpi.handler import DisplayHandler

CANCEL_SCRIPT = False

def toggle_time(timespan_handler):
    if timespan_handler.is_running() is False:
        timespan_handler.start_time()
    else:
        timespan_handler.stop_time()

def display_timespan(display_handler, tm, timespan_handler):
    global CANCEL_SCRIPT
    if CANCEL_SCRIPT:
        return
    timespan = timespan_handler.get_elapsed_time()
    [hours, minutes] = display_handler.timedelta_to_display(timespan)
    tm.numbers(hours, minutes)
    Timer(1, display_timespan, [display_handler, tm, timespan_handler]).start()

def main():
    global CANCEL_SCRIPT
    database = join(expanduser('~'), '.timeslime', 'data.db')
    daily_working_time = timedelta(hours=7, minutes=36)
    status_led = LED(27)
    tm = tm1637.TM1637(clk=3, dio=2)
    try:
        database_handler = DatabaseHandler(database)
        timespan_handler = TimespanHandler(daily_working_time, database_handler)
        display_handler = DisplayHandler()
        if timespan_handler.is_running():
            status_led.on()
        timespan_handler.on_start = status_led.on
        timespan_handler.on_stop = status_led.off
        button = Button(17)
        button.when_pressed = lambda: toggle_time(timespan_handler)
        display_timespan(display_handler, tm, timespan_handler)
        while True:
            sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        CANCEL_SCRIPT = True
        status_led.off()
        tm.write([0, 0, 0, 0])

if __name__ == '__main__':
    main()
