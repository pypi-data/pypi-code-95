import logging
import operator
from functools import reduce

import jsonpath_rw
from box import Box
from requests import Response

_Response = Response

logger = logging.getLogger(__name__)


def get_from_dict(map_data, json_path):
    """
    :param map_data: {'a':1}
    :param json_path: _Response.data.userId
    :return:
    """
    if json_path.startswith('_Response'):
        json_path = json_path.split('.')[1:]
    else:
        json_path = json_path.split('.')
    try:
        return reduce(operator.getitem, json_path, map_data)
    except Exception:
        pass
    return jsonpath_rw.parse(('.'.join(json_path))).find(map_data)[0].value


class Response(_Response):
    def __init__(self, rep):
        """
        对原requests的Response对象添加更多操作和属性
        :param rep: requests的响应对象 rep = requests.get(xxx)
        """
        # self.code = code
        # self.data = data
        # self.message = message
        self.__dict__.update(rep.__dict__)
        
        try:
            self.rep_json = self.json()
        except UnicodeDecodeError:
            self.rep_json = dict(code='', data='', message='')
        
        self.rep_json = Box(self.rep_json)
    
    # @property
    # def code(self):
    #     return self.rep_json.code
    #
    # @property
    # def data(self):
    #     return self.rep_json.data
    #
    # @property
    # def msg(self):
    #     return self.rep_json.msg
    #
    # @property
    # def result(self):
    #     return self.rep_json
    
    def check_ok(self, http_code=200):
        """
        check response http status code
        {self.status_code}
        :param http_code:
        :return:
        """
        assert self.status_code == http_code, f'[http_code校验失败,实际值:{self.status_code} == 预期值：{http_code}]'
        logger.info(f'[http_code校验成功,实际值:{self.status_code} == 预期值：{http_code}]')
        return self
    
    def check_success(self, json_path='code'):
        """
        check biz response code
        :param json_path: _Response.data.name
        :return:
        :example:{'code': 200, data': {'type': 1, 'userId': 56895669}, 'message': ''}
                    json_path='code'
        :example: {'status':'SUCCESS', 'data': {'type': 1, 'userId':56895669, 'code': 200, }, 'message': ''}
                    json_path=data.userId=56895669
        """
        code = get_from_dict(self.json(), json_path)
        assert code == 200, f'[业务代码{json_path}校验失败，实际值:{code}==预期值:200]'
        logger.info(f'[业务代码code校验成功，实际值:{code}==预期值:200]')
        return self
    
    def check_value(self, expect_value, json_path_or_value):
        """
        check expect_value equals response data by json path
        @expect_value: 预期结果值
        @json_path:json path
        """
        if '.' in json_path_or_value:
            json_path_or_value = get_from_dict(self.json(), json_path_or_value)
        assert expect_value == json_path_or_value, f'[校验失败,预期结果={expect_value},实际结果={json_path_or_value}]'
        logger.info(f'[校验成功,预期结果={expect_value},实际结果={json_path_or_value}]')
        return self
