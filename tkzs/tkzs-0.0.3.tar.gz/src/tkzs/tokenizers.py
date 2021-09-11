import spacy
import re
import string

class SpacyTokenizer(object):
    
    def __init__(self, name='en_core_web_sm'):
        
        self.spacy_model = spacy.load(name=name, disable=['parser', 'ner'])
        
    def tokenize(self, sent, lowercase=True):
        
        if lowercase:
            sent = sent.lower()

        return [s.text for s in self.spacy_model(sent)]

def re_tokenizer(txt, lowercase=True):
    """simple tokenization function based on regex

    Args:
        txt (str): string sequence

    Returns:
        list[str]: list of tokens
    """
    t = txt.strip()

    if lowercase:
        t = t.lower()

    t = re.sub(r'([%s])' % re.escape(string.punctuation), r' \1 ', t) 
    t = re.sub(r'\\.', r' ', t) 
    t = re.sub(r'\s+', r' ', t)
    return t.split()