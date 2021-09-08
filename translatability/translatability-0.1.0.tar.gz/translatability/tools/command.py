from .. import io
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from ..preprocessing import extract
from ..translatability import (
    lemmatize_translations,
    lemmatize_TECs,
    normalize_dictionary,
    score_translatability,
    normalize_TECs,
    generate_test_dictionary,
)
import os
import collections


def run(*args, **kwargs):
    assert (
        kwargs["file"] is not None
    ), "You must input a file with the -f param."

    file = kwargs.pop("file")
    # Parse the arguments.
    corpora = []
    for k, v in kwargs.items():
        if v == "check_string_for_empty":
            continue

        corpora.append(v)

    assert all(
        [os.path.exists(pth) for pth in corpora]
    ), "You must provide absolute paths to the corpora."

    text = io.load_text_from_file(file)
    cwd = os.getcwd()
    # Create a dir to store the extracted segments.
    segments_directory = cwd + "\\segments"
    lemmatizer = WordNetLemmatizer()

    print("\n\n\nExtracting nouns...")

    noun_candidates = extract.extract_nouns(text)
    noun_candidates = extract.clean_nouns(noun_candidates)

    print("\n\n\nExtracting compounds...")
    compound_candidates = extract.split_compounds(noun_candidates)

    print("\n\n\nAssessing compound segments...")
    compound_translations = extract.extract_compounds(compound_candidates)
    dictionary_final = collections.defaultdict(dict)
    for word in compound_translations:
        dictionary_final.update(
            {word: dict(translations=compound_translations[word])}
        )

    print("\n\n\nSegment filepaths:")
    os.makedirs(segments_directory, exist_ok=True)
    for word in dictionary_final:
        dictionary_final[word].update(
            extract.prepare_segment_file(word, segments_directory)
        )

    for i in dictionary_final.items():
        print(i)

    for i, corpus in enumerate(corpora):
        print(f"Checking Corpus {i+1} ...")
        fp_en, fp_de = io.get_corpus_filepaths(corpus)
        c = list(extract.prepare_corpus(fp_de, fp_en))
        for word, v in dictionary_final.items():
            print(f"Searching for segments containing {word} ...")
            fp_segments = v["segments"]
            extract.write_segments(extract.query_corpus(c, word), fp_segments)

    extract.extract_translation_candidates(dictionary_final)
    results = io.create_directory()
    dictionary_final = io.export_unscored(dictionary_final, results)
    lemmatize_translations(dictionary_final)
    lemmatize_TECs(dictionary_final)
    normalize_dictionary(dictionary_final)
    score_translatability(dictionary_final)
    text = sent_tokenize(text)
    neat_list = io.print_neat_list(dictionary_final)
    io.export_data_full(dictionary_final, results)
    io.export_original_text(text, results)
