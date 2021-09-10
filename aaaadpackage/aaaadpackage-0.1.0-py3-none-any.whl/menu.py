def menu(**kwargs):
    while True:
        options = '/'.join(sorted(kwargs))
        option = input(f"Pick an option [{options}]: ")
        if option in kwargs:
            return kwargs[option]()
        else:
            print("Invalid!")
