
class A:

    def deco(self, text):
        def docorator(func):
            def wrapper(*args, **kwargs):
                print('{}: {}'.format(text, func.__name__))
                return func(*args, **kwargs)
            return wrapper
        return docorator


    def fly(self):
        print('fly')

    def behavior(self):
        self.fly()

a = A()
a.fly()
a.behavior()
print(a.fly)

@a.deco('override')
def fly():
    print('no fly')

a.fly = fly

a.fly()
a.behavior()

