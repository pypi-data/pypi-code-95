import argparse
from bruin.meal import print_menu_all, print_hour, print_menu_detail_all, Period
from bruin.calendar_tool import print_events_today
from bruin.tasks import add_task_from_input, read_tasks_and_print, terminate_task_by_string, complete_task, remove_daily_task

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("option", type=str, help=
    "Tools that can be used in this cli, including:\n\n\
meal: print today's menu for each dining hall.\n \
calendar: print incoming events/classes today.\n \
tasks: Add and organize your daily tasks."
)

parser.add_argument(
    "--hour", 
    type=str, 
    dest='hour', 
    action='store', 
    default=None, 
    help='Used for meal: fetch hour of operation for dining halls [=all, =\'De Neve\', etc.]'
)

parser.add_argument(
    "-d",
    "--detail", 
    type=str, 
    dest='detail', 
    action='store', 
    default=None, 
    help='Print detail menu for [=Breakfast, =Lunch, =Dinner]'
)

parser.add_argument(
    "-a",
    "--add",
    dest='add',
    action='store_true',
    default=False,
    help="Used for tasks: add a new todo."
)

parser.add_argument(
    "-c",
    "--complete",
    dest='complete',
    action='store',
    type=int,
    default=None,
    help="Used for tasks: complete a task and move to review bucket."
)

parser.add_argument(
    "-t",
    "--terminate",
    dest='terminate',
    action='store',
    type=str,
    default=None,
    help='Used for tasks: remove a task from the list.'
)

parser.add_argument(
    "-r",
    "--remove",
    dest='remove',
    action='store',
    type=int,
    default=None,
    help='Used for tasks: remove a task from the daily list'
)

def main():
    args = parser.parse_args()
    if args.option == "meal":
        if args.hour is not None:
            print_hour(args.hour)
        elif args.detail is not None:
            if Period.contains(args.detail):
                print_menu_detail_all(args.detail)
            else:
                print("Invalid argument for --detail:")
                parser.print_help()
        else:
            print_menu_all()
    elif args.option == "calendar":
        print("Reminder: Please import your calendar data into your Google Calendar!\n")
        print_events_today()
    elif args.option == "tasks":
        if args.add:
            add_task_from_input()
        elif args.complete is not None:
            complete_task(args.complete)
        elif args.terminate is not None:
            terminate_task_by_string(args.terminate)
        elif args.remove is not None:
            remove_daily_task(args.remove)
        else:
            read_tasks_and_print()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()