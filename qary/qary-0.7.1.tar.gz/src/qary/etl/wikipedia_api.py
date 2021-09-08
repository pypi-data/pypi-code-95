import time
import gzip
import copy
from pathlib import Path
from itertools import chain

from tqdm import tqdm
import pandas as pd
import numpy as np
from wikipediaapi import Wikipedia

from qary.constants import DATA_DIR, QUESTION_STOPWORDS, ES_URL
from qary.spacy_language_model import load
from qary.etl.netutils import download_if_necessary
from qary.etl import elastic, utils

import logging
log = logging.getLogger(locals().get('__name__', ''))

nlp = load('en_core_web_md')
EXCLUDE_HEADINGS = ['See also', 'References', 'Bibliography', 'External links']
TOPIC_TITLES = {
    'chatbot': ['Chatbot', 'ELIZA', 'Turing test', 'AIML', 'Chatterbot', 'Loebner prize', 'Chinese room'],
}


class WikiNotFound:
    text = ''
    summary = ''


def read_and_hash_titles(filepath=None, chunksize=100000, numchunks=None):
    """ Numpy crashing due to unit32() on NaNs in wikipedia titles

    >>> hashes = read_and_hash_titles(chunksize=1000, numchunks=8)
    >>> hashes.shape
    (8000,)
    >>> utils.md5('fu') in hashes
    True
    """
    if filepath is None:
        filepath = 'wikipedia-titles-alphaonly'
    filepath = download_if_necessary(filepath)
    hashes = []
    for i, chunk in enumerate(tqdm(pd.read_csv(filepath, chunksize=chunksize))):
        titles = tuple(chunk.dropna()[chunk.columns[0]].astype(str))
        hashes += list(
            utils.md5(utils.squash_wikititle(str(title))) for title in titles)
        if numchunks is not None and i >= numchunks - 1:
            break
    return np.array(hashes, dtype=np.uint64)


def save_hashes(hashes=None,
                dest_filepath=Path(DATA_DIR, 'corpora', 'wikipedia', 'wikipedia-titles-alphaonly-hashed.uint64.npy.gz')):
    r""" Save a compressed set of hashed Wikipedia titles to be used later to predict whether an n-gram is a valid title

    >>> dest = Path(DATA_DIR, 'doctest-save-hashes.uint64.npy.gz')
    >>> str(save_hashes(hashes='1 2 3 123456789'.split(), dest_filepath=dest)).endswith(str(dest))
    True
    """
    hashes = np.fromiter((np.uint64(h) for h in hashes), dtype=np.uint64)
    with gzip.open(dest_filepath, 'wb') as fout:
        np.save(fout, hashes)
    return dest_filepath


def elastic_results_as_page_dict(results):
    see_also_links = []
    return {}
    return dict(
        title=results['title'],
        text=results['text'],
        summary=results['summary'],
        see_also_links=see_also_links)


def guess_topic(query=None):
    """ Use hard coded TOPIC_TITLES dict to infer a topic based on the last word in a question

    >>> guess_topic('What ELIZA?')
    'chatbot'
    >>> guess_topic('What are ChatboTs ? ')
    'chatbot'
    >>> guess_topic('Where did you get the name Qary?')
    """
    if query and isinstance(query, str):
        query = query.lower().strip().strip('?').strip().rstrip('s')
        for topic, titles in TOPIC_TITLES.items():
            for title in titles:
                if query.endswith(title.strip().lower()):
                    return topic


class ArticleCache(dict):
    pass


class WikiScraper:
    """ RAM caching of scraped wikipedia pages

    TODO: preserve cache between runs in sqlite3 or h5py (.hdf)
    """

    def __init__(self,
                 titles_filepath=None,
                 sleep_empty_page=2.17,
                 sleep_downloaded_page=0.01,
                 sleep_nonexistent_page=0.02,
                 es_url=ES_URL,
                 min_articles=3,
                 max_articles=100,
                 max_title_words=5,
                 min_article_len=2,
                 max_depth=3):
        self.min_articles = min_articles
        self.max_articles = max_articles
        self.ngrams = max_title_words
        self.min_len = min_article_len
        self.max_depth = max_depth
        self.sleep_empty_page = sleep_empty_page
        self.sleep_downloaded_page = sleep_downloaded_page
        self.sleep_nonexistent_page = sleep_nonexistent_page
        self.es_url = ES_URL if (es_url and (es_url is True or str(es_url).lower().strip() == 'default')) else es_url
        self.es_url = self.es_url or None

        self.cache = ArticleCache()
        self.section_titles = {}
        self.title_hashes = None
        self.hashes_filepath = None
        self.hashes_filepath = titles_filepath or download_if_necessary('wikipedia-titles-alphaonly-hashed')
        if self.hashes_filepath:
            self.hashes_filepath = Path(self.hashes_filepath)
            self.title_hashes = utils.read_hashes(self.hashes_filepath) if self.hashes_filepath.is_file() else None

    def get_elastic_page(self, title: str):
        if self.es_url:
            elastic_page = elastic.search(title=title)
            # FIXME: convert this to a page_dict like in get_article()
            return elastic_results_as_page_dict(elastic_page)

    def get_article(self,
                    title: str,
                    exclude_headings=EXCLUDE_HEADINGS,
                    see_also=True,
                    prepend_section_headings=True,
                    prepend_title_text=True,
                    ):
        """ same as scrape_article_texts but for single article, and checks cache first """
        # look in the RAM cache first
        normalized_title = utils.normalize_wikititle(title)  # for greater recall, reduced precision, use squash_title
        page_dict = self.cache.get(normalized_title)
        if page_dict and page_dict.get('text') and page_dict.get('summary'):
            return copy.copy(page_dict)

        # then look in the elastic search db
        page_dict = self.get_elastic_page(title)
        if page_dict and page_dict.get('text') and page_dict.get('summary'):
            return copy.copy(page_dict)

        # if we haven't scraped it before then scrape it using Wikipedia-API
        self.wiki = Wikipedia('en')
        page = self.wiki.article(title)

        text, summary, see_also_links = '', '', []
        if page.exists():
            text = getattr(page, 'text', '')
            summary = getattr(page, 'summary', '')
        else:
            time.sleep(self.sleep_nonexistent_page)
            self.cache[normalized_title] = None  # so that cache will short-circuit for nonexistent titles
            return {}

        # FIXME: this postprocessing of Article objects to compost a text string should be in separate funcition
        # TODO: see_also is unnecessary until we add another way to walk deeper, e.g. links within the article
        if see_also:
            # .full_text() includes the section heading ("See also"). .text does not
            section = page.section_by_title('See also')
            if section:
                for t in section.text.split('\n'):
                    log.info(f"  Checking _SEE ALSO_ link: {t}")
                    if t in page.links:
                        see_also_links.append(t)

        text = f'{page.title}\n\n' if prepend_title_text else ''
        # page.text
        for section in page.sections:
            if section.title.lower().strip() in exclude_headings:
                continue
            # TODO: use pugnlp.to_ascii() or nlpia.to_ascii()
            text += f'\n{section.title}\n' if prepend_section_headings else '\n'
            # spacy doesn't handle "latin" (extended ascii) apostrophes well.
            text += section.text.replace('’', "'") + '\n'
            self.section_titles[str(section.title).strip()] = str(section.title).lower().strip().replace('’', "'")
        page_dict = dict(title=page.title, text=text, summary=summary, see_also_links=see_also_links)
        self.cache[normalized_title] = page_dict
        return page_dict

    def filtered_titles(self, titles):
        """ Iterate through sequence of article titles and return list of existing Wikipedia article titles

        >>> ws = WikiScraper()
        >>> ws.filtered_titles('Barack Obama,barack,fuj'.split(','))
        ['Barack Obama', 'barack']
        """
        filtered_titles = []
        for title in titles:
            log.info(f'unfiltered: {title}')
            if self.title_hashes is not None:
                if utils.md5(utils.squash_wikititle(title)) in self.title_hashes:
                    filtered_titles.append(title)
            elif len(utils.squash_wikititle(title)) > 2:
                filtered_titles.append(title)
        log.info(f'filtered_titles: {filtered_titles}')
        return filtered_titles

    def guess_article_titles(
            self,
            query: str,
            max_titles: int = None,
            ngrams: int = None,
            max_ignorable_pct: float = .5,
            ignore: bool = True):
        r""" Search db of wikipedia titles for articles relevant to a statement or questions

        >>> ws = WikiScraper()
        >>> ws.guess_article_titles('What is a chatbot?')[:3]
        ['Chatbot', 'ELIZA', 'Turing test']
        >>> ws.guess_article_titles('What is a ELIZA?')[:1]
        ['Chatbot']
        """
        # a hard-coded list of wikipedia titles about chatbots
        self.max_titles = max_titles = max_titles or self.max_articles * self.ngrams * 2
        self.ngrams = ngrams = ngrams or self.ngrams
        guessed_topic = guess_topic(query)
        if guessed_topic in TOPIC_TITLES:
            return TOPIC_TITLES[guessed_topic][:max_titles]
        ignore = QUESTION_STOPWORDS if ignore is True else ignore
        ignore = ignore if ignore is not None and ignore is not False else []
        log.info(f"ignoring {len(ignore)} stopwords")
        toks = list_ngrams(query, n=self.ngrams)
        ans = []
        for t in toks:
            if count_ignorable_words(
                t.lower().strip(),
                ignore=ignore,
                min_len=self.min_len
            ) < max_ignorable_pct * len(t.strip().split()):
                ans.append(t)
                if len(ans) >= max_titles:
                    return ans
        return ans

    def guess_article_titles_and_sort(
            self,
            query='What is a chatbot?',
            max_titles=50,
            ngrams=5,
            max_ignorable_pct=.5,
            ignore=True,
            reverse=True,
            score=len):
        r""" Use find_ngrams and ignore stopwords then sort the resulting list of titles with longest first

        >>> ws = WikiScraper()
        >>> ws.guess_article_titles_and_sort('What is a ELIZA?',
        ...     max_titles=30, ngrams=3, ignore=False)[:3]
        ['Loebner prize', 'Chinese room', 'Turing test']
        >>> ws.guess_article_titles_and_sort('What is an ELIZA?')[:1]
        ['Loebner prize']
        """
        # TODO Kendra: sort by importance (TFIDF) rather than length of strings
        titles = self.guess_article_titles(query, max_titles=max_titles, ngrams=ngrams, ignore=ignore,
                                           max_ignorable_pct=max_ignorable_pct)
        titles = sorted(((score(t), t) for t in titles), reverse=reverse)
        log.debug(f"sorted titles ({self.ngrams}-grams): \n" + str(pd.DataFrame(titles)))
        return [t for (n, t) in titles]

    def scrape_article_pages(self,
                             titles=TOPIC_TITLES.get('chatbot'),
                             max_articles=None,
                             max_depth=None,
                             exclude_headings=EXCLUDE_HEADINGS,
                             see_also=True,
                             prepend_section_headings=True,
                             prepend_title_text=True):
        r""" Download text for an article and parse into sections and sentences

        TODO: add exclude_title_regexes to exclude page titles like "ELIZA (disambiguation)" with '.*\(disambiguation\)'

        >>> scraper = WikiScraper()
        >>> pages = scraper.scrape_article_pages(['ELIZA'], see_also=False)
        >>> hasattr(pages, '__next__')
        True
        >>> pages = list(pages)
        >>> len(pages)
        1
        >>> texts = list(p['text'] for p in scraper.scrape_article_pages(['Chatbot', 'ELIZA'], max_articles=10, max_depth=3))
        >>> len(texts)
        10
        """
        # persistent state
        self.max_depth = max_depth or self.max_depth
        self.max_articles = max_articles or self.max_articles
        if isinstance(titles, str):
            log.error(f'DEPRECATED: input should be a list of titles, not a str query like "{titles}"')
            titles = self.guess_article_titles(titles)
        filtered_titles = self.filtered_titles(titles)
        exclude_headings = set([eh.lower().strip() for eh in (exclude_headings or [])])
        # depth starts at zero here, but as additional titles are appended the depth will increase
        title_depths = list(zip(filtered_titles, [0] * len(filtered_titles)))
        text_lens = []
        # TODO: record title tree (see also) so that .2*title1+.3*title2+.5*title3 can be semantically appended to sentences
        titles_scraped = set([''])
        d, num_articles, queue_pos = 0, 0, 0
        # TODO: make this a while loop to consolidate d=depth should be able to use depth rather than d:
        log.debug(f'title_depths: \n {title_depths}')
        while num_articles < self.max_articles and d <= self.max_depth and queue_pos < len(title_depths):
            title = ''
            log.debug("title_depths:\n" + '\n'.join(f"{td[1]}: {td[0]}" for td in title_depths))

            # pop another title and keep popping until it's not a title already scraped
            while queue_pos < len(title_depths) and (not title.strip() or title in titles_scraped):
                log.info(f"Skipping '{title}' (already scraped)")
                try:
                    title, d = title_depths[queue_pos]
                    queue_pos += 1
                except IndexError:
                    log.debug(f'Out of titles: {title_depths}')
                    break
                title = title.strip()
            if d > self.max_depth or not title:
                log.info(f"{d} > {self.max_depth} or title ('{title}') is empty")
                continue
            if title in titles_scraped:
                continue
            log.info(f'title: {title}')
            log.info(f'remaining len(title_depths): {len(title_depths)}, queue_pos: {queue_pos}')
            page_dict = self.get_article(
                title,
                see_also=see_also,
                exclude_headings=exclude_headings,
                prepend_section_headings=prepend_section_headings,
                prepend_title_text=prepend_title_text) or dict(text='', summary='', see_also_links=[])
            titles_scraped.add(title)
            if not page_dict:
                continue
            page_dict['title'] = title
            page_dict['depth'] = d
            log.info(f'len(titles_scraped): {len(titles_scraped)}')
            if not len(page_dict['text'] + page_dict['summary']):
                log.warning(f"Unable to retrieve _{title}_ because article text and summary len are 0.")
                time.sleep(self.sleep_empty_page)
                continue
            title_depths.extend([(t, d + 1) for t in page_dict['see_also_links']])
            text_lens.append(len(page_dict['text']))
            num_articles += 1

            log.info(f'Added article #{num_articles} "{title}" with {text_lens[-1]} chars.')
            # TODO: separate scraped from cache-retrieval counts
            log.debug(f'  Total scraped {sum(text_lens)} chars')
            log.info(str([d, self.max_depth, num_articles, title]))
            yield page_dict

    def scrape_article_texts(self,
                             titles=None,
                             max_articles=None,
                             max_depth=None,
                             exclude_headings=EXCLUDE_HEADINGS,
                             see_also=True,
                             prepend_section_headings=True,
                             prepend_title_text=True):
        r""" Download text for an article and parse into sections and sentences

        TODO: add exclude_title_regexes to exclude page titles like "ELIZA (disambiguation)" with '.*\(disambiguation\)'
        >>> nlp('hello')  # to eager-load spacy model
        hello
        >>> scraper = WikiScraper()
        >>> texts = scraper.scrape_article_texts(['ELIZA'], see_also=False)
        >>> texts = list(texts)
        >>> len(texts)
        1
        >>> texts = list(scraper.scrape_article_texts(['Chatbot', 'ELIZA'], max_articles=10, max_depth=3))
        >>> len(texts)
        10
        """
        for page_dict in self.scrape_article_pages(
                titles=titles,
                max_articles=max_articles,
                max_depth=max_depth,
                exclude_headings=exclude_headings,
                see_also=see_also,
                prepend_section_headings=prepend_section_headings,
                prepend_title_text=prepend_title_text):
            yield page_dict['text']

    def scrape_article_sentences(self,
                                 titles=TOPIC_TITLES['chatbot'],
                                 exclude_headings=EXCLUDE_HEADINGS,
                                 see_also=True,
                                 prepend_section_headings=True,
                                 prepend_title_text=True,
                                 max_articles=10_000,
                                 max_depth=1):
        """ Download text for an article and parse into sections and sentences

        >>> scraper = WikiScraper()
        >>> df = scraper.scrape_article_sentences(['ELIZA'], see_also=False)
        >>> df.shape[0] > 50
        True
        >>> df.columns
        Index(['title', 'see_also_links', 'depth', 'sentence', 'section_title', 'section_num'], dtype='object')
        """
        df = []
        for page_dict in self.scrape_article_pages(titles=titles,
                                                   exclude_headings=exclude_headings,
                                                   see_also=see_also,
                                                   prepend_section_headings=prepend_section_headings,
                                                   prepend_title_text=prepend_title_text,
                                                   max_articles=max_articles,
                                                   max_depth=max_depth):
            section_title, section_num = '', 0
            for sentence in nlp(page_dict['text']).sents:
                for s in sentence.text.split('\n'):
                    stripped = s.strip()
                    if not stripped:
                        continue
                    sentence_dict = dict([kv for kv in page_dict.items() if kv[0] not in ('text', 'summary')])
                    sentence_dict['sentence'] = s
                    if self.section_titles.get(stripped):
                        section_title = stripped
                        section_num += 1
                    sentence_dict['section_title'] = section_title
                    sentence_dict['section_num'] = section_num
                    df.append(sentence_dict)

        return pd.DataFrame(df)

    def find_cached_article_texts(self, query):
        log.info("WARN: {self.__class__.__name__}.find_cached_article_texts() returns empty list (stubbed out).")
        return []

    def find_article_texts(self,
                           query=None,
                           ngrams=5,
                           min_len=2,
                           max_ignorable_pct=.5,
                           ignore=True, reverse=True, score=len,
                           **scrape_kwargs):
        r""" Retrieve Wikipedia article texts relevant to the query text using ElasticSearch to cache

        >>> ws = WikiScraper()
        >>> texts = list(ws.find_article_texts('What is a chatbot?', max_articles=3, ngrams=1))
        >>> len(texts) > 2
        True
        """
        texts_list = []
        query = query or ''
        if isinstance(query, str):
            texts_list.extend(list(self.find_cached_article_texts(query=query)))
            if not texts_list or len(texts_list) < self.min_articles:
                titles = self.guess_article_titles_and_sort(query,
                                                            max_ignorable_pct=max_ignorable_pct,
                                                            ignore=ignore,
                                                            reverse=reverse,
                                                            score=score)
        else:
            log.error(f'DEPRECATED: query should be a str, not query={query}')
            titles = list(query)
        if len(texts_list) >= self.max_articles:
            return texts_list[:self.max_articles]
        texts_iterator = self.scrape_article_texts(titles=titles, **scrape_kwargs)
        for i, text in enumerate(chain(texts_list, texts_iterator)):
            if i >= self.max_articles:
                break
            yield text

# wikiscraper = WikiScraper()
# scrape_article_texts = wikiscraper.scrape_article_texts


def count_nonzero_vector_dims(self, strings, nominal_dims=1):
    r""" Count the number of nonzero values in a sequence of vectors

    Used to compare the doc vectors normalized as Marie_Curie vs "Marie Curie" vs "marie curie",
    and found that the spaced version was more complete (almost twice as many title words had valid vectors).

    >> count_nonzero_vector_dims(df[df.columns[0]].values[:100]) / 300
    264.0
    >> df.index = df['page_title'].str.replace('_', ' ').str.strip()
    >> count_nonzero_vector_dims(df.index.values[:100]) / 300
    415.0
    """
    tot = 0
    for s in strings:
        tot += (pd.DataFrame([t.vector for t in nlp(s)]).abs() > 0).T.sum().sum()
    return tot


def list_ngrams(token_list, n=3, sep=' '):
    r""" Return list of n-grams from a list of tokens (words)

    >>> ','.join(list_ngrams('Hello big blue marble'.split(), n=3))
    'Hello,Hello big,Hello big blue,big,big blue,big blue marble,blue,blue marble,marble'
    >>> ','.join(list_ngrams('Hello big blue marble'.split(), n=3, sep='_'))
    'Hello,Hello_big,Hello_big_blue,big,big_blue,big_blue_marble,blue,blue_marble,marble'
    """
    if isinstance(token_list, str):
        token_list = [tok.text for tok in nlp(token_list)]
    ngram_list = []

    for i in range(len(token_list)):
        for j in range(n):
            if i + j < len(token_list):
                ngram_list.append(sep.join(token_list[i:i + j + 1]))

    return ngram_list


def count_ignorable_words(text, ignore=QUESTION_STOPWORDS, min_len=2):
    r""" Count the number of words in a space-delimitted string that are not in set(words)

    >>> count_ignorable_words('what a hello world in')
    3
    >>> count_ignorable_words('what a hello world in', ignore=['what'], min_len=1)
    2
    >>> count_ignorable_words('what a hello world in', ignore=['what'], min_len=0)
    1
    """
    return sum(1 for w in text.split() if w in ignore or len(w) <= min_len)


# def parse_sentences(title, sentences, title_depths, see_also=True, exclude_headings=(), d=0, depth=0, max_depth=3):

#     return sentences, title_depths

# class WikiIndex():
#     """ CRUFT: Semantic and trigram index for wikipedia page titles

#     Uses too much RAM and is too slow.
#     """
#     _url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz'

#     def __init__(self, url=None, refresh=False, **pd_kwargs):
#         self._url = url or self._url
#         self.df_titles = self.load(url=self._url, refresh=refresh, **pd_kwargs)
#         # self.title_slug = self.df_titles.to_dict()
#         # self.df_vectors = pd.DataFrame(nlp(s).vector for s in self.df_titles.index.values)
#         # self.vectors = dict(zip(range(len(self.df_titles)), ))
#         self.title_row = dict(zip(self.df_titles.index.values, range(len(self.df_titles))))
#         # AttributeError: 'tuple' object has no attribute 'lower
#         # self.title_row.update({k.lower(): v for (k, v) in tqdm(self.title_row.items()) if k.lower() not in self.title_row})
#         # self.df_vectors = self.compute_vectors()

#     def compute_vectors(self, filename='wikipedia-title-vectors.csv.gz'):
#         log.warning(f'Computing title vectors for {len(self.df_titles)} titles. This will take a while.')
#         filepath = Path(DATA_DIR, filename)
#         start = sum((1 for line in gzip.open(filepath, 'rb')))
#         total = len(self.df_titles) - start
#         vec_batch = []
#         with gzip.open(filepath, 'ta') as fout:
#             csv_writer = csv.writer(fout)
#             csv_writer.writerow(['page_title'] + [f'x{i}' for i in range(300)])
#             for i, s in tqdm(enumerate(self.df_titles.index.values[start:]), total=total):
#                 vec = [s] + list(nlp(str(s)).vector)  # s can sometimes (rarely) be a float because of pd.read_csv (df_titles)
#                 vec_batch.append(vec)
#                 if not (i % 1000) or i == total - 1:
#                     csv_writer.writerows(vec_batch)
#                     print(f"wrote {len(vec_batch)} rows")
#                     try:
#                         print(f'wrote {len(vec_batch), len(vec_batch[0])} values')
#                     except IndexError:
#                         pass
#                     vec_batch = []
#         time.sleep(1)
#         dtypes = {f'x{i}': pd.np.float16 for i in range(300)}
#         dtypes.update(page_title=str)
#         self.df_vectors = pd.read_csv(filepath, dtype=dtypes)
#         return self.df_vectors

#     def load(
#             self,
#             url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz',
#             refresh=False,
#             **pd_kwargs):
#         url_dir, filename = os.path.split(url)
#         filepath = Path(DATA_DIR, 'corpora', 'wikipedia', filename)
#         df = None
#         if not refresh:
#             try:
#                 df = pd.read_csv(filepath, dtype=str)
#             except (IOError, FileNotFoundError):
#                 log.info(f'No local copy of Wikipedia titles file was found at {filepath}')
#         if not len(df):
#             log.warning(f'Starting download of entire list of Wikipedia titles at {url}...')
#             df = pd.read_table(url, dtype=str)  # , sep=None, delimiter=None, quoting=3, engine='python')
#             log.info(f'Finished downloading {len(df)} Wikipedia titles from {url}.')

#         df.columns = ['page_title']
#         if df.index.name != 'natural_title':
#             df.index = list(df['page_title'].str.replace('_', ' ').str.strip())
#             df.index.name == 'natural_title'
#             df.to_csv(filepath, index=False, compression='gzip')
#             log.info(f'Finished saving {len(df)} Wikipedia titles to {filepath}.')
#         self.df_titles = df
#         return self.df_titles

#     def find_similar_titles(self, title=None, n=1):
#         """ Takes dot product of a doc vector with all wikipedia title doc vectors to find closest article titles """
#         if isinstance(title, str):
#             vec = nlp(title).vector
#         else:
#             vec = title
#         vec /= pd.np.linalg.norm(vec) or 1.
#         dot_products = vec.dot(self.df_vectors.values.T)
#         if n == 1:
#             return self.df_titles.index.values[dot_products.argmax()]
#         sorted(dot_products, reverse=True)
