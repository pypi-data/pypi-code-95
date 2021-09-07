import re


def noise_removal(input_text, noise_list=[]):
    """
    Remove noise from the input text.
    This function can be use to remove comman english words like "is, a , the".
    You can add your own noise words in the optional paramters "noise_list"
    default noise_list = ["is", "a", "this", "the" , "an"]

    :param input_text: Input text to remove noise from
    :type input_text: str
    :param noise_list: (Optional) List of words that you want to remove from the input text
    :type noise_list: list
    :returns: Clean text with no noise
    """

    assert isinstance(input_text, str), "input should be a string"
    if len(noise_list) == 0:
        noise_list = ["is", "a", "this", "the", "an"]

    words = input_text.split()
    noise_free_words = [word for word in words if word not in noise_list]
    noise_free_text = " ".join(noise_free_words)
    return noise_free_text


def remove_regex_pattern(input_text, regex_pattern):
    """
    Remove any regular expressions from the input text

    :param input_text: Input text to remove regex from
    :type input_text: str
    :param noise_list: string of regex that you want to remove from the input text
    :type noise_list: string
    :returns: Clean text with removed regex

    :example:

    >>> regex_pattern = "#[\w]*"
    >>> remove_regex_pattern("remove this #hastag" , regex_pattern)
    "remove this  hastag"
    """

    urls = re.finditer(regex_pattern, input_text)
    for i in urls:
        input_text = re.sub(i.group().strip(), "", input_text)

    return input_text


def remove_hashtags(text):
    """
    Removing hastags from the input text
    :param text: Input text to remove hastags from
    :type input_text: str
    :returns: output text without hastags

    :example:

    >>> remove_hashtags("I love #hashtags")
    "I love "
    """
    return remove_regex_pattern(text, r"(#\w+)")


def remove_url(text):
    """
    Removing urls from the input text
    :param text: Input text to remove urls from
    :type input_text: str
    :returns: text with standard words

    :example:

    >>> remove_urls('I like urls http://www.google.com')
    'I like urls '
    """
    return remove_regex_pattern(text, r"(#\w+)")


def standardize_words(input_text, lookup_dictionary):
    """
    Replace acronyms, hastags, colloquial slangs etc with standard words

    Text data often contains words or phrases which are not present in any standard lexical dictionaries.
    These pieces are not recognized by search engines and models.

    :param input_text: Input text to remove regex from
    :type input_text: str
    :param lookup_dictionary: Dictionary with slang as index and standard word as item or value
    :type lookup_dictionary: dict
    :returns: text with standard words

    :example:

    >>> lookup_dict = {'rt':'Retweet', 'dm':'direct message', "awsm" : "awesome", "luv" :"love", "..."}
    >>> standardize_words(rt I luv to dm, it's awsm)
    Retweet I love to direct message, it's awesome
    """
    words = input_text.split()
    new_words = []
    for word in words:
        if word.lower() in lookup_dictionary:
            word = lookup_dictionary[word.lower()]
        new_words.append(word)
        new_text = " ".join(new_words)
    return new_text
