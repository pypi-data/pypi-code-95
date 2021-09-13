import os

from textalytics_client.text_analysis import Client
from textalytics_core.entity_recognition import EntityRecognizer
from textalytics_core.resources import TextInput, EntityRecognizerOutput, Entity

from tests.test_config import SAMPLE_TEXT


class TextalyticsEntityRecognizer(EntityRecognizer):
    def recognize_entities(self, text_input: TextInput):
        entities = self.invoke_textalytics_detect_entities(text_input.source_text)
        return EntityRecognizerOutput(entities=entities)

    def invoke_textalytics_detect_entities(self, text_content):
        language = "en"
        url = os.environ["TEXTALYTICS_ENDPOINT"]
        username = os.environ["TEXTALYTICS_USERNAME"]
        password = os.environ["TEXTALYTICS_PASSWORD"]

        client = Client(service_base_url=url, username=username, password=password)
        text_input = TextInput(source_text=SAMPLE_TEXT, source_language=language)
        textalytics_response = client.extract_entities(text_input=text_input)
        return self.extract_entities(textalytics_response)

    def extract_entities(self, extract_entities_response):
        entities = []

        if extract_entities_response.status_code == 200:
            extracted_entities = extract_entities_response.json()
            for extracted_entity in extracted_entities["entities"]:
                entities.append(Entity.parse_obj(extracted_entity))

        return entities

