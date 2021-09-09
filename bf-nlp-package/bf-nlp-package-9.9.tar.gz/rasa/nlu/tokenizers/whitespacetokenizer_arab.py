import re
from typing import Any, Dict, List, Text

from rasa.nlu.tokenizers.tokenizer_fr import Token, Tokenizer
from rasa.nlu.training_data import TrainingData, Message
from typing import Text, List, Optional, Dict, Any
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES, TEXT,INTENT
from custom_func.translator_darijaFr_DarijaAr import trans 
from custom_func.generator import generateur_Ar
from itertools import chain
import jellyfish  #correctionPackage"
import unicodedata
from pyarabic.unshape import unshaping_line
import arabic_reshaper
from custom_func.translator_darijaFr_DarijaAr import trans 
from custom_func.generateur_ar import generateur_chrono_ar
import pyarabic.araby as araby
import arabic_reshaper
from itertools import *



class WhitespaceTokenizer_arab(Tokenizer):

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
    
    

    def tokenize_tr_dr(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        if not self.case_sensitive:
            text = text.lower()

        # remove 'not a word character' if
        text2 = ""
        toks = ''
        toks = text.split()
        for t in toks :
            if t.isdigit():
                text2 = text2 + " " + t
            else :
                text2 = text2 + " " + trans(t)
        print("////////////////////////////////text"+text2)
        
        words = re.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w_~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text2,
        ).split()
        
        print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        
        print("****************************************************************************")
        print(words)
        print("****************************************************************************")
        
        
        
        tokens = []
        running_offset = 0
        
        stop_words = ['واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س']
        for word in words:
            if word in stop_words:
                continue
            else :

                word_offset = text2.index(word, running_offset)
                word_len = len(word)
                running_offset = word_offset + word_len
                tokens.append(Token(word, word_offset))


        return tokens

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        if not self.case_sensitive:
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
            r"(?<=[^0-9\s])[^\w_~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        ).split()
        
        print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        
        print("****************************************************************************")
        print(words)
        print("****************************************************************************")
        
        
        
        tokens = []
        running_offset = 0
        
        #stop_words = ['واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س']
        for word in words:
            
                word_offset = text.index(word, running_offset)
                word_len = len(word)
                running_offset = word_offset + word_len
                tokens.append(Token(word, word_offset))


        return tokens
        
    def process(self, message: Message, **kwargs: Any) -> None:
        """Tokenize the incoming message."""

        lettre="abcdefghijklmnopqrstuvwxyzABSCDEFGHIJKLMNOPQRSTUVWXYZ"
        nbre = "123546879"
        arabe="ابتثحخدذرزسشصضطظعغفقكمنهويءإأٱآةؤئىل"
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
        generateur_chrono_ar('data_chrono_ar')
        """Tokenize all training data."""

        for example in training_data.training_examples:
            for attribute in MESSAGE_ATTRIBUTES:
                if example.get(attribute) is not None:
                    if attribute == INTENT:
                        tokens = self._split_intent(example)
                    else:
                        lettre="abcdefghijklmnopqrstuvwxyzABSCDEFGHIJKLMNOPQRSTUVWXYZ"
                        nbre = "1235468790"
                        arabe="ابتثحخدذرزسشصضطظعغفقكمنهلويءإأٱآةؤئى"
                        ar = 0
                        for i in example.get(attribute) :
                            if i in arabe :
                                ar = 1
                                print("break")
                                break
                                
                            else :
                                if i in nbre :
                                    print("continue")
                                    continue
                                else :
                                    ar = 0
                                    print("break")
                                    break
                                
                        if ar == 0 :
                            tokens = self.tokenize_tr_dr(example, attribute)
                            tokens = self.add_cls_token(tokens, attribute)
                        else :
                            tokens = self.tokenize(example, attribute)
                            tokens = self.add_cls_token(tokens, attribute)
                        
                    example.set(TOKENS_NAMES[attribute], tokens)


    
    def tokenize_dr(self, message: Message, attribute: Text ) -> List[Token]:
        print("darijaaaaaaaaaa")
        text = message.get(attribute)

        
        text = text.lower()
        numb = []

        toks = ''
        toks = text.split()
        print("tokssssssssssssssssss")
        numbs = []
        for t in toks:
            
            w=re.search(r'((([\d|\d\.\d]+)+(kg|kgs|g|kilo|كيلو|كلغ|كغ|غ|ج|غرام)))', t)
            if w != None :
                numbs.append(w.group())
                
                print(w[0])
                print('group+++++++++++++++++++++')
             
        
        exp = ['kg','kgs','g','kilo','kilos']
        for word in toks:
            if word in exp :
                print("im here1")
                if toks[toks.index(word)-1].isdigit():
                    print("im here2")
                    numbs.append(word)
                    numbs.append(toks[toks.index(word)-1])


        for s in toks:
            if s.isdigit():
               numb.append(s)
        
        text = trans(text)
        # print(numb)
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
            r"(?<=[^0-9\s])[^\w_~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        ).split()
        
        print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        with open("dictionaries/dict_chrono_ar2.txt", 'r',encoding="utf8") as f:
            list = set(chain(*(line.split() for line in f if line)))
        print("****************************************************************************")
        print(words)
        print("****************************************************************************")
        dicto = {}
        # if we removed everything like smiles `:)`, use the whole text as 1 token
        #words2 = []
        
        tokens = []
        running_offset = 0
        texte = ''
        words_corr = []
        word_cor = ''
        print("////////////////////////////////////////////////////////")
        
        stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']
        for word in words :
            if word in stop_words :
                words.remove(word)
        print(words)
        w=re.search(r'((([\d|\d\.\d]+)+(kg|kgs|g|kilo|كيلو|كلغ|كغ|غ|ج|غرام)))', word)
        for word in words:
            
            
            stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']                                   
            if word.isnumeric():
                min_dist = word 
                print("number")
            
            else: 
                if w != None :
                    print("yes weight")
                    min_dist = w.group()
                else:
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
   
    

    def tokenize_arab(self, message: Message, attribute: Text ) -> List[Token]:
        text = message.get(attribute)
        text.lower()

        print("araaaaaaaaaaaabe")
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
        with open("dictionaries/dict_chrono_ar2.txt", 'r',encoding="utf8") as f:
            list = set(chain(*(line.split() for line in f if line)))
        

        dicto = {}
        
        
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
        w=re.search(r'((([\d|\d\.\d]+)+(kg|kgs|g|kilo|كيلو|كلغ|كغ|غ|ج|غرام)))', word)
        for word in words:
            
            
            stop_words = ['ال','الله','ي','علا','كان','شهي','هل','باغي','و','ف','واحد','ن','لس','ف','هاد','نسولك','عافاك','ممكن','مومكين','في','ف','شي','تقدر','بغيت', 'بغهيت','ديال','ديالكم','واش','ل','نقدر','لس','لك','لو','س','في','لديكم','ف','الا','ديالي','ا','ل','كاين','ولا','يلا']                                   
            if word.isnumeric():
                min_dist = word 
                print("number")
            
            else: 
                if w != None :
                    print("yes weight")
                    min_dist = w.group()
                else:
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