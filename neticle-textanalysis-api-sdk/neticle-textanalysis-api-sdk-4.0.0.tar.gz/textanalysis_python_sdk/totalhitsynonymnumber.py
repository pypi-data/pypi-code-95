class TotalSynonymHitNumber(object):

    def __init__(self, jsonresponse):
        self.__positions = jsonresponse['positions']
        self.__sentence = jsonresponse['sentence']
        self.__synonym_hit = jsonresponse['synonymHit']
        self.__synonym_hit_number = jsonresponse['synonymHitNumber']

    def getPositions(self):
        '''
        List of the positions were the synonym was found in the input text.
        :returns: 
        '''
        return self.__positions

    def getSentence(self):
        '''
        The sentence in which this synonym occurred and it's positions in that sentence.
        :returns: 
        '''
        return self.__sentence

    def getSynonymHit(self):
        '''
        The name of the synonym.
        :returns: 
        '''
        return self.__synonym_hit

    def getSynonymHitNumber(self):
        '''
        Number of hits in the input text for this particular synonym.
        :returns: 
        '''
        return self.__synonym_hit_number