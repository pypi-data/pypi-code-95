import unittest
from easysparql import easysparql, cacher
import hashlib
import os


ENDPOINT = "https://dbpedia.org/sparql"
albert_uri = "http://dbpedia.org/resource/Albert_Einstein"
albert_name = "Albert Einstein"
scientist = "http://dbpedia.org/ontology/Scientist"
foaf_name = "http://xmlns.com/foaf/0.1/name"
cacher = cacher.Cacher(".cache")


class TestCache(unittest.TestCase):

    def test_cache(self):
        query = """
            select distinct ?s where{
                ?s ?p "%s"%s
            }
        """ % (albert_name, "@en")

        fname = hashlib.blake2b(str.encode(query)).hexdigest()+".txt"
        cache_f_path = os.path.join(".cache", fname)
        if os.path.exists(cache_f_path):
            os.remove(cache_f_path)

        results = easysparql.run_query(query=query, endpoint=ENDPOINT)
        data = [r['s']['value'] for r in results]
        self.assertEqual(albert_uri, data[0])
        self.assertFalse(os.path.exists(cache_f_path))
        self.assertIsNone(cacher.get_cache_if_any(query))
        cacher.write_to_cache(query, [[albert_uri]], keys=['s'])
        data = cacher.get_cache_if_any(query)
        self.assertIsNotNone(data)
        self.assertEqual(albert_uri, data[0][0])


if __name__ == '__main__':
    unittest.main()
