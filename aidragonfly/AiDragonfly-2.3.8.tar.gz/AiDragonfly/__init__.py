# -*- coding: utf-8 -*-
# @Time    : 2021/8/9 9:04
# @Author  : liumingming
# @FileName: __init__.py.py
# @Company ：http://www.iqi-inc.com/

from AiDragonfly.aiqi_main import start, Bluetooth_Data_Send,User_Receive_Callback_Register

import AiDragonfly.aiqi_model.mesh.meshModule as Mesh


def __check_platform():
    import platform
    import sys
    __run_system = platform.system()

    if __run_system == "Darwin":
        pass
    elif __run_system == "Windows":
        platform.release()
        if platform.release() >= '10':
            win_ver = platform.version()
            win_verlist = win_ver.split('.')
            __ver_h = int(win_verlist[0])
            __ver_M = int(win_verlist[1])
            __ver_L = int(win_verlist[2])

            if __ver_h >= 10 and __ver_M >= 0 and __ver_L >= 16299:
                pass
            else:
                print(__run_system + " " + platform.release() + ' ' + platform.version())
                print('System version is too low, please update windows 10.0.16299 above')
                sys.exit(0)

        else:
            print(__run_system + " " + platform.release() + ' ' + platform.version())
            print('The system does not support')
            sys.exit(0)
        pass
    else:
        print(__run_system + " " + platform.release() + ' ' + platform.version())
        print('The system does not support')
        sys.exit(0)


__check_platform()
