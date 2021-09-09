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
from custom_func.generateur_ecom_fr import generateur_ecom_fr
from custom_func.clean_data_fr import clean_data_fr
from custom_func.clean_data_fr_training import clean_data_fr_training
from rasa.nlu.training_data import Message



from rasa.nlu.constants import (
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    TEXT,
    INTENT,
)

class WhitespaceTokenizer_ecom_fr(Tokenizer,Component):

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
        generateur_ecom_fr('data_fr',)
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
        print("words")
        print(words)
        with open("dictionaries_ecom/dict_ecom_fr.txt", 'r',encoding="utf8") as f:
            list = set(chain(*(line.split() for line in f if line)))
        words2 = clean_data_fr_training(words)
        print("words2")
        print(words2)
        
        if words2 == []:
            words2 = [text]

        return self._convert_words_to_tokens(words2, text)


    def tokenize_pr(self, message: Message, attribute: Text ) -> List[Token]:
        text = message.get(attribute)
        print(text)
        
        text = text.lower()
        
        

        toks = ''
        toks = text.split()
        print(toks)
        numbs = []
        numb = []
        
        words2 =[]
        
        new_text = ''

        for S in text.split():
            hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',S)
            hours2 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',S)
            hours3 = re.search(r'(([0-9]+):([0-9]+))',S)
            money = re.search(r'(([0-9]+)+(dh|dhs|mad|euro|eu|€|$|usd))',S)
            
            if S.isdigit():
                numb.append(S)
            elif hours1 != None :
                print("date found")
                
            elif hours2 != None :
                print("date found")
                
            elif hours3 != None :
                print("date found")
            
            elif money != None :
                print("money found")

        for t in text :
            new_text = new_text  +  t
            
        print(new_text)
        print("new text")
        text = new_text

        
        words = re.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        ).split()
        print("zyw")
        
        with open("dictionaries_ecom/dict_ecom_fr.txt", 'r',encoding="utf8") as f:
            list = set(chain(*(line.split() for line in f if line)))
        print(words)
        print("dictionary done")
        words2 = clean_data_fr(list,words)
        print("cleaning data done")
        dicto = {}
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        
        tokens = []
        running_offset = 0
        
        
         
        
        if words2 == []:
            words.append('hdjfhj')
            text = text + 'hdjfhj'
        print(words2)
        print("words2")
        
        new_text = ""
        for w in words2 :
            new_text = new_text  +  w


        for word in words2:

            word_corr = word
            word_offset = new_text.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word_corr, word_offset))

        return tokens

    

    
   
