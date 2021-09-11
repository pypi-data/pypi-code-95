

class MenuItem:
    def __init__(self, option: str, name: str):
        self.option = option
        self.name = name

    def __call__(self, action: callable, *args, **kwargs):
        self.action = action

        def inner_function(*args, **kwargs):
            return self.action(*args, **kwargs)

        return self

    def __str__(self):
        return f"{self.option} - {self.name}"

    def show(self):
        print(self)

    def run(self):
        return self.action()
