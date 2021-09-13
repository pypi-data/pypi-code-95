import sys

REQUIRED_PYTHON = "python3"

def test_custom():
    from src.models.LSTM_learner import LSTM_learner
    from src.models.decoder import Decoder

    try:
        LSTM_learner()
        print("LSTM Learner works.")
    except:
        print("LSTM Learner failure.")
    try:
        Decoder()
        print("Decoder works.")
    except:
        print("LSTM Learner failure.")

def main():
    system_major = sys.version_info.major
    if REQUIRED_PYTHON == "python":
        required_major = 2
    elif REQUIRED_PYTHON == "python3":
        required_major = 3
    else:
        raise ValueError("Unrecognized python interpreter: {}".format(
            REQUIRED_PYTHON))

    if system_major != required_major:
        raise TypeError(
            "This project requires Python {}. Found: Python {}".format(
                required_major, sys.version))
    else:
        print(">>> Development environment passes all tests!")

    test_custom()


if __name__ == '__main__':
    main()
