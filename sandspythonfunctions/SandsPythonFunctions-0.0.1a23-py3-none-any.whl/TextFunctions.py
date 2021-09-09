# --------------------------------------------------------------------------------------
# File: "TextFunctions.py"
# Dir: "/mnt/c/Users/ldsan/Downloads/Github_Projects/SandsPythonFunctions/src/SandsPythonFunctions"
# Created: 2020-05-26
# --------------------------------------------------------------------------------------
"""
this file is designed to make cleaning text far easier to do it contains these functions

clean_body_text
clean_text_columns
write_columns_to_text
"""


def clean_text_columns(
    dta,
    target_column="body",
    remove_punctuation=False,
    make_lower=False,
    remove_stopwords=False,
    stem_strings=False,
    remove_urls=False,
    get_number_of_words=False,
    split_words_into_list=False,
    remove_empty_body_posts=False,
    remove_non_alpha=False,
    print_timings=True,
):
    import pandas as pd

    def print_current_time():
        """
        Prints the current date and time of day
        """
        from datetime import datetime

        now = datetime.now()
        now = now.strftime("%m/%d/%Y, %H:%M:%S")
        return now

    # check everything is downloaded and installed
    def get_stopwords():
        """
        this will test to see if the stopwords from the nltk module have already been
        downloaded if they have not they will be download this function is needed for both
        word embedding and topic modeling and is just overall useful
        """
        from nltk.downloader import download
        from nltk.corpus import stopwords

        try:
            return stopwords.words("english")
        except:
            print(f"NLTK needs to download the stopwords. This will take a while.")
            download("stopwords")
            print(f"NLTK has finished downloading stopwords.")
            return stopwords.words("english")

    # clean the text
    def remove_empty_body_posts_function(dta, cleaned):
        """
        this function removes all of the posts that have been deleted and thus contain no
        text in the cleaned column
        """
        dta[cleaned] = dta[cleaned].replace(
            {
                "nan": "",
                "NaN": "",
                "None": "",
                "none": "",
                None: "",
            }
        )
        dta = dta.dropna(subset=[cleaned])
        return dta

    def remove_non_alpha_function():
        dta[cleaned] = dta[cleaned].apply(
            lambda x: " ".join([word for word in x.split() if word.isalpha()])
        )
        return dta

    def remove_urls_in_string_function(dta, cleaned):
        dta[cleaned] = dta[cleaned].str.replace(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            " ",
            regex=True
        )
        dta[cleaned] = dta[cleaned].str.replace(r"<[^<>]+(>|$)", " ", regex=True)
        dta[cleaned] = dta[cleaned].str.replace(r"\[img_assist[^]]*?\]", " ", regex=True)
        dta[cleaned] = dta[cleaned].str.replace(r" +", " ", regex=True)
        return dta

    def remove_stopwords_function(stop_words, dta, cleaned):
        """
        this function removes all of the stopwords from every item in a column in this case
        in the cleaned column
        this function is needed for both word embedding and topic modeling and is just
        overall useful
        """
        import pandas as pd

        dta[cleaned] = dta[cleaned].apply(
            lambda x: " ".join([word for word in x.split() if word not in (stop_words)])
        )
        return dta

    def remove_punctuation_function(dta, cleaned):
        """
        this function will use a regular expression to remove all of the punctuation from
        every item in the column cleaned
        this function is needed for both word embedding and topic modeling and is just
        overall useful
        """
        import pandas as pd

        dta[cleaned] = dta[cleaned].str.replace("[^\w\s]", "", regex=True)
        return dta

    def make_lower_function(dta, cleaned):
        """
        this function makes all of the items in the column cleaned to lower case
        characters
        """
        import pandas as pd

        dta[cleaned] = dta[cleaned].str.lower()
        return dta

    def get_number_of_words_function(dta, cleaned):
        """
        this function gets the number of words in the column cleaned and creates a new
        column called "num_words" which contains that number for each row
        """
        import pandas as pd

        dta["num_words"] = dta[cleaned].apply(lambda x: len(str(x).split()))
        return dta

    def stemmer_function(dta, cleaned):
        """
        this is a stemmer that takes every english word and removes suffixes so that each
        word with the same stem will look the same to python rather than looking different

        Arguments:
            dta {dataframe} -- the main dataframe with the cleaned column
        Returns:
            dta -- returns the dataframe but the strings in the cleaned column has been
            stemmed
        """
        import pandas as pd

        # from nltk.stem import PorterStemmer
        from nltk.stem.snowball import SnowballStemmer

        stemmer = SnowballStemmer("english")
        # st = PorterStemmer()
        dta[cleaned] = dta[cleaned].apply(
            lambda x: " ".join([stemmer.stem(word) for word in x.split() if x != ""])
        )
        return dta

    def split_words_into_list_function(dta, cleaned):
        """
        This function takes each word from the cleaned column and puts them each one
        into a list so that the word2vec module can work with that data
        Arguments:
            dta {dataframe} -- the cleaned dataframe
        Returns:
            dataframe -- the dataframe with a new column "body_word_list"
        """
        import pandas as pd

        # create word list, which keeps the sequential order of words
        dta["body_word_list"] = dta[cleaned].apply(lambda x: x.split())
        return dta

    cleaned = f"{target_column}_clean"
    dta[cleaned] = dta[target_column]
    if remove_empty_body_posts is True:
        dta = remove_empty_body_posts_function(dta, cleaned)
        if print_timings is True:
            print(f"remove_empty_body_posts finished at {print_current_time()}")
    if remove_urls is True:
        dta = remove_urls_in_string_function(dta, cleaned)
        if print_timings is True:
            print(f"remove_urls_in_string finished at {print_current_time()}")
    if remove_punctuation is True:
        dta = remove_punctuation_function(dta, cleaned)
        if print_timings is True:
            print(f"remove_punctuation finished at {print_current_time()}")
    if make_lower is True:
        dta = make_lower_function(dta, cleaned)
        if print_timings is True:
            print(f"make_lower finished at {print_current_time()}")
    if remove_stopwords is True:
        stop_words = get_stopwords()
        dta = remove_stopwords_function(stop_words, dta, cleaned)
        if print_timings is True:
            print(f"remove_stopwords finished at {print_current_time()}")
    if remove_non_alpha is True:
        dta = remove_non_alpha_function()
        if print_timings is True:
            print(f"removed non alpha characters finished at {print_current_time()}")
    if stem_strings is True:
        dta = stemmer_function(dta, cleaned)
        if print_timings is True:
            print(f"stemmer finished at {print_current_time()}")
    if get_number_of_words is True:
        dta = get_number_of_words_function(dta, cleaned)
        if print_timings is True:
            print(f"word counter finished at {print_current_time()}")
    if split_words_into_list is True:
        dta = split_words_into_list_function(dta, cleaned)
        if print_timings is True:
            print(f"split word into list finished at {print_current_time()}")
    return dta


def remove_words_below_freq(dta, column_name, min_num_word_freq=3):
    """this will remove from a dataframe column any words that occur less than the number given in
    the `min_num_word_freq` variable with the default being 3 occurances

    Args:
        dta (dataframe): the dataframe

        min_num_word_freq (int, optional): the number of occurances that will be removed if the word is
        in the series less than or equal to that number. Defaults to 3.
    """
    from collections import defaultdict

    dta["num_words"] = dta[column_name].apply(lambda x: len(str(x).split()))
    print(
        f"average num words before removing words with less than {min_num_word_freq} occurances: {dta['num_words'].values.mean()}"
    )
    if min_num_word_freq >= 2:
        frequency = defaultdict(int)
        for text in dta[column_name].tolist():
            try:  # TODO: this needs to be cleaned up probably a type check
                for token in text.split():
                    frequency[token] += 1
            except:
                for token in text:
                    frequency[token] += 1
        dta[column_name] = dta[column_name].apply(
            lambda x: " ".join([word for word in x.split() if frequency[word] > min_num_word_freq])
        )
    dta["num_words"] = dta[column_name].apply(lambda x: len(str(x).split()))
    print(
        f"average num words after removing words with less than {min_num_word_freq} occurances: {dta['num_words'].values.mean()}"
    )
    return dta


def write_columns_to_text(
    dta,
    text_filename="output.txt",
    seperator=" - ",
    columns=None,
    columns_to_clean=None,
):
    """this function takes a dataframe and writes it to a text file

    Arguments:
        dta {pandas dataframe} -- the input dataframe

    Keyword Arguments:
        text_filename {str} -- the name of the file you want to write (default: {"output.txt"})

        seperator {str} -- the seperator you want between each column (default: {" - "})

        columns {list} -- list of columns you want to include in the text document (default: {None})

        columns_to_clean {list} -- list of columns that contain large blocks of text for a basic cleaning (default: {None})
    """
    import re
    import pathlib

    if columns:
        dta = dta[columns]
    if columns_to_clean:
        for column in columns_to_clean:
            # column_list = dta[column].to_list()
            print(len(dta[column]))
            dta[column] = [
                re.sub(r"\r\n+|\n+|\r+", " [Newline_Char] ", text) for text in dta[column]
            ]
            print(len(dta[column]))
            # dta[column] = column_list
    if len(dta) > 1000:
        print(f"You have {len(dta)} rows this file maybe too large to open easily")
    dta_values = dta.values.tolist()
    final_list = []
    for row in dta_values:
        final_list.append(" - ".join(str(row)))
    final_list = "\n\n\n".join(final_list)
    # get path and write to file
    path = pathlib.Path(".").parent
    if text_filename != "output.txt":
        if text_filename[-4:] != ".txt":
            filename = path / f"{text_filename}.txt"
            print(filename)
        else:
            filename = path / text_filename
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.touch()
    filename.write_text(final_list, encoding="utf-8")
