from . import visualization
app = visualization.app.VisApp()
server = app.app.server


def run():
    app.run()
