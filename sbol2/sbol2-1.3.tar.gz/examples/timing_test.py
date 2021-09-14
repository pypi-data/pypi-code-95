import time
import timeit
import sbol2

EXAMPLE_PATH = '../test/SBOLTestSuite/SBOL2/RepressionModel.xml'
EXAMPLE_PATH = '../W303.xml'


def append_document(doc: sbol2.Document, path):
    doc.append(path)
    doc.clear()


doc = sbol2.Document()
start = time.time()
seconds = timeit.timeit(lambda: append_document(doc, EXAMPLE_PATH), number=1)
end = time.time()
print('timeit result: {}'.format(seconds))
print('elapsed: {}'.format(end-start))
