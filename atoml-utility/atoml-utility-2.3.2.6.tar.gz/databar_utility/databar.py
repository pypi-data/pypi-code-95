
import os
import sys
from general_utility import utils as us
from general_utility.appbase import ab

def ver_strtoint(protocol_version):
    ver_count = 0
    try:
        ver_count = int(protocol_version.replace(".", ""))
    except Exception as e:
        pass
    return ver_count

class Databar():
    def __init__(self, **kwargs):
        self.protocol_version = '1.0'
        if (us.att_isin(kwargs, 'protocol_version')):
            self.protocol_version = kwargs.pop('protocol_version')

        ab.print_log('data protocol version: %s' % self.protocol_version)

        self.databar_pro = None
        try:
            search_dir = os.path.dirname(__file__)
            sys.path.append(search_dir)

            # 只取版本前两位
            version = us.params_split(self.protocol_version, '.')
            imp_class = 'Databar_Pro'
            imp_module = 'databar'
            j = 0
            for v in version:
                if (j < 1):
                    imp_module = ('%s_%s' % (imp_module, v))

                if j >= 3: # 版本最长4位，最后一位为通配
                    imp_class = ('%s_%s' % (imp_class, 'x'))
                else:
                    imp_class = ('%s_%s' % (imp_class, v))
                    
                j = j + 1

            ab.print_log('load databar parser: %s' % imp_module)

            import importlib
            databar_module = importlib.import_module(imp_module)
            ab.print_log('load databar parser successful')
            
            databar_module_cls = getattr(databar_module, imp_class)

            input = us.check_attribute(kwargs, 'input', None)
            params = us.check_attribute(kwargs, 'params', None)

            self.databar_pro = databar_module_cls(input = input, params = params)
        except Exception as e:
            ab.print_log("load databar_pro error: %s" % e)
            self.databar_pro = None

        pass

    def ver_fun(self, fun_name, values):
        if (self.databar_pro is None):
            return None
        if us.obj_hasattr(self.databar_pro, fun_name):
            fun = us.obj_getattr(self.databar_pro, fun_name)
            return fun(values)
        return None

    def add(self, values):
        return self.ver_fun(fun_name = sys._getframe().f_code.co_name, values = values)

    def load(self, values):
        return self.ver_fun(fun_name = sys._getframe().f_code.co_name, values = values)

    def serializes(self, values = None):
        result = self.ver_fun(fun_name = sys._getframe().f_code.co_name, values = values)

        result['writer'] = ("%s.%s" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        result['protocol_version'] = self.protocol_version
        
        return result

    def get_type(self):
        if (self.databar_pro is None):
            return None
        return self.databar_pro.get_type()

    def get_values(self, **kwargs):
        if (self.databar_pro is None):
            return None
        return self.databar_pro.get_values(**kwargs)

    ####################################################################
