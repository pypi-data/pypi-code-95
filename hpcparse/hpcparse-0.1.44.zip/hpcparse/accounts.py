class Accounts:
    def __init__(self):
        self.account = None
        self.descr = None
        self.org = None

    def __str__(self):
        return """Account parameters (Name: {}, Account Description: {},
                  orginization account belongs to: {}""".format(self.account,
                                                                self.descr,
                                                                self.org)
