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
from custom_func.generateur_oncf_ar import generateur_oncf_ar
from custom_func.clean_data_ar import clean_data_ar
from rasa.nlu.constants import (
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    TEXT,
    INTENT,
)

class WhitespaceTokenizer_ecomm_info_ar(Tokenizer, Component):

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

        super(WhitespaceTokenizer_oncf_ar, self).__init__(component_config)

        self.case_sensitive = self.component_config["case_sensitive"]

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        generateur_oncf_ar('data_oncf_ar',)
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
        cleaned_text = clean_data(text)
        print(cleaned_text)
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
        stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']
        for word in words:
            
            word_offset = text.index(word, running_offset)
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
        hours1 = re.search(r'(([0-9]+)+(h|heure|heures))',s)
        hours2 = re.search(r'(([0-9]+)+(h|heure|heures)).([0-9]+)',s)
        hours3 = re.search(r'(([0-9]+):([0-9]+))',s)
        
        for s in text.split(" "):
            print(s)
            dates = re.search(r'(\d{1,2}([.\-/])\d{1,2})',s)
            
            if s.isdigit():
                new_text = new_text + ' ' + s
                print('numeric'+new_text)
            
            elif dates != None :
                print("date found")
                new_text = new_text + ' ' + s
            elif hours1 != None :
                print("date found")
                new_text = new_text + ' ' + s
            elif hours2 != None :
                print("date found")
                new_text = new_text + ' ' + s
            elif hours3 != None :
                print("date found")
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
        with open("dictionaries/dict_oncf_ar.txt", 'r',encoding="utf8") as f:
            list1 = set(chain(*(line.split() for line in f if line)))
        print(words)
        
        
        for word in words:
            
            stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']                                   
            if word.isnumeric() or hours1 != None or hours2 != None or hours3 != None or dates != None:
                min_dist = word 
                print("number")
            
            else :
                for mot in list1:
                    
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

    def tokenize_arab(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        if not self.case_sensitive:
            text = text.lower()
        print("arabiiiiiiiiiiiiiic")
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
        numb = ""
        date1 = ""
        date2 = ""
        hour = ""
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
        with open("dictionaries/dict_oncf_ar.txt", 'r',encoding="utf8") as f:
             list1 = set(chain(*(line.split() for line in f if line)))
        dicto= {}
        for s in text.split():
            if s.isnumeric():
                numb = s
                print("pass")
                date1 = re.search(r'(\d{1,2}([/])\d{1,2}([/])\d{1,4})',s)
                print("pass2")
                if date1 == None :
                    print("no date")
                else :
                    date2 = date1.string
                hours = re.search(r'([0-9]+(h))',s) 
                if hours == None :
                    print("")
                else :
                    hour = hours.string
        print("pass")
        text = text +" "+ date2 + "  " + numb + " " + hour
        print("pass")
        stop_words = ["ال",'الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']
        for word in words :
            if word in stop_words :
                words.remove(word)
        print(words)
        if words == []:
            words.append("hjfhjqf")
            text = text + "hjfhjqf"
        for word in words:
            if word.isnumeric() :
                min_dist = word
            
            else :
                for mot in list1:
                    dicto[mot]=jellyfish.levenshtein_distance(mot, word)
                min_dist = min(dicto.keys(), key=(lambda k: dicto[k]))
            
            if min_dist != '':
                if jellyfish.levenshtein_distance(min_dist, word) > 2:
                   min_dist = word
                
            
            
            print("min_dist")
            print(min_dist)
            if min_dist == '' :
                print("stopword2")
                word_corr = 'hjfhjqf'
            else :
                word_corr = min_dist
                print("mindiiiist"+min_dist)
            
            
            
            print("word_corr_arab"+word_corr)
            word_offset = text.index(word, running_offset)
            word_len = len(word)
            running_offset = word_offset + word_len
            tokens.append(Token(word_corr, word_offset))
        
        return tokens

    