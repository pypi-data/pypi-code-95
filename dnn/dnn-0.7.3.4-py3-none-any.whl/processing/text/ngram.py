import re
import string

class NGram:
    def __init__ (self, t):
        self.t = self.filter (t)

    rx_splt = re.compile (r'[\s%s]' % re.escape(r'!"#$%&\'()*+,:;<=>?@[\\]^`{|}~'))
    rx_alnum = re.compile(r'(?:^|\s)([0-9a-z]+)(?:$|\s)', re.I)
    rx_const = re.compile(r'__([^_]+)__', re.I)
    def filter (self, t):
        t = t.replace ('____', '')
        before = t
        while 1:
            t = self.rx_alnum.sub (r" __\1__ ", t, 1)
            if before == t:
                break
            before = t
        t = self.rx_const.sub (r'|__\1__|', t)
        return t

    def ngram (self, n = 2):
        sentance = []
        for phrase in self.make_phrases (n):
            if phrase.startswith (' __'):
                if n == 2:
                    sentance.append (phrase.strip ())
                continue

            for each in zip (*[phrase[i:] for i in range (n)]):
                each = list (each)
                if n == 2 and (each [0] == " " or each [-1] == " "):
                    continue
                if each [0] == " ":
                    each [0] = "<"
                elif each [-1] == " ":
                    each [-1] = ">"
                sentance.append ("".join (each))
        if sentance and n == 2 and not sentance [-1].endswith ('__'):
            return sentance [:-1]
        return sentance

    rx_punct = re.compile('[%s]' % re.escape(string.punctuation.replace ('_', '')))
    rx_space = re.compile(r'\s+')
    def preprocess (self, t, blank = " "):
        sentences = []
        for each in self.rx_punct.split (t):
            each = each.strip ()
            if not each:
                continue
            each = self.rx_space.sub (blank, each).strip ()
            sentences.append (' {} '.format (each))
        return sentences

    def make_phrases (self, n = 2):
        return self.preprocess (self.t)

    # public -----------------------------
    def analyze (self):
        return self.ngram (2) + self.ngram (3)


class NGramV2 (NGram):
    def make_phrases (self, n = 2):
        if n == 2:
            return self.preprocess (self.t, '')
        return self.preprocess (self.t)
