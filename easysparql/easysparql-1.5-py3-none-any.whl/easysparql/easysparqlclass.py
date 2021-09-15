from SPARQLWrapper import SPARQLWrapper, JSON
import os
import hashlib
from easysparql.cacher import Cacher

try:
    basestring
except:
    basestring = str


class EasySparql:

    def __init__(self, endpoint=None, sparql_flavor="dbpedia", query_limit="", lang_tag="", cache_dir=None):
        self.endpoint = endpoint
        self.sparql_flavor = sparql_flavor
        self.query_limit = query_limit
        self.lang_tag = lang_tag
        self.cacher = None
        if cache_dir:
            if not os.path.exists(cache_dir):
                os.mkdir(self.cache_dir)
            self.cacher = Cacher(cache_dir)

    def run_query(self, query=None, raiseexception=False, printempty=False, keys=[]):
        if self.cacher:
            data = self.cacher.get_cache_if_any(query)
            data = self.cacher.data_to_dict(data)
            if data:
                return data
        sparql = SPARQLWrapper(endpoint=self.endpoint)
        sparql.setQuery(query=query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            if len(results["results"]["bindings"]) > 0:
                if self.cacher and keys!=[]:
                    self.cacher.write_to_cache(query, results["results"]["bindings"], keys)
                return results["results"]["bindings"]
            else:
                logger.debug("returns 0 rows")
                logger.debug("query: <%s>" % str(query).strip())
                return []
        except Exception as e:
            logger.warning(str(e))
            logger.warning("sparql error: $$<%s>$$" % str(e))
            logger.warning("query: $$<%s>$$" % str(query))
            return None

    # def run_query(self, query=None, raiseexception=False, printempty=False):
    #     """
    #     :param query: raw SPARQL query
    #     :param endpoint: endpoint source that hosts the data
    #     :return: query result as a dict
    #     """
    #     if self.endpoint is None:
    #         print("endpoints cannot be None")
    #         return []
    #     if self.cacher:
    #         data = self.cacher.get_cache_if_any(query)
    #         if data:
    #             return data
    #     sparql = SPARQLWrapper(endpoint=self.endpoint)
    #     sparql.setQuery(query=query)
    #     # sparql.setMethod("POST")
    #     sparql.setReturnFormat(JSON)
    #     # sparql.setTimeout(300)
    #     try:
    #         results = sparql.query().convert()
    #         print("run_query> results: ")
    #         print(results)
    #         if len(results["results"]["bindings"]) > 0:
    #             if self.cacher:
    #                 self.cacher.write_to_cache(query, results["results"]["bindings"])
    #             print("run_query> results: ")
    #             print(results)
    #             return results["results"]["bindings"]
    #         else:
    #             if printempty:
    #                 print("returns 0 rows")
    #                 print("endpoint: " + self.endpoint)
    #                 print("query: <%s>" % str(query).strip())
    #             return []
    #     except Exception as e:
    #         print(str(e))
    #         print("sparql error: $$<%s>$$" % str(e))
    #         print("query: $$<%s>$$" % str(query))
    #         if raiseexception:
    #             raise e
    #         return []

    def get_entities(self, subject_name, lang_tag=""):
        """
        assuming only in the form of name@en. To be extended to other languages and other types e.g. name^^someurltype
        :param subject_name:
        :param endpoint
        :return:
        """
        if lang_tag=="":
            lang_tag = self.lang_tag

        query = """
            select distinct ?s where{
                ?s ?p "%s"%s
            }
        """ % (subject_name, lang_tag)

        results = self.run_query(query=query, keys=['s'])
        # print("results")
        # print(results)
        entities = [r['s']['value'] for r in results]
        return entities

    def get_entities_and_classes(self, subject_name, attributes):
        """
        :param subject_name:
        :param attributes:
        :param endpoint: the SPARQL endpoint
        :return:
        """
        inner_qs = []
        csubject = self.clean_text(subject_name)

        if self.sparql_flavor == "dbpedia":
            for attr in attributes:
                cattr = self.clean_text(attr)
                q = """
                    {
                        ?s rdfs:label "%s"@en.
                        ?s a ?c.                        
                    } UNION {
                        ?s rdfs:label "%s"@en.
                        ?s ?p ?e.
                        ?e rdfs:label "%s"@en.
                        ?s a ?c.
                    }
                """ % (csubject, cattr, csubject, cattr)
                inner_qs.append(q)
        elif self.sparql_flavor == "wikidata":
            for attr in attributes:
                cattr = self.clean_text(attr)
                q = """
                    {
                    ?s rdfs:label "%s"@en.
                    ?s wdt:P31 ?c
                    } UNION {
                        ?s rdfs:label "%s"@en.
                        ?s ?p ?e.
                        ?e rdfs:label "%s"@en.
                        ?s wdt:P31 ?c.
                    }
                """ % (csubject, cattr, csubject, cattr)
                inner_qs.append(q)

        inner_q = "UNION".join(inner_qs)

        query = """
            select distinct ?s ?c where{
                %s
            }
        """ % (inner_q)
        results = self.run_query(query=query, keys=['s','c'])
        try:
            entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
        except:
            entity_class_pair = []
        return entity_class_pair

    def get_entities_and_classes_naive(self, subject_name):
        """
        assuming only in the form of name@en. To be extended to other languages and other types e.g. name^^someurltype
        :param subject_name:
        :return:
        """
        csubject = self.clean_text(subject_name)
        if self.sparql_flavor == "dbpedia":
            query = """
                select distinct ?s ?c where{
                    ?s ?p "%s"@en.
                    ?s a ?c
                }
            """ % csubject
        elif self.sparql_flavor == "wikidata":
            query = """
                select distinct ?s ?c where{
                    ?s ?p "%s"@en.
                    ?s wdt:P31 ?c
                }
            """ % csubject
        results = self.run_query(query=query, keys=['s', 'c'])
        try:
            entity_class_pair = [(r['s']['value'], r['c']['value']) for r in results]
        except:
            entity_class_pair = []

        return entity_class_pair

    def get_parents_of_class(self, class_uri):
        """
        get the parent class of the given class, get the first results in case of multiple ones
        :param class_name:
        :param endpoint:
        :return:
        """
        if self.sparql_flavor == "dbpedia":
            query = """
            select distinct ?c where{
            <%s> rdfs:subClassOf ?c.
            }
            """ % class_uri
        elif self.sparql_flavor == "wikidata":
            query = """
            select distinct ?c where{
            <%s> wdt:P279 ?c.
            }
            """ % class_name
        results = self.run_query(query=query, keys=['c'])
        classes = [r['c']['value'] for r in results]
        return classes

    def get_num_class_subjects(self, class_uri):
        query = """
        select count(?s) as ?num
        where {
        ?s a ?c.
        ?c rdfs:subClassOf* <%s>.
        }
        """ % class_uri
        results = self.run_query(query=query, keys=['num'])
        return results[0]['num']['value']

    def clean_text(text):
        ctext = text.replace('"', '')
        ctext = ctext.replace("'", "")
        ctext = ctext.strip()
        return ctext

    # The below two functions are copied from oeg-upm/ttla
    # and are slighly updated
    def get_numerics_from_list(self, nums_str_list, num_perc):
        """
        :param nums_str_list: list of string or numbers or a mix
        :param num_perc: the percentage of numbers to non-numbers
        :return: list of numbers or None if less than {num_perc}% are numbers
        """
        nums = []
        for c in nums_str_list:
            n = self.get_num(c)
            if n is not None:
                nums.append(n)
        if len(nums) < len(nums_str_list) / 2:
            return None
        return nums

    def get_num(self, num_or_str):
        """
        :param num_or_str:
        :return: number or None if it is not a number
        """
        if isinstance(num_or_str, (int, float)):
            return num_or_str
        elif isinstance(num_or_str, basestring):
            if '.' in num_or_str or ',' in num_or_str or num_or_str.isdigit():
                try:
                    return float(num_or_str.replace(',', ''))
                except Exception as e:
                    return None
        return None

    def get_properties_of_subject(self, subject_uri):
        """
        Get properties of a given subject
        :param subject_uri:
        :param endpoint:
        :return:
        """
        query = """
            select distinct ?p
            where{
                <%s> ?p ?o.
            }
        """ % (subject_uri)
        results = self.run_query(query, keys=['p'])
        properties = [r['p']['value'] for r in results]
        return properties

    def get_classes(self, entity_uri):
        """
        :param entity: entity url without <>
        :return:
        """
        query = """
            select distinct ?c where{
            <%s> a ?c
            }
        """ % entity_uri
        results = self.run_query(query=query, keys=['c'])
        # print("get_classes> results:")
        # print(results)
        classes = [r['c']['value'] for r in results]
        return classes

    def get_subjects(self, class_uri):
        """
        Get subjects of a given class
        :param class_uri:
        :param endpoint:
        :return:
        """
        query = """ select ?s
        where{
            ?s a <%s>        
        }
        """ % (class_uri)
        results = self.run_query(query)
        subjects = [r['s']['value'] for r in results]
        return subjects