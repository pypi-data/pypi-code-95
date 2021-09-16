import os
import csv
import re
from collections import OrderedDict
from .fileio import read_yaml_file
from ..userdict.oov_finder import OOVFilter
from .my_utils import has_digit

abspath = os.path.abspath(os.path.dirname(__file__))

CONFIG = read_yaml_file(os.path.join(abspath, "../configs/other_config.yml"))
TERM_SELECTION_FILE = CONFIG['TERM_SELECTION_FILE']

class ResourceLoader(object):

    @staticmethod
    def load_kg_terms():
        with open(os.path.join(abspath, '../../data/nodes_kg.csv'), 'r') as f, open(os.path.join(abspath, '../../data/all_kg_nodes.txt')) as f2:
            csv_reader = csv.reader(f, delimiter='\t')
            next(csv_reader, None)
            i = 0
            all_tags = set()
            for row in csv_reader:
                i += 1
                brand = row[0]
                category = row[1]
                effect = row[2]
                ingredient = row[3]
                product = row[4]
                alias = row[5]
                if brand:
                    brand = brand.lower()
                    all_tags.add(brand)
                if category:
                    category = category.lower()
                    all_tags.add(category)
                if effect:
                    all_tags.add(effect)
                if ingredient:
                    all_tags.add(ingredient)
                if product:
                    all_tags.add(product)
                if alias:
                    all_tags.add(alias)
            for line in f2:
                line = line.strip()
                all_tags.add(line)

        print("All tag size:", len(all_tags))

        return all_tags

    @staticmethod
    def load_query_terms():

        file_path = os.path.join(abspath, '../../data/')
        pattern = re.compile('([^\s]+)\s+(\d+)\s+\d+\s+(\d+\.\d+)')

        term_size_store = []
        terms_store = []
        for i, file_name in enumerate(TERM_SELECTION_FILE):
            input_file = file_path + file_name
            rank = 1
            terms_by_length = OrderedDict()
            with open(input_file, 'r') as f:

                for line in f:
                    # line = chinese_converter.to_simplified(line)
                    matched = re.match(pattern, line)
                    if matched:
                        word = matched.group(1)
                        freq = int(matched.group(2))
                        if OOVFilter.filtered_by_exclusion(word):
                            continue

                        if '2' in input_file and has_digit(word):
                            continue

                        terms_by_length[word] = (rank, freq)
                        rank += 1
                term_size_store.append(rank)
                terms_store.append(terms_by_length)

        # convert rank = ratio
        term_rank = {}
        for i, size in enumerate(term_size_store):
            term_size = term_size_store[i]
            terms_by_length = terms_store[i]
            for word, rank_freq in terms_by_length.items():
                rank = rank_freq[0] / term_size
                freq = rank_freq[1]
                # for bigram, select 0.6 as threhold; otherwise, 0.8
                if i == 0:
                    if rank <= 0.6:
                        term_rank[word] = (rank, freq)
                elif rank <= 0.8:
                    term_rank[word] = (rank, freq)

        return term_rank

    @staticmethod
    def load_online_queries():
        with open(os.path.join(abspath, '../../data/tag.txt'), 'r') as f:
            terms = set()
            for term in f:
                term = term.strip()
                terms.add(term)
            return terms