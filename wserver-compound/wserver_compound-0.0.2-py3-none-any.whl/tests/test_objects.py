""" Модуль содержит разнообразные объекты для тестов, например, WSQLuse """

from wsqluse.wsqluse import Wsqluse


test_sql_shell = Wsqluse('gdb', 'watchman', 'hect0r1337', '192.168.100.118')
