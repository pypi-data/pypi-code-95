from .entity import Entity
from .sentence import Sentence
from .enumtypes import LabelTypes, PhraseTypes
from .keywordstat import KeywordStat
from .maincategory import MainCategory


class TextAnalysisAnswer(object):

    def __init__(self, jsonresponse):
        self.__error_code = jsonresponse.get('errorCode')
        self.__error_message = jsonresponse.get('errorMessage')
        self.__callid = jsonresponse.get('callId')
        self.__input_length = jsonresponse.get('inputLength')
        self.__response_time_in_ms = jsonresponse.get('responseTimeInMs')
        self.__analyzed = jsonresponse.get('analyzed')
        self.__keyword_stats = KeywordStat(jsonresponse.get('keywordStats')) if jsonresponse.get('keywordStats') is not None else None
        self.__opinion_index = jsonresponse.get('opinionIndex')
        self.__summarized_positive_opinion_index = jsonresponse.get('summarizedPositiveOpinionIndex')
        self.__summarized_negative_opinion_index = jsonresponse.get('summarizedNegativeOpinionIndex')
        self.__entities = {}
        entities = dict(jsonresponse.get('entities'))
        for e in entities.keys():
            self.__entities[e] = Entity(entities[e])
        self.__sentences = {}
        sentences = dict(jsonresponse.get('sentences'))
        for s in sentences.keys():
            self.__sentences[s] = Sentence(sentences[s])
        '''
        self.__main_categories = []
        main_categories = jsonresponse['categories']
        for m in main_categories:
            self.__main_categories.append(MainCategory(m))
        '''

    def getErrorCode(self):
        """
        Getter for the error code.
        :returns: If no error happened during the validation, this field will contain 0, otherwise a Neticle error code.
        """
        return self.__error_code

    def getErrorMessage(self):
        """
        Getter for the error message.
        :returns: If no error happened during the validation, this field will be empty, otherwise a Neticle error message.
        """
        return self.__error_message

    def getCallId(self):
        """
        Getter for the callId.
        :returns: The provided callId in the request.
        """
        return self.__callid

    def getInputLength(self):
        """
        Getter for the input length.
        :returns: The length of the provided input.
        """
        return self.__input_length

    def getResponseTimeInMs(self):
        """
        Getter for the response time.
        :returns: The time it took to analyze the request.
        """
        return self.__response_time_in_ms

    def getAnalyzed(self):
        """
        Getter for the analyzed boolean.
        :returns: True if the request was analyzed by the system, false otherwise (e.g.: keywordSynonyms were provided but they did not appear in the input text.
        """
        return self.__analyzed

    def getKeywordStats(self):
        """
        Getter for the provided keyword's statistics.
        :returns: Empty, if no keywordSynonyms were sent. Otherwise it will contain information about the recognized synonyms.
        """
        return self.__keyword_stats

    def getOpinionIndex(self):
        """
        Getter for the summarized opinion index.
        :returns: The summarized opinion index of the input text.
        """
        return self.__opinion_index

    def getSummarizedPositiveOpinionIndex(self):
        """
        Getter for the summarized positive opinion indexes.
        :returns: The summarized positive opinion index of the input text.
        """
        return self.__summarized_positive_opinion_index

    def getSummarizedNegativeOpinionIndex(self):
        """
        Getter for the summarized negative opinion indexes.
        :returns: The summarized negative opinion index of the input text.
        """
        return self.__summarized_negative_opinion_index

    def getAllEntities(self):
        """
        Returns all the entities found in the input text.
        :returns: A list of Entity objects
        """
        return self.__entities.values()
        
    def getAllEntitiesDict(self):
        """
        Returns the entities dictionary found in the input text.
        :returns: A dictionary of Entity objects
        """
        return self.__entities

    def getAllSentences(self):
        """
        Returns all the sentence parts found in the input text.
        :returns: A list of Sentence objects
        """
        return self.__sentences.values()

    def getAllSentencesDict(self):
        """
        Returns the sentence parts dictionary found in the input text.
        :returns: A dictionary of Sentence objects
        """
        return self.__sentences

    def getFullHTMLText(self, wrapSentencePartsWithSynonymHitsInSpans = False):
        """
        Returns an HTML enriched text with html spans around the recognized entities, phrases and synonyms.
        :param decorateNeed: True, if you would like to wrap the sentences with synonym hits inside them in a <span class="contains_keyword">...</span> wrapper, false otherwise.
        :returns: The HTML enriched text.
        """
        if not isinstance(wrapSentencePartsWithSynonymHitsInSpans, bool):
            raise TypeError('wrapSentencePartsWithSynonymHitsInSpans must be an instance of the Boolean class')

        sentences = list(self.__sentences.values())
        sentences.sort(key=Sentence.getPosition)
        text = ''

        for sentence in sentences:
            if sentence.getContainsKeyword() is True and wrapSentencePartsWithSynonymHitsInSpans is True:
                text = text + self.__addContainsKeywordToText(sentence.getHtmlFormattedSentence())
            else:
                text = text + sentence.getHtmlFormattedSentence()

        return text

    def __addContainsKeywordToText(self, text):
        return '<span class=\"contains_keyword\">' + text + '</span>'

    def getRelatedEntities(self, baseEntity):
        """
        Returns all related entities to the provided entity. An entity is considered a related entity to another entity, if they appear together in the same sentence part.
        :param baseEntity: The base entity for which the related entities should be collected.
        :returns: A list of related entities
        """
        if not isinstance(baseEntity, Entity):
            raise TypeError('entity must be an instance of the Entity class')

        relatedEntities = []
        relatedEntityUUIDs = []

        for sentence in self.__sentences.values():
            sentenceEntities = sentence.getEntities()
            if baseEntity.getUUID() in sentenceEntities:
                for e in sentenceEntities:
                    if e not in relatedEntityUUIDs and e != baseEntity.getUUID():
                        relatedEntityUUIDs.append(e)

        for relatedEntity in relatedEntityUUIDs:
            relatedEntities.append(self.__entities[relatedEntity])

        return relatedEntities

    def getAllLabelEntities(self):
        """
        Returns all entities with label types (e.g.: brands, persons, etc...)
        :returns: A list of entities
        """
        entities = []

        for entity in self.__entities.values():
            for labelType in LabelTypes:
                if entity.getType() == labelType.value:
                    entities.append(entity)

        return entities

    def getEntitiesByLabelType(self, labeltype):
        """
        Returns all entities with a specific label type. (e.g.: only brands, only persons, etc...)
        :param labeltype: A label type from the LabelTypes enum
        :returns: A list of entities matching the provided label type.
        """
        if not isinstance(labeltype, LabelTypes):
            raise TypeError('labeltype must be an instance of LabelType Enum')

        entitiesByType = []

        for entity in self.__entities.values():
            if entity.getType() == labeltype.value:
                entitiesByType.append(entity)

        return entitiesByType

    def getAllPhraseEntities(self):
        """
        Returns all positive and negative phrase type entities.
        :returns: A list of entities with positive or negative phrase types.
        """
        entities = []

        for entity in self.__entities.values():
            for phraseType in PhraseTypes:
                if entity.getType() == phraseType.value:
                    entities.append(entity)

        return entities

    def getAllPositivePhraseEntities(self):
        """
        Returns all positive phrase typed entities.
        :returns: a list of entities with positive phrase type.
        """
        entities = []

        for entity in self.__entities.values():
            if entity.getType() == PhraseTypes.POSITIVE.value:
                entities.append(entity)

        return entities

    def getAllNegativePhraseEntities(self):
        """
        Returns all negative phrase typed entities.
        :returns: a list of entities with negative phrase type.
        """
        entities = []

        for entity in self.__entities.values():
            if entity.getType() == PhraseTypes.NEGATIVE.value:
                entities.append(entity)

        return entities

    '''
    def getMainCategories(self):
        TODO: after release this feature read the comment below
        The found categories and their sub-categories in the input text.
        :returns: 
        return self.__main_categories
    '''
