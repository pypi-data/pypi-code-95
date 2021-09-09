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
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.tokenizers.tokenizer_fr import Token, Tokenizer
from rasa.nlu.training_data import Message, TrainingData
from custom_func.translator_darijaFr_DarijaAr import trans 
#from custom_func.generator import generateur_Ar
from custom_func.generateur_omran_fr import generateur_omran_fr
from custom_func.generator_fr_omr import generateur_fr_omr
from rasa.nlu.training_data import Message


from rasa.nlu.constants import (
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    TEXT,
    INTENT,
)

class WhitespaceTokenizer_omr_fr(Tokenizer):

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

        print("heeeeeeeeeeeere")
        txt = message.text
        
        tokens = self.tokenize_fr(message, TEXT)
            
        tokens = self.add_cls_token(tokens, TEXT)
        message.set(TOKENS_NAMES[TEXT], tokens)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        generateur_fr_omr('data_az_fr/omran_dad',)
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
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        if not words:
            words = [text]
        print("ok")

        return self._convert_words_to_tokens(words, text)


    def tokenize_fr(self, message: Message, attribute: Text ) -> List[Token]:
        text = message.get(attribute)
        print(text)
        if not self.case_sensitive:
            text = text.lower()
        
        # remove 'not a word character' if
        print(text)

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
        print("into the tokenizer")
        with open("dictionaries/dictionnaire_omran_fr.txt", 'r',encoding="utf8") as f:
            list = set(chain(*(line.split() for line in f if line)))
        #words =[]
        dicto = {}
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        
        tokens = []
        running_offset = 0
        print("aaaaaaaaaaaay ",text)
        stop_words = ['je','un','une','le','la','vos','d','avec','vous','sur','moi','à','stp','plait','les','tu','toi','tes','il','elle','votre','notre','encore']
        for word in words:
            if word.isnumeric() :
                min_dist = word
            else :
                for mot in list:
                    dicto[mot]=jellyfish.levenshtein_distance(mot, word)
                min_dist = min(dicto.keys(), key=(lambda k: dicto[k]))
            if jellyfish.levenshtein_distance(min_dist, word) > 2:
                min_dist = word 
            
            print("min dist  " +min_dist) 
            if min_dist in stop_words:
                print("stop word")
            else :
                word_corr = min_dist
                word_offset = text.index(word, running_offset)
                word_len = len(word)
                running_offset = word_offset + word_len
                tokens.append(Token(word_corr, word_offset))

        return tokens

    

    
   
