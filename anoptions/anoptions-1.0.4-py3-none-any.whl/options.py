import getopt

from .parameter import Parameter
from .env import Env


class Options(object):
  def __init__(self, parameters, argvs, env_prefix=None, always_include_all=False):
    super().__init__()

    """
    Example:
      parameters = [
        Parameter("host",   str,  "mqtt_host",  default="127.0.0.1"),
        Parameter("port",   int,  "mqtt_port"),
        Parameter("topic",  str,  "mqtt_topic"),
        Parameter("dir",    str,  "filename_dir"),
        Parameter("silent", Parameter.flag, "silent")
      ]
    """

    self.parameters = parameters
    self.argvs      = argvs
    self.env_prefix = env_prefix

    if always_include_all is True:
      for x in self.parameters:
        x.always_include = True

    # replace the regular bool function with one in Parameter
    # to ensure that we get values evaluated correctly
    for x in self.parameters:
      if x.func is bool:
        x.func = Parameter.bool


  def create_env_var_map(self):
    result = {}
    for x in self.parameters:
      result[ self.env_prefix.upper() + "_" + x.name.upper()] = x.var_name

    return result


  @staticmethod
  def _check_duplicates(parameters):
    _short = []
    _long  = []

    for x in parameters:
      if x.name in _long: 
        raise DuplicateOptionException('--' + x.name)
      elif x.short_name in _short:
        raise DuplicateOptionException('-' + x.short_name)

      _long.append(x.name)
      _short.append(x.short_name)


  @classmethod
  def _generate(cls, parameters):
    cls._check_duplicates(parameters)
    result_short = [ x.short_name + ('' if Parameter.is_flag(x.func) else ':') for x in parameters ]
    result_long = [ x.name + ('' if Parameter.is_flag(x.func) else '=') for x in parameters ]
    result_lookup_opt = {}
    result_lookup_var = {}
    for x in parameters:
      result_lookup_opt[ "--" + x.name       ] = x
      result_lookup_opt[ "-"  + x.short_name ] = x
      result_lookup_var[ x.var_name          ] = x

    return "".join(result_short), result_long, result_lookup_opt, result_lookup_var


  @staticmethod
  def bool(value):
    if isinstance(value, bool):
      return value
    elif isinstance(value, int):
      return (value == 1)
    elif isinstance(value, str):
      return (value.upper() in ("1", "TRUE"))
    else:
      return bool(value)


  def eval(self):
    st, ls, lookup_opt, lookup_var = self._generate(self.parameters)
    opts, args = getopt.getopt(self.argvs, st, ls)
    # ^ will raise getopt.GetoptError if fails

    result = {}

    if self.env_prefix is not None:
      envmap = self.create_env_var_map()
      r = Env.get_kv_from_env(envmap)

      for k, v in r.items():
        result[k] = lookup_var[k].func(v)
      
    for opt, arg in opts:
      if opt in lookup_opt.keys():
        p = lookup_opt[opt]
        result[p.var_name] = p.func(arg)
        # ^ will raise an exception if input not acceptable

    # ensure that all flags are represented, i.e. if not 
    # found to be true, they must be  set as false
    for x in self.parameters:
      if x.func is Parameter.flag and x.var_name not in result:
        result[x.var_name] = False

    # set defaults wherever they exist and no values have been inputted
    for x in self.parameters:
      if (
        (x.default is not None or x.always_include is True) and
        x.var_name not in result
      ):
        result[x.var_name] = x.default

    return result


class DuplicateOptionException(Exception):
  pass
