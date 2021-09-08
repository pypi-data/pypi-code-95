import pandas as pd
import numpy as np
from compExtract.utility import xm_text_processor, get_binary_dttb

class ComparativeExtraction:
    """
    Takes in corpus with 
    """

    def __init__(self, corpus, labels, text_processor=xm_text_processor):

        self.corpus = corpus
        self.labels = labels
        self.text_processor=text_processor
    
    def get_distinguish_terms(self, ngram_range=(1,3), min_df=0.01, max_df=0.9, top_n=20):

        # a dataframe of all the reviews
        df = pd.DataFrame({"review_text":self.corpus,"labels":self.labels})

        # Get the binary data table
        dttb = get_binary_dttb(self.corpus,tokenizer=self.text_processor, ngram_range=ngram_range, min_df=min_df,max_df=max_df, binary=True)

        # Separate the terms into positive and negative dataframes
        pos_df = dttb[df['labels'] == 1].reset_index(drop = True)
        neg_df = dttb[df['labels'] == 0].reset_index(drop = True)

        # Get the proportional document frequencies for each term
        pos_shape = pos_df.shape[0]
        pos_count = [sum(pos_df[x] == 1) for x in dttb.columns]
        pos_prop = np.array(pos_count)/pos_shape

        neg_shape = neg_df.shape[0]
        neg_count = [sum(neg_df[x] == 1) for x in dttb.columns]
        neg_prop = np.array(neg_count)/neg_shape

        term_stats_tb = pd.DataFrame({"feature":dttb.columns,\
            "diff":np.array(pos_prop) - np.array(neg_prop),\
            "pos_prop":pos_prop,\
            "pos_count":pos_count,\
            "neg_prop":neg_prop,\
            "neg_count":neg_count})

        # Assign the tables back to the class
        self.binary_dtm = dttb
        self.term_stats_tb = term_stats_tb

        # Sort the table in an ascending order and filter by top N
        self.increased_terms_df = term_stats_tb.sort_values('diff',ascending = False).reset_index(drop = True).head(top_n)

        # Sort the table in an descending order and filter by top N
        self.decreased_terms_df = term_stats_tb.sort_values('diff',ascending = True).reset_index(drop = True).head(top_n)

        return self
        




