import time
import timeit
import rdflib

EXAMPLE_PATH = '../test/SBOLTestSuite/SBOL2/RepressionModel.xml'
EXAMPLE_PATH = '../W303.xml'


def load_document(path):
    graph = rdflib.Graph()
    graph.parse(location=path, format="application/rdf+xml")
    return graph


start = time.time()
seconds = timeit.timeit(lambda: load_document(EXAMPLE_PATH), number=1)
end = time.time()
print('timeit result: {}'.format(seconds))
print('elapsed: {}'.format(end-start))
