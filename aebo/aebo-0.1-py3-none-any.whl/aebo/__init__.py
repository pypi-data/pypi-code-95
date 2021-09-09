import nltk
import numpy as np
import random
import string



from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

lemmer = nltk.stem.WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# Generating response
def response(user_input, filename = "info.txt"):
    f = open(filename, 'r', errors='ignore')
    raw = f.read()
    raw = raw.lower()
    sent_tokens = nltk.sent_tokenize(raw)
    sent_tokens.append(user_input)
    
    robo_response=''
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        #robo_response=robo_response+"I am sorry! I don't understand you"
        #robo_response = robo_response + "Please train me on this"
        print("I am sorry! I don't understand you.Please train me on this")
        train_input = input("enter the information : ")
        f = open(filename, "a")
        f.write("\n")
        f.write(train_input+".")
        f.close()
        robo_response = robo_response+"Thanks for training me..I am ready now"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response
