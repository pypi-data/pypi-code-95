from collections import OrderedDict
import collections
from wbnlu import logger
from pathlib import Path
from .fileio import read_yaml_file
from random import shuffle
import csv
import json
from ..components.text_normalizer import normalize
from ..components.text_normalizer import is_ascii_char
from ..components.text_normalizer import is_unigram

#from spacy.lang.zh import STOP_WORDS

config_path = Path(__file__).parent
CONFIG = read_yaml_file((config_path / "../configs/other_config.yml").resolve())
TEXT_LENTH_LIMIT = CONFIG['MAX_TEXT_LENGTH']
FREQ_CUT_OFF = CONFIG['FREQ_CUT_OFF']
REMOVE_UNIGRAMS = CONFIG['REMOVE_UNIGRAMS']
NOTMALIZE_TEXT = CONFIG['NOTMALIZE_TEXT']


logger = logger.my_logger(__name__)


def mytime(start, end):
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    logger.info("Total time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


def remove_unserializable_results(doc):
    doc.user_data = {}
    for x in dir(doc._):
        if x in ['get', 'set', 'has']: continue
        setattr(doc._, x, None)
    for token in doc:
        for x in dir(token._):
            if x in ['get', 'set', 'has']: continue
            setattr(token._, x, None)
    return doc

def ascii_char_merge_as_token(doc):
    spans = []
    asc_start = -1
    #doc_list = list(doc)
    for index, token in enumerate(doc):
        # print(asc_start, index, token, token.is_ascii, bool(token.whitespace_), spans)
        if token.is_ascii and not token.is_punct:
            if asc_start == -1:
                asc_start = index
            if bool(token.whitespace_):
                spans.append(doc[asc_start:index + 1])
                asc_start = -1
            if token.text == ' ':
                spans.append(doc[asc_start:index + 1])
                asc_start = -1
        else:
            # append ascii string
            if asc_start != -1:
                spans.append(doc[asc_start:index])
                asc_start = -1
            # append chinese
            spans.append(doc[index:index + 1])

    if asc_start != -1:
        spans.append(doc[asc_start:])

    with doc.retokenize() as retokenizer:
        for span in spans:
            span_length = len(span)
            if span_length>1 and span.text.endswith(' '):
                span = span[0:span_length-1]
            elif span_length>1 and span.text.startswith(' '):
                span = span[1:span_length]
            if span_length>1:
                retokenizer.merge(span)
    return doc


def ascii_char_merge_as_token2(doc):
    prev_index = -1
    start = -1
    end = -1

    spans = []
    current_span = None
    for index, token in enumerate(doc):
        if token.is_ascii:
            current_ascii_index = index
            if start == end:
                if token.text != ' ':
                    start = current_ascii_index
            elif current_ascii_index - prev_index == 1:
                end = current_ascii_index
                current_span = doc[start:end + 1]
            else:
                if current_span:
                    spans.append(current_span)
                current_span = None
                start = index
                end = index
            prev_index = current_ascii_index
        else:
            if current_span:
                spans.append(current_span)
            current_span = None
            prev_index = index
            start = index
            end = index

    if current_span:
        spans.append(current_span)

    with doc.retokenize() as retokenizer:
        for span in spans:
            span_length = len(span)
            if span_length > 1 and span.text.endswith(' '):
                span = span[0:span_length - 1]
            elif span_length > 1 and span.text.startswith(' '):
                span = span[1:span_length]
            if span_length>1:
                retokenizer.merge(span)
    return doc

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def checkEnglish(char):
    if (char >= '\u0041' and char <= '\u005a') or (char >= '\u0061' and char <= '\u007a') or (char >= '\u002e' and char <= '\u003a'):
        return True
    else:
        return False


def get_url(doc):
    spans = []
    flag = False
    start = -1
    end = -1
    for index, token in enumerate(doc):
        if not flag:
            if token.text == 'http':
                flag = True
                start = index
        else:
            for c in list(token.text):
                # print (c)
                if not checkEnglish(c):
                    end = index
                    flag = False
                    break
        if end == -1:
            end = len(doc)
    spans.append(doc[start: end])

    with doc.retokenize() as retokenizer:
        for span in spans:
            span_length = len(span)
            if span_length>1 and span.text.endswith(' '):
                span = span[0:span_length-1]
            elif span_length>1 and span.text.startswith(' '):
                span = span[1:span_length]
            if span_length>1:
                retokenizer.merge(span)
    return doc


def sort_dict_by_value(mydict, reverse_order=True):
    sorted_dict = OrderedDict()

    for k, v in sorted(mydict.items(), key=lambda item: item[1], reverse=reverse_order):
        sorted_dict[k] = v

    return sorted_dict


def sort_list(lst, reversed=True):
    lst.sort(key=len, reverse=reversed)
    return lst

def shuffle_list(l, n):
    if n >= len(l):
        raise ValueError("Invalid randomized number. Out of list index boundary")
    shuffle(l)
    return set(l[:n])


def has_digit(text):
    return any(char.isdigit() for char in text)


def text_length(text):
    length = 0
    has_ascii = False
    for c in text:
        if not is_ascii_char(c):
            length += 1
        else:
            has_ascii = True

    if has_ascii:
        length += 1

    return length

# Here 'token' is a NLP token, not text
def non_standard_token(token, REMOVE_UNIGRAMS):
    if token.is_stop or token.is_digit or token.is_ascii:
        return True

    if REMOVE_UNIGRAMS and is_unigram(token.text):
        return True

    return False


def raw_freq_from_text_file(filename, freq_length_list=None, split_with_space=None, test_mode=None):
    freq = collections.Counter()
    freqs = []
    flist_size = 0
    textlines = []
    if freq_length_list is not None:
        flist_size = len(freq_length_list)
        for i in range(flist_size):
            freqs.append(collections.Counter())
        if flist_size == 0:
            freqs.append(collections.Counter())
    else:
        freqs.append(freq)

    with open(filename, 'r') as f:
        log_every_n = 1000000
        line_number = 0
        for line in f:
            # if '年妆容' in line:
            #      print(line)
            if not line:
                continue

            if len(line) > TEXT_LENTH_LIMIT:
                continue

            if NOTMALIZE_TEXT:
                line = normalize(line)

            textlines.append(line)

            lines = []

            if split_with_space:
                lines = [l.strip() for l in line.split(' ') if len(l) > 1]
            else:
                lines.append(line)

            for lne in lines:

                ln = [lne]
                if flist_size != 0:
                    txt_length = text_length(ln[0])
                    ln_size = str(txt_length)
                    if flist_size == 1:
                        if ln_size == freq_length_list[0]:
                            freqs[0].update(ln)
                    elif flist_size == 2:
                        if ln_size == freq_length_list[0]:
                            freqs[0].update(ln)
                        elif ln_size == freq_length_list[1]:
                            freqs[1].update(ln)
                    elif flist_size == 3:
                        if ln_size == freq_length_list[0]:
                            freqs[0].update(ln)
                        elif ln_size == freq_length_list[1]:
                            freqs[1].update(ln)
                        elif ln_size == freq_length_list[2]:
                            freqs[2].update(ln)
                    elif flist_size == 4:
                        if ln_size == freq_length_list[0]:
                            freqs[0].update(ln)
                        elif ln_size == freq_length_list[1]:
                            freqs[1].update(ln)
                        elif ln_size == freq_length_list[2]:
                            freqs[2].update(ln)
                        elif ln_size == freq_length_list[3]:
                            freqs[3].update(ln)
                    elif flist_size == 5:
                        if ln_size == freq_length_list[0]:
                            freqs[0].update(ln)
                        elif ln_size == freq_length_list[1]:
                            freqs[1].update(ln)
                        elif ln_size == freq_length_list[2]:
                            freqs[2].update(ln)
                        elif ln_size == freq_length_list[3]:
                            freqs[3].update(ln)
                        elif ln_size == freq_length_list[4]:
                            freqs[4].update(ln)
                    elif flist_size == 6:
                        if ln_size == freq_length_list[0]:
                            freqs[0].update(ln)
                        elif ln_size == freq_length_list[1]:
                            freqs[1].update(ln)
                        elif ln_size == freq_length_list[2]:
                            freqs[2].update(ln)
                        elif ln_size == freq_length_list[3]:
                            freqs[3].update(ln)
                        elif ln_size == freq_length_list[4]:
                            freqs[4].update(ln)
                        elif ln_size == freq_length_list[5]:
                            freqs[5].update(ln)
                    elif flist_size == 7:
                        if ln_size == freq_length_list[0]:
                            freqs[0].update(ln)
                        elif ln_size == freq_length_list[1]:
                            freqs[1].update(ln)
                        elif ln_size == freq_length_list[2]:
                            freqs[2].update(ln)
                        elif ln_size == freq_length_list[3]:
                            freqs[3].update(ln)
                        elif ln_size == freq_length_list[4]:
                            freqs[4].update(ln)
                        elif ln_size == freq_length_list[5]:
                            freqs[5].update(ln)
                        elif ln_size == freq_length_list[6]:
                            freqs[6].update(ln)
                    else:
                        raise ValueError('Invalid frequency list set, support up to 7 freq list:', flist_size)
                else:
                    freqs[0].update(ln)

            line_number += 1
            if (line_number % log_every_n) == 0:
                logger.info("Line: {}".format(str(line_number)))

            if test_mode is not None:
                if line_number > test_mode:
                    break

    return freqs, textlines


def read_text_to_textlines(filename, line_length=None, split_when_space=None, test_mode=None):
    textlines = []
    line_number = 0
    with open(filename, encoding='utf-8') as cfile:
        log_every_n = 1000000
        for line in cfile:
            if not line:
                continue
            if len(line) > TEXT_LENTH_LIMIT:
                continue
            if NOTMALIZE_TEXT:
                line = normalize(line)

            lines = []
            if split_when_space:
                lines = [l.strip() for l in line.split(' ')]
            else:
                lines.append(line)
            filtered_lines_by_length = []
            for ln in lines:
                if line_length is not None and text_length(ln) != line_length:
                    continue
                filtered_lines_by_length.append(ln)
            line_number += 1

            if test_mode is not None:
                if line_number > test_mode:
                    break

            if (line_number % log_every_n) == 0:
                logger.info("Line: {}".format(str(line_number)))

            textlines.extend(filtered_lines_by_length)

    logger.info("Total line size: {}".format(str(len(textlines))))

    return textlines


def frequency_with_batch(textlines, freq_counter, enable=[]):
    from wbnlu import nlps
    docs = json.loads(json.dumps(nlps(textlines, enable=enable)))
    #json_results = json.loads(docs)
    log_every_n = 100000
    for i, doc in enumerate(docs):
        if (i % log_every_n) == 0:
            logger.info('Doc: {}'.format(str(i)))
        log_every_n += 1
        tokens = doc['nps']
        freq_counter.update(tokens)


def frequency_from_csv_file(filename, column_index):
    freq_counter = collections.Counter()
    frequency_with_batch(read_csv_to_textlines(filename, column_index), freq_counter)
    return freq_counter


def frequency_from_text_file(filename, data_batch, enable=[]):
    freq_counter = collections.Counter()
    with open(filename, 'r') as f:
        for i, batch in enumerate(read_batch(f)):
            logger.info("Batch {}".format(str(i)))
            frequency_with_batch(batch, freq_counter, enable)
            if data_batch == i+1:
                break

    return freq_counter


def frequency_from_textlines(textlines):
    freq_counter = collections.Counter()
    frequency_with_batch(textlines, freq_counter)

    return freq_counter


def read_csv_to_textlines(filename, column_index):
    textlines = []
    line_number = 0
    with open(filename) as cfile:
        csv_file = csv.reader(cfile, delimiter='\t')
        log_every_n = 1000000

        for row in csv_file:
            line_number += 1
            if (line_number % log_every_n) == 0:
                logger.info("Line: {}".format(str(line_number)))
            if len(row) > column_index:
                text = row[column_index]
                if NOTMALIZE_TEXT:
                    text = normalize(text)
                textlines.append(text)
            else:
                logger.warning("Invalid: {} {}".format(str(line_number), str(row)))
                # break

    logger.info("Total line size: {}".format(str(len(textlines))))

    return textlines


def read_batch_from_csv(file_handle, batch_size, delimiter, csv_reader=None, text_field='text', disable=[], remove_hash=False, text_lower=False,
            remove_punct=False, remove_emojis=True, remove_all_space=False, remove_all_but_one_space=True):
    text_batch = []
    row_batch = []
    if not csv_reader:
        csv_reader = csv.DictReader(file_handle, delimiter=delimiter, quoting=csv.QUOTE_NONE)
    #next(csv_reader)
    for row in csv_reader:
        if not row:
            continue
        if text_field not in row:
            text = ''
            logger.warning('No text field ... {}'.format(str(row)))
        else:
            text = row[text_field]
        if 'text_normalizer' not in disable:
            text = normalize(text, remove_hash, text_lower, remove_punct, remove_emojis, remove_all_space,
                             remove_all_but_one_space)
        if len(text) > TEXT_LENTH_LIMIT:
            continue
        text_batch.append(text)
        row_batch.append(row)

        if len(text_batch) == batch_size:
            yield (text_batch, row_batch)
            text_batch.clear()
            row_batch.clear()

    if text_batch and row_batch:
        yield (text_batch, row_batch)


def read_batch(file_handle, batch_size=100000):
    batch = []
    for line in file_handle:
        if not line:
            continue
        if len(line) > TEXT_LENTH_LIMIT:
            continue
        batch.append(line)
        if len(batch) == batch_size:
            yield batch
            batch.clear()
    if batch:
        yield batch

def get_batch_from_list(all_text_data, batch_size=10000):
    return [all_text_data[i:i + batch_size] for i in range(0, len(all_text_data), batch_size)]

def fix_nulls(csv_reader):
    for line in csv_reader:
        yield line.replace('\0', '')

# def space_tokenize(line, stopwords=False):
#     tokens = []
#     for token in line.split(' '):
#         if token:
#             if stopwords:
#                 if token not in STOP_WORDS:
#                     tokens.append(token)
#             else:
#                 tokens.append(token)
#     return tokens
