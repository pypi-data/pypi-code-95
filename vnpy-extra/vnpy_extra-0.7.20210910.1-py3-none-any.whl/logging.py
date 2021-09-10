"""
@author  : MG
@Time    : 2020/11/24 14:35
@File    : logging.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
# import os
# import traceback
# import io
# import logging as logging_base
#
#
# class Logger(logging_base.Logger):
#
#     def __init__(self, name, level=logging_base.NOTSET, parent_stack_num=0):
#         super().__init__(name, level)
#         self.parent_stack_num = parent_stack_num
#
#     def findCaller(self, stack_info=False):
#         """
#         Find the stack frame of the caller so that we can note the source
#         file name, line number and function name.
#         """
#         f = logging_base.currentframe()
#         # On some versions of IronPython, currentframe() returns None if
#         # IronPython isn't run with -X:Frames.
#         if f is not None:
#             f = f.f_back
#         rv = "(unknown file)", 0, "(unknown function)", None
#         parent_stack_num = 0
#         while hasattr(f, "f_code"):
#             co = f.f_code
#             filename = os.path.normcase(co.co_filename)
#             if filename == logging_base._srcfile:
#                 f = f.f_back
#                 continue
#             if parent_stack_num < self.parent_stack_num:
#                 parent_stack_num += 1
#                 continue
#             sinfo = None
#             if stack_info:
#                 sio = io.StringIO()
#                 sio.write('Stack (most recent call last):\n')
#                 traceback.print_stack(f, file=sio)
#                 sinfo = sio.getvalue()
#                 if sinfo[-1] == '\n':
#                     sinfo = sinfo[:-1]
#                 sio.close()
#             rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
#             break
#         return rv


if __name__ == "__main__":
    pass
