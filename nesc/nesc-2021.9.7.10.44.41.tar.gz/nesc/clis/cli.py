#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : __init__.py
# @Time         : 2021/1/31 10:20 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : python meutils/clis/__init__.py


import typer

from meutils.pipe import *
from meutils.log_utils import logger4wecom
from meutils.decorators.catch import wecom_catch, wecom_hook

cli = typer.Typer(name="东北证券 clis")


@wecom_hook("东北证券cli测试")
@cli.command(help="help")  # help会覆盖docstring
def clitest(path: str):
    """

    @param name: name
    @return:
    """

    p = Path(path)
    typer.echo(f"{p}")
    typer.echo(f"{p.absolute()}")


@cli.command()
def extract4ddl(ipath: str, opath=None, encoding='GB18030'):
    """解析ddl
    nesc extract4ddl '/Users/yuanjie/Desktop/notebook/0_TODO/mot_part.sql'
    """
    from nesc.extract import extract4ddl
    extract4ddl.main(ipath, opath, encoding=encoding)


@cli.command()
def extract4excel(ipath: str, opath=None):
    """解析excel
    nesc extract4excel xx
    """
    from nesc.extract import extract4excel
    extract4excel.main(ipath, opath)


@cli.command()
def extract4excel(ipath: str, opath=None):
    """解析excel
    nesc extract4excel xx
    """
    from nesc.extract import extract4excel
    extract4excel.main(ipath, opath)


@cli.command()
def text_match(target, file, topn: int = 10, batch_size: int = 256,
               model_home='chinese_roformer-sim-char-ft_L-6_H-384_A-6'):
    """相似文本匹配"""
    from nesc.sim import sim
    sim.main(target, file, topn, batch_size, model_home)


if __name__ == '__main__':
    cli()
