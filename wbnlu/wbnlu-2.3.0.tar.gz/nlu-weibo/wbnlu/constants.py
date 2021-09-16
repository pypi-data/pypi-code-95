import enum
from enum import Enum

TOOL_DEPENDENCIES = {'content_words': ['text_normalizer', 'seg_corrector', 'tagger', 'edit', 'content_words', 'phrase'],
                    #  'entity': ['tagger', 'seg_corrector', 'dictionary', 'entity'],
                    'entity': ['tagger', 'seg_corrector','phrase_match', 'rule_match', 'entity'],
                    #  'relation': ['tagger', 'seg_corrector', 'dictionary', 'entity', 'relation'],
                     'relation': ['tagger', 'seg_corrector', 'dictionary', 'relation'],
                     'timex': ['tagger', 'seg_corrector', 'phrase_match', 'ner', 'timex'],
                     'tagger': ['tagger', 'seg_corrector'],
                     'ner': ['ner'],
                     'dictionary': ['dictionary'],
                     'edit': ['edit'],
                     'text_normalizer': ['text_normalizer'],
                     'parser': ['tagger', 'seg_corrector', 'parser'],
                     'phrase': ['tagger', 'seg_corrector', 'phrase'],
                     'segmenter': ['tagger', 'seg_corrector'],
                     'wb_tag': ['wb_tag'],
                     'wordpiece': ['wordpiece'],
                     'phrase_match': ['phrase_match'],
                     'rule_match': ['tagger', 'seg_corrector', 'rule_match'],
                     }

COMPONENT_DEPENDENCIES = {
    'phrase_match': ['words'],
    'tagger': ['words'],
    'parser': ['words', 'pos'],
    'ner': ['words'],
    'edit': ['words'],
    'text_normalizer': [],
    'rule_match': ['words', 'pos'],
    'relation': ['words'],
    'phrase': ['words', 'pos'],
    'entity': ['words', 'pos'],
}

SENTIMENT_KEYS = {'pos', 'spos', 'neg', 'sneg'}

NEGATION_WORDS = {"不","不够","无","没","没有", "毫无", "全无", "才能", "不再"}

class FeatureNEEnum(Enum):
    brand = 1
    product = 2
    category = 3
    ingredient = 4
    effect = 5

class FeatureEnum(Enum):
    effect = 1
    ingredient = 2
    alias_head = 3
    alias_tail = 4
    alias_trigger = 5
    alias_filter = 6

class PatternTypeEnum(Enum):
    segmentation = 1
    pos = 2

class FeatureAcronymEnum(Enum):
    e = 1
    i = 2
    pV = 3
    n = 4
    f = 5
    iT = 6
    s = 7
    b = 8
    v = 9
    d = 10
    p = 11
    t = 12
    a = 13
    r = 14
    c = 15
    containV = 16
    no = 17
    pos = 18
    neg = 19
    sneg = 20
    spos = 21

class ExtensionKeys(Enum):
    features = 1
    extracted = 2

FEATURE_HIERARCHY = {
    'DATE': ['week','month'],
    'TIME': ['fuzzyTime', 'time']
}


class NlpToolEnum(enum.Enum):
    #sentencizer = 1
    #np_chunker = 4
    segmenter = 1
    seg_corrector = 2
    tagger = 3
    ner = 4
    edit = 5
    text_normalizer = 6
    parser = 7
    dictionary = 8
    entity = 9
    relation = 10
    content_words = 11
    phrase = 12
    wb_tag = 13
    wordpiece = 14
    phrase_match = 15
    rule_match = 16

    @staticmethod
    def as_list():
        return set([e.name for e in NlpToolEnum])


SegmentationGrammar = {'merge':{'c1c1', 'c2c1', 'c2c1_punct', 'punct_c1c2_punct','(c1c1)', '(c1c1_pub)'}, 'split':{'c1c1is'}}