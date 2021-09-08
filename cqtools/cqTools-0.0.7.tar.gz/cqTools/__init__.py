#!/usr/bin/env python
#-*- coding: utf-8 -*-
__all__ = ["utils", "studentSearch"]
from cqTools.StudentSearch.utils.login import ReportLogin

class studentSearch(ReportLogin):
    def __init__(self) -> None:
        """查找学生信息
        """
        super(studentSearch, self).__init__()

    def login(self, cardNo:str, password:str) -> dict:
        """获取登录token
        """
        return super().login(cardNo=cardNo, password=password)

    def resetPassword(self, cardNo:str) -> bool:
        """重置密码
        """
        return super().resetPassword(cardNo=cardNo)

    def setPassword(self, cardNo:str, password:str, newPassword:str) -> bool:
        """修改密码
        """
        return super().setPassword(cardNo=cardNo, password=password, newPassword=newPassword)