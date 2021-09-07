import os
import re
import string
from typing import Dict

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.feature_extraction.text import CountVectorizer

from nlon_py.data.make_data import loadStopWords

pwd_path = os.path.abspath(os.path.dirname(__file__))
vecfile = os.path.join(pwd_path, 'data/default_vectorizer.joblib')

stop_words_list = loadStopWords()


def preprocess(text, tokenizer=None):
    vectorizer = CountVectorizer(tokenizer=tokenizer)
    analyze = vectorizer.build_analyzer()
    result = []
    for x in text:
        result.extend(analyze(x))
    return result


trigram_vectorizer = CountVectorizer(ngram_range=(
    3, 3), stop_words=preprocess(stop_words_list))
default_preproc = trigram_vectorizer.build_preprocessor()


def preproc(s):
    return re.sub(r'[0-9]', '0', re.sub(r'\\032', '', default_preproc(s)))


trigram_vectorizer.preprocessor = preproc


def Character3Grams(text):
    data = pd.DataFrame.sparse.from_spmatrix(
        trigram_vectorizer.fit_transform(text))
    dump(trigram_vectorizer, vecfile, compress='zlib')
    return data


def Character3GramsForTest(text):
    vectorizer = load(vecfile)
    return pd.DataFrame.sparse.from_spmatrix(vectorizer.transform(text))


class Features:
    def __init__(self):
        self.charCount = lambda x: len(x)
        self.wordCount = lambda x: len(x.split())
        self.stopWords = lambda x, y: len([word for word in preprocess(
            x, tokenizer=y) if word in preprocess(stop_words_list)])
        self.Tokenize1 = lambda x: x.split()
        self.Tokenize2 = None

    def CapsRatio(self, text):
        return len([c for c in text if c.isupper()]) / self.charCount(text)

    def SpecialCharsRatio(self, text):
        return len([c for c in text if c in string.punctuation]) / self.charCount(text)

    def NumbersRatio(self, text):
        return len([c for c in text if c.isnumeric()]) / self.charCount(text)

    def AverageWordLength(self, text):
        return self.charCount(text) / self.wordCount(text)

    def StopwordsRatio1(self, text):
        return self.stopWords(text, self.Tokenize1) / self.wordCount(text)

    def StopwordsRatio2(self, text):
        return self.stopWords(text, self.Tokenize2) / self.wordCount(text)

    def LastCharCode(self, text):
        return 1 if (text.endswith((')', '{', ';')) and not(text.endswith((':-)', ';-)', ':)', ';)', ':-(', ':(')))) else 0

    def LastCharNL(self, text):
        return 1 if text.endswith(('.', '!', '?', ':', ',')) else 0

    def First3CharsLetter(self, text):
        return len([c for c in text.replace(' ', '')[:3] if c.isalpha()])

    def Emoticons(self, text):
        return len([c for c in [':-)', ';-)', ':)', ';)', ':-(', ':('] if c in text])

    def StartWithAt(self, text):
        return 1 if text.lstrip().startswith('@') else 0


def FeatureExtraction(text):

    features = Features()
    features_dict = {'ratio.caps': features.CapsRatio,
                     'ratio.specials': features.SpecialCharsRatio,
                     'ratio.numbers': features.NumbersRatio,
                     'length.words': features.AverageWordLength,
                     'stopwords': features.StopwordsRatio1,
                     'stopwords2': features.StopwordsRatio2,
                     'last.char.code': features.LastCharCode,
                     'last.char.nl': features.LastCharNL,
                     'first.3.chars.letters': features.First3CharsLetter,
                     'emoticons': features.Emoticons,
                     'first.char.at': features.StartWithAt}

    return ComputeFeatures(text, features_dict)


def ConvertFeatures(data):
    if isinstance(data, list):
        data = pd.DataFrame(data)
    if isinstance(data, pd.DataFrame):
        data = np.asarray(data)
    return data


def ComputeFeatures(text, features):
    if callable(features):
        return features(text)
    elif isinstance(features, dict):
        df = pd.DataFrame(text)
        df_out = pd.DataFrame()
        for name, feature in features.items():
            if callable(feature):
                df_out[name] = df.apply(lambda row: feature(row[0]), axis=1)
        return df_out


def TriGramsAndFeatures(text):
    return pd.concat([Character3Grams(text), FeatureExtraction(text)], axis=1)


def TriGramsAndFeaturesForTest(text):
    return pd.concat([Character3GramsForTest(text), FeatureExtraction(text)], axis=1)


class NLoNFeatures:
    def fit_transform(X, feature_type='C3_FE'):
        if feature_type == 'C3':
            features = Character3Grams
        elif feature_type == 'FE':
            features = FeatureExtraction
        elif feature_type == 'C3_FE':
            features = TriGramsAndFeatures
        return ConvertFeatures(ComputeFeatures(X, features))

    def transform(X, feature_type='C3_FE'):
        if feature_type == 'C3':
            features = Character3GramsForTest
        elif feature_type == 'FE':
            features = FeatureExtraction
        elif feature_type == 'C3_FE':
            features = TriGramsAndFeaturesForTest
        return ConvertFeatures(ComputeFeatures(X, features))
