import fire
from rudder import Rudder


def main():
    fire.Fire({
        'execute': Rudder().execute
    })

if __name__ == "__main__":
    main()
