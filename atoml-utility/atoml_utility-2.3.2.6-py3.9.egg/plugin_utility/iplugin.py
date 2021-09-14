#coding:utf-8
import os
import json

import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# from general_utility.bootutils import us, ab, redis_channel, get_redis_db, save_to_redis, load_from_redis

from general_utility import utils as us
from general_utility.appbase import ab

import pickle

USE_REDIS = False

if (USE_REDIS):
    import redis
    REDIS_CHANNEL = 'REDIS_TEST_DB'
        
class iPlugin(object):
    """ 定义一个接口，其他 插件必须实现这个接口，name 属性必须赋值 """
    plugin_config = './plugin_config.json'

    def __init__(self, run_dir = None):

        self.cur_path = run_dir

        plugin_config = os.path.join(self.cur_path, self.plugin_config)
        # 初始化
        ab.print_log('init plugin at:%s' % run_dir, level="CRITICAL")
        app_name = os.environ.get('APP_NAME', '')
        us.initialize(self.cur_path, app_name)

        if (plugin_config is None):
            plugin_config = os.path.join(self.cur_path, self.plugin_config)

        if (us.path_exists(plugin_config) == False):
            return

        input_item_optional = [
                ]

        input_item_require = [
                ]

        output_item_require = [
                ]
        
        config = json.load(open(plugin_config, 'r', encoding='utf-8'))

        # 这句基本没用，只是初始化，版本号以服务器为准，未来可以作为本地和服务器的协议校对
        self.protocol_version = us.check_attribute(config, 'base.protocol_version', '2.1') 

        self.name = us.check_attribute(config, 'base.name', 'noname')
        self.version = us.check_attribute(config, 'base.version', '0.0.1')
        self.showname = us.check_attribute(config, 'base.showname', 'noname')
        self.description = us.check_attribute(config, 'base.description', '')
        self.role = us.check_attribute(config, 'base.role', 'transfer')
        self.params = us.check_attribute(config, 'base.params', None)

        if us.check_attribute(config, 'testdata'):
            if us.obj_hasattr(self, 'testdata'):
                self.testdata = us.dict_merged(self.testdata, us.check_attribute(config, 'testdata'))
            else:
                self.testdata = us.check_attribute(config, 'testdata')
        pass                
        
    def get_name(self):
        return self.name

    def get_version(self):
        return self.version

    def get_showname(self):
        return self.showname

    def get_role(self):
        return self.role

    def get_params(self):
        return self.params

    def get_pin_count(self):
        return self.params['pin_count']

    def get_pin_param(self, index):
        key = list(self.params['pin'])[index]
        value = self.params['pin'][key]
        return {key: value}

    def get_testdata(self):
        return self.testdata

    def connect(self, params):
        return True

    def get_input(self, params):
        next = us.check_attribute(params, 'next', 'input')
        return us.check_attribute(params, next)

    def check_input(self, params):
        self.protocol_version = us.check_attribute(params, 'protocol_version', '2.1') # 检查输入的时候把协议版本号也取值放着

        self.input = self.get_input(params)
        if (self.input is None):
            return False
        
        # 提取所需要的数据
        all_is_ok = True
        if (len(self.input_item_require) > 0):
            all_is_ok, self.input = self.load_default_params(self.input, self.input_item_require)

        if (all_is_ok == False):
            return False

        if (len(self.input_item_optional) > 0):
            input_optional, _ = self.load_default_params(self.input, self.input_item_optional)
            if (self.input is not None) and (input_optional is not None) and (len(input_optional) > 0):
                self.input = us.dict_merged(self.input, input_optional)

        return True

    def check_output(self, params):
        self.output = self.get_output(params)
        if (self.output is None):
            return False

        # 提取所需要的数据
        all_is_ok = True
        if (len(self.output_item_require) > 0):
            all_is_ok, self.output = self.load_default_params(self.output, self.output_item_require)

        if (all_is_ok == False):
            return False

        if (len(self.output_item_optional) > 0):
            output_optional, _ = self.load_default_params(self.output, self.output_item_optional)
            if (self.output is not None) and (output_optional is not None) and (len(output_optional) > 0):
                self.output = us.dict_merged(self.output, output_optional)

        return True

    def load_params_as_name(self, params, items, default = None):
        if (params is None):
            return default

        items = us.params_split(items, '.')
        param = params
        for item in items:
            if ":" in item:
                key, value = us.key_value_split(item)
                for first in param: # 如果是列表类型，取第一个符合条件的返回
                    if (us.check_attribute(first, key, "") == value):
                        param = first
                        break
                pass
            else:
                if isinstance(param, list) and (len(param) > 0):
                    for first in param: # 如果是列表类型，取第一个符合条件的返回
                        param = us.check_attribute(first, item, default)
                        break
                    pass
                if isinstance(param, dict):
                    param = us.check_attribute(param, item, default)

        return param

    def load_default_params(self, params, item_list):
        if isinstance(item_list, str) and (item_list == '*'):
            return True, params # 所有参数都要，全部返回

        default_params = {}
        all_is_ok = True

        if isinstance(item_list, str):
            default_params = self.load_params_as_name(params, item_list)
        else:
            for item in item_list:
                param = self.load_params_as_name(params, item)
                if (param is not None):
                    default_params[item] = param
                else:
                    all_is_ok = False
                    ab.print_log('load default params missing at %s' % item)

        return all_is_ok, default_params

    def load_start_end_date(self, params, \
                            format = "%Y%m%d", default_start_date = '20000101', default_end_date = 'yesterday'):
        start_date = us.check_attribute(params, 'start_date', default_start_date)
        end_date = us.check_attribute(params, 'end_date', default_end_date)
        if (start_date is not None):
            start_date = us.check_date(start_date, format)
        if (end_date is not None):
            end_date = us.check_date(end_date, format)

        return start_date, end_date

    def get_entry_keyname(self, params, name):
        entry = us.check_attribute(params, 'entry', None)
        if (entry is None):
            return name
        return us.check_attribute(entry, name, name)

    def get_item_by_name(self, params, name, default = ''):
        return us.check_attribute(params, self.get_entry_keyname(params, name), default)

    def get_settings(self, params):
        entry = us.check_attribute(params, 'entry', None)
        setting = us.check_attribute(entry, 'settings', 'settings')
        return us.check_attribute(params, setting, None)

    def get_current_params(self):
        return {'now': us.now("%Y-%m-%d-%H-%M")}

    def get_params_from_setting(self, params, name, default = None):
        setting = self.get_settings(params)
        return us.check_attribute(setting, name, default)

    def get_renders(self, params):
        entry = us.check_attribute(params, 'entry', None)
        key = us.check_attribute(entry, 'renders', 'renders')
        return key, us.check_attribute(params, key, None)

    def get_output(self, params):
        _, renders = self.get_renders(params)
        return us.check_attribute(renders, 'output', None)

    def get_protocol_version(self):
        return self.protocol_version

    def params_replace(self, item_params, params):
        entry = us.check_attribute(params, 'entry', None)
        base = us.check_attribute(params, us.check_attribute(entry, 'base', 'base'), {})
        base['current'] = self.get_current_params()

        item_params = us.make_param(item_params, base) # 从参数字典里替换
        for (K, V) in base.items():
            item_params = us.make_param(item_params, V)

        item_params = us.make_param(item_params, None) # 最后系统环境变量先替换

        return item_params

    def handle(self, params):
        ab.print_log(("%s plugin start handle" % self.name), level = "CRITICAL")
        return params

    def handle_done(self, params):
        ab.print_log(("%s plugin end handle" % self.name), level = "CRITICAL")
        return params

    def save_to_file(self, filename, params):
        with open(filename, 'wb') as f:
            pickle.dump(params, f)
        f.close

    def load_from_file(self, filename):
        params = None
        with open(filename, "rb") as f:
            params = pickle.load(f)
        f.close  

        return params

    #########################################################

    def save(self, taget, key, data):
        if data is None:
            return False
        
        if taget.startswith('REDIS'):
            save_to_redis(db_name=taget, key=key, data=data, ex=5000)
        elif taget.startswith('MYSQL'):
            pass
        elif taget.startswith('.') or taget.startswith('/'):
            self.save_to_file(taget, data)
            
    def load(self, source, key):
        params = None

        if source.startswith('REDIS'):
            params = load_from_redis(db_name='REDIS_TEST_DB', key=key)
        elif source.startswith('MYSQL'):
            pass
        elif source.startswith('.') or source.startswith('/'):
            params = self.load_from_file(source)

        return params

    def test(self):
        if (self.get_testdata()):
            taget = os.path.join(os.getcwd(), self.get_name() + '.test.json') # 默认保存本地文件
            if (USE_REDIS):
                taget = REDIS_CHANNEL
            source = taget

            params = self.testdata

            key = ('cts_test:(%s)' % (us.now('%Y-%m-%d')))
            prev_params = self.load(source, key)
            prev_params = us.dict_merged(prev_params, self.testdata)

            if (self.check_input(prev_params)):
                params = self.handle(prev_params)
                if (params is not None):
                    # key = ('Test:%s(%s)' % (self.name, us.now('%Y-%m-%d %H-%M')))
                    self.save(taget, key, params)
                    return 1
                else:
                    return -1
        return 0