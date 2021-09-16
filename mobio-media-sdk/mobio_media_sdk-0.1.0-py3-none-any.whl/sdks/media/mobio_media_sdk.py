import calendar
import json
import os
import shutil
import time
import uuid
from datetime import datetime

import magic
from confluent_kafka import Producer
from mobio.libs.Singleton import Singleton
from mobio.libs.caching import LruCache

from .custom_mimetypes import CustomMimetypes
from .config import ConsumerTopic
from .config import MobioEnvironment
from .config import StoreCacheType, Cache
from .constant import DirSaveFile, FieldConstantResponse, CONSTANT_MAP_FORMAT_FILE
from .dir import APP_TMP_DATA_DIR, STATIC_DATA_DIR


@Singleton
class MobioMediaSDK(object):
    lru_cache = None
    DEFAULT_REQUEST_TIMEOUT_SECONDS = 15
    LIST_VERSION_VALID = ["api/v1.0"]

    def __init__(self):
        self.folder_static = 'static'
        self.media_api_version = MobioMediaSDK.LIST_VERSION_VALID[-1]

        self.redis_uri = None
        self.admin_host = None
        self.instance = None

    def config(
            self,
            admin_host=None,
            redis_uri=None,
            cache_prefix=None,
            api_media_version=None
    ):
        """
        :param admin_host:
        :param admin_host:
        :param redis_uri: config redis_uri
        :param cache_prefix:
        :param api_media_version:

        :return:
        """
        self.admin_host = admin_host
        if api_media_version:
            self.media_api_version = api_media_version
        if redis_uri:
            self.redis_uri = redis_uri
            if cache_prefix:
                cache_prefix += Cache.PREFIX_KEY
            MobioMediaSDK.lru_cache = LruCache(
                store_type=StoreCacheType.REDIS,
                cache_prefix=cache_prefix,
                redis_uri=redis_uri,
            )

        self.instance = Producer(
            {
                "request.timeout.ms": 20000,
                "bootstrap.servers": MobioEnvironment.KAFKA_BROKER,
            }
        )

    @staticmethod
    def valid_input_upload(file_path, file_data, merchant_id, expire=None):
        if not merchant_id:
            raise Exception("merchant_id require")
        if not file_path and not file_data:
            raise Exception("Need to pass 1 of 2 parameters file_path or file_data")
        if file_path and not os.path.isfile(file_path):
            raise Exception("file_path: {} not exist.".format(file_path))
        if expire:
            try:
                expire = datetime.strptime(expire, "%Y-%m-%dT%H:%M:%SZ")
            except Exception as ex:
                raise Exception("format expire: {} error: {}".format(expire, ex))

    @staticmethod
    def get_file_name(file_path, file_data):
        filename = None
        if file_path:
            head, filename = os.path.split(file_path)
        if file_data:
            try:
                filename = file_data.filename
            except Exception as ex:
                print("[ERROR] file_data: {}".format(ex))
        if not filename:
            filename = str(uuid.uuid4())
        return filename

    def upload_without_kafka(
            self,
            merchant_id: str,
            file_path: str = '',
            file_data=None,
            filename: str = '',
            type_media=DirSaveFile.UPLOAD,
            tag: str = '',
            expire=None,
            do_not_delete: bool = False,
            short_link: bool = False,
            desired_format=None
    ):
        """
        :param merchant_id:
        :param file_path:
        :param file_data:
        :param filename:
        :param type_media:
        :param tag:
        :param expire:
        :param do_not_delete
        :param short_link: rút gọn lịnk
        :param desired_format: định dạng mong muốn khi upload

        "return:
        {
            "url": "",
            "local_host":""
        }
        """
        MobioMediaSDK.valid_input_upload(
            file_path=file_path,
            file_data=file_data,
            merchant_id=merchant_id,
            expire=expire
        )

        time_start = time.time()
        mimetype_str = MobioMediaSDK.get_mimetype(file_path=file_path, file_data=file_data)
        MobioMediaSDK.validate_desired_format(desired_format=desired_format, mimetype_str=mimetype_str)
        if not filename:
            filename = MobioMediaSDK.get_file_name(file_path=file_path, file_data=file_data)
        host_by_merchant_id = self._get_host_by_merchant_id(merchant_id=merchant_id)
        print("upload_without_kafka()::get_host_by_merchant_id:: %s" % (time.time() - time_start))
        dist_file, filename = self.create_dir_save_file(
            folder=STATIC_DATA_DIR,
            merchant_id=merchant_id,
            type_media=type_media,
            filename=filename,
            short_link=short_link
        )
        if file_path:
            # shutil.move(file, dist_file)
            shutil.move(file_path, dist_file)
        else:
            file_data.save(dist_file)
        url = os.path.join(host_by_merchant_id, self.folder_static, merchant_id, type_media, filename)
        if short_link:
            url = os.path.join(host_by_merchant_id, self.folder_static, filename)
        print("upload_without_kafka()::url:: %s" % (time.time() - time_start))
        data_send_producer = {
            "filename": filename,
            "merchant_id": merchant_id,
            "url": url,
            "type_media": type_media,
            "tag": tag,
            "expire": expire,
            "dist_file": dist_file,
            "mimetype_str": mimetype_str,
            "do_not_delete": do_not_delete
        }

        # message_data = Message(message=data_send_producer)
        # KafkaUtil().produce(topic=ConsumerTopic.TOPIC_SAVE_INFO_MEDIA_SDK, message=message_data)
        print("upload_without_kafka()::send message to topic:: %s" % (time.time() - time_start))
        self.send_message_to_topic(topic=ConsumerTopic.TOPIC_SAVE_INFO_MEDIA_SDK, data=json.dumps(data_send_producer))
        print("upload_without_kafka()::send message to topic:: %s" % (time.time() - time_start))
        return {
            FieldConstantResponse.URL: url,
            FieldConstantResponse.LOCAL_PATH: dist_file,
            FieldConstantResponse.FILENAME: filename,
            FieldConstantResponse.FORMAT: mimetype_str
        }

    def upload_with_kafka(
            self,
            merchant_id,
            file_path: str = None,
            file_data=None,
            filename=None,
            type_media=DirSaveFile.UPLOAD,
            tag=None,
            expire=None,
            do_not_delete=False,
            short_link=False,
            desired_format=None
    ):
        """
        :param merchant_id:
        :param filename:
        :param file_path:
        :param file_data:
        :param filename:
        :param type_media:
        :param tag:
        :param expire:
        :param do_not_delete:
        :param short_link:
        :param desired_format: định dạng mong muốn khi upload

        :return:
        {
        }
        """
        MobioMediaSDK.valid_input_upload(
            file_path=file_path,
            file_data=file_data,
            merchant_id=merchant_id,
            expire=expire
        )

        time_start = time.time()
        mimetype_str = MobioMediaSDK.get_mimetype(file_path=file_path, file_data=file_data)
        MobioMediaSDK.validate_desired_format(desired_format=desired_format, mimetype_str=mimetype_str)
        if not filename:
            filename = MobioMediaSDK.get_file_name(file_path=file_path, file_data=file_data)

        tmp_file, filename = self.create_dir_save_file(
            folder=APP_TMP_DATA_DIR,
            merchant_id=merchant_id,
            type_media=type_media,
            filename=filename
        )

        if file_path:
            # shutil.move(file, tmp_file)
            shutil.move(file_path, tmp_file)
        else:
            file_data.save(tmp_file)
        print("upload_with_kafka()::move file:: %s" % (time.time() - time_start))
        dist_file, filename = self.create_dir_save_file(
            folder=STATIC_DATA_DIR,
            merchant_id=merchant_id,
            type_media=type_media,
            filename=filename,
            short_link=short_link
        )
        host_by_merchant_id = self._get_host_by_merchant_id(merchant_id=merchant_id)
        print("upload_with_kafka()::get_host_by_merchant_id:: %s" % (time.time() - time_start))
        url = os.path.join(host_by_merchant_id, self.folder_static, merchant_id, type_media, filename)
        if short_link:
            url = os.path.join(host_by_merchant_id, self.folder_static, filename)
        data_send_producer = {
            "filename": filename,
            "merchant_id": merchant_id,
            "tmp_file": tmp_file,
            "type_media": type_media,
            "tag": tag,
            "expire": expire,
            "dist_file": dist_file,
            "mimetype_str": mimetype_str,
            "do_not_delete": do_not_delete,
            "url": url
        }
        self.send_message_to_topic(topic=ConsumerTopic.TOPIC_UPLOAD_MEDIA_SDK, data=json.dumps(data_send_producer))
        print("upload_with_kafka()::send message to topic:: %s" % (time.time() - time_start))
        return {
            FieldConstantResponse.URL: url,
            FieldConstantResponse.LOCAL_PATH: dist_file,
            FieldConstantResponse.FILENAME: filename,
            FieldConstantResponse.FORMAT: mimetype_str,
        }

    @classmethod
    def create_dir_save_file(cls, folder, merchant_id, type_media, filename, short_link=False):
        dir_file = os.path.join(folder, merchant_id)
        if type_media:
            dir_file = os.path.join(folder, merchant_id, type_media)
        if short_link:
            dir_file = folder
        os.makedirs(dir_file, exist_ok=True)
        local_path = os.path.join(dir_file, filename)
        if os.path.isfile(local_path):
            filename = str(calendar.timegm(time.gmtime())) + "_" + filename
            local_path = os.path.join(dir_file, filename)
        return local_path, filename

    @staticmethod
    def validate_desired_format(desired_format, mimetype_str):
        if not desired_format or desired_format == "all":
            return True
        all_format_desired = CONSTANT_MAP_FORMAT_FILE.get(desired_format)
        if (not all_format_desired) or (mimetype_str not in all_format_desired):
            extension = CustomMimetypes().mimetypes.guess_extension(mimetype_str)
            raise Exception("File định dạng {}, không đúng định dạng mong muốn là {}".format(extension, desired_format))

    def get_local_path_by_url(
            self,
            url,
            merchant_id
    ):
        host_by_merchant_id = self._get_host_by_merchant_id(merchant_id=merchant_id)
        host = os.path.join(host_by_merchant_id, self.folder_static)
        url_without_host = url.replace(host, "")
        url_without_host = url_without_host.split("/")
        url_without_host = [url for url in url_without_host if url]
        filename = url_without_host[-1]
        local_path = None
        if len(url_without_host) == 1:
            local_path, filename = self.create_dir_save_file(
                folder=STATIC_DATA_DIR,
                merchant_id=None,
                type_media=None,
                filename=filename
            )

        if len(url_without_host) == 2:
            local_path, filename = self.create_dir_save_file(
                folder=STATIC_DATA_DIR,
                merchant_id=merchant_id,
                type_media=None,
                filename=filename
            )

        if len(url_without_host) == 3:
            local_path, filename = self.create_dir_save_file(
                folder=STATIC_DATA_DIR,
                merchant_id=merchant_id,
                type_media=url_without_host[1],
                filename=filename
            )
        return local_path

    def create_filepath(
            self,
            merchant_id: str,
            filename: str = None,
            type_media: str = DirSaveFile.DOWNLOAD
    ):
        return self.create_dir_save_file(
            folder=STATIC_DATA_DIR,
            merchant_id=merchant_id,
            type_media=type_media,
            filename=filename
        )

    def finish_save_file_by_filepath(
            self,
            filepath,
            do_not_delete: bool = False,
            tag: str = "",
            expire: str = ''
    ):
        if not os.path.isfile(filepath):
            raise FileExistsError
        dist_file = filepath

        filename, file_extension = os.path.splitext(filepath)
        filepath = filepath.split("/")
        filepath = [path for path in filepath if path]
        filename = filepath[-1]
        merchant_id = filepath[-3]
        type_media = self.check_type_media(filepath[-2])

        host_by_merchant_id = self._get_host_by_merchant_id(merchant_id=merchant_id)
        url = os.path.join(host_by_merchant_id, self.folder_static, merchant_id, type_media, filename)
        data_send_producer = {
            "filename": filename,
            "merchant_id": merchant_id,
            "url": url,
            "type_media": type_media,
            "tag": tag,
            "expire": expire,
            "dist_file": dist_file,
            "mimetype_str": file_extension,
            "do_not_delete": do_not_delete
        }

        self.send_message_to_topic(topic=ConsumerTopic.TOPIC_SAVE_INFO_MEDIA_SDK, data=data_send_producer)

        return url

    def check_type_media(self, type_media):
        if type_media not in [DirSaveFile.UPLOAD, DirSaveFile.DOWNLOAD]:
            raise ValueError("Type media is not correct!")
        return type_media

    def _get_host_by_merchant_id(self, merchant_id):
        from .utils import get_host_by_merchant_id
        host_by_merchant_id = get_host_by_merchant_id(
            admin_host=self.admin_host,
            merchant_id=merchant_id,
            media_api_version=self.media_api_version,
            request_timeout=self.DEFAULT_REQUEST_TIMEOUT_SECONDS
        )
        if not host_by_merchant_id:
            return MobioEnvironment.PUBLIC_HOST
        return host_by_merchant_id

    @staticmethod
    def get_mimetype(file_data, file_path):
        if file_path and os.path.isfile(file_path):
            magic_init = magic.Magic(mime=True)
            mimetype_str = magic_init.from_file(file_path)
        else:
            mimetype_str = file_data.mimetype if file_data.mimetype else file_data.content_type
        print("mimetype_str::mimetype_str")
        return mimetype_str

    def override_file(
            self,
            filename=None,
            merchant_id=None,
            url="",
            file_path=None,
            file_data=None,
            desired_format=None
    ):
        MobioMediaSDK.valid_input_upload(
            file_path=file_path,
            file_data=file_data,
            merchant_id=merchant_id
        )
        mimetype_str = MobioMediaSDK.get_mimetype(file_path=file_path, file_data=file_data)
        MobioMediaSDK.validate_desired_format(desired_format=desired_format, mimetype_str=mimetype_str)
        time_start = time.time()
        # mimetype_str = self._get_mimetype(file)
        tmp_file, filename = self.create_dir_save_file(
            folder=APP_TMP_DATA_DIR,
            merchant_id=merchant_id,
            type_media=DirSaveFile.UPLOAD,
            filename=filename
        )
        if file_path:
            shutil.move(file_path, tmp_file)
        else:
            file_data.save(tmp_file)
        print("override_file()::move file:: %s" % (time.time() - time_start))
        data_send_producer = {
            "merchant_id": merchant_id,
            "url_override": url,
            "path_temp_file": tmp_file
        }

        self.send_message_to_topic(
            topic=ConsumerTopic.TOPIC_OVERRIDE_MEDIA_SDK,
            data=json.dumps(data_send_producer)
        )
        print("override_file()::send message to topic:: %s" % (time.time() - time_start))

    def delete_file(
            self,
            merchant_id,
            urls,
            type_delete=None
    ):
        if not urls:
            print("urls empty")
            return None

        data_send_producer = {
            "merchant_id": merchant_id,
            "urls": urls,
            "type_delete": type_delete
        }

        # message_data = Message(message=data_send_producer)
        # KafkaUtil().produce(topic=ConsumerTopic.TOPIC_DELETE_MEDIA_SDK, message=message_data)

        self.send_message_to_topic(
            topic=ConsumerTopic.TOPIC_DELETE_MEDIA_SDK,
            data=json.dumps(data_send_producer)
        )

    def send_message_to_topic(self, topic: str, data):
        self.instance.produce(topic, data)
        self.instance.poll(0)
        print("topic: {}, message: {}".format(topic, data))
        self.instance.flush()
