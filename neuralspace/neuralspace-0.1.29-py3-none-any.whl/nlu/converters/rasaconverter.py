from typing import Any, Dict, List, Text, Union

from rasa.shared.nlu.training_data.training_data import TrainingData

from neuralspace.nlu.converters.base import DataConverter


class RasaConverter(DataConverter):
    def __init__(self, language: Text):
        super().__init__(language=language)

    def lookup_converter(
        self, final_data
    ):
        list_of_lookups = []
        for value in final_data:
            value["entity"] = value.pop("name")
            value["examples"] = value.pop("elements")
            value["language"] = self.language
            value["entityType"] = "lookup"
            list_of_lookups.append(value)
        return list_of_lookups

    def regex_converter(
        self, final_data
    ):
        """
        :param language: To specify which language that the entity belongs
        :type final_data: Dictionary of object that contains all the NLU data.
        """
        list_of_regex = []
        tracker_for_dictionary = []
        for value in final_data:
            if value["name"] not in tracker_for_dictionary:
                tracker_for_dictionary.append(value["name"])
                value["entity"] = value.pop("name")
                value["examples"] = [value.pop("pattern")]
                value["language"] = self.language
                value["entityType"] = "regex"
                list_of_regex.append(value)
            else:
                index = tracker_for_dictionary.index(value["name"])
                list_of_regex[index]["examples"].append(value["pattern"])
        return list_of_regex

    def synonym_converter(
        self, final_data
    ):
        """
        :param language: To specify which language that the entity belongs
        :type final_data: Dictionary of object that contains all the NLU data.
        """
        list_of_synonyms = []
        tracker_for_dictionary = []
        for value, key in zip(final_data.values(), list(final_data.keys())):
            if value not in tracker_for_dictionary:
                tracker_for_dictionary.append(value)
                list_of_synonyms.append(
                    {
                        "entity": value,
                        "examples": [],
                        "language": self.language,
                        "entityType": "synonym",
                    }
                )

            index = tracker_for_dictionary.index(value)
            list_of_synonyms[index]["examples"].append(key)
        return list_of_synonyms

    @staticmethod
    def training_data_converter(
        final_data: TrainingData,
    ) -> List[Union[Text, Dict[Text]]]:
        """
        :type final_data: Dictionary of object that contains all the NLU data.
        """
        list_of_examples = []
        for ex in final_data.nlu_examples:
            list_of_examples.append(ex.as_dict())
        return list_of_examples
