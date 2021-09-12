from oapi_parse.commons.common_methods import CommonMethods
from oapi_parse.exceptions.oapi_exceptions import *
from oapi_parse.reader.oapijson import OpenApiJsonReader
from oapi_parse.reader.oapiyml import OpenApiYamlReader


class OApi_Extraction():

    def __init__(self, openapiinput: str):
        if openapiinput.lstrip().endswith(".yml"):
            self.__openapi_input_file_object = OpenApiYamlReader(openapiinput).read_open_api()
            print()
        elif openapiinput.lstrip().endswith(".json"):
            self.__openapi_input_file_object = OpenApiJsonReader(openapiinput).read_open_api()
        else:
            raise FileFormatError

    def get_info(self) -> dict:
        """
        The method get_info returns the info object of OPEN API documentation
        :return: Dictionary
        """
        if "info" in self.__openapi_input_file_object.keys():
            return self.__openapi_input_file_object["info"]
        else:
            raise OAPI_Info_NotFound

    def get_version(self) -> str:
        """
        The method get_version returns the revised version of the Open API documentation
        :return:
        """
        if "version" in self.get_info():
            return self.get_info()["version"]
        else:
            raise OAPI_Version_NotFound

    def get_open_doc_version(self):
        """
        The method get_open_doc_version returns the Open API documentation Version
        :return:
        :return:
        """
        if "openapi" in self.__openapi_input_file_object.keys():
            return self.__openapi_input_file_object["openapi"]
        else:
            raise OAPI_Version_NotFound

    def get_ref(self,referencepath):
        """
        Calls the main method from common methods
        :return:
        """
        return CommonMethods().get_reference(referencepath,self.__openapi_input_file_object)

    
    def get_paths(self):
        """
        This Method extracts the list of Paths, each element in the list is a dictionary comprising of all the information about the end point
        :return:
        """
        try:
            paths = self.__openapi_input_file_object["paths"]
            paths_list = []
            for path in paths.keys():
                for operation in paths[path].keys():
                    temp = {'endpoint': path, 'operation': operation}
                    temp.update(CommonMethods().check_references(paths[path][operation],self.__openapi_input_file_object))
                    paths_list.append(temp)
            return paths_list
        except Exception as e:
            pass