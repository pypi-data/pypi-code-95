import spacy
from wbnlu import logger
from spacy.pipeline import Sentencizer
from spacy.tokens import Doc, Token
from spacy.language import Language
from spacy.matcher import Matcher
import csv
import sys
import threading
from collections import OrderedDict
import os
import json
import tensorflow as tf
import copy

from wbnlu.constants import TOOL_DEPENDENCIES, COMPONENT_DEPENDENCIES, NlpToolEnum
from wbnlu.dev_tools import NlpUtils
from .components.rule_match import rule_match
from .components.phrase_match import PhraseMatchComponent
from .midlevel.entity_recognition_module import entity_recognition
from .components.text_normalizer import ZH_SEG_PUNCT_CHARS
from .components.rule_segementer import RuleSegmenter
from .components.text_normalizer import Text_Normalizer

logger = logger.my_logger(__name__)

abspath = os.path.abspath(os.path.dirname(__file__))

class WBNlu(object):


    def __init__(self):
        self.spacy = None
        self.pipeline = []
        self.rule_match_component = None
        self.init([],['generic'],[],[])
        logger.info('WBNlu initialization done ...')


    def init(self, disable, data_source, user_dict, user_pattern):
        logger.info('Loading Chinese model ...')
        self.spacy = spacy.load('zh_lg_model')
        logger.info('Chinese model loading done...')
        self.spacy.tokenizer.require_pkuseg = False
        self.spacy.tokenizer.use_jieba = True
        self.spacy.tokenizer.use_pkuseg = False
        self.spacy.tokenizer.HMM = False

        if 'sentencizer' not in self.spacy.pipe_names:
            self.spacy.add_pipe(Sentencizer(punct_chars=ZH_SEG_PUNCT_CHARS))

        logger.info('Initizating pos correction ...')
        self.load_pos_lexicon()

        Token.set_extension('singleAsciiToken', default=False, force=True)
        # doc length
        Token.set_extension('longDoc', default=False, force=True)
        # Bracket token, [数组]
        Token.set_extension('bracket', default=False, force=True)
        # @ token, @斜阳溪语
        Token.set_extension('atToken', default=False, force=True)
        if 'pos_correction' not in self.spacy.pipe_names:
            self.spacy.add_pipe(self.pos_correction, after='tagger')

        if 'seg_corrector' not in disable:
            self.rule_segmenter = RuleSegmenter(self.spacy, disable)
            # if 'rule_segmenter' not in self.spacy.pipe_names:
            #     self.spacy.add_pipe(self.rule_segmenter)
            # if 'custom_tok_attributes' not in self.spacy.pipe_names:
            #     self.spacy.add_pipe(self.custom_tok_attributes, after='rule_segmenter')
            

        self.phrase_match_component = PhraseMatchComponent(self.spacy, disable, data_source, user_dict)
        self.rule_match_component = rule_match(self.spacy, disable, user_pattern)
        self.data_source = data_source
        self.user_dict = user_dict
        self.user_pattern = user_pattern
        


    def load_pos_lexicon(self):
        self.pos_lexicon = {}
        path = os.path.join(abspath, "resources/pos/pos.txt")
        with open(path, 'r', encoding='utf8') as f:
            for line in f:
                if not line or line.startswith('//'):
                    continue
                columns = line.split('\t')
                if len(columns) != 2:
                    raise ValueError('Invalid entry line: ', line)
                self.pos_lexicon[columns[0].strip()] = columns[1].strip()
            logger.info('POS lexicon size: {}'.format(len(self.pos_lexicon)))


    def pos_correction(self, doc):
        for token in doc:
            text = token.text
            if text in self.pos_lexicon:
                token.tag_ = self.pos_lexicon[text]
            elif token.is_ascii and token.shape_ != 'd d' and ' ' in token.text:
                token.tag_ = 'FW'
        return doc


    def custom_tok_attributes(self, doc):
        previous_token = None
        doc_len = len(doc)
        if doc_len==1:
            token = doc[0]
            if token.is_ascii:
                token._.set('singleAsciiToken', True)
        for token in doc:
            if previous_token and previous_token.text == '[':
                token._.set('bracket', True)
            elif previous_token and token.text == ']':
                previous_token._.set('bracket', True)
            elif previous_token and previous_token.text == '@':
                token._.set('atToken', True)
            previous_token = token

            if doc_len >= 50:
                token._.set('longDoc', True)
        return doc


    
    def nlp(self, input_data, enable, data_source=['generic'],user_dict=[], user_pattern=[],remove_meme=False, remove_url=False, remove_all_spaces=False, remove_hash=False, text_lower=False, remove_punct=False, remove_all_but_one_space=True,
        remove_stopwords=True, remove_brand=False, remove_onom=False, remove_internet_phrase=False, HMM=True, cut_all=False):
        
        output = {}

        if isinstance(input_data, str):
            self.disable = self.init_nlp(enable, data_source, user_dict, user_pattern, is_text=True, HMM=HMM, cut_all=cut_all)
            if 'edit' not in self.disable:
                text_normalizer = Text_Normalizer(input_data)
                input_data = text_normalizer(remove_hash=remove_hash, text_lower=text_lower, remove_punct=remove_punct, remove_all_space=remove_all_spaces, remove_all_but_one_space=remove_all_but_one_space, remove_urls=remove_url)
            self.pipeline = []
            doc = self.spacy.tokenizer(input_data)
        elif isinstance(input_data, dict):
            self.disable = self.init_nlp(enable, data_source, user_dict, user_pattern, is_text=False, HMM=HMM)
            self.pipeline = []
            doc = self.make_doc(input_data, enable)
            doc.user_data['word_doc'] = True
        else:
            raise ValueError(
                'The input type is invalid. wbnlu.nlp() can take either STR or DICT inputs')

        if 'phrase_match' not in self.disable:
            self.spacy.add_pipe(self.phrase_match_component)

        if 'rule_match' not in self.disable:
            self.spacy.add_pipe(self.rule_match_component)

        if 'entity' not in self.disable:
            entity_component = entity_recognition(self.spacy, self.rule_match_component)
            self.spacy.add_pipe(entity_component, after='rule_match')

        doc = self.execute_pipeline(doc)

        self.reset_pipeline()

        NlpUtils.extract_nlp(output, doc, self.disable, remove_meme=remove_meme, remove_url=remove_url, remove_all_spaces= remove_all_spaces, remove_stopwords=remove_stopwords,
            remove_brand=remove_brand, remove_onom=remove_onom, remove_internet_phrase=remove_internet_phrase)


        if 'entity' not in self.disable or 'rule_match' not in self.disable:
            # NlpUtils.extract_entity(output, doc, entity_component)
            NlpUtils.extract_entity(output, doc, self.rule_match_component)

        return output

    
    
    def init_nlp(self, enable, data_source, user_dict, user_pattern, is_text=True, HMM=True, cut_all=False):

        comp_list = []
        
        if is_text:
            
            for component in enable:
                
                if component not in TOOL_DEPENDENCIES:
                    raise ValueError('Invalid nlp tool configurations: {}. Available tools are: {}'.format(tool, TOOL_DEPENDENCIES.keys()))

                comp_list.extend(TOOL_DEPENDENCIES[component])
        else:
            comp_list = enable
        
        disable = self.get_disable(comp_list)

        if self.spacy == None:
            self.init(disable, data_source, user_dict, user_pattern)

        if self.data_source != data_source or self.user_dict != user_dict:
            self.phrase_match_component = PhraseMatchComponent(self.spacy, disable, data_source, user_dict)
            self.data_source = data_source
            self.user_dict = user_dict

        if self.user_pattern != user_pattern:
            self.rule_match_component = rule_match(self.spacy, disable, user_pattern)
            self.user_pattern = user_pattern

        self.spacy.tokenizer.HMM = HMM

        self.spacy.tokenizer.cut_all=cut_all

        if 'seg_corrector' not in disable:
            if 'rule_segmenter' not in self.spacy.pipe_names:
                self.spacy.add_pipe(self.rule_segmenter)
            if 'custom_tok_attributes' not in self.spacy.pipe_names:
                self.spacy.add_pipe(self.custom_tok_attributes, after='rule_segmenter')

        return disable

    
    
    def make_doc(self, input_data, enable):
        required_object = []

        for component in enable:
            required_object.extend(COMPONENT_DEPENDENCIES[component])

        if not all(obj in input_data.keys() for obj in required_object ):
            raise ValueError(
                'The DICT input does not have enough informantion')

        if required_object == []:
            raise ValueError(
                'Please use STR input')

        doc = Doc(self.spacy.vocab, words=input_data['words'], spaces=[False]*len(input_data['words']))
        if 'Dewords' in input_data:
            doc = Doc(self.spacy.vocab, words=input_data['Dewords'], spaces=[False]*len(input_data['Dewords']))
        
        if 'pos' in required_object:
            for i, token in enumerate(doc):
                token.tag_ = input_data['pos'][i]
            doc.is_tagged = True
        
        return doc


        
    def execute_pipeline(self, doc):
        component_cfg = {}
            
        # with self.lock:
        for name, proc in self.spacy.pipeline:
            if name in self.disable:
                continue
            if not hasattr(proc, "__call__"):
                raise ValueError(name, "is wrong")
            # print (name)
            
            doc = proc(doc, **component_cfg.get(name, {}))
            if doc is None:
                raise ValueError(name, "is wrong")
            # if name == 'rule_match':
            #     self.spacy.remove_pipe(name)

        return doc

    
    def reset_pipeline(self):
        # for name, proc in self.spacy.pipeline:
        #     if name in ['rule_match', 'phrase_match', 'entity_recognition']:
        #         print('remove name:', name)
        #         self.spacy.remove_pipe(name)
        for name in ['rule_match', 'phrase_match', 'entity_recognition', 'rule_segmenter', 'pos_correction', 'sentencizer', 'custom_tok_attributes']:
            if self.spacy.has_pipe(name):
                self.spacy.remove_pipe(name)



    def get_disable(self, enable):
        return NlpToolEnum.as_list() - set(enable)

    
    
    def test_function(self, text):
        tag_res = self.nlp(text, enable=['tagger'])
        self.nlp(tag_res['tagger'], enable = ['edit'])
        self.nlp(tag_res['tagger'], enable = ['parser'])
        self.nlp(tag_res['tagger'], enable = ['ner'])