import os
import unittest

from oapi_parse.exceptions.oapi_exceptions import FileFormatError
from oapi_parse.extract.extractor import OApi_Extraction

class TestExtract(unittest.TestCase):

    def test_file_format_exception(self):
        """
        Tests the NO exception is raised for a known format
        :return:
        """
        try:
            oapi_extract= OApi_Extraction(os.path.join(os.path.dirname(__file__), os.path.normpath("somefile.yml")))
            assert True
        except FileFormatError:
            assert False

    def test_file_format_exception_negative(self):
        """
        Tests the whether execption is raised for a unknown format
        :return:
        """
        with self.assertRaises(FileFormatError):
            oapi_extract= OApi_Extraction(os.path.join(os.path.dirname(__file__), os.path.normpath("somefile.ylm")))

    def test_get_info(self):
        """
        Tests the get_info method
        :return:
        """
        try:
            oapi_extract = OApi_Extraction(os.getcwd()+"/data/sample.yml")
            if type(oapi_extract.get_info()) is dict:
                assert True
            else:
                assert False
        except FileFormatError:
            assert False

    def test_get_version(self):
        """
        Tests the get_version method
        :return:
        """
        try:
            oapi_extract = OApi_Extraction(os.getcwd()+"/data/sample.yml")
            if oapi_extract.get_version()== "1.0.0":
                assert True
            else:
                assert False
        except FileFormatError:
            assert False

    def test_get_open_doc_version(self):
        """
        Tests the get_open_doc_version method
        :return:
        """
        try:
            oapi_extract = OApi_Extraction(os.getcwd()+"/data/sample.yml")
            if oapi_extract.get_open_doc_version() == "3.0.0":
                assert True
            else:
                assert False
        except FileFormatError:
            assert False

    def test_get_reference(self):
        """
        Tests the get reference method
        :return:
        """
        try:
            oapi_extract = OApi_Extraction(os.getcwd() + "/data/sample.yml")
            value = oapi_extract.get_ref("#/components/schemas/Pet")
            if type(value) is dict:
                assert True
            else:
                assert False

        except Exception as e:
            raise e

    def test_get_paths(self):
        """
        Tests the get reference method
        :return:
        """
        try:
            oapi_extract = OApi_Extraction(os.getcwd() + "/data/pet_store_30.json")
            value = oapi_extract.get_paths()
            print(value)
            if len(value) == 3:
                assert True
            else:
                assert False

        except Exception as e:
            raise e

if __name__ == '__main__':
    unittest.main()