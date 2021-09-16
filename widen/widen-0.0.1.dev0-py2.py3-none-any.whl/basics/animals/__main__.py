import pkg_resources
from .args import args

def main():
    animals = {}
    input_animal = args.kind
    for entry_point in pkg_resources.iter_entry_points('animals'):
        animals[entry_point.name] = entry_point.load()

    animal = animals[input_animal]()
    animal.talk()

if __name__ == '__main__':
    main()