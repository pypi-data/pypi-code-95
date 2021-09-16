from .fileio import read_yaml_file

from wbnlu import logger
import os
import json

logger = logger.my_logger(__name__)

abspath = os.path.abspath(os.path.dirname(__file__))
CONFIG = read_yaml_file(os.path.join(abspath, "../configs/pattern_config.yml"))


class PatternLoader(object):

    @classmethod
    def load_pattern(cls, disable, user_pattern, load_partial=False):
        domains = CONFIG
        domain_patterns = {}

        # 1. Load generic patterns
        # if 'entity' not in disable:
        #     PatternLoader._load_helper('entity', domains, domain_patterns)

        # 2. Load domain (app) specific patterns
        # if 'sentiment' not in disable:
        #     PatternLoader._load_helper('sentiment', domains, domain_patterns)
        # if 'timex' not in disable:
        #     PatternLoader._load_helper('timex', domains, domain_patterns)

        PatternLoader._load_helper('entity', domains, domain_patterns)
        PatternLoader._load_helper('relation', domains, domain_patterns)
        for up in user_pattern:
            PatternLoader._load_helper(up, domains, domain_patterns)

        return domain_patterns

    @staticmethod
    def _load_helper(domain, domains, domain_patterns):
        if domain not in domains:
            raise ValueError(
                'Pattern file not configured for {} extraction in ../configs/pattern_config.yml'.format(domain))
        logger.info("Loading pattern files for '{}'.".format(domain))
        PatternLoader._load(domains[domain], domain_patterns, domain)

    @staticmethod
    def _load(domain_files_and_types, domain_patterns, domain):
        pattern_content = []
        types = []
        if domain_files_and_types:
            PatternLoader._load_patterns(domain, domain_files_and_types[0], pattern_content)
            if len(domain_files_and_types) == 2:
                types = domain_files_and_types[1].split(', ')

        domain_patterns[domain] = (pattern_content, types)

    @staticmethod
    def _load_patterns(domain, domain_files, pattern_content):
        dfiles = domain_files.split(', ')
        size = len(dfiles)
        if size == 0:
            raise ValueError('Invalid pattern file configurations: {} {}'.format(domain, domain_files))
        pattern_file = dfiles[0]
        filter_file = None
        normalization_file = None
        if size >= 2:
            filter_file = dfiles[1]
        if size == 3:
            normalization_file = dfiles[2]

        with open(os.path.join(abspath, '../resources/patterns/' + domain + '/' + pattern_file), 'r',
                  encoding='utf8') as f1:
            pattern_data = f1.read()
            pattern_content.append(json.loads(pattern_data, encoding='utf8'))

        if filter_file:
            filter_dict = {}
            filter_file_path = os.path.join(abspath, '../resources/patterns/' + domain + '/' + filter_file)
            if filter_file.endswith('filter'):
                filter_type = filter_file[0:filter_file.index('.')]
                filtered_items = set()
                with open(filter_file_path, 'r', encoding='utf8') as f2:
                    for item in f2:
                        filtered_items.add(item.strip())
                filter_dict[filter_type] = filtered_items
            else:
                with open(filter_file_path, 'r', encoding='utf8') as f2:
                    filter_data = f2.read()
                    for filter in json.loads(filter_data, encoding='utf8'):
                        for key, values in filter.items():
                            filter_dict[key] = set(values)
            pattern_content.append(filter_dict)

        if normalization_file:
            normalization_dict = {}
            with open(os.path.join(abspath, '../resources/patterns/' + domain + '/' + normalization_file), 'r',
                      encoding='utf8') as f3:
                norm_data = f3.read()
                for norm in json.loads(norm_data, encoding='utf8'):
                    for key, values in norm.items():
                        normalization_dict[key] = set(values)
            pattern_content.append(normalization_dict)


    @classmethod
    def load_nlp_pattern(cls, pattern_type, disable):
        # domains = CONFIG.items()
        if pattern_type.name in CONFIG:
            pattern_file = CONFIG[pattern_type.name]

            logger.info("Loading pattern files for {}.".format(pattern_type))

            abs_pattern_file_path = os.path.join(abspath,
                                                 '../resources/patterns/' + pattern_type.name + '/' + pattern_file[0])

            with open(abs_pattern_file_path, 'r', encoding='utf8') as f:
                pattern_data = f.read()
                return json.loads(pattern_data, encoding='utf8')

        return None
