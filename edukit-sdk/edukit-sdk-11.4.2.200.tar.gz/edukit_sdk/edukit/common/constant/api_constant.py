#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class ApiConstant:
    # 请求接口
    TOKEN_URL = '/api/edukit/aps/v1/token'
    # UPLOAD
    UPLOAD_RESOURCE_URL = '/api/edukit/v1/resource/upload'
    APPLY_UPLOAD_URL = '/api/edukit/v1/media/uploadUrl'
    MULTIPART_PARTS_URL = '/api/edukit/v1/media/multipartParts'
    MULTIPART_COMPOSE_URL = '/api/edukit/v1/media/multipartCompose'
    # COURSE
    CREATE_COURSE_URL = '/api/edukit/v1/course'
    UPDATE_META_COURSE_URL = '/api/edukit/v1/course/metadata/{}/{}'
    UPDATE_PRICE_COURSE_URL = '/api/edukit/v1/course/productPrice/{}'
    UPDATE_LOCALIZED_COURSE_URL = '/api/edukit/v1/course' \
                                  '/localizedData/{}/{}/{}'
    COMMIT_COURSE_URL = '/api/edukit/v1/course/commit/{}/{}'
    CREATE_NEW_COURSE_EDIT_URL = '/api/edukit/v1/course/edit/{}'
    DELETE_COURSE_URL = '/api/edukit/v1/course/localizedData/{}/{}/{}'
    REMOVE_COURSE_URL = '/api/edukit/v1/course/removal/{}'
    GET_COURSE_STATUS_URL = '/api/edukit/v1/course/status/{}'
    # LESSON
    LESSON_CREATE_URL = '/api/edukit/v1/lesson/{}/{}'
    LESSON_URL = '/api/edukit/v1/lesson/{}/{}/{}'
    LESSON_METADATA_URL = '/api/edukit/v1/lesson' \
                          '/metadata/{}/{}/{}/{}'
    LESSON_LOCALIZED_DATA_URL = '/api/edukit/v1/lesson' \
                                '/localizedData/{}/{}/{}/{}/{}'
    LESSON_RESET_URL = '/api/edukit/v1/lesson/reset/{}/{}/{}'
    # TEACHER
    CREATE_TEACHER_URL = '/api/edukit/v1/teacher'
    UPDATE_META_TEACHER_URL = '/api/edukit/v1/teacher/metadata/{}/{}'
    UPDATE_LOCALIZED_TEACHER_URL = '/api/edukit/v1/teacher' \
                                   '/localizedData/{}/{}/{}'
    COMMIT_TEACHER_URL = '/api/edukit/v1/teacher/commit'
    CREATE_NEW_TEACHER_EDIT_URL = '/api/edukit/v1/teacher/edit'
    DELETE_LOCALIZED_TEACHER_URL = '/api/edukit/v1/teacher/' \
                                   'localizedData/{}/{}/{}'
    DELETE_TEACHER_URL = '/api/edukit/v1/teacher/edit/{}/delete'
    # ALBUM
    CREATE_ALBUM_URL = '/api/edukit/v1/api/album'
    CREATE_UPDATE_ALBUM_URL = '/api/edukit/v1/api/album/{}'
    MANAGE_ALBUM_STATUS_URL = '/api/edukit/v1/album/manage/{}'
    DELETE_ALBUM_URL = '/api/edukit/v1/album/{}'
    # NEW PKG
    CREATE_PKG_URL = '/api/edukit/v1/api/pkg'
    UPDATE_PKG_URL = '/api/edukit/v1/api/pkg/{}'
    MANAGE_PKG_STATUS_URL = '/api/edukit/v1/pkg/manage/{}'
    DELETE_PKG_URL = '/api/edukit/v2/pkg/{}'
    UPDATE_PACKAGE_PRODUCT_URL = '/api/edukit/v2/pkg/product/{}'
    DELETE_PACKAGE_PRODUCT_URL = '/api/edukit/v2/pkg/product' \
                                 '/{}?pkgEditId={}&productId={}'
    # SIGNUP
    REPORT_SIGNUP = "/api/edukit/v1/{}/{}/signup?userIdType={}"
    REPORT_SIGNUP_PACKAGE = "/api/edukit/v1/{}/package/signup?userIdType={}"
    BATCH_REPORT_SIGNUP_COURSE = "/api/edukit/v1/{}/signup/batch?userIdType={}"
    # LEARNING
    REPORT_UNITARY_COURSE_LEARNING = "/api/edukit/v1/{}/{}/" \
                                     "learning?userIdType={}"
    REPORT_SERIES_COURSE_LEARNING = "/api/edukit/v1/{}/{}/{}/" \
                                    "learning?userIdType={}"
    # CATALOGUE
    CREATE_CATALOGUE_URL = '/api/edukit/v1/catalogue/{}/{}'
    UPDATE_CATALOGUE_URL = '/api/edukit/v1/catalogue/{}/{}/{}'
    DELETE_CATALOGUE_URL = '/api/edukit/v1/catalogue/{}/{}/{}'
