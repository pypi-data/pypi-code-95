import re
from typing import Any, Dict, List, Text ,Optional
from rasa.nlu.config import RasaNLUModelConfig
import pyarabic.araby as araby
import json
from itertools import chain
import jellyfish  #correctionPackage"
import unicodedata
from pyarabic.unshape import unshaping_line
import arabic_reshaper
from itertools import *
from rasa.nlu.components import Component
from custom_func.remove_stop_words import is_stop_words_fr
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.tokenizers.tokenizer_fr import Token, Tokenizer
from rasa.nlu.training_data import Message, TrainingData
from custom_func.generateur_oncf_fr import generateur_oncf_fr
from rasa.nlu.training_data import Message


from rasa.nlu.constants import (
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    TEXT,
    INTENT,
)

class WhitespaceTokenizer_oncf_fr(Tokenizer):

    defaults = {
        # Flag to check whether to split intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Text will be tokenized with case sensitive as default
        "case_sensitive": True,
    }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        self.case_sensitive = self.component_config["case_sensitive"]
    
    def process(self, message: Message, **kwargs: Any) -> None:
        """Tokenize the incoming message."""

        
        txt = message.text
        
        tokens = self.tokenize_pr(message, TEXT)
            
        tokens = self.add_cls_token(tokens, TEXT)
        message.set(TOKENS_NAMES[TEXT], tokens)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        generateur_oncf_fr('data_oncf_fr',)
        """Tokenize all training data."""

        for example in training_data.training_examples:
            for attribute in MESSAGE_ATTRIBUTES:
                if example.get(attribute) is not None:
                    if attribute == INTENT:
                        tokens = self._split_intent(example)
                    else:
                        tokens = self.tokenize(example, attribute)
                        tokens = self.add_cls_token(tokens, attribute)
                    example.set(TOKENS_NAMES[attribute], tokens)

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        
        text = text.lower()
        #new_text = ''
        
        #punct='''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        '''for t in text :
            if t not in punct :
                
                new_text = new_text  +  t
            else :
                new_text = new_text + " "
        print(new_text)
        print("new text")
        text = new_text
        '''
        # remove 'not a word character' if
        words = re.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        ).split()
        words2 =[]
        stop_words = ["a",'à','veux','dois','vos','serais','serai','vous','pour','c','voulais','avec','l','d','les','en','j','ai','des','les','quelles','sont','quels','du','que','ce','est','je','un','une','le','la','avec','sur','moi','avec','des','stp','plait','les','tu','puis','oh','la','lol']

        '''for word in words :
            if is_stop_words_fr(word) == 0:
                words2.append(word)
                print("appended")
            else :
                print('stop word')
        print(words2)'''
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        if not words:
            words = [text]
        print("ok")

        return self._convert_words_to_tokens(words, text)


    def tokenize_pr(self, message: Message, attribute: Text ) -> List[Token]:
        text = message.get(attribute)
        print(text)
        
        text = text.lower()
        
        stop_words = ['le','a','à','veux','dois','vos','serais','serai','vous','pour','c','voulais','avec','l','les','en','j','ai','des','les','quelles','sont','quels','du','que','ce','est','je','un','une','le','la','avec','sur','moi','avec','des','stp','plait','les','tu','puis','oh','la','lol','souhaite','connaitre','savoir','si','les','des',"le"]

        toks = ''
        toks = text.split()
        print(toks)
        numbs = []
        numb = []
        print(stop_words)
        print(toks)
        
        
        
        mot = ''
        print("********************text1************************"+ text)
        for S in text.split():
            hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',S)
            hours2 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',S)
            hours3 = re.search(r'(([0-9]+):([0-9]+))',S)
            if S.isdigit():
                numb.append(S)
            elif hours1 != None :
                print("date found")
                
            elif hours2 != None :
                print("date found")
                
            elif hours3 != None :
                print("date found")
                
#Remove punctuation !!

        print( text)
        new_text = ''
        punct='''!()-[]{};:",<>?@#$%^&*_~'''
        for t in text :
            if t not in punct :
                
                new_text = new_text  +  t
            else :
                new_text = new_text + " "
        print(new_text)
        print("new text")
        text = new_text

        words = re.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        ).split()
        print("zyw")
        with open("dictionaries/dict_oncf_fr.txt", 'r',encoding="utf8") as f:
            list = set(chain(*(line.split() for line in f if line)))
        
        dicto = {}
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        
        tokens = []
        running_offset = 0
        
        
        for word in words :
            
            if word in stop_words :
                print(word)
                print("stoooooooooooooooooooooooppppppppppppppp wooooooooooooooooooooooooord")
                words.remove(word)
                
        
        if words == []:
            words.append('hdjfhj')
            text = text + 'hdjfhj'
        print(words)
        print("words")
        for word in words:
            

            if word.isnumeric()  or hours1 != None or hours2 != None or hours3 != None :
                min_dist = word
            
            else :
                for mot in list:
                    dicto[mot]=jellyfish.levenshtein_distance(mot, word)
                min_dist = min(dicto.keys(), key=(lambda k: dicto[k]))
            if jellyfish.levenshtein_distance(min_dist, word) > 2:
                    min_dist = word 
            
            print("min"+min_dist) 
            
            
            word_corr = min_dist
            word_offset = text.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word_corr, word_offset))

        return tokens

    

    
   
