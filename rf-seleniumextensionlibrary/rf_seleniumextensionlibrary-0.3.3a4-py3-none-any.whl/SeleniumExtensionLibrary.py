# Copyright (C) 2019 Spiralworks Technologies Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import psutil
import time
import warnings
import datetime
from browsermobproxy import Server
from urllib.parse import urlparse, parse_qs
from .version import VERSION
from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.utils import LibraryListener, timestr_to_secs, is_truthy

from robotlibcore import DynamicCore

from SeleniumLibrary.base import keyword
from SeleniumLibrary.locators import ElementFinder
from SeleniumLibrary.keywords import (
    AlertKeywords,
    BrowserManagementKeywords,
    CookieKeywords,
    ElementKeywords,
    FormElementKeywords,
    FrameKeywords,
    JavaScriptKeywords,
    RunOnFailureKeywords,
    ScreenshotKeywords,
    SelectElementKeywords,
    TableElementKeywords,
    WaitingKeywords,
    WebDriverCache,
    WindowKeywords
)
from PIL import Image


# force override warn method
# ignore the warning for capture page keyword
# since we are re-writing the png file to jpg
# this will suppress the warning message
def _new_warn(message, category=None, stacklevel=1, source=None):
    if str(message) == "name used for saved screenshot does not \
            match file type. It should end with a `.png` extension":
        return

    old_warn(message, category, stacklevel, source)


old_warn = warnings.warn
setattr(warnings, "warn", _new_warn)


class ScreenshotExtensionKeywords(ScreenshotKeywords):

    @keyword
    def element_capture_screenshot(self, locator, *options):
        """
        Takes a screenshot of an element and embeds it into the log.

        *Example:*
        | Element Capture Screenshot | css=#element |
        | Element Capture Screenshot | css=#element | style=grayscale |
        """
        self.capture_element_screenshot(locator)

    @keyword
    def capture_page(self, filename='selenium-screenshot-{index}.jpg'):
        """
        Takes a screenshot of the current page and embeds it into a log file.

        ``filename`` argument specifies the name of the file to write the
        screenshot into. The directory where screenshots are saved can be
        set when `importing` the library or by using the `Set Screenshot
        Directory` keyword. If the directory is not configured, screenshots
        are saved to the same directory where Robot Framework's log file is
        written.

        Starting from SeleniumLibrary 1.8, if ``filename`` contains marker
        ``{index}``, it will be automatically replaced with an unique running
        index, preventing files to be overwritten. Indices start from 1,
        and how they are represented can be customized using Python's
        [https://docs.python.org/3/library/string.html#format-string-syntax|
        format string syntax].

        An absolute path to the created screenshot file is returned.

        Examples:
        | `Capture Page`            |                                        |
        | `File Should Exist`       | ${OUTPUTDIR}/selenium-screenshot-1.jpg |
        | ${path} =                 | `Capture Page`              |
        | `File Should Exist`       | ${OUTPUTDIR}/selenium-screenshot-2.jpg |
        | `File Should Exist`       | ${path}                                |
        | `Capture Page`            | custom_name.jpg                        |
        | `File Should Exist`       | ${OUTPUTDIR}/custom_name.jpg           |
        | `Capture Page`            | custom_with_index_{index}.jpg          |
        | `File Should Exist`       | ${OUTPUTDIR}/custom_with_index_1.jpg   |
        | `Capture Page`            | formatted_index_{index:03}.jpg         |
        | `File Should Exist`       | ${OUTPUTDIR}/formatted_index_001.jpg   |
        """

        # this will save png file content in a jpg file name
        # this is needed in order for robot report to reflect proper filename
        return_path = self.capture_page_screenshot(filename)

        # converts file content from png to jpg
        im = Image.open(return_path)
        rgb_im = im.convert('RGB')
        rgb_im.save(return_path)

        return return_path


class WaitingExtensionKeywords(WaitingKeywords):

    @keyword
    def wait_until_location_is(self, expected, timeout=None, case_sensitive=True, message=None):
        """Waits until the current URL is ``expected``.

        Ignores case when ```case_sensitive``` is False (default is True).

        The ``expected`` argument is the expected value in url.

        Fails if ``timeout`` expires before the location is. See
        the `Timeouts` section for more information about using timeouts
        and their default value.

        The ``message`` argument can be used to override the default error
        message.

        New in SeleniumLibrary 4.0
        """

        current_url = self.driver.current_url().lower() if not case_sensitive \
            else self.driver.current_url
        expected_url = str(expected).lower() if not case_sensitive else str(expected)
        self._wait_until(lambda: expected_url == current_url,
                         "Location did not is '%s' in <TIMEOUT>." % expected,
                         timeout, message)


class JavaScriptExtensionKeywords(JavaScriptKeywords):

    @keyword
    def element_execute_javascript(self, locator, *code):
        """ Executes the given JavaScript code with possible arguments.

            Similar to `Execute Javascript` except that keyword accepts locator parameter
            and can use locator element in javascript command.

            ``code`` may be divided into multiple cells in the test data and
            ``code`` may contain multiple lines of code and arguments. In that case,
            the JavaScript code parts are concatenated together without adding
            spaces and optional arguments are separated from ``code``.

            If ``code`` is a path to an existing file, the JavaScript
            to execute will be read from that file. Forward slashes work as
            a path separator on all operating systems.

            The JavaScript executes in the context of the currently selected
            frame or window as the body of an anonymous function. Use ``window``
            to refer to the window of your application and ``document`` to refer
            to the document object of the current frame or window, e.g.
            ``document.getElementById('example')``.

            This keyword returns whatever the executed JavaScript code returns.
            Return values are converted to the appropriate Python types.

            Starting from SeleniumLibrary 3.2 it is possible to provide JavaScript
            [https://seleniumhq.github.io/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webdriver.html#selenium.webdriver.remote.webdriver.WebDriver.execute_script|
            arguments] as part of ``code`` argument. The JavaScript code and
            arguments must be separated with `JAVASCRIPT` and `ARGUMENTS` markers
            and must be used exactly with this format. If the Javascript code is
            first, then the `JAVASCRIPT` marker is optional. The order of
            `JAVASCRIPT` and `ARGUMENTS` markers can be swapped, but if `ARGUMENTS`
            is the first marker, then `JAVASCRIPT` marker is mandatory. It is only
            allowed to use `JAVASCRIPT` and `ARGUMENTS` markers only one time in the
            ``code`` argument.

            Examples:
            | `Execute JavaScript` | css=#id | | ${CURDIR}/js_to_execute.js | ARGUMENTS | 123 |

            Sample ${CURDIR}/js_to_execute.js file:

            ``arguments[0].value=arguments[1]``

            *SeleniumExtensionLibrary Only Keyword*.
        """

        element = self.find_element(locator)
        self.info("Element " + str(element))

        js_code, js_args = self._get_javascript_to_execute(code)
        actual_js_args = list()
        actual_js_args.append(element)
        actual_js_args += js_args
        self.info(f'Executing JavaScript {js_code}, {actual_js_args}')
        return self.driver.execute_script(js_code, *actual_js_args)


class SeleniumExtensionLibrary(SeleniumLibrary):
    # use the same doc as SeleniumLibrary
    __doc__ = "SeleniumExtensionLibrary is SeleniumLibrary extension.\n" + SeleniumLibrary.__doc__

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(self, timeout=5.0, implicit_wait=0.0, run_on_failure='Capture Page',
                 screenshot_root_directory=None, plugins=None, event_firing_webdriver=None):
        self.timeout = timestr_to_secs(timeout)
        self.implicit_wait = timestr_to_secs(implicit_wait)
        self.speed = 0.0
        self.run_on_failure_keyword \
            = RunOnFailureKeywords.resolve_keyword(run_on_failure)
        self._running_on_failure_keyword = False
        self.screenshot_root_directory = screenshot_root_directory
        self._element_finder = ElementFinder(self)
        self._plugin_keywords = []
        libraries = [
            AlertKeywords(self),
            BrowserManagementKeywords(self),
            CookieKeywords(self),
            ElementKeywords(self),
            FormElementKeywords(self),
            FrameKeywords(self),
            JavaScriptExtensionKeywords(self),
            RunOnFailureKeywords(self),
            ScreenshotExtensionKeywords(self),
            SelectElementKeywords(self),
            TableElementKeywords(self),
            WaitingExtensionKeywords(self),
            WindowKeywords(self)
        ]
        self.last_har = None
        self.ROBOT_LIBRARY_LISTENER = LibraryListener()
        self._running_keyword = None
        self.event_firing_webdriver = None
        if is_truthy(event_firing_webdriver):
            self.event_firing_webdriver = self._parse_listener(event_firing_webdriver)
        self._plugins = []
        if is_truthy(plugins):
            plugin_libs = self._parse_plugins(plugins)
            self._plugins = plugin_libs
            libraries = libraries + plugin_libs
        self._drivers = WebDriverCache()
        DynamicCore.__init__(self, libraries)

    @keyword
    def parse_url(self, url):
        """ Parse a url giving a string argument. Parse attributes are returned as dictionary.

            Query string data are also returned as a dictionary. The dictionary keys are the
            unique query variable names and the values are lists of values for each name.

            See https://docs.python.org/3/library/urllib.parse.html

            *SeleniumExtension Only Keywords*
        """
        parse_result = urlparse(url)

        result = dict(scheme=parse_result.scheme, host=parse_result.netloc,
                      path=parse_result.path, params=parse_result.params,
                      query_string=parse_result.query, query_params=parse_qs(parse_result.query))
        return result

    @keyword
    def kill_proxy_process(self):
        """ Searches for ``browsermob-proxy`` process running and kills it.

            See `Create HAR`  for complete instructions in generating HTTP Archive file.

            *SeleniumExtension Only Keyword*
        """
        for proc in psutil.process_iter():
            # check whether the process name matches
            try:
                print(proc.name())
                if proc.name() == "browsermob-proxy":
                    proc.kill()
            except OSError as error:
                print("OS error: {0}".format(error))

    @keyword
    def start_proxy_server(self, proxy_path, proxy_options):
        """ Prepare and start a proxy server and creates a proxy client using `BrowserMob Proxy`

            BrowserMob Proxy requires path and options as parameter when starting proxy server

            Example:
            | `Library` |  SeleniumExtensionLibrary |

            | `Kill Proxy Process` |
            | `Start Proxy Server` | proxy_path=${browsermobproxy}[path] |
            | ... | proxy_options=${browsermobproxy}[options] |
            | | |
            | `Stop Proxy Server` |

            where:
            - ``proxy_path`` is the path of BrowserMob Proxy application
            - ``proxy_options`` is the dictionary that holds the port
                - ex. { "options" : 8090 }

            See `Create HAR` for complete instructions in generating HTTP Archive file.

            *SeleniumExtension Only Keyword*
        """
        self.server = Server(path=proxy_path, options=proxy_options)
        self.server.start()
        self.proxy_client = self.server.create_proxy()

    @keyword
    def stop_proxy_server(self):
        """ Stops the proxy server

            See `Create HAR`  for complete instructions in generating HTTP Archive file.

            *SeleniumExtension Only Keyword*
        """
        self.server.stop()

    @keyword
    def get_proxy_server(self):
        """ Returns the proxy server set.

            Example:
            | `Start Proxy Server` | browsermobproxy_path=${browsermobproxy}[path] |
            | ... | browsermobproxy_options=${browsermobproxy}[options] |
            | ${proxy_server} | `Get Proxy Server` |

            See `Create HAR`  for complete instructions in generating HTTP Archive file.

            *SeleniumExtension Only Keywords*
        """
        proxy_server = urlparse(self.proxy_client.proxy).netloc
        return proxy_server

    @keyword
    def proxy_setup(self, desired_capabilities):
        """ Setup browser desired capabilty in proxy client. The same desire capability
            is also used in creating browser webdriver.

            `acceptSslCerts` and `acceptInsecureCerts` should be set to `True`

            Example:
            | `Kill Proxy Process` |
            | `Start Proxy Server` | proxy_path=${browsermobproxy}[path] |
            | ... | proxy_options=${browsermobproxy}[options] |
            | | |
            | Launch Website in Chrome |
            | | |
            | `Stop Proxy Server` |

            | *** Keywords *** |
            | Launch Website in Chrome |
            | | ${dc} | `Evaluate` | \
             sys.modules['selenium.webdriver'].DesiredCapabilities.CHROME | \
             sys, selenium.webdriver |
            | | `Set To Dictionary` | ${dc} | acceptSslCerts | ${True} |
            | | `Set To Dictionary` | ${dc} | acceptInsecureCerts | ${True} |
            | |
            | | # Sets the desired capability to the proxy client |
            | | `Proxy Setup` | ${dc} |
            | |
            | | # Sets the desired capability to the webdriver |
            | | `Create WebDriver` | Chrome | desired_capabilities=${dc} |

            See `Create HAR`  for complete instructions in generating HTTP Archive file.

            *SeleniumExtension Only Keyword*
        """
        self.proxy_client.add_to_capabilities(desired_capabilities)

    @keyword
    def create_har(self, title, captureHeaders=True, captureContent=True):
        """ Start request and marks the start of generating a new HTTP Archive (HAR) file.
            Defaults to capture header and contents.

            Introduction:

            `BrowserMob Proxy` allows you to manipulate HTTP requests and responses, capture HTTP
            content, and export performance data as a HAR file. To read more about
            `BrowserMob Proxy` see the following references:
            - https://github.com/lightbody/browsermob-proxy/
            - https://github.com/lightbody/browsermob-proxy/#using-with-selenium
            - https://readthedocs.org/projects/browsermob-proxy-py/downloads/pdf/latest/

            Setup requirements:
            - 1. BrowserMob Proxy installed in machine
            - 2. BrowserMob Proxy certificate set

            Usage:
            - BrowserMob Proxy requires path and options as parameter when starting proxy server
            - Sets the desired capability to the proxy client

            Example:
            | Library |  SeleniumExtensionLibrary |

            | `Kill Proxy Process` |
            | `Start Proxy Server` | proxy_path=${browsermobproxy}[path] |
            | ... | proxy_options=${browsermobproxy}[options] |
            | |
            | Launch Website in Chrome |
            | |
            | `Create HAR` | <har title> |
            | `Go To` | google.com |
            | `Generate HAR` | <filename> |
            | |
            | `Create HAR` | <har title> |
            | `Go To` | yahoo.com   |
            | `Generate HAR` | <filename> |
            | |
            | `Stop Proxy Server` |

            | *** Keywords *** |
            | Launch Website in Chrome |
            | | ${dc} | `Evaluate` | \
             sys.modules['selenium.webdriver'].DesiredCapabilities.CHROME | \
             sys, selenium.webdriver |
            | | `Set To Dictionary` | ${dc} | acceptSslCerts | ${True} |
            | | `Set To Dictionary` | ${dc} | acceptInsecureCerts | ${True} |
            | |
            | | # Sets the desired capability to the proxy client |
            | | `Proxy Setup` | ${dc} |
            | |
            | | # Sets the desired capability to the webdriver |
            | | `Create WebDriver` | Chrome | desired_capabilities=${dc} |

            where:
            - ``proxy_path`` is the path of BrowserMob Proxy application
            - ``proxy_options`` is the dictionary that holds the port
                - ex. { "options" : 8090 }

            *SeleniumExtension Only Keyword*
        """
        self.proxy_client.new_har(title, options={'captureHeaders': captureHeaders,
                                                  'captureContent': captureContent})

    @keyword
    def new_har_page(self, ref_name=None, title=None):
        """ This sets a new page to be recorded
            *SeleniumExtension Only Keyword*
        """
        self.proxy_client.new_page(ref_name, title)

    @keyword
    def generate_har(self, title):
        """ Generate and stores result in an HTTP Archive (*.har) file

            Returns the generated har in json format

            Example:
            | `Create HAR` | <har title> |
            | `Go To` | google.com |
            | ${generated_har_json} | `Generate HAR` | <filename> |

            See `Create HAR`  for complete instructions in generating HTTP Archive file.

            *SeleniumExtension Only Keyword*
        """
        self.last_har = self.proxy_client.har
        result = json.dumps(self.last_har, ensure_ascii=False)
        self._store_into_file(title, result)
        return result

    @keyword
    def get_har_page_load_time(self, pageref=None):
        """ Returns HAR elapsed page load time in milliseconds

            Example:
            | `Create HAR` | <har title> |
            | `Go To` | google.com |
            | ${harTime} | `Get Har Page Load Time` |

            *SeleniumExtension Only Keyword*
        """
        self.last_har = self.proxy_client.har
        assert self.last_har, "No HAR found"

        time = 0
        min_datetime = None
        max_datetime = None
        for entry in self.last_har['log']['entries']:
            if not pageref or entry['pageref'] == pageref:
                created_time = datetime.datetime.strptime(
                    entry['startedDateTime'][:-7], '%Y-%m-%dT%H:%M:%S.%f')
                end_time = created_time + datetime.timedelta(milliseconds=entry['time'])

                if not min_datetime:
                    min_datetime = created_time
                else:
                    min_datetime = min(created_time, min_datetime)

                if not max_datetime:
                    max_datetime = end_time
                else:
                    max_datetime = max(end_time, max_datetime)

        # make sure we have computed the minimum date time from created time.
        # and max_datetime will be the maximum end date time.
        assert min_datetime and max_datetime, \
            'Unable to retrieve minimum created time and maximum end time.'

        return (max_datetime - min_datetime).microseconds / 1000

    @keyword
    def get_har_transferred_file_size(self):
        """ Returns total har transferred file size

            Example:
            | `Create HAR` | <har title> |
            | `Go To` | google.com |
            | ${harSize} | `Get Har Transferred File Size` |

            *SeleniumExtension Only Keyword*
        """
        self.last_har = self.proxy_client.har
        assert self.last_har, "No HAR found"

        size = 0
        for entry in self.last_har['log']['entries']:
            size = size + entry['response']['bodySize']

        return size

    @staticmethod
    def _store_into_file(title, result):
        """ Store result """
        har_file = open(title + '.har', 'w')
        har_file.write(str(result))
        har_file.close()


# use the same documentation as SeleniumLibrary
SeleniumExtensionLibrary.__init__.__doc__ = SeleniumLibrary.__init__.__doc__
