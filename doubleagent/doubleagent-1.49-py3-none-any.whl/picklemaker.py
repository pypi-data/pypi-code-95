import pickle


def picklemaker(savename, value):

    f = open(savename, "wb")
    pickle.dump(value, f)
    f.close()
