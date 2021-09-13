from .textanalysisanswer import TextAnalysisAnswer
from .exception import NeticleException
from .enumtypes import ExceptionTypes
from .enumtypes import TextSplitType
import requests


class TextAnalysis(object):

    def __init__(self, token):
        self.__token = token

    def getTextAnalyzed(self, language, input, callid='', replaceaccent=False, lowercase=False, keywordsynonyms=None, textSplitType=TextSplitType.SUBSENTENCE):
        '''
        Returns a TextAnalysisAnswer from Textanalysis API by request.

        :param language: The language of the input text. If this parameters is empty, the API will try to identify the language based on the text and process it accordingly. If you know the language, the preferred option is to provide it to the API.

                            Possible values:
                            
                            bg - Bulgarian
                            de - German
                            en - English
                            ge - Georgian
                            hu - Hungarian
                            nl - Dutch
                            pl - Polish
                            ro - Romanian
                            ru - Russian
                            ua - Ukrainian
        :param token: Token received from Neticle Labs to authenticate the user.
        :param input: The text to analyze.
        :param callid:  (Optional) A field to be used by the client, 
                        to help tracking calls from different sources from the client's side. 
                        Length is max 255 characters.
                        
                        The default value is an empty string.
        :param replaceaccent:  (Optional) If set to true, the API will remove all accents from the characters before processing.
                                For example it will convert the letters é á ű ó into e a u o.
                                
                                The default value is false.
        :param lowercase:  (Optional) If set to true, the API will convert the input text to lowercase before processing.

                            The default value is false.
        :param keywordSynonyms:  (Optional) Synonyms are case-sensitive spellings, misspellings, synonyms of the target entity of the sentiment analysis. For example to analyze comments about the internet coverage, the following synonyms should be set: internet, Internet, INTERNET, net, Net, NET

                                    If synonyms are set, then only the phrases and labels related to the target (represented by synonyms) will be recognized (also known as entity oriented sentiment analysis). If we set the synonym as "net" it will analyze only the related parts of the text: <i>I like this neighborhood, but the <b>net is terrible</b>.</i>
                                    
                                    If no synonyms are set, then the full text will be analyzed (aka. document level sentiment analysis). This version should be use only in special cases, because often gives bad results for precise analysis: <i><b>I like</b> this neighborhood, but the <b>net is terrible</b>.</i>
                                    
                                    The default value is null.
                                    Error will be thrown if an empty list or a list with empty string(s) is provided.
        :param textSplitType:  (Optional) Incoming text will be split based on this into smaller entities. The default value is SUBSENTENCE.

                                Possible values are in the TextSplitType enum:

                                SUBSENTENCE - spits the text into clauses (smaller fragments than a sentence)
                                SENTENCE - spits the text into sentences
                                PARAGRAPH - spits the text into paragraphs
        :returns: a TextAnalysisAnswer object
        '''
        url = 'https://textanalysis.neticle.com/text_analysis/4.0'
        body = {
            "language": language,
            "token": self.__token,
            "input": input,
            "callid": callid,
            "replaceaccent": replaceaccent,
            "lowercase": lowercase,
            "keywordSynonyms": keywordsynonyms,
            "textSplitType": textSplitType.value
        }

        headers = {'Content-type': 'application/json'}

        response = requests.post(url, json=body, headers=headers)

        responseJson = response.json()

        if response.status_code == 200:
            answer = TextAnalysisAnswer(responseJson)
            return answer
        else:
            if response.status_code == 500:
                raise NeticleException(ExceptionTypes.SERVERERROR.errorMessage)
            else:
                answer = TextAnalysisAnswer(responseJson)
                raise NeticleException(answer.getErrorMessage())
