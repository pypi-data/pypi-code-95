import math

import sbol2


class MySampleSequence(sbol2.Identified):

    RDF_TYPE = 'http://example.org#MySampleSequence'

    def __init__(self, uri='example', letters='gcat'):
        super().__init__(uri=uri,
                         type_uri=MySample.RDF_TYPE)
        self.letters = sbol2.TextProperty(self, 'http://example.org#MyLetters', 1, 1,
                                          letters)


class MySample(sbol2.TopLevel):

    RDF_TYPE = 'http://example.org#MySample'

    def __init__(self, uri=None):
        super().__init__(uri=uri,
                         type_uri=MySample.RDF_TYPE)
        self.sequences = sbol2.OwnedObject(self, sbol2.SBOL_SEQUENCE_PROPERTY,
                                           MySampleSequence, 0, math.inf)


doc = sbol2.Document()
seq = sbol2.Sequence('seq1', 'cattag')
cd = sbol2.ComponentDefinition('cd1')
doc.add(cd)
cd.sequence = seq
print(doc.writeString())

sample_seq = MySampleSequence('myseq1', seq.elements)
sample = MySample('mysample1')
sample.sequences = [sample_seq]
doc.add(sample)
print(doc.writeString())
