# Imported libraries

import pandas as pd

from greykite.framework.templates.autogen.forecast_config import ForecastConfig
from greykite.framework.templates.forecaster import Forecaster
from greykite.framework.templates.model_templates import ModelTemplateEnum

import warnings
warnings.filterwarnings("ignore")

from nltk.corpus import stopwords
from ml_utils import *
import re
from nltk.stem import RSLPStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

class Recommendation:
    def __init__(self, metrics_path, reviews_path):
        self.metrics_path = metrics_path
        self.reviews_path = reviews_path

    def analyse(self):
        metrics = pd.read_csv(self.metrics_path, index_col=[0])

        # specify dataset information
        metadata = dict(
            time_col="Time_col",  # name of the time column
            value_col="Value",  # name of the value column
            freq="D"  # "H" for hourly, "D" for daily, "W" for weekly, etc.
        )
        # specify changepoint parameters in model_components
        model_components = dict(
            changepoints={
                # it's ok to provide one of ``changepoints_dict`` or ``seasonality_changepoints_dict`` by itself
                "changepoints_dict": {
                    "method": "auto",
                    "yearly_seasonality_order": 15,
                    "regularization_strength": 0.6,
                    "resample_freq": "7D",
                    "potential_changepoint_n": 25,
                    "no_changepoint_proportion_from_end": 0.05
                }
            },
            custom={
                "fit_algorithm_dict": {
                    "fit_algorithm": "ridge"}})  # use ridge to prevent overfitting when there many changepoints

        # Generates model config
        config = ForecastConfig.from_dict(
            dict(
                model_template=ModelTemplateEnum.SILVERKITE.name,
                forecast_horizon=30,
                coverage=0.95,  # 95% prediction intervals
                metadata_param=metadata,
                model_components_param=model_components))

        # Then run with changepoint parameters
        forecaster = Forecaster()
        result = forecaster.run_forecast_config(
            df=metrics,
            config=config)

        import plotly
        from plotly import graph_objs as go

        plotly.io.renderers.default = 'browser'

        fig = result.model[-1].plot_trend_changepoint_detection(dict(plot=False))
        print(fig.show())

        fig = go.Figure(fig)

        return fig





    def recommend(self):

        reviews = pd.read_csv(self.reviews_path)
        ## 1. DATA PREVIEW

        reviews = reviews.sort_values(by='review_answer_timestamp')
        reviews.to_csv('revtest.csv')
        df_comments = reviews.loc[:, ['review_score', 'review_comment_message']]
        df_comments = df_comments.iloc[99332:, :]
        df_comments = df_comments.dropna(subset=['review_comment_message'])
        df_comments = df_comments.reset_index(drop=True)
        # print(f'Dataset shape: {df_comments.shape}')
        df_comments.columns = ['score', 'comment']
        df_comments.to_csv('revtest2.csv')

        # print(df_comments.head())

        # we have nearly 42000 comments, but we have to prepare the text before applying sentiment analysis

        ## 2. REGULAR EXPRESSIONS

        # Breakline and carriage returns

        def re_breakline(text_list):
            """
            Args:
            ----------
            text_list: list object with text content to be prepared [type: list]
            """

            # Applying regex
            return [re.sub('[\n\r]', ' ', r) for r in text_list]

        # Creating a list of comment reviews
        reviews = list(df_comments['comment'].values)

        # Applying RegEx
        reviews_breakline = re_breakline(reviews)
        df_comments['re_breakline'] = reviews_breakline

        ## 3. SITES AND HYPERLINKS

        def re_hyperlinks(text_list):
            """
            Args:
            ----------
            text_list: list object with text content to be prepared [type: list]
            """

            # Applying regex
            pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            return [re.sub(pattern, ' link ', r) for r in text_list]

        # Applying RegEx
        reviews_hyperlinks = re_hyperlinks(reviews_breakline)
        df_comments['re_hyperlinks'] = reviews_hyperlinks

        ## 4. DATES

        def re_dates(text_list):
            """
            Args:
            ----------
            text_list: list object with text content to be prepared [type: list]
            """

            # Applying regex
            pattern = '([0-2][0-9]|(3)[0-1])(\/|\.)(((0)[0-9])|((1)[0-2]))(\/|\.)\d{2,4}'
            return [re.sub(pattern, ' data ', r) for r in text_list]

        # Applying RegEx
        reviews_dates = re_dates(reviews_hyperlinks)
        df_comments['re_dates'] = reviews_dates

        ## 5. MONEY

        def re_money(text_list):
            """
            Args:
            ----------
            text_list: list object with text content to be prepared [type: list]
            """

            # Applying regex
            pattern = '[R]{0,1}\$[ ]{0,}\d+(,|\.)\d+'
            return [re.sub(pattern, ' dinheiro ', r) for r in text_list]

        # Applying RegEx
        reviews_money = re_money(reviews_dates)
        df_comments['re_money'] = reviews_money

        ## 6. NUMBERS

        def re_numbers(text_list):
            """
            Args:
            ----------
            text_series: list object with text content to be prepared [type: list]
            """

            # Applying regex
            return [re.sub('[0-9]+', ' numero ', r) for r in text_list]

        # Applying RegEx
        reviews_numbers = re_numbers(reviews_money)
        df_comments['re_numbers'] = reviews_numbers

        ## 7. NEGATION

        def re_negation(text_list):
            """
            Args:
            ----------
            text_series: list object with text content to be prepared [type: list]
            """

            # Applying regex
            return [re.sub('([nN][ãÃaA][oO]|[ñÑ]| [nN] )', ' negação ', r) for r in text_list]

        # Applying RegEx
        reviews_negation = re_negation(reviews_numbers)
        df_comments['re_negation'] = reviews_negation

        ## 8. SPECIAL CHARACTERS

        def re_special_chars(text_list):
            """
            Args:
            ----------
            text_series: list object with text content to be prepared [type: list]
            """

            # Applying regex
            return [re.sub('\W', ' ', r) for r in text_list]

        # Applying RegEx
        reviews_special_chars = re_special_chars(reviews_negation)
        df_comments['re_special_chars'] = reviews_special_chars

        ## 9. WHITESPACES

        def re_whitespaces(text_list):
            """
            Args:
            ----------
            text_series: list object with text content to be prepared [type: list]
            """

            # Applying regex
            white_spaces = [re.sub('\s+', ' ', r) for r in text_list]
            white_spaces_end = [re.sub('[ \t]+$', '', r) for r in white_spaces]
            return white_spaces_end

        # Applying RegEx
        reviews_whitespaces = re_whitespaces(reviews_special_chars)
        df_comments['re_whitespaces'] = reviews_whitespaces

        ## 10. NEGATION

        def re_negation(text_list):
            """
            Args:
            ----------
            text_series: list object with text content to be prepared [type: list]
            """

            # Applying regex
            return [re.sub('([nN][ãÃaA][oO]|[ñÑ]| [nN] )', ' negação ', r) for r in text_list]

        # Applying RegEx
        reviews_negation = re_negation(reviews_numbers)
        df_comments['re_negation'] = reviews_negation

        ## 11. SPECIAL CHARACTERS

        def re_special_chars(text_list):
            """
            Args:
            ----------
            text_series: list object with text content to be prepared [type: list]
            """

            # Applying regex
            return [re.sub('\W', ' ', r) for r in text_list]

        # Applying RegEx
        reviews_special_chars = re_special_chars(reviews_negation)
        df_comments['re_special_chars'] = reviews_special_chars

        ## 12. ADDITIONAL WHITESPACES

        def re_whitespaces(text_list):
            """
            Args:
            ----------
            text_series: list object with text content to be prepared [type: list]
            """

            # Applying regex
            white_spaces = [re.sub('\s+', ' ', r) for r in text_list]
            white_spaces_end = [re.sub('[ \t]+$', '', r) for r in white_spaces]
            return white_spaces_end

        # Applying RegEx
        reviews_whitespaces = re_whitespaces(reviews_special_chars)
        df_comments['re_whitespaces'] = reviews_whitespaces

        ## 13. STOPWORDS

        pt_stopwords = stopwords.words('portuguese')

        # Defining a function to remove the stopwords and to lower the comments
        def stopwords_removal(text, cached_stopwords=stopwords.words('portuguese')):
            """
            Args:
            ----------
            text: list object where the stopwords will be removed [type: list]
            cached_stopwords: stopwords to be applied on the process [type: list, default: stopwords.words('portuguese')]
            """

            return [c.lower() for c in text.split() if c.lower() not in cached_stopwords]

        # Removing stopwords and looking at some examples
        reviews_stopwords = [' '.join(stopwords_removal(review)) for review in reviews_whitespaces]
        df_comments['stopwords_removed'] = reviews_stopwords

        ## 14. STEMMING

        def stemming_process(text, stemmer=RSLPStemmer()):
            """
            Args:
            ----------
            text: list object where the stopwords will be removed [type: list]
            stemmer: type of stemmer to be applied [type: class, default: RSLPStemmer()]
            """

            return [stemmer.stem(c) for c in text.split()]

        # Applying stemming and looking at some examples
        reviews_stemmer = [' '.join(stemming_process(review)) for review in reviews_stopwords]
        df_comments['stemming'] = reviews_stemmer

        # Feature Extraction

        def extract_features_from_corpus(corpus, vectorizer, df=False):
            """
            Args
            ------------
            text: text to be transformed into a document-term matrix [type: string]
            vectorizer: engine to be used in the transformation [type: object]
            """

            # Extracting features
            corpus_features = vectorizer.fit_transform(corpus).toarray()
            features_names = vectorizer.get_feature_names()

            # Transforming into a dataframe to give interpetability to the process
            df_corpus_features = None
            if df:
                df_corpus_features = pd.DataFrame(corpus_features, columns=features_names)

            return corpus_features, df_corpus_features

        ## 1. CountVectorizer

        # Creating an object for the CountVectorizer class
        count_vectorizer = CountVectorizer(max_features=300, min_df=7, max_df=0.8, stop_words=pt_stopwords)

        # Extracting features for the corpus
        countv_features, df_countv_features = extract_features_from_corpus(reviews_stemmer, count_vectorizer, df=True)

        ## 2. TF-IDF

        # Creating an object for the CountVectorizer class
        tfidf_vectorizer = TfidfVectorizer(max_features=300, min_df=7, max_df=0.8, stop_words=pt_stopwords)

        # Extracting features for the corpus
        tfidf_features, df_tfidf_features = extract_features_from_corpus(reviews_stemmer, tfidf_vectorizer, df=True)

        # Labelling Data
        ##fig, ax = plt.subplots(figsize=(10, 5))
        ##single_countplot(x='score', df=df_comments, ax=ax)

        # Scores of 1-3 will be considered negative and scores of 4-5 will be considered positive

        # Labelling data
        score_map = {
            1: 'negative',
            2: 'negative',
            3: 'positive',
            4: 'positive',
            5: 'positive'
        }
        df_comments['sentiment_label'] = df_comments['score'].map(score_map)

        # Verifying results
        ##fig, ax = plt.subplots(figsize=(7, 7))
        ##donut_plot(df_comments.query('sentiment_label in ("positive", "negative")'), 'sentiment_label',
        ##           label_names=df_comments.query('sentiment_label in ("positive", "negative")')['sentiment_label'].value_counts().index,
        ##           ax=ax, colors=['darkslateblue', 'crimson'])

        def ngrams_count(corpus, ngram_range, n=-1, cached_stopwords=stopwords.words('portuguese')):
            """
            Args
            ----------
            corpus: text to be analysed [type: pd.DataFrame]
            ngram_range: type of n gram to be used on analysis [type: tuple]
            n: top limit of ngrams to be shown [type: int, default: -1]
            """

            # Using CountVectorizer to build a bag of words using the given corpus
            vectorizer = CountVectorizer(stop_words=cached_stopwords, ngram_range=ngram_range).fit(corpus)
            bag_of_words = vectorizer.transform(corpus)
            sum_words = bag_of_words.sum(axis=0)
            words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
            words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
            total_list = words_freq[:n]

            # Returning a DataFrame with the ngrams count
            count_df = pd.DataFrame(total_list, columns=['ngram', 'count'])
            return count_df

        # Splitting the corpus into positive and negative comments
        positive_comments = df_comments.query('sentiment_label == "positive"')['stemming']
        negative_comments = df_comments.query('sentiment_label == "negative"')['stemming']

        # Extracting the top 10 unigrams by sentiment
        unigrams_pos = ngrams_count(positive_comments, (1, 1), 10)
        unigrams_neg = ngrams_count(negative_comments, (1, 1), 10)

        # Extracting the top 10 unigrams by sentiment
        bigrams_pos = ngrams_count(positive_comments, (2, 2), 10)
        bigrams_neg = ngrams_count(negative_comments, (2, 2), 10)

        # Extracting the top 10 unigrams by sentiment
        trigrams_pos = ngrams_count(positive_comments, (3, 3), 10)
        trigrams_neg = ngrams_count(negative_comments, (3, 3), 10)

        # Joining everything in a python dictionary to make the plots easier
        ngram_dict_plot = {
            'Top Unigrams on Positive Comments': unigrams_pos,
            'Top Unigrams on Negative Comments': unigrams_neg,
            'Top Bigrams on Positive Comments': bigrams_pos,
            'Top Bigrams on Negative Comments': bigrams_neg,
            'Top Trigrams on Positive Comments': trigrams_pos,
            'Top Trigrams on Negative Comments': trigrams_neg,
        }

        metrics = pd.read_csv(self.metrics_path, index_col=[0])




        d21 = '2017-01-24'
        d22 = '2017-07-23'

        d31 = '2017-07-23'
        d32 = '2017-11-26'

        d41 = '2017-11-26'
        d42 = '2018-07-22'




        def rev_change(date1, date2):
            d1 = metrics.loc[metrics['Time_col'] == date1]
            d2 = metrics.loc[metrics['Time_col'] == date2]

            rev_change = pd.concat([d1, d2])
            rev_change = rev_change.iloc[:, 1]
            rev_change = rev_change.pct_change().iloc[1]
            rev_change = rev_change * 100

            revenue = round(rev_change, 2)

            return revenue


        rev2 = rev_change(d21, d22)
        rev3 = rev_change(d31, d32)
        rev4 = rev_change(d41, d42)

        def date_dif(date1, date2):
            d1 = metrics.loc[metrics['Time_col'] == date1]
            d2 = metrics.loc[metrics['Time_col'] == date2]

            df = pd.concat([d1, d2])
            df = df.iloc[:, 1:]
            df = df.pct_change().iloc[1, 3:]
            # complement to 100% #
            # df = df.iloc[:,2:]
            # df = df[2:]

            norm = [float(i) / sum(df) for i in df]
            norm = [i * 100 for i in norm]

            rev_change = pd.concat([d1, d2])
            rev_change = rev_change.iloc[:, 1]
            rev_change = rev_change.pct_change().iloc[1]
            rev_change = rev_change * 100

            revenue = round(rev_change, 2)

            print('\nThe change in revenue between', date1, 'and', date2, 'is of', revenue, '%')

            if revenue >= 0:
                print('\nThe trend is UP.')
            else:
                print('\nThe trend is DOWN.')

            print('\nThe root-causes for the changepoint in', date2, 'are:\n')

            # print('Total good reviews:',round(norm[0],2),'%')
            # print('Total bad reviews:',round(norm[1],2),'%')
            print('Average review score:', round(norm[0], 2), '%')
            print('Total freight value:', round(norm[1], 2), '%')
            print('Average delivery score:', round(norm[2], 2), '%')

            if revenue < 0:
                print('\nRecommendations\n')

                if round(norm[0], 2) < -15:
                    print('Product Reviews:\nThe  main trigrams in the reviews are:\n', trigrams_neg)
                else:
                    pass

                if trigrams_neg['ngram'].eq('neg receb produt').any():
                    print('\n', trigrams_neg.loc[trigrams_neg['ngram'] == 'neg receb produt', 'count'].iloc[0],
                          'customers did not receive their product.')

                if trigrams_neg['ngram'].eq('produt códig vem').any():
                    print(trigrams_neg.loc[trigrams_neg['ngram'] == 'produt códig vem', 'count'].iloc[0],
                          'customers had a problem with the tracking code.')

                if trigrams_neg['ngram'].eq('outr total difer').any():
                    print(trigrams_neg.loc[trigrams_neg['ngram'] == 'outr total difer', 'count'].iloc[0],
                          'customers received a different product than the one they ordered.')

                if round(norm[1], 2) < -15:
                    print('\nDelivery Score:\nOrders to the North and Northeast regions have a longer delivery time.')
                    # print(
                    #    'The installation of a distribution centre in the northern region of Brazil will improve the delivery score.')
                else:
                    pass

                if round(norm[2], 2) < -15:
                    print('\nDelivery Cost:\nOrders to the North and Northeast regions have a higher delivery cost.')
                    # print(
                    #    'The installation of a distribution centre in the northern region of Brazil will reduce the delivery cost.')
                else:
                    pass
            else:
                pass

        cp2 = date_dif('2017-01-24','2017-07-23')
        cp3 = date_dif('2017-07-23','2017-11-26')
        cp4 = date_dif('2017-11-26','2018-07-22')

        #print(cp2)
        #print(cp3)
        #print(cp4)

        return cp2,cp3,cp4





#r2 = Recommendation('C:\\Users\\julgonza\\PycharmProjects\\test\\metrics_pvalue.csv',
#                    r'C:\Users\julgonza\OneDrive - everis\Datasets\Brazilian\Brazilian Ecommerce Dataset\olist_order_reviews_dataset.csv')
#print(r2.recommend())


#r1 = Recommendation('C:\\Users\\julgonza\\PycharmProjects\\test\\metrics_pvalue.csv',
#                    r'C:\Users\julgonza\OneDrive - everis\Datasets\Brazilian\Brazilian Ecommerce Dataset\olist_order_reviews_dataset.csv')
#r1.analyse()
#r1.recommend()