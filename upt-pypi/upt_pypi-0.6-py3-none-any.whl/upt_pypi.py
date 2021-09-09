# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import pkg_resources
import re
import tempfile
from urllib import request

import pkginfo
import requests
import upt

from .licenses import guess_licenses


class PyPIPackage(upt.Package):
    pass


class PyPIFrontend(upt.Frontend):
    name = 'pypi'

    @staticmethod
    def get_archive_info(release, kind):
        for elt in release:
            if elt['packagetype'] == kind:
                digests = elt.get('digests', {})
                return (elt['url'], elt.get('size', 0),
                        digests.get('md5'), digests.get('sha256'))
        raise ValueError(f'No archive of type "{kind}" could be found')

    def get_sdist_archive_url(self, release):
        url, _, _, _ = self.get_archive_info(release, 'sdist')
        return url

    def get_wheel_url(self, release):
        url, _, _, _ = self.get_archive_info(release, 'bdist_wheel')
        return url

    @staticmethod
    def _string_req_to_upt_pkg_req(string_req):
        r = pkg_resources.Requirement.parse(string_req)
        name = r.project_name
        specifier = ','.join(op+version for (op, version) in r.specs)
        return upt.PackageRequirement(name, specifier)

    @classmethod
    def _string_req_list_to_upt_pkg_req_list(cls, string_req_list):
        return [cls._string_req_to_upt_pkg_req(s) for s in string_req_list]

    def parse_requires_dist(self, requires_dist):
        run_reqs = []
        test_reqs = []
        for req in requires_dist:
            try:
                req_name, extra = req.split(';')
                extra = extra.strip()
            except ValueError:  # No "extras".
                req_name = req
                extra = None
            pkg = self._string_req_to_upt_pkg_req(req_name)
            if extra is not None:
                # We only care about extras if they are likely to define the
                # test requirements.
                # TODO: care about optional runtime requirements when upt
                # provides support for them.
                # TODO: handle cases where 'extra' matches a requirement on the
                # Python version.
                m = re.match("extra == '(.*)'", extra)
                if m:
                    extra_name = m.group(1)
                    if extra_name in ('test', 'tests', 'testing'):
                        test_reqs.append(pkg)
            else:
                run_reqs.append(pkg)
        return run_reqs, test_reqs

    def compute_requirements_from_wheel(self, wheel_url):
        reqs = {}
        with tempfile.NamedTemporaryFile(suffix=".whl") as wheelfile:
            request.urlretrieve(wheel_url, wheelfile.name)
            wheel = pkginfo.Wheel(wheelfile.name)
            run_reqs, test_reqs = self.parse_requires_dist(wheel.requires_dist)
            if run_reqs:
                reqs['run'] = run_reqs
            if test_reqs:
                reqs['test'] = test_reqs
        return reqs

    def compute_requirements_from_pypi_json(self, json):
        reqs = {}
        requires_dist = json.get('info', {}).get('requires_dist', [])
        run_reqs, test_reqs = self.parse_requires_dist(requires_dist or [])
        if run_reqs:
            reqs['run'] = run_reqs
        if test_reqs:
            reqs['test'] = test_reqs
        return reqs

    def compute_requirements(self):
        """Computes the requirements using various methods.

        Try to compute the runtime requirements of the package by;
        - looking at the requires_dist field of the JSON document we are
          parsing.
        - looking at the contents of the wheel. It is the most reliable
          method, but it is a bit slower since we need to download the wheel.

        The relevant data is not always available in the JSON returned by PyPI.
        For instance, alembic 1.7.1 depends on a few packages, but none of them
        are shown in on https://pypi.org/pypi/alembic/1.7.1/json: the
        .info.requires_dist field is null. The dependencies are available in
        the wheel, though.
        """
        reqs = self.compute_requirements_from_pypi_json(self.json)
        if reqs:
            return reqs
        else:
            # If we did not get any requirements from the JSON we parsed, this
            # could mean two different things:
            # 1) The package has no dependencies at all (unlikely)
            # 2) Data was missing from the JSON we parsed (this does happen for
            #    some releases, for unknown reasons)
            # Since this is suspicious, we try to get the requirements from the
            # wheel (if there is one) instead.
            try:
                version = self.json['info']['version']
                wheel_url = self.get_wheel_url(self.json['releases'][version])
                return self.compute_requirements_from_wheel(wheel_url)
            except ValueError:  # No wheel for this package
                return {}

    def get_archives(self, release):
        url, size, md5, sha256 = self.get_archive_info(release, 'sdist')
        archive = upt.Archive(url, size=size, md5=md5, sha256=sha256)
        return [archive]

    @staticmethod
    def get_name(json):
        """Return the name of the package.

        We cannot just rely on the name submitted by the user, since they may
        use the wrong capitalization.
        """
        return json['info']['name']

    def parse(self, pkg_name, version=None):
        if version is not None:
            url = f'https://pypi.org/pypi/{pkg_name}/{version}/json'
            r = requests.get(url)
            if not r.ok:
                raise upt.InvalidPackageVersionError(self.name, pkg_name,
                                                     version)
        else:
            url = f'https://pypi.org/pypi/{pkg_name}/json'
            r = requests.get(url)
            if not r.ok:
                raise upt.InvalidPackageNameError(self.name, pkg_name)
        self.json = r.json()
        version = self.json['info']['version']
        requirements = self.compute_requirements()
        try:
            self.archives = self.get_archives(self.json['releases'][version])
            sdist_url = self.archives[0].url
        except ValueError:
            self.archives = []
            sdist_url = ''
        d = {
            'homepage': self.json['info']['home_page'],
            'summary': self.json['info']['summary'],
            'description': self.json['info']['description'],
            'requirements': requirements,
            'archives': self.archives,
            'licenses': guess_licenses(self.json, sdist_url),
        }
        return PyPIPackage(self.get_name(self.json), version, **d)
