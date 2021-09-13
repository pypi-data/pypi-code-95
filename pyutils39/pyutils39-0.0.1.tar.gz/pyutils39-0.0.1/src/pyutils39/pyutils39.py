def reverse(data):
    x = str(data)
    datalen = len(data)
    x = x[datalen::-1]
    return x
def consoleask(question):
    while True:
        print(str(question)+' (Y/N)')
        x = input()
        if x.lower().startswith('y'):
            return True
            break
        elif x.lower().startswith('n'):
            return False
            break