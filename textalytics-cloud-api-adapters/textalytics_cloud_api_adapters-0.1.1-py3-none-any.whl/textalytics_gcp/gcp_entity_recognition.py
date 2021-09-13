from google.cloud import language_v1
from textalytics_core.entity_recognition import EntityRecognizer
from textalytics_core.resources import TextInput, EntityRecognizerOutput, Entity


class GcpEntityRecognizer(EntityRecognizer):
    def recognize_entities(self, text_input: TextInput):
        entities = self.invoke_gcp_analyze_entities(text_input.source_text)
        return EntityRecognizerOutput(entities=entities)

    def invoke_gcp_analyze_entities(self, text_content):
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT
        language = "en"
        document = {"content": text_content, "type_": type_, "language": language}
        encoding_type = language_v1.EncodingType.UTF8

        gcp_response = client.analyze_entities(request = {'document': document, 'encoding_type': encoding_type})
        return self.extract_entities(gcp_response)

    def extract_entities(self, gcp_response):
        entity_data = {}
        for gcp_entity in gcp_response.entities:
            ent_text = gcp_entity.name
            entity_data.setdefault(ent_text, {})
            entity_data[ent_text]["entity"] = ent_text

            entity_label = language_v1.Entity.Type(gcp_entity.type_).name
            entity_data[ent_text]["label"] = entity_label

            for metadata_name, metadata_value in gcp_entity.metadata.items():
                if metadata_name == "wikipedia_url":
                    entity_data[ent_text]["resolution_link"] = metadata_value
                elif metadata_name == "mid":
                    entity_data[ent_text]["resolution_id"] = metadata_value
                    entity_data[ent_text]["resolution_type"] = metadata_name

        entities = []
        for key, values in entity_data.items():
            print(values)
            entities.append(Entity.parse_obj(values))
        return entities
