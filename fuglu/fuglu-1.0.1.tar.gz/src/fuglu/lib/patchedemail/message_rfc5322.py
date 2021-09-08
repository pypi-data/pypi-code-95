# -*- coding: UTF-8 -*-
#   Copyright 2009-2021 Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
from typing import Optional
from email.message import EmailMessage
from .message import PatchedGenerator
from io import StringIO
from email.policy import Policy


class PatchedMessage(EmailMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def as_string(self,
                  unixfrom: bool = False,
                  maxheaderlen: int = 0,
                  policy: Optional[Policy] = None) -> str:
        """
        Return the entire formatted message as a string.

        Overwrites the original method to use patched version of generator
        """
        policy = self.policy if policy is None else policy
        fp = StringIO()
        g = PatchedGenerator(fp,
                             mangle_from_=False,
                             maxheaderlen=maxheaderlen,
                             policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()
