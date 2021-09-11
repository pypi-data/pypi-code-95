from pythainlp.tokenize import word_tokenize
def sentencescore(sentence,bdict):
    wlist = word_tokenize(sentence)
    score = 0
    res = {}
    for w in wlist:
        w = w.lower()
        try:
            res[w] = bdict[w]
            score = score + bdict[w]
        except:
            res[w] = 0
    senscore = score/len(wlist)
    res['sentencescore'] = senscore
    return res