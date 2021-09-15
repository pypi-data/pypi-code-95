import spacy
from textalytics_core.entity_recognition import EntityRecognizer
from textalytics_core.resources import TextInput, EntityRecognizerOutput, Entity

nlp = spacy.load("en_core_web_sm")

class SpacyEntityRecognizer(EntityRecognizer):
    def recognize_entities(self, text_input: TextInput):
        entities = self.invoke_spacy_detect_entities(text_input.source_text)
        return EntityRecognizerOutput(entities=entities)

    def invoke_spacy_detect_entities(self, text_content):
        spacy_response = nlp(text_content)
        return self.extract_entities(spacy_response)

    def extract_entities(self, spacy_response):
        pos_tags = {}
        for token in spacy_response:
            pos_tags[token.text] = token.tag_

        entity_data = {}
        for spacy_entity in spacy_response.ents:
            ent_text = spacy_entity.text
            entity_data.setdefault(ent_text, {})
            entity_data[ent_text]["entity"] = ent_text

            entity_data[ent_text]["label"] = spacy_entity.label_

            entity_data[ent_text]["start_offset"] = spacy_entity.start_char
            entity_data[ent_text]["end_offset"] = spacy_entity.end_char

            if ent_text in pos_tags.keys():
                entity_data[ent_text]["pos_tag"] = pos_tags[ent_text]

        entities = []
        for key, values in entity_data.items():
            print(values)
            entities.append(Entity.parse_obj(values))
        return entities
