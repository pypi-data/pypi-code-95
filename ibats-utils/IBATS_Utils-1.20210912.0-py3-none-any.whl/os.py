#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/6/20 下午12:21
@File    : os.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import functools
import importlib
import logging
import os
import platform
import shutil
import subprocess
import warnings
from typing import ClassVar

from matplotlib.font_manager import FontManager

logger = logging.getLogger(__name__)


def create_instance(module_name, class_name, *args, **kwargs):
    """
    动态加载模块中的类，并实例化
    参见例子：src/fh_tools/language_test/base_test/dynamic_import_demo/dynamic_load.py
    :param module_name: 例如："src.fh_tools.language_test.base_test.dynamic_import_demo.a_class"
    :param class_name: 例如："AClass"
    :param args: "my_name" 类初始化参数
    :param kwargs:
    :return:
    """
    class_meta = load_class(module_name, class_name)
    obj = class_meta(*args, **kwargs)
    return obj


def load_class(module_name, class_name):
    """
    动态加载模块中的类
    参见例子：src/fh_tools/language_test/base_test/dynamic_import_demo/dynamic_load.py
    :param module_name: 例如："src.fh_tools.language_test.base_test.dynamic_import_demo.a_class"
    :param class_name: 例如："AClass"
    :return:
    """
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    return class_meta


def is_sub_class(sub_cls: ClassVar, cls: ClassVar) -> bool:
    """检查某一个类是否是另一个类的子类"""
    is_ok = False
    try:
        for _ in sub_cls.mro():
            if _ == cls:
                is_ok = True
                break
    except AttributeError:
        pass
    return is_ok


def open_file_with_system_app(file_path, asyn=True):
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Linux':
            import subprocess
            if asyn:
                subprocess.Popen(["xdg-open", file_path])
            else:
                subprocess.call(["xdg-open", file_path])
        else:
            import subprocess
            if asyn:
                subprocess.Popen(["open", file_path])
            else:
                subprocess.call(["open", file_path])
    except:
        import webbrowser
        webbrowser.open(f'file:///{file_path}')


def is_windows_os():
    return platform.system() == 'Windows'


def is_linux_os():
    return platform.system() == 'Linux'


def get_chinese_font_iter():
    fm = FontManager()
    mat_fonts = set(f.name for f in fm.ttflist)

    output = subprocess.check_output(
        'fc-list :lang=zh -f "%{family}\n"', shell=True)
    output = output.decode('utf-8')
    # print '*' * 10, '系统可用的中文字体', '*' * 10
    # print output
    zh_fonts = set(f.split(',', 1)[0] for f in output.split('\n'))
    available = mat_fonts & zh_fonts
    yield from available

    # print('*' * 10, '可用的字体', '*' * 10)
    # for num, f in enumerate(available, start=1):
    #     print(num, ')', f)


def get_project_root_path():
    import sys
    import os
    work_path = os.getcwd()
    # path_list = []
    # for path in sys.path:
    #     if work_path.find(path) == 0:
    #         print(path)
    #         path_list.append(path)
    path_list = list({_ for _ in sys.path if work_path.find(_) == 0})
    path_list.sort(key=len)
    project_root_path = path_list[0]
    return project_root_path, work_path


def get_module_path(stg_class: type):
    import os
    import sys
    module_path = stg_class.__module__
    if module_path == '__main__':
        project_root_path, work_path = get_project_root_path()
        # windows 环境下，sys.argv[0] 中路径分割为 "/" 而系统分隔符为 r"\" 导致匹配失败，因此需要进行一次转换
        module_file_path = os.path.splitext(sys.argv[0])[0].replace('/', os.path.sep)
        module_segment = [str(_) for _ in module_file_path[len(project_root_path):].split(os.path.sep) if _ != '']
        module_path = '.'.join(module_segment)
    return module_path


def copy_module_file_to(module_str_or_class, folder_path):
    """将模板备份到指定目录下，不改变文件名"""
    if isinstance(module_str_or_class, str):
        module = importlib.import_module(module_str_or_class)
    # elif hasattr(module_str_or_class, '__module__'):
    #     module = importlib.import_module(module_str_or_class.__module__)
    elif isinstance(module_str_or_class, type):
        module = importlib.import_module(module_str_or_class.__module__)
    elif hasattr(module_str_or_class, '__file__'):
        module = module_str_or_class
    else:
        raise ValueError(f'{module_str_or_class} <{type(module_str_or_class)}> 不是有效的对象')

    file_path = module.__file__
    # _, file_name = os.path.split(file_path)
    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)
    # new_file_path = os.path.join(folder_path, file_name)
    # shutil.copy(file_path, new_file_path)
    # return new_file_path
    return copy_file_to(file_path, folder_path)


def copy_file_to(file_path, folder_path):
    """将文件拷贝到指定目录"""
    _, file_name = os.path.split(file_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    new_file_path = os.path.join(folder_path, file_name)
    shutil.copy(file_path, new_file_path)
    return new_file_path


def _test_copy_module_file_to():
    from ibats_utils.pandas import DataFrame
    copy_module_file_to(DataFrame, r'd:\Downloads')


def copy_folder_to(source_folder_path, target_folder_path):
    """将文件拷贝到指定目录，文件名不变"""
    _, folder_name = os.path.split(source_folder_path)
    new_folder_path = os.path.join(target_folder_path, folder_name)
    if os.path.exists(new_folder_path):
        shutil.rmtree(new_folder_path)
    shutil.copytree(source_folder_path, new_folder_path)
    return new_folder_path


def _test_copy_folder_to():
    folder_path = r'/home/mg/github/IBATS_Common/ibats_common/example/drl/d3qn1'
    copy_folder_to(folder_path, r'/home/mg/Downloads')


def populate_obj(model_obj, data_dic: dict, attr_list=None, error_if_no_key=False):
    """
    通过 dict 设置模型对应的属性
    :param model_obj:
    :param data_dic:
    :param attr_list:
    :param error_if_no_key:
    :return:
    """
    for name in (attr_list if attr_list is not None else data_dic.keys()):
        if name in data_dic:
            setattr(model_obj, name, data_dic[name])
        elif error_if_no_key:
            raise KeyError("data_dic 缺少 '%s' key 无法设置到 %s" % (name, model_obj.__class__.__name__))
        else:
            warnings.warn("data_dic 缺少 '%s' key 无法设置到 %s" % (name, model_obj.__class__.__name__))


def log_param_when_exception(func):
    """
    当函数异常是 log 记录异常
    """

    @functools.wraps(func)
    def handler(*arg, **kwargs):
        try:
            return func(*arg, **kwargs)
        except Exception as exp:
            msg = '%s(%s, %s)' % (
                func.__name__,
                ', '.join([str(v) for v in arg]),
                ', '.join(
                    ['{key}={value}'.format(key=str(key), value=str(value))
                     for key, value in kwargs.items()]
                )
            )
            logger.exception(msg)
            raise exp from exp

    return handler


if __name__ == "__main__":
    pass

    # _test_get_module_file_path()
    # _test_copy_module_file_to()
    # _test_copy_folder_to()

    # 测试 log_param_when_exception 函数
    # @log_param_when_exception
    # def foo(a, b, c=None, *args, **kwargs):
    #     raise Exception('some error')
