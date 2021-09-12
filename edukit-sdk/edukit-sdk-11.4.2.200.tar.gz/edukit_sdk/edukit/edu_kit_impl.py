# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.album.impl.album_create_request import \
    AlbumCreateRequest
from edukit_sdk.edukit.album.impl.album_delete_request import \
    AlbumDeleteRequest
from edukit_sdk.edukit.album.impl.album_manage_request import \
    AlbumManageRequest
from edukit_sdk.edukit.album.impl.album_update_request import \
    AlbumUpdateRequest
from edukit_sdk.edukit.album.model.album import Album
from edukit_sdk.edukit.catalogue.impl.catalogue_create_request import \
    CatalogueCreateRequest
from edukit_sdk.edukit.catalogue.impl.catalogue_delete_request import \
    CatalogueDeleteRequest
from edukit_sdk.edukit.catalogue.impl.catalogue_update_request import \
    CatalogueUpdateRequest
from edukit_sdk.edukit.catalogue.model.catalogue import Catalogue
from edukit_sdk.edukit.catalogue.model.catalogue_edit_data import \
    CatalogueEditData
from edukit_sdk.edukit.common.log.logger import Logger
from edukit_sdk.edukit.course.impl.course_create_request import \
    CourseCreateRequest
from edukit_sdk.edukit.course.impl.course_off_shelf_request import \
    CourseOffShelfRequest
from edukit_sdk.edukit.course.impl.course_status_request import \
    CourseStatusRequest
from edukit_sdk.edukit.course.impl.course_update_request import \
    CourseUpdateRequest
from edukit_sdk.edukit.course.model.course import Course
from edukit_sdk.edukit.course.model.course_edit import CourseEdit
from edukit_sdk.edukit.learning.impl.learning_report_request import \
    LearningReportRequest
from edukit_sdk.edukit.learning.model.series_course_learning_info import \
    SeriesCourseLearningInfo
from edukit_sdk.edukit.learning.model.unitary_course_learning_info import \
    UnitaryCourseLearningInfo
from edukit_sdk.edukit.lesson.impl.lesson_create_request import \
    LessonCreateRequest
from edukit_sdk.edukit.lesson.impl.lesson_delete_request import \
    LessonDeleteRequest
from edukit_sdk.edukit.lesson.impl.lesson_update_request import \
    LessonUpdateRequest
from edukit_sdk.edukit.package.impl.pkg_create_request import PkgCreateRequest
from edukit_sdk.edukit.package.impl.pkg_delete_request import PkgDeleteRequest
from edukit_sdk.edukit.package.impl.pkg_manage_request import PkgManageRequest
from edukit_sdk.edukit.package.impl.pkg_product_delete_request import \
    PkgProductDeleteRequest
from edukit_sdk.edukit.package.impl.pkg_product_update_request import \
    PkgProductUpdateRequest
from edukit_sdk.edukit.package.impl.pkg_update_request import PkgUpdateRequest
from edukit_sdk.edukit.package.model.pkg import Pkg
from edukit_sdk.edukit.signup.impl.signup_request import SignupRequest
from edukit_sdk.edukit.signup.model.batch_report_signup_course_request import \
    BatchReportSignupCourseRequest
from edukit_sdk.edukit.signup.model.package_signup_info import \
    PackageSignupInfo
from edukit_sdk.edukit.teacher.impl.teacher_create_request import \
    TeacherCreateRequest
from edukit_sdk.edukit.teacher.impl.teacher_delete_request import \
    TeacherDeleteRequest
from edukit_sdk.edukit.teacher.impl.teacher_update_request import \
    TeacherUpdateRequest
from edukit_sdk.edukit.teacher.model.teacher import Teacher
from edukit_sdk.edukit.teacher.model.teacher_edit import TeacherEdit


class EduKitImpl:
    """
    华为教育中心EduKit服务入口类
    @author MWX1057591
    @since 2021-06-08
    """
    def __init__(self, credential_list):
        self.credential_list = credential_list
        self.logger = Logger.get_logger()

    def get_course_create_request(self, course: Course):
        return CourseCreateRequest(course, self.credential_list)

    def get_course_update_request(self, course_edit: CourseEdit):
        return CourseUpdateRequest(course_edit, self.credential_list)

    def get_course_off_shelf_request(self, course: Course):
        return CourseOffShelfRequest(course, self.credential_list)

    def get_course_status_request(self, course_id):
        return CourseStatusRequest(course_id, self.credential_list)

    def get_lesson_create_request(self, course_id, course_edit_id, lesson):
        return LessonCreateRequest(course_id, course_edit_id, lesson,
                                   self.credential_list)

    def get_lesson_delete_request(self, course_id, course_edit_id, lesson_id):
        return LessonDeleteRequest(course_id, course_edit_id, lesson_id,
                                   self.credential_list)

    def get_lesson_update_request(self, lesson_edit):
        return LessonUpdateRequest(lesson_edit, self.credential_list)

    # 通知用户课程订购状态的变更
    def get_report_signup(self, user_id, course_id, user_id_type, signup_info):
        return SignupRequest.report_signup(user_id, course_id, user_id_type,
                                           signup_info, self.credential_list)

    # 批量通知用户课程订购状态的变更
    def get_batch_report_signup_course(self, user_id, user_id_type,
                                       batch: BatchReportSignupCourseRequest):
        return SignupRequest.batch_report_signup_course(
            user_id, user_id_type, batch, self.credential_list)

    # 通知会员包订购状态的变更
    def get_report_signup_package(self, user_id, user_id_type,
                                  package: PackageSignupInfo):
        return SignupRequest.report_signup_package(user_id, user_id_type,
                                                   package,
                                                   self.credential_list)

    # 上报用户单体课学习信息
    def get_report_unitary_course_learning(self, user_id, course_id,
                                           user_id_type,
                                           unitary: UnitaryCourseLearningInfo):
        return LearningReportRequest.report_unitary_course_learning(
            user_id, course_id, user_id_type, unitary, self.credential_list)

    # 上报用户系列课学习信息
    def get_report_series_course_learning(self, user_id, course_id,
                                          user_id_type, lesson_id,
                                          series: SeriesCourseLearningInfo):
        return LearningReportRequest.report_series_course_learning(
            user_id, course_id, user_id_type, lesson_id, series,
            self.credential_list)

    # 创建专辑
    def get_create_album(self, album: Album):
        return AlbumCreateRequest(album, self.credential_list)

    # 更新专辑
    def get_update_album(self, album_id, album: Album):
        return AlbumUpdateRequest(album_id, album, self.credential_list)

    # 删除专辑
    def get_delete_album(self, album_id):
        return AlbumDeleteRequest(album_id, self.credential_list)

    # 管理专辑
    def get_manage_album(self, album_id, action, removal_reason):
        return AlbumManageRequest(album_id, action, removal_reason,
                                  self.credential_list)

    # 目录创建
    def get_catalogue_create_request(self,
                                     catalogue_edit_data: CatalogueEditData,
                                     course_id, course_edit_id):
        return CatalogueCreateRequest(catalogue_edit_data, course_id,
                                      course_edit_id, self.credential_list)

    # 目录更新
    def get_catalogue_update_request(self, catalogue: Catalogue, course_id,
                                     course_edit_id):
        return CatalogueUpdateRequest(catalogue, course_id, course_edit_id,
                                      self.credential_list)

    # 目录删除
    def get_catalogue_delete_request(self, course_id, course_edit_id,
                                     catalogue_id):
        return CatalogueDeleteRequest(course_id, course_edit_id, catalogue_id,
                                      self.credential_list)

    def get_teacher_create_request(self, teacher: Teacher):
        return TeacherCreateRequest(teacher, self.credential_list)

    def get_teacher_update_request(self, teacher_edit: TeacherEdit):
        return TeacherUpdateRequest(teacher_edit, self.credential_list)

    def get_teacher_delete_request(self, teacher_id, reason):
        return TeacherDeleteRequest(teacher_id, reason, self.credential_list)

    def get_pkg_create_request(self, pkg: Pkg):
        return PkgCreateRequest(pkg, self.credential_list)

    def get_pkg_update_request(self, pkg_id, pkg):
        return PkgUpdateRequest(pkg_id, pkg, self.credential_list)

    def get_pkg_delete_request(self, pkg_id):
        return PkgDeleteRequest(pkg_id, self.credential_list)

    def get_pkg_manage_request(self, pkg_id, action, removal_reason):
        return PkgManageRequest(pkg_id, action, removal_reason,
                                self.credential_list)

    def get_pkg_product_update_request(self, pkg_id, pkg_product_list):
        return PkgProductUpdateRequest(pkg_id, pkg_product_list,
                                       self.credential_list)

    def get_pkg_product_delete_request(self, pkg_id, pkg_edit_id, product_id):
        return PkgProductDeleteRequest(pkg_id, pkg_edit_id, product_id,
                                       self.credential_list)
