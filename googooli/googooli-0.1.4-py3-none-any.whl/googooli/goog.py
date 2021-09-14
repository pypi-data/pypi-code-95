import pickle

def hello():
    filename = 'googooli/models/test.pickle'
    infile = open(filename,'rb')
    new_dict = pickle.load(infile)
    infile.close()
    print(new_dict)
    print("Done")






