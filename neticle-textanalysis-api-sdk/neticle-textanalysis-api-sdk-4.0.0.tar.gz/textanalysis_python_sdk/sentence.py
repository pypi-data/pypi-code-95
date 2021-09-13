

class Sentence(object):

    def __init__(self, jsonresponse):
        self.__uuid = jsonresponse.get('uuid')
        self.__position = jsonresponse.get('position')
        self.__html_formatted_sentence = jsonresponse.get('htmlFormattedSentence')
        self.__contains_keyword = jsonresponse.get('containsKeyword')
        self.__entities = jsonresponse.get('entities')
        self.__opinionIndex = jsonresponse.get('opinionIndex')
        self.__sentence = jsonresponse.get('sentence')

    def getUUID(self):
        '''
        A unique identifier for this sentence part.
        :returns: 
        '''
        return self.__uuid

    def getPosition(self):
        '''
        The position of this sentence part in the overall text starting from 0.
        :returns: The position number of this sentence part.
        '''
        return self.__position

    def getOpinionIndex(self):
        '''
        The summarized opinion index of the current sentence.
        '''
        return self.__opinionIndex

    def getHtmlFormattedSentence(self):
        '''
        The sentence part enriched with HTML code around the recognized entities, phrases and synonyms.
        :returns: HTML enriched sentence text.
        '''
        return self.__html_formatted_sentence

    def getContainsKeyword(self):
        '''
        True if the sentence part contains any of the provided synonyms, false otherwise.
        :returns: True if the sentence part contains any of the provided synonyms, false otherwise.
        '''
        return self.__contains_keyword

    def getEntities(self):
        '''
        Returns the list of the entities' UUIDs that were found in this sentence part.
        :returns: The list of the entities' UUIDs that were found in this sentence part.
        '''
        return self.__entities

    def getSentence(self):
        '''
        Returns the original text of this sentence part.
        :returns: The original text of this sentence part.
        '''
        return self.__sentence
