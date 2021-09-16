class String:
    def __init__(self):
        pass

    def extract_between(self, input_string : str, character : str) -> str:
        return input_string[input_string.find(character)+1 : input_string.rfind(character)]