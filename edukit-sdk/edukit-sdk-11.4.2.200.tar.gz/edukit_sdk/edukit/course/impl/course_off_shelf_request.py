# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.course.impl.course_handler import CourseHandler
from edukit_sdk.edukit.course.model.course import Course


class CourseOffShelfRequest:
    def __init__(self, course: Course, credential_list):
        self._course = course
        self._course_handler = CourseHandler(
            EduKitRequestSender(credential_list))

    def off_shelf(self):
        return self._course_handler.off_shelf(self._course)
