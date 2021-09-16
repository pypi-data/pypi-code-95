from collections import defaultdict
from .components.edit import EDIT
from .components.parser import Parser
from .components.entity import Entity
from .components.phrase import Phrase
from .components.dictionary import Dictionary
from .constants import TOOL_DEPENDENCIES


class NlpUtils(object):

    @staticmethod
    def entities(doc):
        ner_dict = defaultdict(list)
        if doc.ents:
            for span in doc.ents:
                ner_dict[span.label_].append(span.text)
        return dict(ner_dict)

    
    
    @staticmethod
    def extract_nlp(output, doc, disable, remove_meme=False, remove_url=False, remove_all_spaces=True, 
        remove_stopwords=True, remove_brand=False, remove_onom=False, remove_internet_phrase=False):

        if 'edit' not in disable:
            edit = EDIT(doc, output, remove_meme=remove_meme, remove_url=remove_url, remove_all_spaces=remove_all_spaces, remove_stopwords=remove_stopwords,
                remove_brand=remove_brand, remove_onom=remove_onom, remove_internet_phrase=remove_internet_phrase)
            edit()

            if 'tagger' not in disable:
                # output['tagger'] = {}
                output['words'] = [token.text for token in doc if token.text]
                output['pos'] = [token.tag_ for token in doc if token.text and token.text in output['Dewords']]

        else:
            if 'tagger' not in disable:
                # output['tagger'] = {}
                output['words'] = [token.text for token in doc if token.text]
                output['pos'] = [token.tag_ for token in doc if token.text ]

        if 'parser' not in disable:
            parser = Parser(doc, output)
            parser()

        if 'ner' not in disable:
            entities = NlpUtils.entities(doc)
            # logger.info(doc.text)
            if entities:
                # TODO: this merge function needs to be improved when actual data shows up!
                if 'entities' in output:
                    output['entities'] = {**entities, **output['entities']}
                else:
                    output['entities'] = entities

        if 'phrase' not in disable:
            phrase = Phrase(doc, output)
            phrase()

        if 'phrase_match' not in disable:
            phrase_match = Dictionary(doc, output)
            phrase_match()

        if len(disable) == len(TOOL_DEPENDENCIES):
            output['words'] = [token.text for token in doc if token.text]


    @staticmethod
    def extract_entity(output, doc, entity_component):
        entities = Entity(doc, output, entity_component)
        e = entities()
        # print ('e:', e)
        # if e:
        #     # TODO: this merge function needs to be improved when actual data shows up!
        #     if 'entities' in output:
        #         output['entities'] = {**e, **output['entities']}
        #     else:
        #         output['entities'] = e
        # return output