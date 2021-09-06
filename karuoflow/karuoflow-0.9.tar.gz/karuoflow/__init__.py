# -*- encoding: utf-8 -*-
'''
@文件    :__init__.py
@说明    :
@时间    :2020/09/02 16:27:09
@作者    :caimmy@hotmail.com
@版本    :0.1
'''


from .flowapp import KaruoFlow
from .db.tables import InitKaruoflowTables
from .datadef import DbConfig

'''
@version 0.6 [2021-05-26] 增加会签、加签(InsertSign)、转签(AddSign)等功能
@version 0.7 [2021-06-10] 增加直接转入下一阶段的功能，供业务层决定阶段变更
@version 0.8 [2021-06-15] 审批接口 AgreeJobFlow_V2 增加手写签名参数
@version 0.9 [2021-08-26] 支持同一个审核人的连续审批
'''

__version__ = 0.9