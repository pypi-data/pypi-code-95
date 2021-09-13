# Copyright (C) 2019  Nexedi SA and Contributors.
#                     Romain Courteaud <romain@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.

import requests
from urllib.parse import urlparse, urlunsplit
from forcediphttpsadapter.adapters import ForcedIPHTTPSAdapter
from peewee import fn


PREFERRED_TYPE = "text/html"
TIMEOUT = 2
ELAPSED_FAST = 0.2
ELAPSED_MODERATE = 0.5


def getUrlHostname(url):
    return urlparse(url).hostname


def getRootUrl(url):
    parsed_url = urlparse(url)
    return "%s://%s" % (parsed_url.scheme, parsed_url.hostname)


def getUserAgent(version):
    return "%s/%s (+%s)" % (
        "SURYKATKA",
        version,
        "https://lab.nexedi.com/nexedi/surykatka",
    )


def request(url, timeout=TIMEOUT, headers=None, session=requests, version=0):

    if headers is None:
        headers = {}
    if "Accept" not in headers:
        headers["Accept"] = "%s;q=0.9,*/*;q=0.8" % PREFERRED_TYPE
    if "User-Agent" not in headers:
        # XXX user agent
        headers["User-Agent"] = getUserAgent(version)

    kwargs = {}
    kwargs["stream"] = False
    kwargs["timeout"] = timeout
    kwargs["allow_redirects"] = False
    kwargs["verify"] = True
    args = ["GET", url]

    kwargs["headers"] = headers

    try:
        response = session.request(*args, **kwargs)
    except requests.exceptions.SSLError:
        # XXX Enter into unknown host
        response = requests.models.Response()
        response.status_code = 526
    except requests.exceptions.ConnectionError:
        response = requests.models.Response()
        response.status_code = 523
    except (
        requests.exceptions.Timeout,
        requests.exceptions.ChunkedEncodingError,
    ):
        response = requests.models.Response()
        response.status_code = 524
    except requests.exceptions.TooManyRedirects:
        response = requests.models.Response()
        response.status_code = 520
    return response


def reportHttp(db, ip=None, url=None):
    query = (
        db.HttpCodeChange.select(db.HttpCodeChange)
        .group_by(db.HttpCodeChange.ip, db.HttpCodeChange.url)
        .having(
            db.HttpCodeChange.status_id == fn.MAX(db.HttpCodeChange.status_id)
        )
    )

    if ip is not None:
        if type(ip) == list:
            query = query.where(db.HttpCodeChange.ip << ip)
        else:
            query = query.where(db.HttpCodeChange.ip == ip)

    if url is not None:
        if type(url) == list:
            query = query.where(db.HttpCodeChange.url << url)
        else:
            query = query.where(db.HttpCodeChange.url == url)

    return query


def packHttp(db):
    with db._db.atomic():
        result = [x for x in reportHttp(db)]
        for http_change in result:
            db.HttpCodeChange.delete().where(
                db.HttpCodeChange.status_id != http_change.status_id,
                db.HttpCodeChange.url == http_change.url,
                db.HttpCodeChange.ip == http_change.ip,
            ).execute()


def calculateSpeedRange(total_seconds, fast, moderate):
    # Prevent updating the DB by defining acceptable speed range
    if total_seconds == 0:
        # error cases
        return "BAD"
    elif total_seconds < fast:
        return "FAST"
    elif total_seconds < moderate:
        return "MODERATE"
    else:
        return "SLOW"


def logHttpStatus(
    db,
    ip,
    url,
    code,
    http_header_dict,
    total_seconds,
    fast,
    moderate,
    status_id,
):

    with db._db.atomic():
        try:
            # Check previous parameter value
            previous_entry = reportHttp(db, ip=ip, url=url).get()
        except db.HttpCodeChange.DoesNotExist:
            previous_entry = None

        if (
            (previous_entry is None)
            or (previous_entry.status_code != code)
            or (previous_entry.http_header_dict != http_header_dict)
            or (
                calculateSpeedRange(
                    previous_entry.total_seconds, fast, moderate
                )
                != calculateSpeedRange(total_seconds, fast, moderate)
            )
        ):
            previous_entry = db.HttpCodeChange.create(
                status=status_id,
                ip=ip,
                url=url,
                status_code=code,
                http_header_dict=http_header_dict,
                total_seconds=total_seconds,
            )
        return previous_entry.status_id


def checkHttpStatus(
    db,
    status_id,
    url,
    ip,
    bot_version,
    timeout=TIMEOUT,
    elapsed_fast=ELAPSED_FAST,
    elapsed_moderate=ELAPSED_MODERATE,
):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    request_kw = {"timeout": timeout}
    # SNI Support
    if parsed_url.scheme == "https":
        # Provide SNI support
        base_url = urlunsplit(
            (parsed_url.scheme, parsed_url.netloc, "", "", "")
        )
        session = requests.Session()
        session.mount(base_url, ForcedIPHTTPSAdapter(dest_ip=ip))
        request_kw["session"] = session
        ip_url = url
    elif parsed_url.scheme == "http":
        # Force IP location
        parsed_url = parsed_url._replace(netloc=ip)
        ip_url = parsed_url.geturl()
    else:
        raise NotImplementedError("Unhandled url: %s" % url)

    response = request(
        ip_url, headers={"Host": hostname}, version=bot_version, **request_kw
    )

    # Blacklisted, because of non stability
    # 'Date'
    header_list = [
        # Redirect
        "Location",
        # HTTP Range
        "Accept-Ranges",
        # HTTP Cache
        "Vary",
        "Cache-Control",
        "WWW-Authenticate",
        # gzip
        "Content-Type",
        "Content-Encoding",
        "Content-Disposition",
        # Security
        "Content-Security-Policy",
        "Referrer-Policy",
        "Strict-Transport-Security",
        "Feature-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        # CORS
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Headers",
        "Access-Control-Expose-Headers",
    ]
    header_dict = {}
    for header_key in header_list:
        header_value = response.headers.get(header_key, None)
        if header_value is not None:
            header_dict[header_key] = header_value

    # Store key only, because of non stability
    # 'Etag', 'Last-Modified', 'Set-Cookie', 'Date', 'Age', 'Expires'
    key_only_header_list = [
        "Etag",
        "Last-Modified",
        "Set-Cookie",
        "Age",
        "Expires",
    ]
    for header_key in key_only_header_list:
        header_value = response.headers.get(header_key, None)
        if header_value is not None:
            header_dict[header_key] = True

    logHttpStatus(
        db,
        ip,
        url,
        response.status_code,
        header_dict,
        response.elapsed.total_seconds(),
        elapsed_fast,
        elapsed_moderate,
        status_id,
    )
