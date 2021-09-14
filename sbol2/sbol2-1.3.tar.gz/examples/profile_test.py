import time
import timeit
import sbol2

EXAMPLE_PATH = '../test/SBOLTestSuite/SBOL2/RepressionModel.xml'
EXAMPLE_PATH = '../W303.xml'


def load_document(doc, path, n_times=1):
    for i in range(n_times):
        doc = sbol2.Document(path)
    return doc


start = time.time()
my_doc = load_document(None, EXAMPLE_PATH, 1)
end = time.time()
print('elapsed seconds: {}'.format(end-start))
print('Loaded document size: {}'.format(len(my_doc)))
