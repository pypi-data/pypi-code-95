
class Entity(object):

    def __init__(self, jsonresponse):
        self.__uuid = jsonresponse.get('uuid')
        self.__mention_number = jsonresponse.get('mentionNumber')
        self.__opinion_index = jsonresponse.get('opinionIndex')
        self.__name = jsonresponse.get('name')
        self.__english_name = jsonresponse.get('englishName', None)
        self.__label_id = jsonresponse.get('labelId', None)
        self.__type = jsonresponse.get('type')
        self.__sentences = jsonresponse.get('sentences')
        self.__recognized_synonym = jsonresponse.get('recognizedSynonym', None)

    def getUUID(self):
        """
        A unique identifier for this entity.
        :returns:
        """
        return self.__uuid

    def getMentionNumber(self):
        """
        The number of times this entity was found in the input text.
        :returns: An integer value of the number of mentions for this entity.
        """
        return self.__mention_number

    def getOpinionIndex(self):
        """
        The overall opinion index of this entity.
        :returns: The overall opinion index of this entity.
        """
        return self.__opinion_index

    def getName(self):
        """
        The name of this entity.
        :returns: The name of this entity.
        """
        return self.__name

    def getType(self):
        """
        The type of this entity.
        :returns: The type of this entity.
        """
        return self.__type

    def getSentences(self):
        """
        The list of the sentence parts' UUIDs in which this entity was found.
        :returns: The list of the sentence parts' UUIDs in which this entity was found.
        """
        return self.__sentences

    def getEnglishName(self):
        """
        The english translation of this entity.
        :return: The english translation of this entity.
        """
        return self.__english_name

    def getLabelId(self):
        """
        The id of the label.
        :return: The id of the label.
        """
        return self.__label_id

    def getRecognizedSynonym(self):
        """
        The synonym that was recognized for this label.
        :return: The synonym that was recognized for this label.
        """
        return self.__recognized_synonym
