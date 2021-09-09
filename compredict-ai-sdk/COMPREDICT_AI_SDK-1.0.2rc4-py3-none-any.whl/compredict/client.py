import base64
from json import dumps as json_dump, dump
from os import remove
from os.path import exists
from tempfile import NamedTemporaryFile
from typing import Optional, Union, IO, List, Type

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from pandas import DataFrame
from pandas.io.common import get_handle

from compredict.connection import Connection
from compredict.exceptions import ClientError, Error
from compredict.resources import resources
from compredict.singleton import Singleton

CONTENT_TYPES = ["application/json", "application/parquet", "text/csv"]


@Singleton
class api:

    def __init__(self,
                 token: Optional[str] = None,
                 callback_url: Optional[str] = None,
                 ppk: Optional[str] = None,
                 passphrase: Optional[str] = None,
                 url: Optional[str] = None):
        """
        COMPREDICT's AI Core Client that will provide an interface for communication. This class is singleton.

        :param token: API Key used for authorization.
        :param callback_url: URL for sending the results of long processes.
        :param ppk: Path to private key for decrypted requests responses (optional, only valid if public key is given \
        in dashboard)
        :param passphrase: Password to the private key.
        """
        if token is not None and len(token) != 40:
            raise Exception("API Key is not in valid format!")

        self.callback_url = callback_url
        url = api.BASE_URL.format(api.API_VERSION) if url is None else url
        self.connection = Connection(url, token=token)
        self.rsa_key = None
        if ppk is not None:
            self.set_ppk(ppk, passphrase)

    def fail_on_error(self, option: bool = True):
        """
        Ability to choose whether to raise exception on receiving error or return false.

        :param option: Boolean, True is to raise exception otherwise return false on error.
        :return: None
        """
        self.connection.fail_on_error = option

    def set_ppk(self, ppk: str, passphrase: str = ''):
        """
        Load the private key from the path and set the correct padding scheme.

        :param ppk: path to private key
        :param passphrase: password of the private key if any
        :return: None
        """
        with open(ppk) as f:
            self.rsa_key = RSA.importKey(f.read(), passphrase=passphrase)
            self.rsa_key = PKCS1_OAEP.new(self.rsa_key)
        pass

    def verify_peer(self, option: str):
        """
        Prompt SSL connection

        :param option: Boolean True/False
        :return:
        """
        self.connection.ssl = option

    @property
    def last_error(self) -> Error:
        return self.connection.last_error

    def _set_callback_urls(self, callback_url: Union[List[str], str]) -> str:
        """
        Accept list of urls and format them into one string with dividing '|' in between.
        This is the format accepted by ai core.
        :param callback_url: list of callback urls
        :return: one callback_url string
        """
        if isinstance(callback_url, list):
            multiple_callback = "|".join(callback_url)
        else:
            multiple_callback = callback_url

        return multiple_callback

    @staticmethod
    def __map_resource(
            resource: str,
            a_object: Union[dict, bool]
    ) -> Union[Type[resources.BaseResource], bool]:
        """
        Map the result to the correct resource

        :param resource: String name to the resource
        :param a_object: The values returned from the request.
        :return: New class of the resources with the response values.
        """
        if a_object is False:
            return a_object
        try:
            model_class = getattr(resources, resource)
            instance = model_class(**a_object)
        except(AttributeError, ModuleNotFoundError):
            raise ImportError("Resource {} was not found".format(resource))
        return instance

    @staticmethod
    def __map_collection(
            resource: str,
            objects: Union[dict, bool]
    ) -> Union[List[Type[resources.BaseResource]], bool]:
        """
        Create a list of resources if the results returns a list

        :param resource: String name to the resource
        :param objects: The list of values returned from the request.
        :return: List of instances of the given resource
        """
        if objects is False:
            return objects

        try:
            instances = list()
            for obj in objects:
                model_class = getattr(resources, resource)
                instances.append(model_class(**obj))
        except(AttributeError, ModuleNotFoundError):
            raise ImportError("Resource {} was not found".format(resource))
        return instances

    def get_algorithms(self) -> Union[List[resources.Algorithm], bool]:
        """
        Returns the collection of algorithms

        :return: list of algorithms
        """
        response = self.connection.GET('/algorithms')
        return self.__map_collection('Algorithm', response)

    def get_algorithm(self, algorithm_id: str) -> Union[resources.Algorithm, bool]:
        """
        Get the information of the given algorithm id

        :param algorithm_id: String identifier of the algorithm
        :return: Algorithm resource
        """
        response = self.connection.GET('/algorithms/{}'.format(algorithm_id))
        return self.__map_resource('Algorithm', response)

    def __process_data(self, data, content_type=None, compression=None):
        """
        Process the given data and convert it to file.

        :param data: The data to be sent for computation and prediction.
        :type data: dict | str | pandas
        :param content_type: The file content type to be converted to and sent.
        :type content_type: string
        :return: opened file, str, bool
        """
        if content_type is not None and content_type not in CONTENT_TYPES:
            raise ValueError("`{}` is not one of the allowed content types: {}".format(content_type,
                                                                                       CONTENT_TYPES))

        if isinstance(data, str):
            return open(data, "rb+"), content_type, False

        file = NamedTemporaryFile('wb+', delete=False)
        if isinstance(data, dict):
            content_type = "application/json"
            self.__write_json_file(file, data, compression=compression)
        elif isinstance(data, DataFrame):
            if content_type is None or content_type == "application/json":
                content_type = "application/json"
                self.__write_json_file(file, data.to_dict("list"), compression=compression)
            elif content_type == "application/parquet":
                data.to_parquet(file.name, compression=compression)
            elif content_type == "text/csv":
                data.to_csv(file.name, sep=',', compression=compression)
        return file, content_type, True

    @staticmethod
    def __write_json_file(t_file, data, compression=None):
        """
        function to write JSON into a file and point again to the top of the file for reading.

        :param t_file: temporary file to contain the data
        :type t_file: tempfile.NamedTemporaryFile
        :param data: The data to be stored.
        :type data: dict
        :param compression: JSON compression type, same compression methods as in `to_json` in pandas.
        :type compression: string.
        :return: saved file.
        """
        file_handle = get_handle(t_file.name, "w", compression=compression)
        file = file_handle[0] if isinstance(file_handle, tuple) else file_handle.handle

        with file as f:
            dump(data, f)
        t_file.seek(0)

    def run_algorithm(self,
                      algorithm_id: str,
                      data: Union[str, DataFrame, dict],
                      version: Optional[str] = None,
                      evaluate: bool = True,
                      encrypt: bool = False,
                      callback_url: Optional[Union[str, List[str]]] = None,
                      callback_param: Optional[Union[dict, List[dict]]] = None,
                      file_content_type: Optional[str] = None,
                      compression: Optional[str] = None) -> Union[resources.Task, resources.Result, bool]:
        """
        Run the given algorithm id with the passed data. The user have the ability to toggle encryption and evaluation.

        :param algorithm_id: String identifier of the algorithm
        :param data: JSON format of the data given with the correct keys as specified in the algorithm's template.
        :param version: Choose the version of the algorithm you would like to call. Default is latest version.
        :param evaluate: Boolean to whether evaluate the results of predictions or not.
        :param encrypt: Boolean to encrypt the data if the data is escalated to queue or not.
        :param callback_param: The callback additional parameter to be sent back when requesting the results.
                               If multiple callback_urls are specified, different parameters can be defined for each
                               url. In this case list of dictionaries is required. If single callback dictionary is
                               passed with list of callback urls - then the same parameters will be used with all
                               callback urls.
        :param callback_url: Callback urls to send the results to once computed, can be a list of urls.
        :param file_content_type: type of data to be sent to AI Core.
        :param compression: The compressed type of the data, the compression supported is what pandas supports \
        for the file content type you will send. Compression is only supported if encrypt is false. Based on data type:
            - if data is pandas or dict, then the compression is done by the function.
            - if string or path, then it describes the compression of the file sent.
        :return: Prediction if results are return instantly or Task otherwise.
        """
        if encrypt is True and self.rsa_key is None:
            raise ClientError("Please supply private key to encrypt the data")
        compression = compression if encrypt is False else None

        file, to_remove = None, False
        try:
            file, file_content_type, to_remove = self.__process_data(data, file_content_type,
                                                                     compression=compression)

            callback_url = self._set_callback_urls(
                callback_url) if callback_url is not None else self.callback_url

            params = dict(evaluate=self.__process_evaluate(evaluate), encrypt=encrypt,
                          callback_url=callback_url, callback_param=json_dump(callback_param),
                          compression=compression, version=version)
            if encrypt:
                self.RSA_encrypt(file)
            files = {"features": ('features.json', file, file_content_type)}
            response = self.connection.POST('/algorithms/{}/predict'.format(algorithm_id),
                                            data=params, files=files)
            resource = 'Task' if response is not False and 'job_id' in response else 'Result'
        except Exception as e:
            raise ClientError(e)
        finally:
            if file is not None:
                file.close()
                if to_remove and exists(file.name):
                    remove(file.name)
        return self.__map_resource(resource, response)

    @staticmethod
    def __process_evaluate(evaluate):
        """
        Check the type of evaluate parameter and parse it accordingly.

        :param evaluate: evaluation of the algorithm
        :type evaluate: bool|dict|string
        :return: bool|string
        """
        if isinstance(evaluate, dict):
            return json_dump(evaluate)
        return evaluate

    def get_task_results(self, task_id: str) -> Union[resources.Task, bool]:
        """
        Check COMPREDICT'S AI Core for the results of the computation.

        :param task_id: String identifier of the job.
        :return: The new results of the Task
        """
        response = self.connection.GET('/algorithms/tasks/{}'.format(task_id))
        return self.__map_resource('Task', response)

    def get_algorithm_versions(self, algorithm_id: str) -> Union[List[resources.Version], bool]:
        """
        Get all versions of an algorithm.

        :param algorithm_id: The id of the main algorithm
        :return: List of versions
        """
        response = self.connection.GET('/algorithms/{}/versions'.format(algorithm_id))
        if isinstance(response, list):
            [response[i].update(dict(algorithm_id=algorithm_id)) for i in range(len(response))]
        return self.__map_collection('Version', response)

    def get_algorithm_version(self, algorithm_id: str, version: str) -> Union[resources.Version, bool]:
        """
        Get a specific version of an algorithm.

        :param algorithm_id: The id of the main algorithm
        :param version: Specify the version of the algorithm
        :return: Version
        """
        response = self.connection.GET('/algorithms/{}/versions/{}'.format(algorithm_id, version))
        if isinstance(response, dict):
            response.update(dict(algorithm_id=algorithm_id))
        return self.__map_resource('Version', response)

    def get_template(self, algorithm_id: str,
                     file_type: str = 'input',
                     version: Optional[str] = None) -> NamedTemporaryFile:
        """
        Return the template that explains the data to be sent for the algorithms. Bear in mind, to close the file once
        done to delete it.

        :param algorithm_id: String identifier of the Algorithm.
        :param file_type: (default `input`) to retrieve the type of the document. Can be either `input` or `output`
        :param version: (default None) ability to specify the version of the template to retrieve. Default will get
        the latest version.
        :return: NamedTemporaryFile of the results.
        """
        get_args = self.__build_get_args(type=file_type, version=version)
        response = self.connection.GET('/algorithms/{}/template{}'.format(algorithm_id, get_args))
        return response

    def get_graph(self, algorithm_id: str, file_type: str,
                  version: Optional[str] = None) -> NamedTemporaryFile:
        """
        Return the graph that explains the input data to be sent for the algorithms.

        :param algorithm_id: String identifier of the Algorithm.
        :param file_type: (default `input`) to retrieve the type of the document. Can be either `input` or `output`
        :param version: (default None) ability to specify the version of the graph to retrieve. Default will get
        the latest version.
        :return: NamedTemporaryFile of the results.
        """
        get_args = self.__build_get_args(type=file_type, version=version)
        response = self.connection.GET('/algorithms/{}/graph{}'.format(algorithm_id, get_args))
        return response

    @staticmethod
    def __build_get_args(**kwargs):
        return "?" + "&".join(
            ["{}={}".format(key, value) for key, value in kwargs.items() if value is not None])

    def RSA_encrypt(self, data: Union[str, IO], chunk_size: int = 214):
        """
        Encrypt the message by the provided RSA public key.

        :param data: message of file contains the data to be encrypted
        :type data: string | file
        :param chunk_size: the chunk size used for PKCS1_OAEP decryption, it is determined by \
        the private key length used in bytes - 42 bytes.
        :type chunk_size: int
        :return: Base 64 encryption of the encrypted message
        :rtype: binray
        """
        if self.rsa_key is None:
            raise Exception("Path to private key should be provided to decrypt the response.")

        is_file = hasattr(data, 'read') and hasattr(data, 'write')
        msg = data if not is_file else data.read()

        padding = b"" if isinstance(msg, bytes) else ""

        encrypted = b''
        offset = 0
        end_loop = False

        while not end_loop:
            chunk = msg[offset:offset + chunk_size]

            if len(chunk) % chunk_size != 0:
                chunk += padding * (chunk_size - len(chunk))
                end_loop = True

            chunk = chunk if isinstance(msg, bytes) else chunk.encode()
            encrypted += self.rsa_key.encrypt(chunk)
            offset += chunk_size

        encrypted = base64.b64encode(encrypted)

        if is_file:
            data.seek(0)
            data.write(encrypted)
            data.seek(0)

        return encrypted

    def RSA_decrypt(self, encrypted_msg: Union[str, bytes], chunk_size=256, to_bytes=False):
        """
        Decrypt the encrypted message by the provided RSA private key.

        :param encrypted_msg: Base 64 encode of The encrypted message.
        :type encrypted_msg: binary
        :param chunk_size: It is determined by the private key length used in bytes.
        :type chunk_size: int
        :param to_bytes: Return bytes instead of string
        :type to_bytes: Boolean (default False)
        :return: The decrypted message
        :rtype: string
        """
        if self.rsa_key is None:
            raise Exception("Path to private key should be provided to decrypt the response.")

        encrypted_msg = base64.b64decode(encrypted_msg)

        offset = 0
        decrypted = b""

        while offset < len(encrypted_msg):
            chunk = encrypted_msg[offset:offset + chunk_size]

            decrypted += self.rsa_key.decrypt(chunk)

            offset += chunk_size

        return decrypted.decode() if not to_bytes else decrypted

    @staticmethod
    def __is_binary(filepath: str):
        """
        Return true if the given filename appears to be binary.
        File is considered to be binary if it contains a NULL byte.
        FIXME: This approach incorrectly reports UTF-16 as binary.
        """
        with open(filepath, 'rb') as f:
            for block in f:
                if b'\0' in block:
                    return True
        return False
