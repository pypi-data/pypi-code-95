#coding:utf-8

import os
import sys
from imp import find_module,load_module,acquire_lock,release_lock

from general_utility import utils as us
from general_utility.appbase import ab
from plugin_utility.iplugin import iPlugin

CURRENT_DIR = __file__
for i in range(2):
    CURRENT_DIR = os.path.dirname(CURRENT_DIR)

APPUTILITY_DIR = CURRENT_DIR # Workspaces/apputility
sys.path.append(APPUTILITY_DIR)

PLUGIN_UTILITY_DIR = os.path.join(APPUTILITY_DIR, 'plugin_utility')
PROJECT_DIR = os.getcwd()

default_params = {
    'project_path': PROJECT_DIR,
    'plugin_utility_path': PLUGIN_UTILITY_DIR,
    'plugin_utility_example_path': os.path.join(PLUGIN_UTILITY_DIR, 'Example'),
    'plugin_config_filename': 'plugin_config.json',
    'media_path': os.path.join(PROJECT_DIR, 'background', 'media'),
    'document_path': os.path.join(PROJECT_DIR, 'background', 'media', 'documents'),
    'plugin_search_dir': os.getenv('PLUGINS_DIR', os.path.join(PROJECT_DIR, 'plugins')),
    'plugin_download_dir': os.getenv('PLUGIN_DOWNLOAD_DIR', os.path.join(PROJECT_DIR, 'downloads', 'plugins')),
}

TRY_LOCAL_PLUGINS = os.getenv("TRY_LOCAL_PLUGINS", 'True')
PIP_MIRRORS_URL = os.getenv("PIP_MIRRORS_URL", None)

#######################################################################################

def get_timer_from_json(values):
    result = []
    if (isinstance(values, dict)):
        name = us.check_attribute(values, 'name', '')
        timers = us.check_attribute(values, 'timer', None)
        if (timers is None):
            return None
        for timer in timers:
            result.append(timer)
    elif (isinstance(values, list) and len(values) > 0):
        for value in values:
            result.extend(get_timer_from_json(value))

    return result

def get_timer_from_url(url):
    job_config = us.get_json_from_url(url)
    if (job_config is None):
        return None

    timer_entry = us.check_attribute(job_config, 'values.entry.timers', 'timers')
    values = us.check_attribute(job_config, ('values.%s' % timer_entry), 'now')
    if (isinstance(values, str)):
        return values

    return get_timer_from_json(values)

def get_timer_from_urls(url):
    job_config = us.get_json_from_url(url)
    if (job_config is None):
        return None
    timers = []
    items = us.check_attribute(job_config, 'items', [])
    for item in items:
        detail_url = us.check_attribute(item, 'meta.detail_url', None)
        if (detail_url is not None):
            timer = get_timer_from_url(detail_url)
            if (timer is not None):
                timers.append(timer)
    pass

#######################################################################################

def plugin_handle(url):
    params = default_params
    plugin_Runner = Plugin_Runner(url, params)
    if (plugin_Runner is not None):
        print(plugin_Runner.get_plugins_dict())
        plugin_Runner.run()
    pass

# 插件运行管理类
class Plugin_Runner(object):

    def __init__(self, config, local_params = None):
        self.__plugins = []

        self.params = {}

        # 当前的插件搜索路径
        if (local_params is not None):
            self.local_params = local_params
            self.plugin_search_dir = us.check_attribute(self.local_params, 'plugin_search_dir') # 用于本地的插件加载

        type = us.get_type(config)

        if (type.lower() == 'dir'):
            self.load_from_dirs(config)
        elif (type.lower() == 'file'):
            self.load_from_file(config)
        elif (type.lower() == 'http') or (type.lower == 'https'):
            self.load_from_url(config)
        elif (type.lower() == 'dict') or (type.lower() == 'json'):
            self.load_from_json(config)
        pass

    def print_log(self, log, level = "info"):
        if self.ab is None:
            return
        
        self.ab.print_log(log = log, level = level)
                
    def test(self):
        plugin_utility_example_path = us.check_attribute(self.local_params, 'plugin_utility_example_path')
        config_file = os.path.join(plugin_utility_example_path, "plugins_config.json")
        if (us.path_exists(config_file)):
            # 按照配置文件来加载
            import json
            plugin_config_json = json.load(open(config_file, 'r', encoding='UTF-8'))
            testdata = plugin_config_json['testdata']
            self.run(testdata)

        pass

    def run(self, params=None): 
        if (params is None):
            params = self.params
        else:
            params = us.dict_merged(self.params, params)

        return self.project_infos_handle(params)

    def on_scripts(self, scripts, moment='START'):
        for script in scripts:
            if (us.check_attribute(script, 'moment', 'START').upper() == moment.upper()):
                value = us.check_attribute(script, 'script', None)

                import tempfile
                script_filename = tempfile.mktemp(suffix='.sh')
                with open(script_filename, "wb") as f:
                    f.write(value.replace("\r", "").encode())
                f.close

                ab.print_log('执行脚本.(%s : %s)' % (moment, script_filename), level="INFO")
                os.system('chmod +x %s' % script_filename)
                os.system(script_filename)
            pass

    def project_infos_handle(self, params): # 项目数据流入口
        if (params is None):
            ab.print_log("project_infos_handle params is None, so exit!", level="ERROR")
            return

        ab.print_log("project_infos_handle start...", level="CRITICAL")

        for plugin in self.__plugins:
            ab.print_log("start execute plugin %s (%s)" % (plugin.get().get_name(), plugin.get().get_showname()), level="CRITICAL")

            params['last_error'] = ''
            params['last_result'] = -100
            if (plugin.get().check_input(params)):
                params = plugin.get().handle(params)
                if (params is None):
                    break

                if (params['last_result'] < 0):
                    ab.print_log("plugin %s result error, error id: %d error message: '%s'" %
                                (plugin, params['last_result'], params['last_error']), level="ERROR")
                    break

                if (params.__contains__('last_result_cmd') == False): # 判断是否有后续的处理命令
                    continue

                last_result_cmd = params['last_result_cmd']
                cmd = last_result_cmd['cmd']
                if (cmd == "add_project_info"): # 特殊处理，动态添加新的插件
                    # project_config_file = last_result_cmd['project_config_file']
                    # project_obj = pi.ProjectInfo(project_config_file)
                    # self.add_project_info(project_config_file, project_obj)
                    break
                
            else:
                ab.print_log("plugin check input error id: %d error message: '%s'" % # 连接测试都不通过，直接中断
                                (params['last_result'], params['last_error']), level="ERROR")
                break

        scripts = us.check_attribute(params, "scripts", None)
        if (scripts is not None):
            self.on_scripts(scripts, 'END')

        ab.print_log("project_infos_handle end...", level="CRITICAL")

        ab.remove_loger()
            
        return params

    #######################################################################################

    def __iter__(self):
        return iter(self.plugins)

    def addPlugin(self, plugin):
        ab.print_log(("PluginManager add plugin name: %s" % plugin.obj.name), level="INFO")
        self.__plugins.append(plugin)

    def addPlugins(self, plugins):
        if (plugins is None):
            return
        for plug in plugins:
            self.addPlugin(plug)

    def delPlugin(self, plugin):
        if (self.__plugins is None) or (plugin is None):
            return

        if plugin in self.__plugins:
            self.__plugins.remove(plugin)

    def delPlugins(self, plugins):
        if (plugins is None):
            return
        for plug in plugins:
            self.delPlugin(plug)

    def getPlugin(self, name = None):
        if (self.__plugins is None):
            return

        for plugin in self.__plugins:
            if ((name is not None) and (plugin.name.upper() == name.upper())):
                return plugin
        return None

    def get_plugins(self, name = None):
        plugins = []
        for plugin in self.__plugins:
            if ((name is None) or (plugin.name.upper() == name.upper())):
                plugins.append(plugin)
        return plugins

    def get_plugins_dict(self, name = None):
        plugins = {}
        for plugin in self.__plugins:
            if ((name is None) or (plugin.name.upper() == name.upper())):
                plugins[plugin.get().get_name()] = plugin.get().get_showname()
        return plugins

    #######################################################################################

    def load_from_file(self, plugin_config):
        ab.print_log("load from file %s" % plugin_config, level="INFO")

        if (us.path_exists(plugin_config) == False):
            ab.print_log('plugin config file %s is not exists.' % plugin_config, level="ERROR")
            return
        # 按照配置文件来加载
        import json
        plugin_config_jaon = json.load(open(plugin_config, 'r', encoding='UTF-8'))
        self.load_from_json(plugin_config_jaon)

    def load_from_dirs(self, plugin_dir):
        if (us.path_exists(plugin_dir) == False):
            ab.print_log("plugin file is not exists (%s)" % plugin_dir, level="ERROR")
        
        config_file = os.path.join(plugin_dir, "plugins_config.json")
        if (us.path_exists(config_file)):
            self.load_from_file(config_file)
        else:
            # 遍历子目录，目前这个方案是有排序问题的，只作为测试使用
            for root, dirs, _ in os.walk(plugin_dir):
                if (root == plugin_dir): # 此处只遍历一级子目录
                    for dir in dirs:
                        plugin_obj = Plugin_Object(os.path.join(root, dir))
                        if (plugin_obj is not None):
                            self.addPlugin(plugin_obj)

    def load_from_url(self, url):
        parsed = us.get_parse_from_url(url)
        if (parsed.scheme.lower() != 'http'): # 暂时只支持http协议
            return None

        self.host = parsed.scheme + '://' + parsed.netloc

        plugin_config_jaon = us.get_json_from_url(url)
        if (plugin_config_jaon is None):
            return None

        self.load_from_json(plugin_config_jaon)

    #######################################################################################

    def load_2_1(self, values):
        if (values is None):
            return None

    def get_params_by_name(self, name, default = None):
        return us.check_attribute(self.params, name, default)

    # 从配置文件中加载插件框架，注意此处分协议版本
    def load_from_json(self, json_obj):

        #####################################################################
        
        id = us.check_attribute(json_obj, 'id', -1)
        meta = us.check_attribute(json_obj, 'meta', None)

        log_name =  "${PID}_${TIME}"
        if (meta is not None):
            name = us.check_attribute(meta, "name")
            log_name = ("%s_%s" % (name, log_name))

        ab.set_loger(log_name = log_name, level = "info", logconsole = False)

        #####################################################################

        values = us.check_attribute(json_obj, 'values', None)
        self.params['protocol_version'] = us.check_attribute(values, 'protocol_version', '2.0')
        self.params['timers'] = us.check_attribute(values, 'timers', None)
        self.params['entry'] = us.check_attribute(values, 'entry', None)

        #####################################################################

        key_name = us.check_attribute(self.params['entry'], 'base', 'base')
        base = us.check_attribute(values, key_name, {})
        self.params[key_name] = base
        self.params[key_name] = {"id": id, "meta": meta, 'local_setting': default_params}

        #####################################################################

        key_name = us.check_attribute(self.params['entry'], 'scripts', 'scripts')
        scripts = us.check_attribute(values, key_name, None)
        self.params[key_name] = scripts
        self.params['next'] = key_name

        # 脚本执行
        if (scripts is not None):
            self.on_scripts(scripts, 'START')

        #####################################################################

        plugins = us.check_attribute(values, us.check_attribute(self.params['entry'], 'engine', 'plugins'), None)
        plugins = plugins_loader(plugins, self.params['protocol_version'])
        self.addPlugins(plugins.get_values())

        #####################################################################

        key_name = us.check_attribute(self.params['entry'], 'settings', 'settings')
        setting = us.check_attribute(values, key_name, None)
        setting = setting_loader(setting, self.params['protocol_version'])
        self.params[key_name] = setting.get_values()

        envs = us.check_attribute(self.params[key_name], 'env', None)
        if (envs is not None):
            for env in envs:
                for k, v in env.items():
                    os.environ.setdefault(k, v)
                pass
            pass

        #####################################################################

        key_name = us.check_attribute(self.params['entry'], 'databars', 'databars')
        databar = us.check_attribute(values, key_name, None)
        self.params[key_name] = databar
        self.params['next'] = key_name

        #####################################################################

        key_name = us.check_attribute(self.params['entry'], 'renders', 'renders')
        render = us.check_attribute(values, key_name, None)
        render = base_loader(render, self.params['protocol_version'])
        self.params[key_name] = render.get_values()

        self.params['output'] = key_name

        #####################################################################

        key_name = us.check_attribute(self.params['entry'], 'processors', 'processors')
        processors = us.check_attribute(values, key_name, [])
        self.params[key_name] = processors

        ab.print_log(self.params, level="INFO")

        pass

#######################################################################################

class base_loader():
    def __init__(self, values, protocol_version = '2.1'):
        self.__protocol_version = protocol_version
        self.__values = self.load(values)

    def get_values(self):
        return self.__values
    
    def load_2_1(self, values):
        if (values is None):
            return None
        if (isinstance(values, list)):
            for item in values:
                return self.load_2_1(item)  # 此处值处理第一个源数据方案， 多方案的以后再说
            pass
        elif (isinstance(values, dict)):
            return values # 第一个就返回来

    def load_2_2(self, values):
        if (values is None):
            return None
        if (isinstance(values, list)):
            if (len(values) == 1):
                return self.load(values[0])  # 此处值处理第一个源数据方案， 多方案的以后再说
            else:
                result = []
                for item in values:
                    result.append(self.load_2_1(item))
                return result
        elif (isinstance(values, dict)):
            return values

    def load_2_3_1(self, values):
        return self.load_2_2(values)

    def load_2_3_2_x(self, values):
        return self.load_2_2(values)

    def load(self, values):
        fun_name, fun_name_x = us.get_funname_from_protocol_version(self.__protocol_version, 'load')

        if us.obj_hasattr(self, fun_name):
            fun = us.obj_getattr(self, fun_name)
            return fun(values)
        elif us.obj_hasattr(self, fun_name_x):
            fun = us.obj_getattr(self, fun_name_x)
            return fun(values)
        
        return None

class setting_loader(base_loader):
    def load_2_1(self, values):
        if (values is None):
            return None
        if (isinstance(values, list)):
            result = {}
            for item in values:
                result = us.dict_merged(result, self.load_2_1(item))  # 此处值处理第一个插件方案， 多方案的以后再说
            return result
        elif (isinstance(values, dict)):
            return values # 第一个就返回来

class plugins_loader(base_loader):
    # 递归方式依次加载插件到插件列表
    def load_2_1(self, values):
        if (values is None):
            return None
        if (isinstance(values, list)):
            for item in values:
                name = us.check_attribute(item, 'name', None)
                description = us.check_attribute(item, 'description', None)
                params = us.check_attribute(item, 'params', None)
                plugins = us.check_attribute(item, 'plugins', None)
                
                ab.print_log('start load plugins of name: %s %s' % (name, description), level = "CRITICAL")   
                return self.load_2_1(plugins)  # 此处值处理第一个插件方案， 多方案的以后再说
            pass
        elif (isinstance(values, dict)):
            return self.load_plugins(values) # 第一个就返回来
    
    def load_2_2(self, values):
        return self.load_2_1(values)

    def load_2_3_1(self, values):
        return self.load_2_1(values)

    def load_2_3_2(self, values):
        return self.load_2_1(values)

    def load_plugins(self, plugins, 
                            plugin_search_dir = default_params['plugin_search_dir'], 
                            plugin_download_dir = default_params['plugin_download_dir']):
        if (plugins is None):
            return

        plugins_list = []
        ab.print_log("load plugins obj from plugins list %s." % plugins.items(), level = "CRITICAL")
        for (name, obj) in plugins.items():
            if (TRY_LOCAL_PLUGINS.upper() == "TRUE") and (us.path_exists(os.path.join(plugin_search_dir, name))):
                ab.print_log("plugin search dir: %s" % (plugin_search_dir), level = "CRITICAL")
                url =  os.path.join(plugin_search_dir, name)

                ab.print_log("plugins %s is exists on local, and load from local dir : %s" % (name, url), level = "CRITICAL")
            else:
                # 网络下载方式
                url =  obj['url']
                url_type = us.get_type(url)

                if (url_type == 'file') and (url[-3:].lower() == 'zip'):

                    if (self.host is not None):
                        host = self.host
                    else:
                        host = us.check_attribute(self.params, 'host', us.check_attribute(self.local_params, 'host'))

                    if (host is None):
                        ab.print_log('host is None.', level = "ERROR")
                    elif (url[0] == '/') and (url[-3:].lower() == 'zip'):
                        url = host + url

                    ab.print_log("plugins %s is not exists on local, and load from web addr : %s" % (name, url), level = "CRITICAL")
                else:
                    pass
                    
            plugin = Plugin_Object(url, plugin_download_dir)
            if (plugin != None):
                plugins_list.append(plugin)

        return plugins_list

#######################################################################################

class Plugin_Object(object):
    def __init__(self, plugin_url, plugin_download_dir = None):
        self.obj = None
        self.plugin_dir = plugin_download_dir
        if (os.path.isdir(plugin_url)):
            self.obj = self.load_from_dir(plugin_url)
        elif (os.path.isfile(plugin_url)):
            self.obj = self.load_from_file(plugin_url)
        else:
            scheme = us.get_scheme_from_url(plugin_url)
            if (scheme != None) and (scheme.lower() in 'https'):
                self.obj = self.load_from_url(plugin_url, self.plugin_dir)

    def __iter__(self):
        return iter(self.obj)

    def get(self):
        return self.obj

    def load_from_dir(self, plugin_url):
        ab.print_log('load plugin from dir: %s' % plugin_url, level="INFO")
        if (us.path_exists(plugin_url) == False):
            ab.print_log("plugin file is not exists (%s)" % plugin_url, level="ERROR")

        config_file = os.path.join(plugin_url, default_params['plugin_config_filename'])
        if (us.path_exists(config_file) == False):
            ab.print_log("plugin config file is not exists (%s)" % config_file, level="ERROR")
            return None

        ab.print_log('load plugin obj from %s' % config_file, level="INFO")
        import json
        self.config = json.load(open(config_file, 'r', encoding='UTF-8'))
        start_file = self.config['base']['start']
        start_name = start_file[:-3]
        
        us.initialize(plugin_url, '')

        try:
            acquire_lock()
            fh, filename, desc = find_module(start_name, [plugin_url])
            old = sys.modules.get(start_name)
            if old is not None:
                # make sure we get a fresh copy of anything we are trying
                # to load from a new path
                del sys.modules[start_name]
            mod = load_module(start_name, fh, filename, desc)
        finally:
            if fh:
                fh.close()
            release_lock()
        
        if hasattr(mod, "__all__"):
            attrs = [getattr(mod, x) for x in mod.__all__]
            for obj in attrs:
                if (issubclass(obj, iPlugin) == False):
                    ab.print_log('plug is not subclass', level="ERROR")
                    continue
                plugin = obj()
                
                ab.print_log('load plugin success, plugin name is %s' % plugin.get_name(),  level="CRITICAL")  
                return plugin             
    
    def load_plugin(self, file_path):
        from imp import acquire_lock, release_lock, load_module, PY_SOURCE
        import sys
        sys.path.append(os.path.join(os.getcwd(), 'background', "plugin_utility"))
        from iplugin import iPlugin

        plugin = None
        try:        
            with open(file_path, 'r', encoding='UTF-8') as openfile:
                acquire_lock()
                mod = load_module("mod", openfile, file_path, ('.py', 'r', PY_SOURCE))
                if hasattr(mod, "__all__"):
                    attrs = [getattr(mod, x) for x in mod.__all__]
                    for obj in attrs:
                        if not issubclass(obj, iPlugin):
                            continue
                        plugin = obj()
                        ab.print_log("find plug name: %s" % plugin.name,  level="INFO")
        except Exception as e:
            plugin = None
            ab.print_log("load plug error: %s" % e,  level="ERROR")
        finally:
            pass
        release_lock()  
        if openfile:
            openfile.close()
        ab.print_log('load plugin success, plugin name is %s' % plugin.get_name(),  level="INFO")  
        return plugin

    def load_from_file(self, plugin_url):
        ab.print_log('load plugin from file: %s' % plugin_url,  level="INFO")
        if (us.path_exists(plugin_url) == False):
            ab.print_log("plugin file is not exists (%s)" % plugin_url,  level="ERROR")
            return None

        _, _, name, suffix = us.get_path_name_suffix_from_filepath(plugin_url)
        if (suffix != '') and (suffix.lower() == '.zip'): # 暂时只处理没有后缀或者后缀为zip的文件
            if (self.plugin_dir is None):
                import tempfile
                plugin_dir = tempfile.mkdtemp()
            else:
                plugin_dir = self.plugin_dir
            
            plugin_dir = os.path.join(plugin_dir, name)
            if (not us.path_exists(plugin_dir)):
                us.check_path_exists(plugin_dir)

                filecount = us.extract_file(plugin_url, plugin_dir)
                ab.print_log("extract file count: (%d)" % filecount,  level="INFO")
            return self.load_from_dir(plugin_dir)
        elif (suffix != '') and (suffix.lower() == '.py'):
            return self.load_plugin(plugin_url)

        ab.print_log("plugin file is not zip suffix (%s)" % plugin_url,  level="INFO")
        return None

        # 临时文件咋删除？
        pass

    def load_from_url(self, plugin_url, download_dir):
        ab.print_log('load plugin from url: %s' % plugin_url,  level="INFO")
        pulgin_filepath = us.get_filepath_from_url(plugin_url, download_dir)
        if (pulgin_filepath  == None):
            return

        return self.load_from_file(pulgin_filepath)

    ###################################################################################

    def test(self):
        if (us.obj_hasattr(self, 'obj') == False):
            return

        if (self.obj is None):
            ab.print_log("plugin object is none, don't initialize?",  level="INFO")

        params = None
        if hasattr(self.obj, "testdata"):
            params = self.obj.testdata
        
        if (self.obj.check_input(params)):
            params = self.obj.handle(params)

#######################################################################################
