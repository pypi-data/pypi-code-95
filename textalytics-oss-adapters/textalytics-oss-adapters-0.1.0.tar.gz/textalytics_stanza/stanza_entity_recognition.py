import stanza
from stanza.server import CoreNLPClient
from textalytics_core.entity_recognition import EntityRecognizer
from textalytics_core.resources import TextInput, EntityRecognizerOutput, Entity
import time

stanza.install_corenlp()

class StanzaEntityRecognizer(EntityRecognizer):
    def __init__(self):
        self.client = CoreNLPClient(
            annotators=['ner'],
            memory='4G',
            endpoint='http://localhost:9001',
            be_quiet=True)
        self.client.start()
        time.sleep(10)

    def recognize_entities(self, text_input: TextInput):
        entities = self.invoke_stanza_detect_entities(text_input.source_text)
        return EntityRecognizerOutput(entities=entities)

    def invoke_stanza_detect_entities(self, text_content):
        language = "en"
        stanza_response = self.client.annotate(text_content)
        return self.extract_entities(stanza_response)

    def extract_entities(self, stanza_response):
        entity_data = {}
        for sentence in stanza_response.sentence:
            for token in sentence.token:
                label = token.ner
                if label and label != "O":
                    ent_text = token.word
                    entity_data.setdefault(ent_text, {})
                    entity_data[ent_text]["entity"] = ent_text

                    entity_data[ent_text]["label"] = label

                    entity_data[ent_text]["pos_tag"] = token.pos
                    entity_data[ent_text]["start_offset"] = token.beginChar
                    entity_data[ent_text]["end_offset"] = token.endChar

        entities = []
        for key, values in entity_data.items():
            print(values)
            entities.append(Entity.parse_obj(values))
        return entities
