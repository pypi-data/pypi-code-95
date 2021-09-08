import pickle


def picklereader(location):

    f = open(location, "rb")
    temp = pickle.load(f)
    f.close()
    return temp
