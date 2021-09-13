import operator
from typing import List

'''
This preprocessing code was given by the instructor.
'''

def get_caption_dictionaries(captions: List):
    total_words, max_caption_length, num_words = 0, 0, 1  # 1 due to '_'
    word_frequecies = {}

    for image_captions in captions:
        for caption in image_captions:
            if len(caption) > max_caption_length:
                max_caption_length = len(caption)
            for word in caption:
                # if not bool(num_regex.match(word)): # Numbers are included
                try:
                    word_frequecies[word] += 1
                except KeyError:
                    num_words += 1
                    word_frequecies[word] = 1
                total_words += 1

    sorted_word_freqs = sorted(
        word_frequecies.items(), key=operator.itemgetter(1), reverse=True)

    word_to_idx = {'_': 0}
    index = len(word_to_idx)
    for word, _ in sorted_word_freqs:
        word_to_idx[word] = index
        index += 1

    idx_to_word = dict((v, k) for (k, v) in word_to_idx.items())

    print('total_words', total_words)  # total_words 426431
    print('max_caption_length', max_caption_length)  # max_caption_length 35
    print('num_words', num_words)  # num_words 2992
    print('sorted_word_freqs', sorted_word_freqs[:10])
    '''
    sorted_word_freqs [('a', 62986), ('in', 18974), ('the', 18418), ('on', 10743), ('is', 9345), 
                    ('and', 8851), ('dog', 8136), ('with', 7765), ('man', 7265), ('of', 6713)]
    '''

    return idx_to_word, word_to_idx, max_caption_length, total_words, num_words