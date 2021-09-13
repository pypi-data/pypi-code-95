from .totalhitsynonymnumber import TotalSynonymHitNumber

class KeywordStat(object):

    def __init__(self, jsonresponse):
        self.__total_keyword_hit_number = jsonresponse['totalKeywordHitNumber']
        self.__total_synonym_hit_numbers = []
        hit_numbers = jsonresponse['totalSynonymHitNumbers']
        for h in hit_numbers:
            self.__total_synonym_hit_numbers.append(TotalSynonymHitNumber(h))

    def getTotalKeywordHitNumber(self):
        '''
        Number of synonym hits in the input text.
        :returns: 
        '''
        return self.__total_keyword_hit_number

    def getTotalSynonymHitNumbers(self):
        '''
        Detailed statistics about the individual synonym hits in the input text.
        :returns: 
        '''
        return self.__total_synonym_hit_numbers