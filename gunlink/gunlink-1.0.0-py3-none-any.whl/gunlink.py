"""
MIT License

Copyright (c) 2020 Brijeshkrishna

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


"""

from .core.funtions import *
from .core.subclass import *


class link:
    def __init__(self, url):
        self.url: str = url
        self.protocol: str = ''
        self.domain: str = ''
        self.subDomain: list = []
        self.rootDomain: str = ''
        self.topDomain: str = ''
        self.path: list = []
        self.query: dict = {}
        self.is_valid_link: bool = isurl(url=self.url)
        self.ip: str = '-1'

        if self.is_valid_link:
            self.url = add_backslash(url=self.url)

            self.protocol: str = protocol(url=self.url)
            self.sub_domain, self.root_domain, self.top_domain, self.port, self.main_domain, self.host = domain(
                url=self.url, url_protocol=self.protocol)
            self.path, self.query = path_query(url=self.url)

            self.ip = find_ip(main_domain=self.main_domain)

    def whois(self):
        return whois(self.ip)

    def tiny(self):
        return tiny(self.url)
