# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.course.impl.course_handler import CourseHandler


class CourseStatusRequest:
    def __init__(self, course_id, credential_list):
        self._course_id = course_id
        self._credential_list = credential_list
        self._course_handler = CourseHandler(
            EduKitRequestSender(credential_list))

    def get_course_status(self):
        return self._course_handler.get_course_status(self._course_id)
