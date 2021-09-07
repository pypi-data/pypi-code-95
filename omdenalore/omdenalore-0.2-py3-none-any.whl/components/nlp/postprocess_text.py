import re
import warnings
from itertools import groupby
from typing import List, Set, Union

import pandas as pd
import spacy


def doc2df(doc: spacy.tokens.Doc, regex_pmid: str = r"PMID: (\d+)") -> pd.DataFrame:
    """
    Get a dataframe from SpaCy `Doc` objects.

    :param doc: A single spaCy `Doc` object with annotations (entities)
    :type doc: spacy.tokens.Doc
    :param regex_pmid: Raw string with regex to get the PMID numbers from text (defaults to `r"PMID: (\\d+)"`
    :type regex_pmid: str
    :return: Pandas dataframe with columns [`pmid`,`text`,`start`,`stop`,`entity`,`entity_text`]
    """

    match = re.search(regex_pmid, doc.text)
    if match:
        pmid = match.group(1)
    else:
        raise ValueError("Could not find PMID.")
    if len(doc.ents) <= 0:
        annotations = [(None, None, None, None)]
        warnings.warn(f"No annotations found on document with PMID `{pmid}`.")
    else:
        annotations = [(e.start_char, e.end_char, e.label_, e.text) for e in doc.ents]
    start, stop, entity, ent_text = zip(*annotations)
    df = pd.DataFrame(
        {
            "pmid": [pmid] * len(annotations),
            "text": [doc.text] * len(annotations),
            "start": start,
            "stop": stop,
            "entity": entity,
            "entity_text": ent_text,
        }
    )
    return df


def doc2df_wide(
    doc: spacy.tokens.Doc, regex_pmid: str = r"PMID: (\d+)"
) -> pd.DataFrame:
    """
    Get a wide dataframe from SpaCy `Doc` objects.

    :param doc: A single spaCy `Doc` object with annotations (entities)
    :type doc: spacy.tokens.Doc
    :param regex_pmid: Raw string with regex to get the PMID numbers from text (defaults to `r"PMID: (\\d+)"`
    :type regex_pmid: str
    :return: Pandas dataframe with one column for each {`start`,`stop`,`entity_text`} in entity
    """

    df = doc2df(doc=doc, regex_pmid=regex_pmid).reset_index(drop=True)
    # catch edge-case where there are no entities predicted in document
    if df["entity"].isna().any():
        return df[["pmid", "text"]].set_index("pmid")

    # pivot table (aggregate duplicate pmid entries using lists)
    df = df.pivot_table(
        index=["pmid", "text"],
        columns="entity",
        values=["start", "stop", "entity_text"],
        aggfunc=list,
    ).swaplevel(axis="columns")
    df.columns = df.columns.to_flat_index()

    return df.sort_index(axis=1).reset_index("text")


def df2jsonl(
    df: pd.DataFrame,
    path: str = None,
    pmid: str = "pmid",
    text: str = "text",
    start: str = "start",
    stop: str = "stop",
    entity: str = "entity",
    entity_text: str = "entity_text",
) -> Union[str, None]:
    """
    Get the output format JSONL from a pandas dataframe

    :param df: Dataframe with entity information
    :type df: pd.DataFrame
    :param path: Destination file path (if None will return a string with equivalent JSONL
    :type path: str
    :param pmid: Column name for PMID column
    :type pmid: str
    :param text: Column name for text column
    :type text: str
    :param start: Column name for start column
    :type start: str
    :param stop: Column name for stop column
    :type stop: str
    :param entity: Column name for entity column
    :type entity: str
    :param entity_text: Column name for entity_text column
    :type entity_text: str
    :return: None if path is provided (file is written to disk), JSONL string if path is None
    Output JSONL file has the shape `{id:pmid, text: <abstract>, predictions: [{start: x, end: y, entity:x}, ...]}`
    """
    _df = df.copy()
    _df = _df.reset_index(drop=True)
    _df["predictions"] = pd.Series(
        zip(_df[start], _df[stop], _df[entity], _df[entity_text])
    ).apply(lambda x: dict(zip(["start", "end", "entity", "entity_text"], x)))
    _df = _df.groupby([pmid, text])["predictions"].apply(list).reset_index()
    return _df.to_json(path, orient="records", lines=True)


def list2iob(tags: List[str]) -> List[str]:
    """
    Go from a list of strings to IOB list of tags.

    :param tags: List of tags
    :type tags: List[str]

    :return: List of IOB tags
    """

    def _add_iob_prefix(idx: int, tag: str) -> str:
        """
        Add IOB prefix to sequence of repeated tags.
        """
        return tag if tag == "O" else "B-" + tag if idx == 0 else "I-" + tag

    return [
        _add_iob_prefix(i, grp) for _, grp in groupby(tags) for i, grp in enumerate(grp)
    ]


def adjust_tags(
    tags: List[str], tag_set: Set[str] = None, length: int = 512
) -> List[List[str]]:
    """
    Keep only tags that were used in training and get all list of tokens to the same length.

    :param tags: List of tags
    :type tags: List[str]
    :param tag_set: Set of tags to keep
    :type tag_set: Set[str]
    :param length: Length of tokens to keep

    :return: List of tags
    """

    def _pad_and_truncate(tags_doc: List[str], seq_len: int) -> List[List[str]]:
        """Get all the list of tags to the correct length."""
        tags_doc = tags_doc + ["O"] * (seq_len - len(tags_doc))  # pad
        tags_doc = tags_doc[:512]  # truncate
        return tags_doc

    if tag_set is None:
        tag_set = set(tags)
    else:
        # put tag set in IOB format
        tag_set = sorted(
            [tag.split("-")[-1] for tag in tag_set] * 2
        )  # go to list and duplicate
        tag_set = list2iob(tag_set)  # make IOB set

    # keep tag if it's in the tag set
    tags = [tag if tag in tag_set else "O" for tag in tags]
    return _pad_and_truncate(tags, seq_len=length)
