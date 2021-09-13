from enum import Enum


class LabelTypes(Enum):
    TOPIC = 'topic'
    ATTRIBUTE = 'attribute'
    EMOTION = 'emotion'
    LOCATION = 'location'
    ORGANIZATION = 'organization'
    BRAND = 'brand'
    BUSINESS = 'business'
    LEGAL = 'legal'
    MEDICAL = 'medical'
    HR = 'hr'
    PERSON = 'person'
    HASHTAG = 'hashtag'
    PROFESSION = 'profession'
    CUSTOMLABEL = 'custom_label'

class TextSplitType(Enum):
    SUBSENTENCE = 'SUBSENTENCE'
    SENTENCE = 'SENTENCE'
    PARAGRAPH = 'PARAGRAPH'

class PhraseTypes(Enum):
    POSITIVE = 'pos_phrase'
    NEGATIVE = 'neg_phrase'


class ExceptionTypes(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, errorcode, errormessage):
        self.errorCode = errorcode
        self.errorMessage = errormessage

    IPBLACKLISTED = 1, 'This IP has been blacklisted. Please contact us at dev at neticle dot com for further details.'
    LANGMISSING = 2, 'Missing lang parameter. This is a mandatory parameter, please always include it in the request. Further details can be found on the https://neticle.com/textanalysisapi/en/ website.'
    LANGINCORRECT = 3, 'This language is not implemented yet. Further details can be found on the https://neticle.com/textanalysisapi/en/ website. If you would like us to implement this language, please contact us on the sales at neticle dot com email address.'
    TOKENMISSING = 4, 'Missing token parameter. This is a mandatory parameter, please always include it in the request. Further details can be found on the https://neticle.com/textanalysisapi/en/ website.'
    TOKENINCORRECT = 5, 'This token is not valid. If you would like to renew it, please refer to the https://neticle.com/textanalysisapi/en/ website or contact us at dev at neticle dot com for further details.'
    INPUTMISSING = 6, 'The input parameter is missing or empty. Please refer to the https://neticle.com/textanalysisapi/en/ website for further details.'
    FORMATINCORRECT = 7, 'The format parameter is incorrect. For supported formats please refer to the https://neticle.com/textanalysisapi/en/ website for further details.'
    NOTSUPPORTEDVERSION = 8, 'The provided version is not supported. Please refer to the https://neticle.com/textanalysisapi/en/ website for further details.'
    CALLIDINCORRECT = 9, 'The callId parameter is too long, it must be less than 255 characters. Please refer to the https://neticle.com/textanalysisapi/en/ website for further details.'
    SERVERERROR = 100, 'Something went wrong during the analysis. Please contact us at dev at neticle dot com for further details.'
    KEYWORDSETTINGSMISSING = 10, 'The provided keyword settings list is empty.'
    KEYWORDSETTINGCONTAINSEMPTYSTRING = 11, 'The provided keyword settings list contains an element which is an empty string.'
    ASPECTSETTINGSMISSING = 12, 'The provided aspect settings list is empty.'
    ASPECTSETTINGCONTAINSEMPTYSTRING = 13, 'The provided aspect settings list contains an element which is an empty string.'
    CANNOTDETECTLANGUAGE = 14, 'There were no language provided and we could not recognise a language based on the input string.'
