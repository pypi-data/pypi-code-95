from . import prep_data
from . import setup_db
import argparse

parser = argparse.ArgumentParser(description="IF_LICENSE_PLATES_COULD_TALK")
parser.add_argument("cmd", nargs="?", default="run")

args = parser.parse_args()

if args.cmd == "prep":
    prep_data.prep_data()
elif args.cmd == "db":
    setup_db.setup_db()
else:
    from . import app
    app.run()
