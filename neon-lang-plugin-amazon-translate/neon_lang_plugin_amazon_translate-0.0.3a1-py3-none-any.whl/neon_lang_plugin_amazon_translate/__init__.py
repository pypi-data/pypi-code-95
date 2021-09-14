# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from ovos_plugin_manager.templates.language import LanguageDetector,\
    LanguageTranslator
import boto3


class AmazonTranslator(LanguageTranslator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keys = self.config.get("keys", self.config).get("amazon", self.config)
        self.client = boto3.Session(
            aws_access_key_id=self.keys.get("aws_access_key_id") or self.keys.get("key_id"),
            aws_secret_access_key=self.keys.get("aws_secret_access_key") or self.keys.get("secret_key"),
            region_name=self.keys.get("region", "us-west-2")).client('translate')

    def translate(self, text, target=None, source="auto"):
        target = target or self.internal_language

        response = self.client.translate_text(
            Text=text,
            SourceLanguageCode="auto",
            TargetLanguageCode=target.split("-")[0]
        )
        return response["TranslatedText"]


class AmazonDetector(LanguageDetector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keys = self.config.get("keys", self.config).get("amazon", self.config)
        self.client = boto3.Session(
            aws_access_key_id=self.keys.get("aws_access_key_id") or self.keys.get("key_id"),
            aws_secret_access_key=self.keys.get("aws_secret_access_key") or self.keys.get("secret_key"),
            region_name=self.keys.get("region", "us-west-2")).client('comprehend')

    def detect(self, text):
        response = self.client.detect_dominant_language(
            Text=text
        )
        return response['Languages'][0]['LanguageCode']

    def detect_probs(self, text):
        response = self.client.detect_dominant_language(
            Text=text
        )
        langs = {}
        for lang in response["Languages"]:
            langs[lang["LanguageCode"]] = lang["Score"]
        return langs
