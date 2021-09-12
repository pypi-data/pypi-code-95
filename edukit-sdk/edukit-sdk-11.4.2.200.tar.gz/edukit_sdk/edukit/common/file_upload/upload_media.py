#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json
import logging
import math
import os
import shutil
import time
import uuid

from edukit_sdk.edukit.common.config.config import Config
from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.constant.error_constant import ErrorConstant
from edukit_sdk.edukit.common.constant.file_upload_constant import \
    FileUploadConstant
from edukit_sdk.edukit.common.constant.http_constant import HttpConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.file_upload.file_upload_request import \
    FileUploadRequest
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse


def tuple2_to_dict(lists: list):
    # 将返回头列表中的二元元组转化为字典列表
    headers_list = []
    if lists:
        for dict2 in lists:
            list_dict = []
            mydict = dict2.get(ClientConstant._HEADERS)
            if mydict:
                for item in mydict:
                    d = {item[0]: item[1]}
                    list_dict.append(d)
                dict2[ClientConstant._HEADERS] = list_dict
                headers_list.append(dict2)
    return headers_list


# 获取返回头列表中字典元素指定key的value
def get_list_dict_value(list_table: list, p_key):
    if list_table:
        for header in list_table:
            (key, value), = header.items()
            if key == p_key:
                return value


class UploadMedia:
    def __init__(self, file_request: FileUploadRequest,
                 request_sender: EduKitRequestSender):
        self._file_request = file_request
        config = Config()
        self._part_size = int(config.get_config().get(
            ClientConstant.PART_MAXSIZE))
        self._request_sender = request_sender

    def upload(self):
        suffix = os.path.splitext(self._file_request.path)[-1]
        if suffix not in FileUploadConstant.FILE_SUFFIX:
            raise EduKitException('Upload failed! ErrorMessage:{}'
                                  .format(ErrorConstant.MEDIA_FILE_TYPE_ERROR))
        apply_rsp = self.apply_upload_url()
        try:
            if self.is_multi_part(apply_rsp):
                # 需要分片,分片上传
                self.upload_file_parts(apply_rsp)
            else:
                logging.info('Uploading file ' + self._file_request.file_name)
                # 不需要分片,一次性上传文件
                self.upload_file(apply_rsp, self._file_request.path)
                logging.info('Uploading file ' + self._file_request.file_name +
                             ' success')
        except EduKitException as e:
            raise EduKitException("Upload failed! ErrorMessage:{}"
                                  .format(str(e)))
        return apply_rsp

    @staticmethod
    def is_multi_part(apply_rsp):
        return True if apply_rsp.get(ClientConstant.MULTI_PART_FLAG) else False

    def apply_upload_url(self):
        """
        申请文件上传地址
        :return:mixed
        """
        url = ApiConstant.APPLY_UPLOAD_URL
        body = {
            ClientConstant.FILE_NAME: self._file_request.file_name,
            ClientConstant.FILE_TYPE: self._file_request.file_type,
            ClientConstant.FILE_SIZE: self._file_request.file_size,
            ClientConstant.FILE_SHA256: self._file_request.sha256,
            ClientConstant.PUBLIC_FILE: self._file_request.public_file,
        }
        body = bytes(json.dumps(body), encoding=ClientConstant.UTF_8)
        headers = {HttpConstant.CONTENT_TYPE: HttpConstant.APPLICATION_JSON}
        rsp = HttpCommonResponse(
            self._request_sender.post(url=url, body=body, headers=headers))
        return rsp.get_rsp()

    def upload_file(self, apply_rsp, file_path):
        """
        不分片时一次性上传文件
        :param file_path: 要上传的文件地址
        :param apply_rsp: 申请上传文件返回的结果集包含上传地址,请求头,上传方法
        :return:mixed
        """
        url = apply_rsp.get(ClientConstant.TMP_UPLOAD_URL)
        headers = json.loads(apply_rsp.get(ClientConstant.UPLOAD_HEADERS))
        method = apply_rsp.get(ClientConstant.UPLOAD_METHOD)
        with open(file_path, ClientConstant.RB) as f:
            file = f.read()
        try:
            rsp = HttpCommonResponse(
                self._request_sender.upload_once(url=url,
                                                 headers=headers,
                                                 body=file,
                                                 method=method))
        except EduKitException as e:
            raise EduKitException('Upload failed! ErrorMessage:{}'
                                  .format(str(e)))
        return rsp.get_headers()

    def upload_file_parts(self, apply_rsp):
        """
        上传分片
        :param apply_rsp: 申请上传文件地址后的返回结果
        :return:
        """
        cache_rsp = self.part_file(apply_rsp.get(ClientConstant.MAX_PAER_SIZE))
        try:
            upload_start_time = time.time()
            # 获得分片上传信息列表
            part_upload_list = self.get_part_upload_list(
                apply_rsp.get(ClientConstant.FILE_ID), cache_rsp)
            # 上传分片文件
            part_upload_rsp_list = self.upload_file_list(
                part_upload_list.get(ClientConstant.FILE_PARTS), cache_rsp,
                apply_rsp.get(ClientConstant.FILE_ID), upload_start_time)
            # 分片合并
            response = self.multipart_compose(
                apply_rsp.get(ClientConstant.FILE_ID), part_upload_rsp_list)
            return response
        except EduKitException as e:
            raise EduKitException(
                'Compose file parts failed!, ErrorMessage:{}'.format(str(e)))
        finally:
            if os.path.exists(cache_rsp.get('cache_path')):
                shutil.rmtree(cache_rsp.get('cache_path'))

    def part_file(self, api_max_part_size):
        """
        将文件分片保存到缓存目录中
        :param api_max_part_size: 返回的最大分片size
        :return:
        """
        file_path = self._file_request.path
        chunk_size = self._part_size \
            if api_max_part_size \
               > self._part_size else api_max_part_size
        file_size = os.path.getsize(file_path)
        total_chunks = math.ceil(file_size / chunk_size)
        cache_id = str(uuid.uuid1()).replace("-", "")
        cache_path = CommonConstant.ROOT_PATH + \
                     FileUploadConstant.FILE_CACHE_DIR + cache_id
        os.makedirs(cache_path, CommonConstant.DIR_DEFAULT_MOD)

        for index in range(0, total_chunks):
            try:
                with open(file_path, ClientConstant.RB) as file:
                    file.seek(index * chunk_size, 0)
                    chunk = file.read(chunk_size)
                    chunk_cached_path = cache_path + os.sep + str(index)
                    with open(chunk_cached_path,
                              CommonConstant.FILE_MODE_CREATE_WRITE)\
                            as cached_file:
                        cached_file.write(chunk)
                    os.chmod(chunk_cached_path,
                             CommonConstant.FILE_DEFAULT_MOD)
            except Exception as e:
                raise EduKitException(
                    "Part file failed, ErrorMessage:{}".format(str(e)))

        logging.info('Part file {}'.format(self._file_request.file_name) +
                     ' to {}'.format(total_chunks) + ' parts.')
        return {'cache_path': cache_path, 'total_chunks': total_chunks}

    def upload_file_list(self, file_parts, cache_rsp, file_id,
                         upload_start_time):
        """
        * 上传分片文件
        * :param: fileParts 分片上传文件申请返回的分片文件信息集合
        * :param: cacheRsp 返回的最大分片大小
        * :param: fileId 申请上传地址返回的文件id
        * :param: uploadStartTime 上传开始时间
        """
        part_upload_rsp_list = []
        for index, file_part in enumerate(file_parts):
            # 当上传超过一定时间需要重新获取上传信息
            single_start_time = time.time()
            if self.is_upload_timeout(upload_start_time, single_start_time):
                part_upload_list = self.get_part_upload_list(
                    file_id, cache_rsp)
                file_parts = part_upload_list.get(ClientConstant.FILE_PARTS)
                upload_start_time = time.time()

            single_upload_info = {
                ClientConstant.TMP_UPLOAD_URL:
                    file_part.get(ClientConstant.MATERIAL_URL),
                ClientConstant.UPLOAD_HEADERS:
                    file_part.get('headers'),
                ClientConstant.UPLOAD_METHOD:
                    file_part.get('method')
            }

            logging.info('Uploading file part ' + str(index))
            try:
                single_rsp = self.upload_file(single_upload_info,
                                              (cache_rsp.get('cache_path') +
                                               os.sep + str(index))).__dict__
                part_object = {
                    ClientConstant.PART_OBJECT_ID:
                        file_part.get(ClientConstant.PART_OBJECT_ID)
                }
                # 合并两个字典
                part_upload_rsp_dict = single_rsp.copy()
                part_upload_rsp_dict.update(part_object)
                part_upload_rsp_list.append(part_upload_rsp_dict)
            except EduKitException as e:
                # 删除非空目录
                shutil.rmtree(cache_rsp.get('cache_path'))
                raise EduKitException(
                    'Upload file part {} failed!, ErrorMessage:{}'.format(
                        str(index + 1), str(e)))

        # 如果在上传分片超时,会重新获取分片上传信息,故将缓存数据放在最后删除
        shutil.rmtree(cache_rsp['cache_path'])
        part_upload_rsp_list = tuple2_to_dict(part_upload_rsp_list)
        return part_upload_rsp_list

    def get_part_upload_list(self, file_id, cache):
        """
            * 获得分片上传信息列表
            * :param: fileId
            * :param: cache
            * :return: HttpCommonResponse
           """
        chunk_list = []
        if cache.get('total_chunks'):
            for index in range(0, cache.get('total_chunks')):
                temp_path = cache.get('cache_path') + os.sep + str(index)
                chunk_dict = {
                    ClientConstant.FILE_SHA256: Helpers.get_sha256(temp_path),
                    ClientConstant.FILE_SIZE: os.path.getsize(temp_path)
                }
                # 将字典元素放入列表中
                chunk_list.append(chunk_dict)

        url = ApiConstant.MULTIPART_PARTS_URL
        body = {
            ClientConstant.FILE_PARTS: chunk_list,
            ClientConstant.FILE_ID: file_id
        }
        body = bytes(json.dumps(body), encoding=ClientConstant.UTF_8)
        headers = {HttpConstant.CONTENT_TYPE: HttpConstant.APPLICATION_JSON}
        rsp = HttpCommonResponse(
            self._request_sender.post(url=url, body=body, headers=headers))
        return rsp.get_rsp()

    @staticmethod
    def is_upload_timeout(upload_start_time, single_start_time):
        return single_start_time - upload_start_time > \
               FileUploadConstant.FILE_UPLOAD_LIMIT_TIME

    def multipart_compose(self, file_id, part_upload_rsp_list):
        """
        * 分片合并
        * :param: fileId:文件id
        * :param: part_upload_rsp_list 请求分片上传后的返回集合
        """
        url = ApiConstant.MULTIPART_COMPOSE_URL
        file_parts_list = []

        if part_upload_rsp_list:
            for part_rsp in part_upload_rsp_list:
                # 上一步骤接口返回数据多了引号'"'，封装数据时删除
                single_file_part = {
                    ClientConstant.PART_OBJECT_ID:
                        part_rsp.get(ClientConstant.PART_OBJECT_ID),
                    "etag":
                        get_list_dict_value(
                            part_rsp.get(ClientConstant._HEADERS),
                                            ClientConstant.E_TAG).strip('"'),
                    ClientConstant.GOOGLE_GENERATION:
                        ""
                }

                if part_rsp.get(ClientConstant.X_GOOGLE_GENERATION):
                    single_file_part[
                        ClientConstant.
                            GOOGLE_GENERATION] = get_list_dict_value(
                        part_rsp.get(ClientConstant._HEADERS),
                        ClientConstant.X_GOOGLE_GENERATION).strip('"')
                file_parts_list.append(single_file_part)
        body = {
            ClientConstant.FILE_ID: file_id,
            ClientConstant.FILE_PARTS: file_parts_list
        }
        body = bytes(json.dumps(body), encoding=ClientConstant.UTF_8)
        headers = {HttpConstant.CONTENT_TYPE: HttpConstant.APPLICATION_JSON}
        return HttpCommonResponse(
            self._request_sender.post(url=url, body=body, headers=headers))
