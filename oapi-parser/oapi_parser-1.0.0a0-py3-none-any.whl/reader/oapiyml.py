"""
The Class deals with parsing the Open API json file and send verify the Open API doc validation
"""
import yaml


class OpenApiYamlReader():

    def __init__(self, yamlfilepath: str):
        """
        Takes Json Filepath
        :param jsonfilepath:
        """
        self.__file = yamlfilepath

    def read_open_api(self) -> dict:
        """
        Reads the open api json doc and returns the json object
        :return:
        """
        try:
            with open(self.__file) as openapi_json_input:
                return yaml.safe_load(openapi_json_input)
        except FileNotFoundError as e:
            print("File Not Found Error: Please make sure that the file name is accurate along with valid path")
            print("Provided file is "+self.__file)
        except Exception as oe:
            print(oe)
