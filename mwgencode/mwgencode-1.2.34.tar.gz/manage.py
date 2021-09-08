from typing import TextIO
import logging
from gencode.gen_code import GenCode,GenProject_Sample,GenProject_Flask,GenProject_Aiohttp,GenSwagger
import argparse
import os
import sys
from gencode.gencode.export_class2swgclass import ExportClass2SWGClass
import yaml
class Gen_Code():
    def __init__(self,args):
        # project 类型，flask，aiohttp
        # self.type = type
        # self.umlfile = os.path.abspath(umlfile)
        # self.rootpath = os.path.abspath(rootpath)
        self.args = args
        self.prj_conf = None

    def _get_config(self) -> dict:
        def load_config():
            cnfgfile = os.path.join(os.path.abspath(self.args.root_path), 'gen_code.yaml')
            if not os.path.exists(cnfgfile):
                raise Exception('gen_code.yaml文件不存在，请先执行 gencode init 初始化项目！')
            yml = open(cnfgfile)
            try:
                self.prj_conf = yaml.full_load(yml)
            except Exception as e:
                raise Exception('载入 gen_code.yaml 出错，error:%s' % e)
            return self.prj_conf
        if self.prj_conf is None:
            self.prj_conf  = load_config()
        return self.prj_conf

    def _get_apptype(self):
        try:
            return self._get_config().get('project', {}).get('type', 'flask')
        except Exception as e:
            raise Exception('gen_code.yaml 文件内容出错，%s' % e)

    def _get_rootpath(self):
        try:
            # cmd有指定rootpath 时，以指定的rootpath
            return self.args.root_path if self.args.root_path!='.' else self._get_config().get('project',{}).get('rootpath','.')
        except Exception as e:
            raise Exception('gen_code.yaml 文件内容出错，%s'%e)

    def _get_umlfile(self):
        try:
            return os.path.join(self._get_rootpath(),
                                   self._get_config()['project']['doc_dir'],
                                   self._get_config().get('project',{}).get('models',{}).get(self.args.model)['file'])
        except Exception as e:
            raise Exception('gen_code.yaml 文件内容出错，%s'%e)

    def init_project(self):
        '''
        产生一个包含 sample.mdj文件和gen_code_run.py单元的专案
        :return:
        '''
        gp = GenProject_Sample(r'%s' % self.args.umlfile,
                        r'%s' % self.args.project_name)
        gp.gen_code(self.args.python_code)

    def gen_model(self,outfile='model_base.py'):
        '''
        产生model单元
        :return:
        '''
        logging.info(self.args)
        g = GenCode(self.umlfile, self.rootpath)
        g.model(outfile=outfile)

    def gen_swagger(self):
        '''
        产生swagger.yaml单元
        :return:
        '''
        g = GenCode(self.umlfile, self.rootpath)
        g.swagger()

    def gen_export(self):
        exp = ExportClass2SWGClass(self.umlfile,self.umlfile)
        exp.export()

    def gen_add(self):
        prj_type = self._get_apptype()
        umlfile = self._get_umlfile()
        prj_rootpath = self._get_rootpath()
        if prj_type == 'flask':
            '''
            1，修改gen_code.yaml
            2，生成uml
            3，修改代码
            '''
            pass
        elif prj_type =='aiohttp':
            pass
        else:
            raise Exception('不支持该project type(%s)'%prj_type)


    def gen_build(self):
        prj_type = self._get_apptype()
        umlfile = self._get_umlfile()
        prj_rootpath = self._get_rootpath()
        if prj_type =='flask':
            gp = GenProject_Flask(r'%s' % umlfile,
                                  r'%s' % prj_rootpath)
        elif prj_type =='aiohttp':
            gp = GenProject_Aiohttp(r'%s' % umlfile,
                                    r'%s' % prj_rootpath)
        else:
            raise Exception('不支持该project type(%s)'%prj_type)
        gp.gen_code()

def main():
    parser = argparse.ArgumentParser(description='''产生flask web框架的代码''')
    parser.add_argument('-r', '--root-path',
                           help='专案的根目录(default: 当前目录名)',
                           default='.')
    subparsers = parser.add_subparsers(title='Command')

    # 初始项目，建立sample umlmodel，config等文件
    gp_parser = subparsers.add_parser('init', help='创建项目的初始文件，包括uml，cconfig等文件', add_help=False)
    gp_parser.set_defaults(command='init_project')
    gp_parser.add_argument('-f', '--umlfile',
                        type = str,
                        help='指定mdj文件 (default: sample.mdj)，不指定时以项目名为文件名',
                        default='default.mdj')
    gp_parser.add_argument('-p', '--project-name',
                        help='专案名称(default: 当前目录名)',
                        default='.')
    gp_parser.add_argument('-t', '--project-type',
                        help='专案类型 ：flask，aiohttp，default为 flask',
                        type=str, choices=['flask', 'aiohttp'],
                        default='flask')
    gp_parser.add_argument('-c', '--python-code',
                        help='产生gen_code_run.py 单元',
                        action='store_true')

    gp_parser = subparsers.add_parser('build', help='产生项目相关的文件'
                                                 '-m model名称', add_help=False)
    gp_parser.set_defaults(command='gen_build')
    gp_parser.add_argument('-m','--model', help='model名称',type=str,default = 'main')

    gp_parser = subparsers.add_parser('add', help='添加新的model', add_help=False)
    gp_parser.set_defaults(command='gen_add')
    gp_parser.add_argument('-m','--model', help='model名称',type=str)

    gp_parser = subparsers.add_parser('exp', help='把mdj的umlclass 转成 swagger class', add_help=False)
    gp_parser.set_defaults(command='gen_export')


    # gp_parser = subparsers.add_parser('gctrl', help='根据xmi创建umlclass 的 swagger ctrole单元', add_help=False)
    # gp_parser.set_defaults(command='gen_ctrl')

    if len(sys.argv)==1:
        parser.print_help()
        print('sample 1 : python gen_code.py -f ./docs/test.mdj -p d:/temp/swg -t aiohttp gp')
        print('sample 2 : gencode -f ./docs/test.mdj  -t aiohttp gp')
        print('sample 3 : gencode -f ./docs/test.mdj gp')
        print('sample 4 : gencode gp #-f gencode.mdj -t flask')
        sys.exit()
    args = parser.parse_args(sys.argv[1:])
    print(args)
    gen_code = Gen_Code(args)
    getattr(gen_code, args.command)()
    print('gen code success!')

if __name__ == '__main__':
    main()
    rootpath = r'./order_system'
    # umlfile = r'./docs/order_system.mdj'
    # umlfile = r'D:\mwwork\projects\mwgencode\order_system\docs\test.mdj'
    umlfile = r'D:\mwwork\projects\mwgencode\order_system\docs\ordermng.mdj'
    g = GenCode(umlfile, rootpath)
    # # #  把boclass 汇出成 swagger class
    # # g.export(umlfile,umlfile,exclude_classes=['user'])
    # # #  产生model单元，type= flask:产生flask_sqlalchemy 的 model
    # # #               type = sql ：产生 sqlalchemy 的 model
    g.model()
    gen_swg = GenSwagger(umlfile)
    gen_swg.export_one_swgclass('xxxx')
    gen_swg.add_operation('xxxxmng','tttt',)
    p = GenProject_Flask(umlfile, rootpath)
    # # 产生专案代码
    p.gen_code()
    # # umlfile=r'D:\mwwork\projects\mwgencode\order_system\docs\realtime.mdj'
    # # gen_swg = GenSwagger(umlfile)
    # # gen_swg.add_operation('geomng','tttt','post')
    # #
    # # p = GenProject_Aiohttp(umlfile,rootpath)
    # # p.gen_code()