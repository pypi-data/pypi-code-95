try:
    from . import visualization

    app = visualization.app.VisApp()
    server = app.app.server
except:
    pass

from .data import db


def load_regional_data():
    """ Load data frame"""
    return db.get_data()
