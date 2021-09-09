class A1:
    x = 1

class A2:
    pass

def get_a() -> A1:
    return A2()

def use_a():
    a = get_a()
    print(a.x)
