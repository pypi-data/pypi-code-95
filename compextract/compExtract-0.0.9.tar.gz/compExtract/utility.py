#from gensim.parsing.preprocessing import STOPWORDS
from tokenizer_xm import TextPreProcessor
from sklearn.feature_extraction.text import CountVectorizer
from datetime import datetime
import numpy as np
import pandas as pd
import re

# Remove "not" from the list

# all_stops = list(STOPWORDS)
# all_stops.remove("not")

def xm_text_processor(text):
    tpp = TextPreProcessor(text=text, lemma_flag=True, stem_flag=False)
    return tpp.process()

def get_binary_dttb(corpus, ngram_range, tokenizer, min_df, max_df,binary):
    """
    Given a list of text, return the document term table
    """
    vec = CountVectorizer(ngram_range=ngram_range, tokenizer=tokenizer, min_df=min_df, max_df=max_df, binary=binary)
    fitted_vec = vec.fit(corpus)
    dttb = pd.DataFrame(fitted_vec.transform(corpus).toarray())
    dttb.columns = fitted_vec.get_feature_names()

    return dttb

# def get_ngrams_on_term(target,corpus,ng_range = (2,4),filter_by_extreme = True):
#     """
#     given a target term and corpus containing the target, output the n-grams containin the target
    
#     ---Parameters
#     filter_by_extreme: a boolean value indicating whether the results only display the outliers
#     of the ngrams
#     """
#     # Fit the Count vectorizer with more strict
#     vec_count = CountVectorizer(ngram_range = ng_range,tokenizer=tokenizer,min_df = 0.01, max_df = 0.99) 
#     # Added a "try + except" for the "after pruning no terms remain error"
#     try:
#         vec_count_f = vec_count.fit(corpus)
#     except:
#         # If there is no term remain return an empty dataframe
#         n_count_df = pd.DataFrame({"ngram":[],"count":[]})
#         return n_count_df

#     # Create the triaining document-term matrix
#     dtm = vec_count_f.transform(corpus)

#     # Create a data frame
#     dtm_df = pd.DataFrame(dtm.toarray())
#     dtm_df.columns = vec_count_f.get_feature_names()  

#     # filter the features based on whether they contain the target
#     contain_target = [x for x in dtm_df.columns if ((target) in x)]
#     dtm_target_only = dtm_df[contain_target]
#     n_count_df = pd.DataFrame(dtm_target_only.sum(axis = 0)).reset_index()
#     n_count_df.columns = ['ngram','count']

#     # Get the boundary. Only display the outliers of the n-grams (whose count significantly higher than the median count of all such n-grams)
#     if filter_by_extreme:
#         median = np.median(n_count_df['count'])
#         sd = np.std(n_count_df['count'])
#         boundary = median + 2 * sd
#     else:
#         boundary = 0

#     class output:
#         input_corpus = corpus
#         related_ngrams = n_count_df[n_count_df['count']>=boundary].sort_values("count",ascending = False).reset_index(drop = True)
#         index_containing_ngrams = dtm_target_only
#     return output


