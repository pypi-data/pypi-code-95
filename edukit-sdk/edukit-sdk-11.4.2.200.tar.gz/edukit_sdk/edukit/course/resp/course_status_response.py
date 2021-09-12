# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.common.model.response import Response


class CourseStatusResponse(Response):
    """
    课程状态结果
    """
    def __init__(self):
        self._content_id = None
        self._content_version_id = None
        self._review_status = None
        self._listing_status = None
        self._reject_reason = None

    @property
    def content_id(self):
        return self._content_id

    @content_id.setter
    def content_id(self, content_id):
        # 课程id
        self._content_id = content_id

    @property
    def content_version_id(self):
        return self._content_version_id

    @content_version_id.setter
    def content_version_id(self, content_version_id):
        """
        * 当前最新的课程版本ID
        * 教育中心会同时维护课程的一个在架版本和一个审核版本
        * 一个课程新建或者更新的版本审核上架后，该版本成为最新的版本
        * 一个已上架课程如果创建了新版本，该版本将成为最新版本
        :param content_version_id:
        :return:
        """
        self._content_version_id = content_version_id

    @property
    def review_status(self):
        return self._review_status

    @review_status.setter
    def review_status(self, review_status):
        """
        * 课程当前审核状态
        * 1-新建待提交：新创建课程，当前尚未提交审核
        * 2-新建待审核：新创建课程，已提交审核，当前在审核过程中
        * 3-新建审核通过：新创建课程，审核通过已处于上架状态
        * 4-新建审核驳回：新创建课程，审核未通过已被驳回
        * 5-更新待提交：课程新版本，当前尚未提交审核
        * 6-更新待审核：课程新版本，已提交审核，当前在审核过程中
        * 7-更新审核通过：课程新版本，审核通过已处于上架状态
        * 8-更新审核驳回：课程新版本，审核未通过已被驳回
        * 9-下架待审核：已提交下架申请，当前在审核过程中
        * 10-下架审核驳回：已提交下架申请，审核未通过
        * 11-运营下架：课程已被华为运营人员下架
        * 12-开发者下架审核通过：下架申请审核通过，课程已下架
        * 13-到期自动下架：设置的课程自动下架时间已到，课程被自动下架
        :param review_status:
        :return:
        """
        self._review_status = review_status

    @property
    def listing_status(self):
        return self._listing_status

    @listing_status.setter
    def listing_status(self, listing_status):
        """
        * 课程当前在架状态
        * 1-未上架: 用户无法浏览和购买课程
        * 2-已上架: 用户可正常浏览和购买课程
        :param listing_status:
        :return:
        """
        self._listing_status = listing_status

    @property
    def reject_reason(self):
        return self._reject_reason

    @reject_reason.setter
    def reject_reason(self, reject_reason):
        """
        当reviewStatus为驳回状态时，返回运营录入的驳回原因
        :param reject_reason:
        :return:
        """
        self._reject_reason = reject_reason
