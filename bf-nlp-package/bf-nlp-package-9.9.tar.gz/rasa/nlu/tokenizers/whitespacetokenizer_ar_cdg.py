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
from custom_func.generateur_cdg import generateur_cdg
from rasa.nlu.constants import (
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    TEXT,
    INTENT,
)

class WhitespaceTokenizer_ar_cdg(Tokenizer, Component):

    provides = [TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]


    def unique_words(lines):
        return set(chain(*(line.split() for line in lines if line)))
    
    dict= {}

    
    defaults = {
        # text will be tokenized with case sensitive as default
        "case_sensitive": True
    }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super(WhitespaceTokenizer_ar_cdg, self).__init__(component_config)

        self.case_sensitive = self.component_config["case_sensitive"]

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        generateur_cdg('data_cdg',)
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
        space = " "
        
        txt = message.text
        
        
        texte = txt.split(" ")
         
        print("in process")
        print(texte)
 
        
        for i in texte:
            print(i+"process")
            if i.isdigit() :

                print("number in process ====== next")
                numb = 0 
                continue
            else :
                print("no fucking number")
                for l in i :
                    if l in arabe :
                        print(l)
                        print("arabic letter ===== break")
                        tokens = self.tokenize_arab(message, TEXT)
                        numb = 1
                        break
                    elif l== "\u200f" :
                        print('spaaace')
                        continue

                    else :
                        print('darija letter === break')
                        print(l+"l")
                        print(l)
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
        stop_words = ['وك','نعرف','تاعي','عليها','واحد','علا','كان','شهي','هل','من','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','اين','عن','ف','الا','ديالي','ا']
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
        if not self.case_sensitive:
            text = text.lower()
        print("DARIJA")
        numb = ""
        date = ""
        hour = ""
        
        #print("********************text1************************"+ text)
        for s in text.split(" "):
            if s.isnumeric():
                numb = s
            dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',s)
            if dates == None :
                print("")
            else : 
                date = dates.string
            hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',s)
            
            if hours1 == None :
                hours1 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',s)
            if hours1 == None :
                hours1 = re.search(r'(([0-9]+):([0-9]+))',s)
            if hours1 == None:
                print('No heure in tokenizer')
            else :
                print('Heure detected in tokenizer')
                hour = hours1.string 
        new_text= ''
        print(text)
        dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',s)
        hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',s)
        hours2 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',s)
        hours3 = re.search(r'(([0-9]+):([0-9]+))',s)
        for w in text.split(" "):
            dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',w)
            hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',w)
            hours2 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',w)
            hours3 = re.search(r'(([0-9]+):([0-9]+))',w)
            print(w+"initial text")
            if w.isnumeric():
                print("s is numeric")
                new_text = new_text + ' ' + w
                print(new_text+"numeric text !!!!!")
            elif dates != None :
                    print("date found")
                    new_text = new_text + ' ' + w
            elif hours1 != None :
                    print("heure found")
                    new_text = new_text + ' ' + w
            elif hours2 != None :
                    print("heure found")
                    new_text = new_text + ' ' + w
            elif hours3 != None :
                    print("heure found")
                    new_text = new_text + ' ' + w
            else :
                print("translataration")
                print(w)
                print(new_text+"before translatioon !!!")
                print(trans(w))
                new_text = new_text + ' ' + trans(w)
                print(new_text+"final text translated")

        

        print(new_text+"texxxxxtttt")   
        
        
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
            new_text,
        ).split()
        
        running_offset = 0
        tokens = []
        dicto={}
        texte = ''
        words_corr = []
        word_cor = ''
        with open("dictionaries/dict_cdg.txt", 'r',encoding="utf8") as f:
            list1 = set(chain(*(line.split() for line in f if line)))
        print(words)
        for word in words:
            hours = re.search(r'(([0-9]+)+(h|heure|heures))',word)
            if word == 'و':
                word == ""
            stop_words = ['وك','نعرف','تاعي','عليها','واحد','علا','كان','شهي','هل','من','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','اين','عن','ف','الا','ديالي','ا']
            if word.isnumeric() or hours != None :

                min_dist = word  
                print("number")
            else :
                for mot in list1:
                    
                    dicto[mot]=jellyfish.levenshtein_distance(mot, word)
                min_dist = min(dicto.keys(), key=(lambda k: dicto[k]))
            
            if jellyfish.levenshtein_distance(min_dist, word) > 2:
                min_dist = word
                
            print(min_dist)
            if min_dist in stop_words :
                print("non")
            else :
                word_cor = min_dist
                print("mindiiiist"+min_dist)


            words_corr.append(word_cor)
            #print(words_corr+"word_corr")
            texte = texte +" "+word_cor
            print(texte +"text")
        print(texte)
        #print(words_corr)
        
        #texte = texte + " " + numb  
        #words_corr.append(numb)
        print("**************** wooords in the text *************")
        #print(words_corr)
        print(words_corr)

        for word in words_corr :
            

            print("word_corr_darija"+word)
            word_offset = texte.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))
            print("susbstrung ok")
        
        return tokens

    def tokenize_arab(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        if not self.case_sensitive:
            text = text.lower()
        print("arabiiiiiiiiiiiiiic")
        # remove 'not a word character' if
        numb = ""
        date1 = ""
        date2 = ""
        hour = ""
        word_cor = ''
        texte = ''
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
        #print(words) 
        running_offset = 0
        tokens = []
        with open("dictionaries/dict_cdg.txt", 'r',encoding="utf8") as f:
             list1 = set(chain(*(line.split() for line in f if line)))
        dicto= {}
        for s in text.split(" "):
            if s.isnumeric():
                numb = s
            dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',s)
            if dates == None :
                print("")
            else : 
                date = dates.string
            hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',s)
            
            if hours1 == None :
                hours1 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',s)
            if hours1 == None :
                hours1 = re.search(r'(([0-9]+):([0-9]+))',s)
            if hours1 == None:
                print('No heure in tokenizer')
            else :
                print('Heure detected in tokenizer')
                hour = hours1.string 
        new_text= ''
        print(text)
        
        for w in text.split(" "):
            dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',w)
            hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',w)
            hours2 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',w)
            hours3 = re.search(r'(([0-9]+):([0-9]+))',w)
            print(w+"initial text")
            if w.isnumeric():
                print("s is numeric")
                new_text = new_text + ' ' + w
                print(new_text+"numeric text !!!!!")
            elif dates != None :
                    print("date found")
                    new_text = new_text + ' ' + w
            elif hours1 != None :
                    print("heure found")
                    new_text = new_text + ' ' + w
            elif hours2 != None :
                    print("heure found")
                    new_text = new_text + ' ' + w
            elif hours3 != None :
                    print("heure found")
                    new_text = new_text + ' ' + w
            else :
                print(w)
                new_text = new_text + ' ' + w
                print(new_text+"final text")

        

        print(new_text+"texxxxxtttt")   
        
        
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
            new_text,
        ).split()
        
        running_offset = 0
        tokens = []
        dicto={}
        texte = ''
        words_corr = [] 
        word_cor = ''
        with open("dictionaries/dict_cdg.txt", 'r',encoding="utf8") as f:
            list1 = set(chain(*(line.split() for line in f if line)))
        print(words)
        for word in words:
            '''if word == 'و':
                word == "فهڢفجقهعفجهقف"
            
            print(word)'''
            stop_words = ['فهڢفجقهعفجهقف','جاو','وك','نعرف','تاعي','عليها','واحد','علا','كان','شهي','هل','من','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','اين','عن','ف','الا','ديالي','ا']
            if word.isnumeric() or word == " ":
                min_dist = word
                print("number")
            else :
                for mot in list1:
                    
                    dicto[mot]=jellyfish.levenshtein_distance(mot, word)
                min_dist = min(dicto.keys(), key=(lambda k: dicto[k]))
            
            
            if jellyfish.levenshtein_distance(min_dist, word) > 2:
                min_dist = word
                
            print(min_dist)
            if min_dist in stop_words :
                print("non")
            else :
                word_cor = min_dist
                print("mindiiiist"+min_dist)


            words_corr.append(word_cor)
            #print(words_corr+"word_corr")
            texte = texte +" "+word_cor
            print(texte +"text")
        print(texte)
        #print(words_corr)
        
        #texte = texte + " " + numb  
        #words_corr.append(numb)
        print("**************** wooords in the text *************")
        print(words_corr)

        for word in words_corr :
            

            print("word_corr_darija"+word)
            word_offset = texte.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word, word_offset))
            print("susbstrung ok")
        
        return tokens
        

    



