from . import data
import sys


def setup_db():
    data.db.populate_db()
    data.db.get_data()
