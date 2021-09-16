caribedict = {
  "waz de scene": "How are you",
  "come nah boi": "I am being serious",
  "Father lawd": "Jesus help me", 
  "Skinnin yuh teet":"grinning",
  "Skinnin yuh teeth":"grinning",
  "Tabanca": "still holding feelings",
  "allyuh":"Everybody",
  "chupid": "stupid",
  "dotish": "stupid",
  "chupidee": "stupid",
  "tick":"thick",
  "crapo": "Frog",
  "trinbago": "Trinidad and Tobago",
  "dias":"that is",
  "lix" : "beating",
  "ent": "Is that not so?",
  "fed up": "tired",
  "preshah": "pressure",
  "ahse": "ass",
  "wajang":"roudy",
  "tief":"thief",
  "hush": "quiet",
  "whey":"where",
  "whey yuh say": "can you repeat?",
  "you an all":  "You too?",
  "you so": "people like you",
  "yuh makin joke":  "you can't be serious",
  "yuh look fuh dat": "it is your fault",
  "boldface": "ignorant",
  "bolface": "ignorant",
  "bacchanal":"confusion", 
  "liming": "hanging out",
  "hambug":"pester",
  "ting":"thing",
  "tanty":"aunty",
  "tantie":"aunty",
  "gyul": "girl",
  "gyal": "girl",
  "horn":"cheat",
  "Yo": "Hi",
  "Yoo": "Hi",
  "Yooo": "Hi",
  "dis":"this",
  "wah": "what",
  "meh": "me",
   "modda" : "mother",
  "fadda" : "father",
  "fada" : "father",
  "faddah": "father",
  "brodda": "brother",
  "broda": "brother",
  "dougla": "mixed race person",
  "backchat":"talks",
  "boi" : "boy",
  "yuh": "you",
  "dey" : "there",
  "Ah" : "I",
  "doh": "do not",
  "eh" : "not",
  "cah": "cannot",
  "fuh":"for",
  "dat": "that",
  "waz": "what is",
  "dah": "that",
  "nah": "no",
  "de": "the",
  "scene":"weather",
  "rel": "very",
  #"me":"my",
  "mi": "my",
  "ah": "I",
 
}

def trinidad_decode(sentence):
    sentence=sentence.lower()
    sentence = " " + sentence 

    for x in caribedict:
        if sentence.find(x):
            sentence=sentence.replace(x, caribedict[x])
    return sentence.strip()


def trinidad_decode_split(sentence):
    sentence= sentence.lower()


    for subs in sentence.split():
        if subs in caribedict: 	
            sentence = sentence.replace(subs, str(caribedict[subs.lower()]))
    return sentence