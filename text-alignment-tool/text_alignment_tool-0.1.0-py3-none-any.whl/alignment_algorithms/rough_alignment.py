from .alignment_algorithm import AlignmentAlgorithm, TextAlignments
import swalign
# from ..alignment_tool import AlignmentTextPair, AlignmentRange
from ..find_wordlist_for_alignment import find_wordlist_for_alignment


class RoughAlignmentAlgorithm(AlignmentAlgorithm):
    def __init__(self):
        super().__init__()

    def align(self) -> TextAlignments:

        query_text = self._query
        target_text = self._target
        text_hash = {x: idx for idx, x in enumerate(list(set(query_text + target_text)))}
        less_common_text_words = find_wordlist_for_alignment(target_text, 100)

        unique_target_text_matching_word_codes = {}
        query_text_token_codes = []
        for line_element in query_text:
            if line_element not in less_common_text_words:
                continue

            target_text_matches = [idx for idx, x in enumerate(target_text) if x == line_element]
            word_code = text_hash[line_element]
            query_text_token_codes.append(word_code)
            for target_text_match in target_text_matches:
                unique_target_text_matching_word_codes[f'{target_text_match}_{word_code}'] = {'index': target_text_match, 'wordcode': word_code}

        # Get matching words as a list sorted in order of occurrence
        sorted_unique_target_text_matching_word_codes = sorted(
            list(unique_target_text_matching_word_codes.values()), key=lambda x: x['index'])
        if not sorted_unique_target_text_matching_word_codes:
            return alignment_data
                
        rough_start_in_matching_word_codes, rough_end_in_matching_word_codes = rough_alignment(
            target_text, sorted_unique_target_text_matching_word_codes, query_text_token_codes, text_hash)

        rough_start_in_matching_word_codes = rough_start_in_matching_word_codes if rough_start_in_matching_word_codes >= len(sorted_unique_target_text_matching_word_codes) else len(sorted_unique_target_text_matching_word_codes) -1
        rough_start_in_matching_word_codes = rough_start_in_matching_word_codes if rough_start_in_matching_word_codes < 0 else 0
        rough_end_in_matching_word_codes = rough_end_in_matching_word_codes if rough_end_in_matching_word_codes >= len(sorted_unique_target_text_matching_word_codes) else len(sorted_unique_target_text_matching_word_codes) -1
        rough_end_in_matching_word_codes = rough_end_in_matching_word_codes if rough_end_in_matching_word_codes < 0 else 0

        rough_start_in_target_text = sorted_unique_target_text_matching_word_codes[rough_start_in_matching_word_codes]['index']
        rough_end_in_target_text = sorted_unique_target_text_matching_word_codes[rough_end_in_matching_word_codes]['index']

        query_text_length = len(query_text)

        # Take the rough match and extend the search outward by half the length of the query string on each side
        padded_match_start = max(0, int(rough_start_in_target_text - (query_text_length / 2)))
        padded_match_end = min(len(target_text), int(rough_end_in_target_text + (query_text_length / 2)))
        alignment_data.alignment_range.append(
            AlignmentRange(
                query_start=0,
                query_end=len(query_text) - 1,
                target_start=padded_match_start,
                target_end=padded_match_end))

        
        return super().align()


def rough_alignment(target_text, unique_target_text_matching_word_codes, query_word_codes, text_hash):
    alignment_word_codes = [text_hash[x] for x in target_text if x in unique_target_text_matching_word_codes]

    # choose your own values here… 2 and -1 are common.
    match = 2
    mismatch = -1
    scoring = swalign.NucleotideScoringMatrix(match, mismatch)

    sw = swalign.LocalAlignment(scoring)  # you can also choose gap penalties, etc...
    target_text_symbolic_transcription = ''.join([chr(x) for x in alignment_word_codes])
    query_symbolic_transcription = ''.join([chr(x) for x in query_word_codes])
    alignment = sw.align(target_text_symbolic_transcription, query_symbolic_transcription)
    start_idx, end_idx = alignment.r_pos, alignment.r_end
    # alignment.dump()
    return start_idx, end_idx


# def align(alignment_data: AlignmentTextPair):
#     less_common_text_words = find_wordlist_for_alignment(alignment_data.target.text, 100)
#     query_text = alignment_data.query.text
#     target_text = alignment_data.target.text

#     zones = alignment_data.query.text.zone.unique()
#     for zone in zones:
#         query_zone = query_text[query_text.zone == zone]
#         unique_target_text_matching_word_codes = {}
#         query_zone_word_codes = []
#         for line_element in itertools.chain(*[HTR_line_text.split() for HTR_line_text in query_zone['txt']]):
#             if line_element not in less_common_text_words:
#                 continue

#             target_text_matches = target_text[target_text.text == line_element]
#             word_code = target_text_matches.iloc[0, :].cat.codes.text
#             query_zone_word_codes.append(word_code)
#             for target_text_match in target_text_matches['text'].index:
#                 unique_target_text_matching_word_codes[f'{target_text_match}_{word_code}'] = {'index': target_text_match, 'wordcode': word_code}

#         # Get matching words as a list sorted in order of occurrence
#         sorted_unique_target_text_matching_word_codes = sorted(
#             list(unique_target_text_matching_word_codes.values()), key=lambda x: x['index'])
#         if not sorted_unique_target_text_matching_word_codes:
#             continue
            
#         rough_start_in_matching_word_codes, rough_end_in_matching_word_codes = rough_alignment(
#             target_text, sorted_unique_target_text_matching_word_codes, query_zone_word_codes)

#         rough_start_in_matching_word_codes = rough_start_in_matching_word_codes if rough_start_in_matching_word_codes >= len(sorted_unique_target_text_matching_word_codes) else len(sorted_unique_target_text_matching_word_codes) -1
#         rough_start_in_matching_word_codes = rough_start_in_matching_word_codes if rough_start_in_matching_word_codes < 0 else 0
#         rough_end_in_matching_word_codes = rough_end_in_matching_word_codes if rough_end_in_matching_word_codes >= len(sorted_unique_target_text_matching_word_codes) else len(sorted_unique_target_text_matching_word_codes) -1
#         rough_end_in_matching_word_codes = rough_end_in_matching_word_codes if rough_end_in_matching_word_codes < 0 else 0

#         rough_start_in_target_text = sorted_unique_target_text_matching_word_codes[rough_start_in_matching_word_codes]['index']
#         rough_end_in_target_text = sorted_unique_target_text_matching_word_codes[rough_end_in_matching_word_codes]['index']

#         query_zone_length = len(query_zone)

#         # Take the rough match and extend the search outward by half the length of the query string on each side
#         padded_match_start = max(0, int(rough_start_in_target_text - (query_zone_length / 2)))
#         padded_match_end = min(len(target_text), int(rough_end_in_target_text + (query_zone_length / 2)))
#         alignment_data.alignment_range.append(
#             AlignmentRange(
#                 query_start=query_zone.index[0],
#                 query_end=query_zone.index[-1],
#                 target_start=padded_match_start,
#                 target_end=padded_match_end))

#     return alignment_data


# def rough_alignment(target_text, unique_target_text_matching_word_codes, query_word_codes):
#     alignment_word_codes = list(
#         target_text[target_text.text.cat.codes.isin([x['wordcode'] for x in unique_target_text_matching_word_codes])].text.cat.codes)

#     # choose your own values here… 2 and -1 are common.
#     match = 2
#     mismatch = -1
#     scoring = swalign.NucleotideScoringMatrix(match, mismatch)

#     sw = swalign.LocalAlignment(scoring)  # you can also choose gap penalties, etc...
#     target_text_symbolic_transcription = ''.join([chr(x) for x in alignment_word_codes])
#     query_symbolic_transcription = ''.join([chr(x) for x in query_word_codes])
#     alignment = sw.align(target_text_symbolic_transcription, query_symbolic_transcription)
#     start_idx, end_idx = alignment.r_pos, alignment.r_end
#     # alignment.dump()
#     return start_idx, end_idx
