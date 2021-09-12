#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.teacher.impl.teacher_handler import TeacherHandler


class TeacherDeleteRequest:
    def __init__(self, teacher_id, reason, credential_list):
        self._teacher_id = teacher_id
        self._reason = reason
        self._teacher_handler = TeacherHandler(
            EduKitRequestSender(credential_list))

    def delete(self):
        return self._teacher_handler.delete(self._teacher_id, self._reason)
