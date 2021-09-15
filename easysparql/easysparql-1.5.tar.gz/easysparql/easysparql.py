from SPARQLWrapper import SPARQLWrapper, JSON
import logging

try:
    basestring
except:
    basestring = str


def get_logger(name, level=logging.INFO):
    # logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=level)
    logger = logging.getLogger(name)
    return logger


logger = get_logger(__name__, level=logging.INFO)


def run_query(query, endpoint):
    """
    :param query: raw SPARQL query
    :param endpoint: endpoint source that hosts the data
    :return: query result as a dict
    """
    sparql = SPARQLWrapper(endpoint=endpoint)
    sparql.setQuery(query=query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        if len(results["results"]["bindings"]) > 0:
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


def get_entities(subject_name, endpoint, language_tag=None):
    """
    assuming only in the form of name@en. To be extended to other languages and other types e.g. name^^someurltype
    :param subject_name:
    :param endpoint
    :return:
    """
    if language_tag is None:
        query = """
            select distinct ?s where{
                ?s ?p "%s"@en
            }
        """ % (subject_name)
    else:
        query = """
            select distinct ?s where{
                ?s ?p "%s"%s
            }
        """ % (subject_name, language_tag)

    results = run_query(query=query, endpoint=endpoint)
    entities = [r['s']['value'] for r in results]
    return entities


def get_classes(entity_uri, endpoint):
    """
    :param entity: entity url without <>
    :param endpoint:
    :return:
    """
    query = """
        select distinct ?c where{
        <%s> a ?c
        }
    """ % entity_uri
    results = run_query(query=query, endpoint=endpoint)
    classes = [r['c']['value'] for r in results]
    return classes


def get_parents_of_class(class_uri, endpoint):
    """
    get the parent class of the given class, get the first results in case of multiple ones
    :param class_uri:
    :param endpoint:
    :return:
    """
    query = """
    select distinct ?c where{
    <%s> rdfs:subClassOf ?c.
    }
    """ % class_uri
    results = run_query(query=query, endpoint=endpoint)
    classes = [r['c']['value'] for r in results]
    return classes


def get_subjects(class_uri, endpoint):
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
    results = run_query(query, endpoint)
    subjects = [r['s']['value'] for r in results]
    return subjects


def get_properties_of_subject(subject_uri, endpoint):
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
    results = run_query(query, endpoint)
    properties = [r['p']['value'] for r in results]
    return properties


# The below two functions are copied from oeg-upm/ttla
# and are slighly updated
def get_numerics_from_list(nums_str_list, num_perc):
    """
    :param nums_str_list: list of string or numbers or a mix
    :param num_perc: the percentage of numbers to non-numbers
    :return: list of numbers or None if less than {num_perc}% are numbers
    """
    nums = []
    for c in nums_str_list:
        n = get_num(c)
        if n is not None:
            nums.append(n)
    if len(nums) < len(nums_str_list) / 2:
        return None
    return nums


def get_num(num_or_str):
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
