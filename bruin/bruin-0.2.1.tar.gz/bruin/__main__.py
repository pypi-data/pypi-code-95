import argparse
from bruin.meal import print_menu_all, print_hour, print_menu_detail_all, Period
from bruin.calendar_tool import print_events_today

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("option", type=str, help=
    "Tools that can be used in this cli, including:\n\n\
meal: print today's menu for each dining hall.\n \
calendar: print incoming events/classes today."
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
    "--detail", 
    type=str, 
    dest='detail', 
    action='store', 
    default=None, 
    help='Print detail menu for [=Breakfast, =Lunch, =Dinner]'
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
    else:
        parser.print_help()

if __name__ == '__main__':
    main()