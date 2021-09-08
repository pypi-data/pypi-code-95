import collections
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
import heapq


lemmatizer = WordNetLemmatizer()
brown_ic = wordnet_ic.ic("ic-brown.dat")
semcor_ic = wordnet_ic.ic("ic-semcor.dat")


def generate_test_dictionary():
    with open("data.txt", "r", encoding="utf-8") as f:
        lines = [line for line in f.read().splitlines() if line]
        lines_dict = collections.defaultdict()
        for line in lines:
            string1 = str(line).replace("(", "{", 1).replace(",", ":", 1)
            string2 = string1[::-1].replace(")", "}", 1)
            string3 = string2[::-1]
            dictionary = eval(string3)
            lines_dict.update(dictionary)

    return lines_dict


def lemmatize_translations(dictionary):
    """
    Normalizes translations by
    lemmatizing and rendering in lower case.
    """
    lemmatizer = WordNetLemmatizer()
    for word in dictionary:
        translations = []
        for translation in dictionary[word]["translations"]:
            translations.append(lemmatizer.lemmatize(translation).lower())

        dictionary[word]["translations"] = translations


def lemmatize_TECs(dictionary):
    """
    Normalizes TECs by lemmatizing a
    nd rendering in lower case
    """
    lemmatizer = WordNetLemmatizer()
    for word in dictionary:
        TECs = []
        for TEC in dictionary[word]["TECs"]:
            TECs.append(
                tuple(
                    [
                        lemmatizer.lemmatize(TEC[0]).lower(),
                        TEC[1],
                        TEC[2],
                        TEC[3],
                    ]
                )
            )

        dictionary[word]["TECs"] = TECs


def normalize_dictionary(dictionary):
    """
    The output is that the scores for
    ea are updated according to the
    calculations here reached.
    """
    for word in dictionary:
        if len(dictionary[word]["TECs"]) > 2:
            dictionary[word]["score"] = [0]
            dictionary[word]["TECs"] = normalize_TECs(
                dictionary[word]["translations"], dictionary[word]["TECs"]
            )

        elif dictionary[word]["TECs"][0][1] >= 0.2:
            dictionary[word]["score"] = [1]

        elif dictionary[word]["TECs"][0][1] < 0.2:
            dictionary[word]["score"] = [0]


def normalize_TECs(translations, TECs):
    """
    Accepts a list of tuples from dictionary entry and
    reduces this list to two entries based on
    translations of same dictionary entry,
    normalizing to length of other entries.
    """
    TECs_new = []
    for translation in translations:
        TEC_similarity_comparision = collections.defaultdict()
        for TEC in TECs:
            synset_translation = wn.synsets(translation)
            synset_TEC = wn.synsets(TEC[0])
            similarity_measures = []
            if len(synset_translation) > 0 and len(synset_TEC) > 0:
                for x in synset_translation:
                    for y in synset_TEC:
                        similarity = x.wup_similarity(y)
                        if similarity:
                            similarity_measures.append(similarity)

                        else:
                            similarity_measures.append(0)

                TEC_similarity_comparision.update({TEC[0]: max(similarity_measures)})

            else:
                similarity_measures.append(0)
                TEC_similarity_comparision.update({TEC[0]: max(similarity_measures)})

        most_similar = max(
            TEC_similarity_comparision,
            key=lambda k: TEC_similarity_comparision[k],
        )
        translation_matched_TEC = (most_similar, 0, 0, 0)
        TECs_new.append(translation_matched_TEC)

    return TECs_new


def score_translatability(dictionary):
    """
    Scores each word in a dictionary according to
    the average of several semantic distance measures.
    Returns the original score list as a single float.
    """
    for word in dictionary:
        scores = dictionary[word]["score"]
        translations = dictionary[word]["translations"]
        TECs = dictionary[word]["TECs"]
        scores.append(wordnet_similarity_wup(translations, TECs))
        scores.append(wordnet_similarity_path(translations, TECs))
        scores.append(wordnet_similarity_lin(translations, TECs))
        dictionary[word]["score"] = sum(scores) / 4


def wordnet_similarity_wup(translations, TECs):
    scores_all = []
    for translation in translations:
        for TEC in TECs:
            synset_translation = wn.synsets(translation)
            synset_TEC = wn.synsets(TEC[0])
            similarity_measures = []
            if len(synset_translation) > 0 and len(synset_TEC) > 0:
                for x in synset_translation:
                    for y in synset_TEC:
                        similarity = x.wup_similarity(y)
                        if similarity:
                            similarity_measures.append(similarity)

                        else:
                            similarity_measures.append(0)

                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

            else:
                similarity_measures.append(0)
                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

    scores_avg = sum(scores_all) / 4
    return scores_avg


def wordnet_similarity_path(translations, TECs):
    scores_all = []
    for translation in translations:
        for TEC in TECs:
            synset_translation = wn.synsets(translation)
            synset_TEC = wn.synsets(TEC[0])
            similarity_measures = []
            if len(synset_translation) > 0 and len(synset_TEC) > 0:
                for x in synset_translation:
                    for y in synset_TEC:
                        similarity = x.path_similarity(y)
                        if similarity:
                            similarity_measures.append(similarity)

                        else:
                            similarity_measures.append(0)

                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

            else:
                similarity_measures.append(0)
                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

    scores_avg = sum(scores_all) / 4
    return scores_avg


def wordnet_similarity_jcn(translations, TECs):
    scores_all = []
    for translation in translations:
        for TEC in TECs:
            synset_translation = wn.synsets(translation)
            synset_TEC = wn.synsets(TEC[0])
            similarity_measures = []
            if len(synset_translation) > 0 and len(synset_TEC) > 0:
                for x in synset_translation:
                    for y in synset_TEC:
                        try:
                            similarity = x.jcn_similarity(y, brown_ic)
                            if similarity:
                                similarity_measures.append(similarity)

                            else:
                                similarity_measures.append(0)

                        except nltk.corpus.reader.wordnet.WordNetError:
                            similarity_measures.append(0)

                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

            else:
                similarity_measures.append(0)
                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

    scores_avg = sum(scores_all) / 4
    return scores_avg


def wordnet_similarity_lin(translations, TECs):
    scores_all = []
    for translation in translations:
        for TEC in TECs:
            synset_translation = wn.synsets(translation)
            synset_TEC = wn.synsets(TEC[0])
            similarity_measures = []
            if len(synset_translation) > 0 and len(synset_TEC) > 0:
                for x in synset_translation:
                    for y in synset_TEC:
                        try:
                            similarity = x.lin_similarity(y, semcor_ic)
                            if similarity:
                                similarity_measures.append(similarity)

                            else:
                                similarity_measures.append(0)

                        except nltk.corpus.reader.wordnet.WordNetError:
                            similarity_measures.append(0)

                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

            else:
                similarity_measures.append(0)
                scores_all.append(sum(heapq.nlargest(2, similarity_measures)) / 2)

    scores_avg = sum(scores_all) / 4
    return scores_avg
