from typing import Text

from neuralspace.nlu.converters.base import DataConverter


class DialogflowConverter(DataConverter):
    def __init__(self, language: Text):
        super().__init__(language=language)

    @staticmethod
    def training_data_converter(final_data):
        """
        :type final_data: Dictionary of object that contains all the NLU data.
        """
        list_of_examples = []
        for value in final_data["common_examples"]:
            list_of_examples.append(value)
        return list_of_examples

    def regex_converter(self, final_data):
        """
        :type final_data: Dictionary of object that contains all the NLU data.
        """
        tracker_for_dictionary = []
        regex_entity = []
        for value in final_data["regex_features"]:
            if value["name"] not in tracker_for_dictionary:
                tracker_for_dictionary.append(value["name"])
                regex_entity.append(
                    {
                        "entity": value["name"],
                        "examples": [],
                        "language": self.language,
                        "entityType": "regex",
                    }
                )
            index = tracker_for_dictionary.index(value["name"])
            regex_entity[index]["examples"].append(value["pattern"])
        return regex_entity

    def lookup_converter(self, final_data):
        """
        :type final_data: Dictionary of object that contains all the NLU data.
        """
        list_of_lookup = []
        for value in final_data["lookup_tables"]:
            value["entity"] = value.pop("name")
            value["examples"] = value.pop("elements")
            value["language"] = self.language
            value["entityType"] = "lookup"
            list_of_lookup.append(value)

        return list_of_lookup

    def synonym_converter(self, final_data):
        """
        :type final_data: Dictionary of object that contains all the NLU data.
        """
        list_of_synonyms = []
        for value in final_data["entity_synonyms"]:
            value["entity"] = value.pop("value")
            value["examples"] = value.pop("synonyms")
            value["language"] = self.language
            value["entityType"] = "synonym"
            list_of_synonyms.append(value)
        return list_of_synonyms
