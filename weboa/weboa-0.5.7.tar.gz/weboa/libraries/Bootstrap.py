from weboa.libraries import Library

class Bootstrap(Library):
    def __init__(self):
        self.name = "Bootstrap 4"
        self.js = ["https://ex.nvg-group.com/libs/bootstrap/4.3.1/f.min.js"]
        self.css = ["https://ex.nvg-group.com/libs/bootstrap/4.3.1/f.min.css"]

class Bootstrap5(Library):
    def __init__(self):
        self.name = "Bootstrap 5"
        self.js = ["https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js"]
        self.css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"]