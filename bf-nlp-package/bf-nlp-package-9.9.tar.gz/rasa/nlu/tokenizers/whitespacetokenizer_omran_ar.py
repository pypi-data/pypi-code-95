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
from custom_func.remove_stop_words import is_stop_words_ar
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.tokenizers.tokenizer_fr import Token, Tokenizer
from rasa.nlu.training_data import Message, TrainingData
from custom_func.translator_darijaFr_DarijaAr import trans 
#from custom_func.generator import generateur_Ar
from custom_func.generator_omran import generateur_omran
from rasa.nlu.training_data import Message


from rasa.nlu.constants import (
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    TEXT,
    INTENT,
)

class WhitespaceTokenizer_omran_ar(Tokenizer):

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

        lettre="abcdefghijklmnopqrstuvwxyzABSCDEFGHIJKLMNOPQRSTUVWXYZ"
        nbre = "123546879"
        arabe="البتثحخدذرزسشصضطظعغفقكمنهويءإأٱآةؤئى"
        print("heeeeeeeeeeeere")
        txt = message.text
        txt.lower()
        print(txt)
        nb = 0
        for i in txt:
            print(i+"process")
            if i in arabe:
               
                tokens = self.tokenize_arab(message, TEXT)
                nb = 1
                break
            elif i in nbre :
                continue
            else :
                tokens = self.tokenize_dr(message, TEXT)
                nb =1 
                break
        if nb == 0 :
            tokens = self.tokenize_arab(message, TEXT)
        
        tokens = self.add_cls_token(tokens, TEXT)
        message.set(TOKENS_NAMES[TEXT], tokens)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        generateur_omran('data/omran')
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
        tokens = []
        running_offset = 0
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        stop_words = ['اذا','علا','كان','شهي','هل','من','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','اين','عن','ف','الا']
        for word in words:
            
            if word in stop_words:
                continue
            
            elif word.isdigit():
                continue
            else :
                word_offset = text.index(word, running_offset)
                word_len = len(word)
                running_offset = word_offset + word_len
                tokens.append(Token(word, word_offset))

        return tokens


    def tokenize_dr(self, message: Message, attribute: Text ) -> List[Token]:
        text = message.get(attribute)
        print("innnnnnnnnnnnnnnnnnnnnnnnnnnn")
        if not self.case_sensitive:
            text = text.lower()
        toks = ''
        toks = text.split()
        numbs = []
        numb = []

        print(toks)
        for t in toks:
            w=re.search(r'((([0-9]+).(dh|m|m²|m2|million|درهم|مليون|mlyoun|م)))', t)
            if w != None :
                numbs.append(w.group())
                print(w.group()+"wgroup")
        print("ok1")
        exp = ['m²','m','m2','dh','dhs','million','millions','درهم','مليون','م2','م','ألف'] 
        for word in toks:
            if word in exp :
                print("im here1")
                if toks[toks.index(word)-1].isdigit():
                    print("im here2")
                    numbs.append(word)
                    numbs.append(toks[toks.index(word)-1])
        print("ok2")
        mot = '' 
        #print("********************text1************************"+ text)
        for S in text.split():
            if S.isdigit():
                numb.append(S)
                print("number")
        print("ok3")
        stop_word_drj =["bghit",'n3raf','n3ref','f','li','chi','lia','bghi','xhi','n9dr','wach','chnu','kayn','ana','ntouma',"nta"]
        
        #print("nuumber*************************"+ numb)
        text = trans(text)
        print("ok4")
        print("texttranslateld******************"+ text)
        for i in range(0,len(numb)):

            text = text+" "+ str(numb[i]) + " " 
        
        for i in range(0,len(numbs)):

            text = text+" "+ str(numbs[i]) + " " 
        
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
        print("zyw")
        with open("dictionaries/dict_omran_ar.txt", 'r',encoding="utf8") as f:
             list = set(chain(*(line.split() for line in f if line)))
        #words =[]
        dicto = {}
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        
        tokens = []
        running_offset = 0
        texte = ''
        words_corr = []
        word_cor = ''
        print("aaaaaaaaaaaay")
        stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']
        for word in words :
            if word in stop_words :
                words.remove(word)
        print(words)
        for word in words:
            
            stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']                                   
            if word.isnumeric() :
                min_dist = word 
                print("number")
            
            else :
                for mot in list:
                    
                    dicto[mot]=jellyfish.levenshtein_distance(mot, word)
                min_dist = min(dicto.keys(), key=(lambda k: dicto[k]))
            
            if min_dist != '':
                if jellyfish.levenshtein_distance(min_dist, word) > 2:
                   min_dist = word
            
            print("min_dist")
            print(min_dist)
            if min_dist == '' :
                print("stopword2")
                word_cor = 'hjfhjqf'
            else :
                word_cor = min_dist
                print("mindiiiist"+min_dist)


            


            words_corr.append(word_cor)
            #print(words_corr+"word_corr")
            texte = texte +" "+word_cor
            print(texte +"text")
        print(texte)
        print(words_corr)
        if words_corr == []:
            words_corr.append('hjfhjqf')
            texte = texte + "hjfhjqf"
        
        #texte = texte + " " + numb  
        #words_corr.append(numb)
        print("**************** wooords in the text *************")
        #print(words_corr)

        for word in words_corr :
            

            print("word_corr_darija"+word)
            word_offset = texte.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))
            print("susbstrung ok")
        
        return tokens

    

    
    def tokenize_arab(self,  message: Message, attribute: Text ) -> List[Token]:
        text = message.get(attribute)
    
        if not self.case_sensitive:
            text = text.lower()
        print("arabe")
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
        stop_words = ['اذا','كان','خويا','ا','ليكوم','مومكن','شهي','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س']
        with open("dictionaries/dict_omran_ar.txt", 'r',encoding="utf8") as f:
             list = set(chain(*(line.split() for line in f if line)))
        
        dicto = {}
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        print
        tokens = []
        running_offset = 0
        texte = ''
        words_corr = []
        word_cor = ''
        stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']
        for word in words :
            if word in stop_words :
                words.remove(word)
        print(words)
        for word in words:
            
            stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']                                   
            if word.isnumeric() :
                min_dist = word 
                print("number")
            
            else :
                for mot in list:
                    
                    dicto[mot]=jellyfish.levenshtein_distance(mot, word)
                min_dist = min(dicto.keys(), key=(lambda k: dicto[k]))
            
            if min_dist != '':
                if jellyfish.levenshtein_distance(min_dist, word) > 2:
                   min_dist = word
            
            print("min_dist")
            print(min_dist)
            if min_dist == '' :
                print("stopword2")
                word_cor = 'hjfhjqf'
            else :
                word_cor = min_dist
                print("mindiiiist"+min_dist)


            


            words_corr.append(word_cor)
            #print(words_corr+"word_corr")
            texte = texte +" "+word_cor
            print(texte +"text")
        print(texte)
        print(words_corr)
        if words_corr == []:
            words_corr.append('hjfhjqf')
            texte = texte + "hjfhjqf"
        
        #texte = texte + " " + numb  
        #words_corr.append(numb)
        print("**************** wooords in the text *************")
        #print(words_corr)

        for word in words_corr :
            

            print("word_corr_darija"+word)
            word_offset = texte.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))
            print("susbstrung ok")
        
        return tokens
