import os
import collections
from nltk.tokenize import sent_tokenize


def get_corpus_filepaths(dirpath):
    """
    Finds corpus fp given a directory.
    """
    en = de = dirpath
    for file in os.listdir(dirpath):
        if file.lower().endswith(".de"):
            de = os.path.join(dirpath, file)

        elif file.lower().endswith(".en"):
            en = os.path.join(dirpath, file)

    return en, de


def load_text_from_file(fp):
    """
    Loads text from a file path.
    """
    with open(fp, "r", encoding="utf-8") as f:
        ret = " ".join(f.read().splitlines())

    return ret


def create_directory():
    """
    Creates a directory within which the results will be stored
    """
    cwd = os.getcwd()
    results_directory = cwd + "\\results"
    os.makedirs(results_directory, exist_ok=True)

    return results_directory


def export_unscored(dictionary, directory):
    """
    Removes unscorable words from the dictionary
    and exports them to a separate list in the results directory
    """
    new_dictionary = collections.defaultdict()
    unscorable = collections.defaultdict()
    for key, value in dictionary.items():
        if dictionary[key]["score"] == 0:
            new_dictionary.update({key: value})

        elif dictionary[key]["score"] == "n/a":
            unscorable.update({key: value})

    unscorable_document = directory + "\\unscored.txt"
    for key in unscorable:
        with open(unscorable_document, "a", encoding="utf-8") as f:
            f.write(key + "\n")

    return new_dictionary


def print_neat_list(dictionary):
    """
    Prints the words and scores from the
    dictionary into a neat, readable format.
    """
    neat_list = []
    for item in dictionary:
        word, score = item, dictionary[item]["score"]
        neat_list.append((score, word))

    neat_list_sorted = sorted(neat_list, key=lambda x: x[0], reverse=True)

    print("\n\n\nThe final list of scored words:")
    for score, word in neat_list_sorted:
        print(score, word)

    return neat_list_sorted


def export_data_full(dictionary, directory):
    """
    Exports all dictionary data into list in results folder.
    Includes words, scores, translations, and TECs.
    """
    listed = []
    export_file = directory + "\\scored.txt"
    for item in dictionary:
        score, word, translations, TECs = (
            dictionary[item]["score"],
            item,
            dictionary[item]["translations"],
            dictionary[item]["TECs"],
        )
        listed.append((score, word, translations, TECs))

    listed_sorted = sorted(listed, key=lambda x: x[0], reverse=True)
    with open(export_file, "a", encoding="utf-8") as f:
        for item in listed_sorted:
            f.write(str(item))
            f.write("\n")


def export_original_text(text, directory):
    export_file = directory + "\\text_original.txt"
    with open(export_file, "a", encoding="utf-8") as f:
        for line in text:
            f.write(line)
            f.write("\n")


def export_marked_text(text, neat_list, directory):
    export_file = directory + "\\text_marked.txt"
    text_joined = "".join(text)
    for tpl in neat_list:
        text_joined = text_joined.replace(
            tpl[1],
            "[{word}:{score}]".format(
                word=tpl[1], score="{0:.2f}".format(tpl[0])
            ),
        )

    text_split = sent_tokenize(text_joined)
    with open(export_file, "a", encoding="utf-8") as f:
        for line in text:
            f.write(line)
            f.write("\n")
