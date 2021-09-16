import spacy
from spacy.gold import biluo_tags_from_offsets


TRAIN_DATA = [
    ("谁是毛泽东？", {"entities": [(2, 6, "PERSON")]}),
    ("他是毛泽东？", {"entities": [(2, 5, "PERSON")]}),
    ("他是习近平？", {"entities": [(2, 5, "PERSON")]}),
    ("他是习近平吗？", {"entities": [(2, 5, "PERSON")]}),
    ("他不是毛泽东？", {"entities": [(3, 6, "PERSON")]}),
    ("他是不是毛泽东？", {"entities": [(4, 7, "PERSON")]}),
    ("他还是毛泽东？", {"entities": [(3, 6, "PERSON")]}),
    ("他是毛泽东吧？", {"entities": [(2, 5, "PERSON")]}),
    ("我喜欢北京和武汉", {"entities": [(3, 5, "LOC"), (6, 8, "LOC")]}),
    ("我喜欢北京和天津的食物", {"entities": [(3, 5, "LOC"), (6, 8, "LOC")]}),
    ("我喜欢北京和武汉吧", {"entities": [(3, 5, "LOC"), (6, 8, "LOC")]}),
    ("我喜欢北京", {"entities": [(3, 5, "LOC")]}),
]

nlp = spacy.blank("zh")

for text, annot in TRAIN_DATA:
    doc = nlp.make_doc(text)
    biluo = biluo_tags_from_offsets(doc, annot["entities"])
    print([t.text for t in doc], biluo)