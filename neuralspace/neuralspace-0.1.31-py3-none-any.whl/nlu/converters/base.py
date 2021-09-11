from typing import Text


class DataConverter:
    def __init__(self, language: Text):
        self.language = language

    @staticmethod
    def training_data_converter(final_data):
        NotImplementedError("Training data converter is not implemented")
        pass

    def regex_converter(self, final_data):
        NotImplementedError("Regex converter is not implemented")

    def synonym_converter(self, final_data):
        NotImplementedError("synonym converter is not implemented")

    def lookup_converter(self, final_data):
        NotImplementedError("lookup converter is not implemented")
