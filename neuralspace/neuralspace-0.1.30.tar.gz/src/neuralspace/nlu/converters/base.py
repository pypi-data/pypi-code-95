from typing import Any, Dict, List, Text, Union


class DataConverter:
    def __init__(self, language: Text):
        self.language = language

    @staticmethod
    def training_data_converter(final_data) -> List[Union[Text, Dict[Text, Any]]]:
        NotImplementedError("Training data converter is not implemented")
        pass

    def regex_converter(
        self, final_data
    ) -> List[Dict[str, Union[Union[str, List[Any]], Any]]]:
        NotImplementedError("Regex converter is not implemented")

    def synonym_converter(
        self, final_data
    ) -> List[Dict[str, Union[Union[str, List[Any]], Any]]]:
        NotImplementedError("synonym converter is not implemented")

    def lookup_converter(self, final_data):
        NotImplementedError("lookup converter is not implemented")
