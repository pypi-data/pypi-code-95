import boto3
from textalytics_core.entity_recognition import EntityRecognizer
from textalytics_core.resources import TextInput, EntityRecognizerOutput, Entity


class AwsEntityRecognizer(EntityRecognizer):
    def recognize_entities(self, text_input: TextInput):
        entities = self.invoke_aws_detect_entities(text_input.source_text)
        return EntityRecognizerOutput(entities=entities)

    def invoke_aws_detect_entities(self, text_content):
        language = "en"
        comprehend_client = boto3.client('comprehend')
        aws_response = comprehend_client.detect_entities(Text=text_content, LanguageCode=language)
        return self.extract_entities(aws_response)

    def extract_entities(self, aws_response):
        entity_data = {}
        for aws_entity in aws_response["Entities"]:
            ent_text = aws_entity["Text"]
            entity_data.setdefault(ent_text, {})
            entity_data[ent_text]["entity"] = ent_text

            entity_data[ent_text]["label"] = aws_entity["Type"]

            entity_data[ent_text]["start_offset"] = aws_entity["BeginOffset"]
            entity_data[ent_text]["end_offset"] = aws_entity["EndOffset"]

        entities = []
        for key, values in entity_data.items():
            print(values)
            entities.append(Entity.parse_obj(values))
        return entities
