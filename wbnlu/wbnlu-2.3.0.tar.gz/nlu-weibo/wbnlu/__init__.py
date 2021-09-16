from wbnlu import wbnlp
from spacy.lang.zh import STOP_WORDS, DOMAIN_EXCLUSIONS
from wbnlu.uplevel.content_words import content_words as cw

nlu = wbnlp.WBNlu()

init = nlu.init

nlp = nlu.nlp

make_doc = nlu.make_doc

content_words = cw.Content_Words

test_function = nlu.test_function