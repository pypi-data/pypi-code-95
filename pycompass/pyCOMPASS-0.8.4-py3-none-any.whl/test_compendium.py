from unittest import TestCase

from pycompass.ontology_node import OntologyNode
from pycompass.biological_feature import BiologicalFeature
from pycompass.experiment import Experiment
from pycompass.ontology import Ontology
from pycompass.platform import Platform
from pycompass.plot import Plot
from pycompass.sample import Sample
from pycompass.sample_set import SampleSet


class TestCompendium(TestCase):

    def test_all(self):
        from pycompass import Compendium, Connect, BiologicalFeature, Module, SampleSet, Plot, Annotation, Experiment, Sample, Platform, Ontology, Sparql, RawData
        connect = Connect('http://compass.fmach.it/graphql')
        compendium = connect.get_compendium('vespucci')

        s = Sample.using(compendium).get(filter={'first': 1})
        rd = RawData(s[0])

        bfs = rd.get_biofeatures()

        #compendium_tpm = connect.get_compendium('vespucci', normalization='tpm')

        #all_samplesets = SampleSet.using(compendium_tpm).get()
        #all_bf = BiologicalFeature.using(compendium_tpm).get()

        #tpm_module = Module.using(compendium_tpm).create(biofeatures=all_bf, samplesets=all_samplesets)

        #sparql = "SELECT ?s ?p ?o WHERE { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.obolibrary.org/obo/NCIT_C19157> . ?s <http://purl.obolibrary.org/obo/NCIT_C68774> ?bn1 . ?bn1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o FILTER (strstarts(str(?o), 'http://purl.obolibrary.org/obo/NCBITaxon_'))}"
        #Sample.using(compendium_tpm).by(sparql=sparql)

        #gene_list = ["VIT_01s0010g03720","VIT_01s0011g01300","VIT_01s0011g03480","VIT_01s0011g06390","VIT_01s0026g02700","VIT_01s0137g00030","VIT_03s0038g01460","VIT_03s0038g04220","VIT_08s0007g07100","VIT_11s0016g03490","VIT_15s0021g02170","VIT_15s0046g00330","VIT_17s0000g05400","VIT_17s0000g08110","VIT_19s0015g00960","VIT_19s0015g00150","VIT_19s0015g01280"]
        #bf = BiologicalFeature.using(compendium).get(filter={'name_In': gene_list})

        #alias = []
        #for n in ['B9S8R7', 'Q7M2G6', 'D7SZ93', 'B8XIJ8', 'Vv00s0125g00280', 'Vv00s0187g00140', 'Vv00s0246g00010',
        #          'Vv00s0246g00080', 'Vv00s0438g00020', 'Vv00s0246g00200']:
        #    alias.append("{{?s <http://purl.obolibrary.org/obo/NCIT_C41095> '{n}'}}".format(n=n))
        #sparql = 'SELECT ?s ?p ?o WHERE {{ {alias} }}'.format(alias=' UNION '.join(alias))

        #for _bf in BiologicalFeature.using(compendium).by(sparql=sparql):
        #    bf.append(_bf)

        #module_1 = Module.using(compendium).create(biofeatures=bf)

        #print(module_1.sample_sets[0].short_annotation_description)
        #desc = module_1.get_enrichment()
        #print(desc)

        #OntologyNode.using(compendium).get(filter={''})

        #root = OntologyNode.using(compendium).get(filter={"originalId": "PO_0009005"})
        #pass



