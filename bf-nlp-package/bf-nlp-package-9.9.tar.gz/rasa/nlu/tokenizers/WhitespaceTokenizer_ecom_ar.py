import re
from typing import Any, Dict, List, Text,Optional
import pyarabic.araby as araby
import json
import time
from itertools import chain 
import datefinder 
import jellyfish  #correctionPackage"
import unicodedata 
from pyarabic.unshape import unshaping_line
import arabic_reshaper
from itertools import *
from dateutil.parser import parse
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.tokenizers.tokenizer_fr import Token, Tokenizer
from rasa.nlu.training_data import Message, TrainingData
from custom_func.translator_darijaFr_DarijaAr import trans
from custom_func.clean_data_ar import clean_data_ar 
from custom_func.clean_data_ar_training import clean_data_ar_training
from custom_func.generateur_ecom_ar import generateur_ecom_ar
from rasa.nlu.constants import (
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    TEXT,
    INTENT,
)

class WhitespaceTokenizer_ecom_ar(Tokenizer, Component):

    provides = [TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]


    def unique_words(lines):
        return set(chain(*(line.split() for line in lines if line)))
    
    dict= {}

    
    defaults = {
        # text will be tokenized with case sensitive as default
        "case_sensitive": True,
        "token_pattern": None,
    }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super(WhitespaceTokenizer_ecom_ar, self).__init__(component_config)

        self.case_sensitive = self.component_config["case_sensitive"]

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        generateur_ecom_ar('data_ar',)
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

    def process(self, message: Message, **kwargs: Any) -> None:
        lettre="abcdefghijklmnopqrstuvwxyzABSCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
        nbre = "123546879"
        arabe="ابتثحخدذجرزسشصضطظعغفقكمنهويءإأٱآةؤئىل"
        txt = message.text
        texte = txt.split(" ")
         
        print("in process")
        print(texte)
 
        tokens =[]
        for i in texte:
            print(i+"process")
            numb = -1
            if i.isdigit() :
                print("number in process ====== next")
                numb = 0
                continue
            else :
                print("no fucking number")
                for l in i :
                    if l in arabe :
                        print("arabic letter ===== break")
                        tokens = self.tokenize_arab(message, TEXT)
                        numb = 1
                        break
                    elif l== "\u200f" :
                        print('spaaace')
                        continue
                    else :
                        print('darija letter === break')
                        tokens = self.tokenize_dr(message, TEXT)
                        numb = 1
                        break
            break
        if numb == 0 :
            tokens = self.tokenize_arab(message, TEXT)
            print("arab")
        
        tokens = self.add_cls_token(tokens, TEXT)
        message.set(TOKENS_NAMES[TEXT], tokens)
                     

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        
        text = text.lower()
        #Remove punctuation !!

        print( text)
        new_text = ''
        punct='''!()-[]{};:'"\,<>./?#$%^&*_~'''
        for t in text :
            if t not in punct :
                
                new_text = new_text  +  t
            else :
                new_text = new_text + " "
        print(new_text)
        print("new text")
        text = new_text

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
        tokens = []
        running_offset = 0
        # if we removed everything like smiles `:)`, use the whole text as 1 token

        #Cleaning data
        with open("../dictionaries/dict_ecom_ar.txt", 'r',encoding="utf8") as f:
            list2 = set(chain(*(line.split() for line in f if line)))
        wordss = []
        words_2 = []
        wordss = clean_data_ar_training(list2,words)
        
        print("wordss")
        print(wordss)
        texte = ""
        
        if wordss == [] :
            wordss = [text]

        for word in wordss:
            
            
            words_2.append(word)
            texte = texte +" "+word
        print(texte +"texte")
        print(words_2)

        

        for word in words_2:
            
            word_offset = texte.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))

        return tokens


    def tokenize_dr(self, message: Message, attribute: Text ) -> List[Token]:
        text = message.get(attribute)
        
        text = text.lower()
        print("DARIJA")
        numb = ""
        date = ""
        hour = ""
        print(text)
        string = text
        
        
#replace indou arabic numbers
        if '۰' in string :
		        string = string.replace('۰','0')
        if '١' in string :
            string = string.replace('١','1')
        if '٢' in string :
            string = string.replace('٢','2')
        if '۳' in string :
            string = string.replace('۳','3')
        if '۴' in string :
            string = string.replace('۴','4')
        if '۵' in string :
            string = string.replace('۵','5')
        if '۶' in string :
            string = string.replace('۶','6')
        if '۷' in string :
            string = string.replace('۷','7')
        if '۸' in string :
            string = string.replace('۸','8')
        if '۹' in string :
            string = string.replace('۹','9')

        text = string

        #print("********************text1************************"+ text)

        for s in text.split(" "):
            if s.isnumeric():
                numb = s
            dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',s)
            if dates == None :
                print("")
            else : 
                date = dates.string
            
        new_text= ''
        
        print("text")
        
        for s in text.split(" "):
            print("s")
            print(s)
            dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',s)
            
            if s.isdigit():
                new_text = new_text + ' ' + s
                print('numeric'+new_text)
            
            elif dates != None :
                print("date found")
                print(dates)
                new_text = new_text + ' ' + s
            
            else : 
                new_text = new_text + ' ' + trans(s)
                print('it is text'+new_text)

        

        print(new_text+"texxxxxtttt")
         
        
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
            new_text,
        ).split()
        
        
        running_offset = 0
        tokens = []
        dicto={}
        texte = ''
        words_corr = []
        word_cor = ''
        #Dictionnaire pour correction
        with open("dictionaries_ecom/dict_ecom_ar.txt", 'r',encoding="utf8") as f:
            list1 = set(chain(*(line.split() for line in f if line)))
        #Cleaning DATA & Spell Checker
        print("Cleaning data")
        words2 = clean_data_ar(list1,words)
        print("words2")
        print(words2)
        
        for word in words2:
            
            word_cor = word
            words_corr.append(word_cor)
            texte = texte +" "+word_cor
        print(texte +"texte")
        print(words_corr)
        #Only stop words in the msg 
        if words_corr == []:
            words_corr.append('hjfhjqf')
            texte = texte + "hjfhjqf"
        
         
        
        print("**************** final msg *************")
        print(words_corr)

        for word in words_corr :
            word_offset = texte.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))
        print("End Tokenizer")
        
        return tokens

    def tokenize_arab(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        if not self.case_sensitive:
            text = text.lower()
        print("arabiiiiiiiiiiiiiic")
        #Remove punctuation !!

        print( text)
        new_text = ''
        
        text = new_text
        # remove 'not a word character' if
        numb = ""
        date1 = ""
        date2 = ""
        hour = ""
        words = new_text.split()
        #print(words)
        running_offset = 0
        tokens =[]
        with open("../dictionaries/dict_ecom_ar.txt", 'r',encoding="utf8") as f:
             list1 = set(chain(*(line.split() for line in f if line)))
        words2 = clean_data_ar(list1,words)
        words_corr =[]
        texte = ""
        for word in words2:
            
            word_cor = word
            words_corr.append(word_cor)
            texte = texte +" "+word_cor
        
        print(words_corr)
        #Only stop words in the msg 
        if words_corr == []:
            words_corr.append('hjfhjqf')
            texte = texte + "hjfhjqf"
        
        #text = texte + " " + numb  
        #words_corr.append(numb)
        print("**************** final msg *************")
        print(words_corr)

        for word in words_corr :
            word_offset = texte.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))
        print("Start training")
        
        return tokens
        