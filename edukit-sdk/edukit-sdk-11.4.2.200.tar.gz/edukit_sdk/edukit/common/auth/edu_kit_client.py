#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from typing import Optional


class EduKitClient:
    def __init__(self,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 grant_type="client_credentials"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
