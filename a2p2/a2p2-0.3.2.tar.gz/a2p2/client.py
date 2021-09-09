#!/usr/bin/env python

__all__ = ['A2p2Client']

import time
import traceback
import os
import configparser
import logging

from a2p2 import __version__
from a2p2.facility import FacilityManager
from a2p2.gui import MainWindow
from a2p2.ob import OB
from a2p2.samp import A2p2SampClient
from a2p2.vlti.facility import VltiFacility


# prepare global logging
a2p2Rootlogger = logging.getLogger("a2p2")
a2p2Rootlogger.setLevel(logging.INFO)
# uncomment next two lines to log requests done by p2api and maybe other ones...
#a2p2Rootlogger = logging.getLogger()
#a2p2Rootlogger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter(
    '%(levelname)s - %(name)s  - %(asctime)s - %(filename)s:%(lineno)d - %(message)s')
console.setFormatter(consoleFormatter)
a2p2Rootlogger.addHandler(console)

logger = logging.getLogger(__name__)


class A2p2Client():
    """Transmit your Aspro2 observation to remote Observatory scheduling database.

       with A2p2Client() as a2p2:
           a2p2.run()
           ..."""

    def __init__(self, fakeAPI=False, verbose=False):
        """Create the A2p2 client."""

        self.preferences = A2P2ClientPreferences()

        self.apiName = ""
        if fakeAPI:
            self.apiName = "fakeAPI"
        self.fakeAPI = fakeAPI

        if verbose:
            a2p2Rootlogger.setLevel(logging.DEBUG)

        self.ui = MainWindow(self)
        # Instantiate the samp client and connect to the hub later
        self.a2p2SampClient = A2p2SampClient()
        self.facilityManager = FacilityManager(self)

        if self.preferences.exists():
            pass
        else:
            self.ui.addToLog(
                "No preference file found, please create one so your data persists (launch program with -c option).\n\n")

        self.errors = []

        pass

    def __enter__(self):
        """Handle starting the 'with' statements."""

        self.ui.addToLog("              Welcome in the A2P2 V" + __version__)
        self.ui.addToLog("")
        self.ui.addToLog("( https://github.com/JMMC-OpenDev/a2p2/wiki )")

        return self

    def __del__(self):
        """Handle deleting the object."""
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """Handle closing the 'with' statement."""
        del self.a2p2SampClient
        del self.ui
        # TODO close the connection to the obs database ?

        # WARNING do not return self only. Else exceptions are hidden
        # return self

    def __str__(self):
        instruments = "\n- ".join(["Supported instruments:", "TBD"])
        apis = "\n- ".join(["Supported APIs:", "TBD"])
        return """a2p2 client\n%s\n%s\n""" % (instruments, apis)

    def changeSampStatus(self, connected_flag):
        self.sampConnected = connected_flag

    def setProgress(self, perc, actionName=None):
        if actionName:
            print("%s action progress is  %s" % (actionName, perc))
        else:
            print("progress is  %s %%" % (perc))

    def clearErrors(self):
        self.errors.clear()

    def getErrors(self):
        return self.errors

    def addError(self, error):
        self.errors.append(error)

    def processOB(self, ob):
        self.facilityManager.processOB(ob)

    def run(self):
        # bool of status change
        flag = [0]

        logger.info("Running client ...")

        # handle autologin
        if self.preferences.getP2AutoLoginBoolean():
            logger.debug("Autologin using '%s' file" %
                         A2P2ClientPreferences.getPreferencesFileName())
            self.ui.loop()
            vltifacility = self.facilityManager.facilities.get(
                VltiFacility.getName())
            vltifacility.autologin()

        # We now run the loop to wait for the message in a try/finally block so that if
        # the program is interrupted e.g. by control-C, the client terminates
        # gracefully.

        # We test every 1s to see if the hub has sent a message
        delay = 0.1
        each = 10
        loop_cnt = 0
        warnForAspro = True

        while loop_cnt >= 0:
            try:
                loop_cnt += 1
                time.sleep(delay)

                self.ui.loop()

                if not self.a2p2SampClient.is_connected() and loop_cnt % each == 0:
                    try:
                        self.a2p2SampClient.connect()
                        self.ui.setSampId(self.a2p2SampClient.get_public_id())
                    except:
                        self.ui.setSampId(None)
                        if warnForAspro:
                            warnForAspro = False
                            self.ui.addToLog(
                                "\nPlease launch Aspro2 to submit your OBs.")
                        # TODO test for other exception than SAMPHubError(u'Unable to find a running SAMP Hub.',)
                        pass

                if self.a2p2SampClient.has_message():
                    try:
                        ob = OB(self.a2p2SampClient.get_ob_url())
                        self.facilityManager.processOB(ob)
                    except:
                        self.ui.addToLog(
                            "Exception during ob creation: " + traceback.format_exc(), False)
                        self.ui.addToLog("Can't process last OB")

                    # always clear previous received message
                    self.a2p2SampClient.clear_message()

                if self.ui.requestAbort:
                    loop_cnt = -1
            except KeyboardInterrupt:
                loop_cnt = -1

    def createPreferencesFile():
        A2P2ClientPreferences.createPreferencesFile()


class A2P2ClientPreferences():
    # define application name
    appname = "a2p2"

    def __init__(self):
        self._config = A2P2ClientPreferences.getPreferences()
        pass

    def exists(self):
        if self._config.sections():
            return True
        else:
            return False

    def getPreferences():
        preferences_file = A2P2ClientPreferences.getPreferencesFileName()
        config = configparser.ConfigParser()
        config.read(preferences_file)
        return config

    def getPreferencesFileName():
        from appdirs import user_config_dir
        preferences_file = os.path.join(user_config_dir(
            A2P2ClientPreferences.appname), "prefs.ini")
        return preferences_file

    def createPreferencesFile():
        filename = A2P2ClientPreferences.getPreferencesFileName()

        if os.path.exists(filename):
            print("%s already exists. Nothing done" % filename)
        else:
            config = configparser.ConfigParser()
            #config['DEFAULT'] = {'_noprefyet': '42'}
            config['p2'] = {}
            import getpass
            config['p2']['# = > please uncomment and update next properties to make it active <'] = ""
            config['p2']['#username'] = getpass.getuser()
            config['p2']['#password'] = "12345zZ"
            config['p2']['#user_comment_name'] = "changed it if your local USER name is not fine"
            config['p2']['#autologin'] = "yes"

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w+') as configfile:
                config.write(configfile)

            print("%s template created. Please adjust." % filename)

    def getConfig(self, section, key, default=None):
        try:
            return self._config[section][key]
        except:
            return default

    def getConfigBoolean(self, section, key, default=None):
        try:
            return self._config.getboolean(section, key)
        except:
            return default

    # retrieve P2 username in config or use default demo account

    def getP2Username(self):
        return self.getConfig("p2", "username", '52052')

    # retrieve P2 password in config or use default demo account
    def getP2Password(self):
        return self.getConfig("p2", "password", 'tutorial')

    def getP2UserCommentName(self):
        import getpass
        return self.getConfig("p2", "user_comment_name", getpass.getuser())

    def getP2AutoLoginBoolean(self):
        return self.getConfigBoolean("p2", "autologin", False)


