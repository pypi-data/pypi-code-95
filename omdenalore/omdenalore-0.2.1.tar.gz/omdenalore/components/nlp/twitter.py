from _typeshed import Self
import pandas as pd
import datetime
from langdetect import detect
from typing import List
from collections import Counter, defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import spacy
import re


class TwitterClient:
    """
    Process and gain relevant information from tweets
    """

    def __init__(
        self,
        tweets: List = None,
        file_to_read: str = None,
        query_words: List = None,
        lang: str = "en",
        nlp: spacy.language.Language = None,
        ngrams: int = 2,
    ):
        """
        Initialize the class

        :param tweets: list of tweets
        :type tweets: list
        :param file_to_read: file to read
        :type file_to_read: str
        :param query_words: list of words to find cooccurrences
        :type query_words: list
        :param lang: language of tweets
        :type lang: str
        :param nlp: spacy model
        :type nlp: spacy.language.Language
        :param ngrams: ngrams to use
        :type ngrams: int

        :return: None
        """

        if file_to_read:
            self.tweets = self.read_file(file_to_read)

        else:
            self.tweets = tweets

        self.lang = lang
        self.nlp = nlp
        self.ngrams = ngrams
        self.query_words = query_words
        self.nlp = spacy.load("en_core_web_sm")

    def read_file(self, filename):
        """
        Read a file and return a list of tweets

        :param filename: file to read
        :type filename: str

        :return: list of tweets
        """

        assert (
            filename is not None and filename != ""
        ), "filename cannot be None or empty"

        tweets_from_file = pd.read_csv(filename, lineterminator="\n")
        tweets_from_file = tweets_from_file[tweets_from_file["language"] == "en"]
        tweets_from_file["datetime"] = tweets_from_file["date"].apply(
            lambda x: dateExtractor(x)
        )
        tweets_from_file["yearvalue"] = tweets_from_file["datetime"].apply(
            lambda x: x.year
        )

        return tweets_from_file

    def clean_data(self, tweets):
        """
        Clean the tweets

        :param tweets: list of tweets
        :type tweets: list

        :return: list of cleaned tweets
        """

        # define clean tweet data function
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U0001f921-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+",
            flags=re.UNICODE,
        )

        email_pattern = re.compile("\S+@\S+\.\S{2,3}")
        link_pattern = re.compile("https?\S+")

        tweets_cleaned = set()
        for tweet in tweets:
            try:
                lang = self.lang
                if lang == "en":
                    tweet_rep = emoji_pattern.sub(r"", tweet)  # remove emojis
                    tweet_rep = email_pattern.sub(r"", tweet_rep)  # remove emails
                    tweet_rep = link_pattern.sub(r"", tweet_rep)  # remove links
                    tweet_rep = tweet_rep.replace("’", "'")
                    tweet_rep = tweet_rep.strip()  # split tweet
                    tweets_cleaned.add(tweet_rep)
                else:
                    print("Only english tweets supported right now")
                    return []
            except:
                print("Item not processed:", tweet)
        return tweets_cleaned

    def find_cooccurrences(self, query_words):
        """
        Find cooccurrences of words in tweets

        :param query_words: list of words to find cooccurrences
        :type query_words: list

        :return: cooccurrences
        :returntype: defaultdict
        """

        self.query_words = query_words
        tweets = self.clean_data(self.tweets)

        pos_meaningful = ["NOUN", "PROPN", "ADJ", "VERB"]
        co_occurrences = defaultdict(list)  # creates a dict with list as default key

        for query in query_words:
            co_occurrences[query] = Counter()

        for doc in tqdm(self.nlp.pipe(tweets, disable=["ner"])):
            lemmas = [
                token.lemma_ for token in doc
            ]  # get list of words in doc with inflections
            for query in query_words:
                if query in lemmas:
                    # get list of meainingful word, if len of doc is greater than 1 and the word is part of the define POS list, then convert to lower case
                    meaningful_words = [
                        token.lemma_.lower()
                        for token in doc
                        if token.pos_ in pos_meaningful and len(token.text) > 1
                    ]
                    # create bigrams
                    bigrams = []
                    for i in range(len(doc) - 1):
                        if (
                            doc[i].pos_ in pos_meaningful
                            and doc[i + 1].pos_ in pos_meaningful
                        ):
                            bigram = doc[i].text + " " + doc[i + 1].text
                            bigrams.append(bigram)
                    # count number of times, meaningful phrases and bigram cooccur
                    for phrase in meaningful_words + bigrams:
                        co_occurrences[query][phrase] += 1

        self.co_occurrences = co_occurrences

        return co_occurrences

    def compute_edge_weights(self):
        """
        Compute edge weights for cooccurrences

        :return: edge weights
        :returntype: List
        """

        coocurrence_dict = self.co_occurrences

        # get total occurences
        total_occurences = 0
        for j in range(len(coocurrence_dict)):
            total_occurences = total_occurences + int(coocurrence_dict[j][1])

        # compute normalised weights
        edge_weights = []
        for i in range(len(coocurrence_dict)):
            edge_weights.append((int(coocurrence_dict[i][1]) / total_occurences) * 30)

        self.edge_weights = edge_weights

        return edge_weights

    def make_adjacency_list(self):
        """
        Make adjacency list with edge weights

        :return: adjacency list
        :returntype: List
        """

        edge_weights = (
            self.compute_edge_weights()
            if self.edge_weights is None
            else self.edge_weights
        )
        coocurrence_dict = (
            self.find_cooccurrences(self.query_words)
            if self.co_occurrences is None
            else self.co_occurrences
        )
        adjacency_list = []

        for i in range(len(coocurrence_dict)):
            edge = (coocurrence_dict[0][0], coocurrence_dict[i][0], edge_weights[i])
            adjacency_list.append(edge)

        self.adjacency_list = adjacency_list

        return adjacency_list

    def build_graph(self):
        """
        Build graph with networkx

        :return: graph
        :returntype: networkx.nx.Graph
        """

        adjacency_list = (
            self.make_adjacency_list()
            if self.adjacency_list is None
            else self.adjacency_list
        )

        network = nx.Graph()  # make empty graph

        for i in range(len(adjacency_list)):
            # build network by adding edges
            network.add_edge(
                adjacency_list[i][0], adjacency_list[i][1], weight=adjacency_list[i][2]
            )

        self.network = network

        return network

    def draw_graph(self):
        """
        Visualize the graph
        """

        network = self.network
        edge_weights = self.edge_weights

        # draw
        pos = nx.spring_layout(network)
        # colors = range(len(network))
        options = {
            "edge_color": "b",
            "node_color": "b",
            "width": 10,
            "edge_cmap": plt.cm.Blues,
            "with_labels": True,
            "font_weight": "bold",
            "width": edge_weights,
        }
        nx.draw(network, pos, **options)
        # show
        plt.show()

    @staticmethod
    def dateExtractor(x):
        """
        Extract the date from a string

        :param x: date string
        :type x: str

        :return: datetime.date2
        """

        v = ""

        try:
            v = datetime.datetime.strptime(x, "%Y-%m-%d")

        except:
            try:
                v = datetime.datetime.strptime(x, "%d-%m-%Y")
            except Exception as e:
                print(x)
                print(e)
        return v
