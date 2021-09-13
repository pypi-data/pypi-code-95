import os

from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

from textalytics_core.entity_recognition import EntityRecognizer
from textalytics_core.resources import TextInput, EntityRecognizerOutput, Entity


class AzureEntityRecognizer(EntityRecognizer):
    def recognize_entities(self, text_input: TextInput):
        entities = self.invoke_azure_detect_entities(text_input.source_text)
        return EntityRecognizerOutput(entities=entities)

    def invoke_azure_detect_entities(self, text_content):
        language = "en"
        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        documents = []
        documents.append(text_content)
        azure_response = text_analytics_client.recognize_entities(documents)
        azure_response = [review for review in azure_response if not review.is_error]
        return self.extract_entities(azure_response)

    def extract_entities(self, azure_response):
        entity_data = {}
        for idx, azure_entities in enumerate(azure_response):
            for azure_entity in azure_entities.entities:
                ent_text = azure_entity.text
                entity_data.setdefault(ent_text, {})
                entity_data[ent_text]["entity"] = ent_text

                entity_data[ent_text]["label"] = azure_entity.category

                entity_data[ent_text]["start_offset"] = azure_entity.offset
                entity_data[ent_text]["end_offset"] = azure_entity.offset + azure_entity.length

        entities = []
        for key, values in entity_data.items():
            print(values)
            entities.append(Entity.parse_obj(values))
        return entities
