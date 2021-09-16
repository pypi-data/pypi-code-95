# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2017-08-02 16:45:33
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-08-03 11:19:30

import easyspider
from os.path import join, exists, abspath
from scrapy.commands.startproject import Command
from shutil import ignore_patterns, move, copy2, copystat

class easyCommand(Command):

    def run(self, args, opts):
        if len(args) not in (1, 2):
            raise UsageError()

        project_name = args[0]
        project_dir = args[0]

        if len(args) == 2:
            project_dir = args[1]

        if exists(join(project_dir, 'scrapy.cfg')):
            self.exitcode = 1
            print('Error: scrapy.cfg already exists in %s' % abspath(project_dir))
            return

        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return

        self._copytree(self.templates_dir, abspath(project_dir))
        """
        # 只是完整的复制过来，创建修改时间和文件夹的名字都没有变
        # 不方便记录新增时间
        """
        # print join(project_dir, 'crawler')
        # print join(project_dir, project_name)
        # 不需要把scrapy里面的文件夹名字也变成project_name, 直接用crawler挺好的
        # 只要最外层是project_name 就好了
        # move(join(project_dir, 'crawler'), join(project_dir, project_name))
        
        # TODO: 创建时间修改时间问题..希望能是最新的



    @property
    def templates_dir(self):
        _templates_base_dir = join(easyspider.__path__[0], 'template_dir')
        return join(_templates_base_dir)