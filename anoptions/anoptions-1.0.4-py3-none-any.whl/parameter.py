class Parameter(object):


  def __init__(self, name, func, var_name, short_name=None, default=None, always_include=False):
    super().__init__()

    self.name           = name
    self.func           = func
    self.var_name       = var_name
    self.short_name     = short_name[0] if short_name is not None and len(short_name) > 0 else name[0]
    self.default        = default
    self.always_include = always_include


  @staticmethod
  def dummy(arg):
    return arg


  @staticmethod
  def flag(*argv):
    return True


  @classmethod
  def bool(cls, *argv):
    # if no params are given, act like flag()
    if len(argv) < 1:
      return cls.flag(*argv)

    # if this is a flag from getopt, the value is str and len=0
    if isinstance(argv[0], str) and len(argv[0]) == 0:
      return True

    # else we evaluate the variable contents
    return cls._eval_bool(argv[0])


  @classmethod
  def is_flag(cls, f):
    return (f == cls.flag or f == cls.bool)


  @staticmethod
  def _eval_bool(value):
    if isinstance(value, bool):
      return value
    elif isinstance(value, int):
      return (value == 1)
    elif isinstance(value, str):
      return (value.upper() in ("1", "TRUE"))
    else:
      return bool(value)
