import re
from typing import Any, Dict, List, Text, Optional
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.components import Component
from rasa.nlu.tokenizers.tokenizer_fr import Token, Tokenizer
from rasa.nlu.training_data import TrainingData, Message
from itertools import *
from custom_func.generateur_fr import generateur_fr
from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES, TEXT,INTENT
import jellyfish


class WhitespaceTokenizer(Tokenizer):
    
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

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        
        text = text.lower()
        
        numb = []

        toks = ''
        toks = text.split()
        numbs = []
        
        
        stop_words = ["a",'à','veux','dois','vos','serais','serai','vous','pour','c','voulais','avec','l','d','les','en','j','ai','des','les','quelles','sont','quels','du','que','ce','est','je','un','une','le','la','avec','sur','moi','avec','des','stp','plait','les','tu','puis','oh','la','lol']


        for s in toks:
            if s.isdigit():
               numb.append(s)
        
        for i in range(0,len(numb)):

            text = text+" "+ str(numb[i]) + " " 
        
        for i in range(0,len(numbs)):

            text = text+" "+ str(numbs[i]) + " " 
        
        # remove 'not a word character' if
        print(text)

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
        with open("dictionaries/dict_chrono_fr.txt", 'r',encoding="utf8") as f:
            list = set(chain(*(line.split() for line in f if line)))
        

        dicto = {}
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        #words2 = []
        
        tokens = []
        running_offset = 0
        for word in words :
            if word in stop_words :
                words.remove(word)
        
        if words == []:
            words.append('hdjfhj')
            text = text + 'hdjfhj'
        print(words)
        print("words")
        w=re.search(r'((([\d|\d\.\d]+)+(kg|kgs|g|kilo|كيلو|كلغ|كغ|غ|ج|غرام)))', word)
        for word in words:
            print(word)
            print("ok1")
            if word.isnumeric()   :
                min_dist = word
                print("ok2")
            else :
                print("ok3")
                if w != None :
                    print("yes weight")
                    min_dist = w.group()
                else:
                    print("ok4")
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
    def tokenize_tr(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        stop_words = ['veux','je','sont','qui','toujours','souhaiterais','souhaite','qu','et','ceci','cela','si','pouvez','tout','faites','avant','vous','sur','dans','peut','peux','votre','c','quoi','t','pouvez','pour','me','veuillez','s','d','ca','cette','ce','est','il','a','plus','est-il','avoir','etre','que','qui','si','veux','en','j','ai','des','les','quelles','sont','quels','du','que','ce','est','je','un','une','le','la','de','avec','sur','moi','avec','des','stp','plait','les','tu','puis','svp','par','aux','et','voudrais','souhaite','souhaiterai','me','d','puis','m','avant']
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
        words2 =[]
        

        for word in words :
            if word not in stop_words:
                words2.append(word)
                print("appended")
            else :
                print('stop word')
        print(words2)
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        
        print("ok")
        
        
        tokens = []
        running_offset = 0
        for word in words2:
            word_offset = text.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))

        return tokens
    
    def process(self, message: Message, **kwargs: Any) -> None:
        """Tokenize the incoming message."""
        tokens = self.tokenize(message, TEXT)
        tokens = self.add_cls_token(tokens, TEXT)
        message.set(TOKENS_NAMES[TEXT], tokens)
    
    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        generateur_fr('data_chrono_fr')
        """Tokenize all training data."""

        for example in training_data.training_examples:
            for attribute in MESSAGE_ATTRIBUTES:
                if example.get(attribute) is not None:
                    if attribute == INTENT:
                        tokens = self._split_intent(example)
                    else:
                        tokens = self.tokenize_tr(example, attribute)
                        tokens = self.add_cls_token(tokens, attribute)
                    example.set(TOKENS_NAMES[attribute], tokens)
