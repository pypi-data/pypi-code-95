import unittest
from easysparql import easysparql

ENDPOINT = "https://dbpedia.org/sparql"
albert_uri = "http://dbpedia.org/resource/Albert_Einstein"
albert_name = "Albert Einstein"
scientist = "http://dbpedia.org/ontology/Scientist"
foaf_name = "http://xmlns.com/foaf/0.1/name"


class TestEasySPARQL(unittest.TestCase):

    def test_get_entities(self):
        entities = easysparql.get_entities(subject_name=albert_name, endpoint=ENDPOINT, language_tag="@en")
        self.assertGreater(len(entities), 0, 'No entities are returned')

    def test_get_classes(self):
        classes = easysparql.get_classes(entity_uri=albert_uri, endpoint=ENDPOINT)
        self.assertGreater(len(classes), 0, 'No classes are returned')

    def test_parents_of_class(self):
        parents = easysparql.get_parents_of_class(class_uri=scientist, endpoint=ENDPOINT)
        self.assertGreater(len(parents), 0, 'No parents are returned')

    def test_get_subjects(self):
        subjects = easysparql.get_subjects(class_uri=scientist, endpoint=ENDPOINT)
        self.assertGreater(len(subjects), 0, 'No subjects are returned')

    def test_subject_properties(self):
        properties = easysparql.get_properties_of_subject(subject_uri=albert_uri, endpoint=ENDPOINT)
        self.assertGreater(len(properties), 0, 'No properties are returned')

    def test_num_detection(self):
        a = ["1.2", "2", "4", "3", 3, 6, "a", "b", "ccc", "1jasdf"]
        nums = easysparql.get_numerics_from_list(a, num_perc=0.5)
        self.assertIsNotNone(nums, 'the numbers in the list is more than 50%')
        a = ["1.2", "2dfs", "df4", "3aaa", 3, 6, "a", "b", "ccc", "1jasdf"]
        txts = easysparql.get_numerics_from_list(a, num_perc=0.5)
        self.assertIsNone(txts, 'the numbers in the list is more than 50%')
        self.assertEqual(1.2, easysparql.get_num("1.2"), '1.2 should be a number')
        self.assertIsNone(easysparql.get_num("1.2.3"), '1.2.3 should not be a number')
        self.assertIsNone(easysparql.get_num("acd1.2"), 'acd1.2 should not be a number')
        self.assertIsNone(easysparql.get_num("abc"), 'abc should not be a number')
        self.assertEqual(122, easysparql.get_num("122"), '122 should be a number')


if __name__ == '__main__':
    unittest.main()
