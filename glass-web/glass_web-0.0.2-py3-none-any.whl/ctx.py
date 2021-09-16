from .utils import _thread_local
import threading


class AppStack:
    def __init__(self):
        self.local = threading.local()

    def push(self, obj):
        if not hasattr(self.local, 'stack'):
            self.local.stack = []
        self.local.stack.append(obj)
        print(self.local.stack)

    def pop(self):
        return self.local.stack.pop()

    def top(self):
        try:
            return self.local.stack[-1]
        except (AttributeError, IndexError):
            return None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.pop()
        # app.unmount()


class App:
    def __enter__(self):
        return app_stack.top().__enter__

    def __exit__(self):
        return app_stack.top().__exit__

    def __getattr__(self, attr):
        app = app_stack.top()
        if app is None:
            raise RuntimeError('Working outside app '
                "This means you are trying to use function "
                "that requires active application")
        return getattr(app, attr)

    def __setattr__(self,x,y):
        app_stack.top().__setattr__(x,y)


app_stack = AppStack()

current_app = App()
