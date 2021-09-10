# -*- coding: utf-8 -*-
"""
ekca_service.plugins.otp.privacyidea - OTP check plugin for privacyIDEA
"""
import requests
import json

from ekca_service.plugins.otp.base import OTPWebService, OTPCheckFailed

ENDPOINT = "/validate/check"


class PrivacyIdeaOTPChecker(OTPWebService):
    """
    Check OTP against web service of privacyIDEA
    """

    def check(self, username, otp):
        """
        Check OTP against web service of privacyIDEA

        Use the config parameters:

        * OTP_CHECK_URL
        * OTP_PRIVACYIDEA_SSLVERIFY (optional, default=True)
        * OTP_PRIVACYIDEA_UA (optional)
        * OTP_PRIVACYIDEA_REALM (optional)

        Raises Exception in case of an error.

        """
        url = self._cfg['OTP_CHECK_URL']
        ssl_verify = self._cfg.get('OTP_PRIVACYIDEA_SSLVERIFY', True)
        useragent = self._cfg.get('OTP_PRIVACYIDEA_UA', 'ekca/0.1')
        realm = self._cfg.get("OTP_PRIVACYIDEA_REALM")
        headers = {'user-agent': useragent,
                   'Content-Type': 'application/json'}
        if not url.lower().endswith("/validate/check"):
            url += "/validate/check"
        data = {"user": username,
                "pass": otp}
        if realm:
            data["realm"] = realm
        response = requests.post(url,
                                 data=json.dumps(data).encode(),
                                 headers=headers, verify=ssl_verify)
        resp = response.json()
        result = resp.get("result")
        if not result.get("status"):
            self._log.warning("privacyIDEA failed to handle the authentication request.")
            raise OTPCheckFailed("Failed to handle request.")
        elif not result.get("value"):
            self._log.info("User failed to authenticate against privacyIDEA.")
            raise OTPCheckFailed("User failed to authenticate.")
