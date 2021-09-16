# from nltk.stem.wordnet import WordNetLemmatizer
# from nltk.corpus import twitter_samples, stopwords
# from nltk.tag import pos_tag
# from nltk.tokenize import word_tokenize
# from nltk import FreqDist, classify, NaiveBayesClassifier
# import pickle
# import time
# import os
# import re, string, random
#
# def remove_noise(tweet_tokens, stop_words = ()):
#
#     cleaned_tokens = []
#
#     for token, tag in pos_tag(tweet_tokens):
#         token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
#                        '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
#         token = re.sub("(@[A-Za-z0-9_]+)","", token)
#
#         if tag.startswith("NN"):
#             pos = 'n'
#         elif tag.startswith('VB'):
#             pos = 'v'
#         else:
#             pos = 'a'
#
#         lemmatizer = WordNetLemmatizer()
#         token = lemmatizer.lemmatize(token, pos)
#
#         if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
#             cleaned_tokens.append(token.lower())
#     return cleaned_tokens
#
# def predict(text):
#     dirname = os.path.dirname(__file__)
#     filename = 'sentiment_analysis_classifier.sav'
#     loaded_model = pickle.load(open(dirname + '/sentiment_analysis_classifier.sav', 'rb'))
#
#     custom_tokens = remove_noise(word_tokenize(text))
#
#     result = loaded_model.classify(dict([token, True] for token in custom_tokens))
#     return result