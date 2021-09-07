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

cli = typer.Typer(name="东北证券 clis")


def _run_cmd(cmd, nohup=0):
    cmd = f"nohup {cmd} &" if nohup else cmd
    logger.debug(cmd)
    return os.system(cmd)


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
    nesc extract4excel "/Users/yuanjie/Downloads/UF20表结构/UF20表结构/UF20表信息.xls"
    """
    from nesc.extract import extract4excel
    extract4excel.main(ipath, opath)


if __name__ == '__main__':
    cli()
