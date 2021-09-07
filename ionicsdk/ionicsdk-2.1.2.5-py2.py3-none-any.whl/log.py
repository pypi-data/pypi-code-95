"""!Logger configuration."""

import ionicsdk._private as _private

class ISLog:
    """!Defines the different ways to configure SDK logging.

    ==========================
    Available severity levels:
    ==========================

    SEV_INVALID                     -1
    Represents an invalid/unknown log severity level.

    SEV_TRACE                       0
    Represents TRACE level log severity.

    SEV_DEBUG                       1
    Represents DEBUG level log severity.

    SEV_INFO                        2
    Represents INFO level log severity.

    SEV_WARN                        3
    Represents WARN level log severity.

    SEV_ERROR                       4
    Represents ERROR level log severity.

    SEV_FATAL                       5
    Represents FATAL level log severity.
    """

## \brief	Represents an invalid/unknown log severity level.
SEV_INVALID = -1

## \brief	Represents TRACE level log severity.
SEV_TRACE = 0

## \brief	Represents DEBUG level log severity.
SEV_DEBUG = 1

## \brief	Represents INFO level log severity.
SEV_INFO = 2

## \brief	Represents WARN level log severity.
SEV_WARN = 3

## \brief	Represents ERROR level log severity.
SEV_ERROR = 4

## \brief	Represents FATAL level log severity.
SEV_FATAL = 5

## \brief   Name of the log channel for python-specific logging
PYTHON_LOG_CHANNEL = "ISPython"


def setup_simple(outputLogFile, append, severityLevel):
    """!Sets up SDK logging to write to the specified file path.  If the file does not exist, it will be created.
		 To achieve more fine grained control over the logger, its output mechanism(s), etc. refer to
		 setup_from_config_file() and setup_from_config_json().

    Example:\n
        ionicsdk.log.setup_simple("log.txt", False, ionicsdk.log.SEV_DEBUG)\n\n

    Available severity levels:
    - SEV_INVALID                     -1
    - SEV_TRACE                       0
    - SEV_DEBUG                       1
    - SEV_INFO                        2
    - SEV_WARN                        3
    - SEV_ERROR                       4
    - SEV_FATAL                       5

    @param
        outputLogFile (string): The output file path to log to. If the file does not exist, it will be created.
    @param
        append (bool): If set to true, the log file will be appended to if it already exists.
            Otherwise, the log file will be overwritten and any existing data at the specified path will effectively be erased.
    @param
        severityLevel (int): Specifies how detailed the logging will be - SEV_TRACE and SEV_FATAL are the most
            detailed and the least detailed levels, respectively.
            
    @return
        None
    """
    _private.cLib.ionic_log_setup_simple(_private.CMarshalUtil.stringToC(outputLogFile), append, severityLevel)

def setup_from_config_json(configJson, baseFileWriterPath=None):
    """!Sets up SDK logging using the specified JSON-formatted configuration string.

    Example: 
        ionicsdk.log.setup_from_config_json({ "sinks":  [ {
            "channels": [ "*" ],

            "filter": { "type": "Severity",
                        "level": "INFO" },

            "writers": [
                         { "type": "Console" },

                         { "type": "RotatingFile",
                           "filePattern": "ionic_ie_%Y-%m-%d_%H-%M-%S.log",
                           "rotationSchedule": "DAILY",
                           "rotationSize": "100mb" }
                       ]
          },

          {
            "channels": [ "MyModuleName" ],

            "filter": { "type": "Severity",
                        "level": "TRACE" },

            "writers": [
                        { "type": "File",
                          "filePattern": "ionic_http_trace_%Y-%m-%d_%H-%M-%S.log" }
                     ]
          } ] }, "/home/base/path")
          
          See \ref islogconfig for full documentation on the supported JSON configuration format.
    @param
        configJson (string): The log configuration JSON-formatted string.
    @param
        baseFileWriterPath (string, optional): If specified, this path will be prepended to any relative file paths found
            in the logger configuration. Otherwise, the base path defaults to the current working directory.

    @return
        None
    """
    _private.cLib.ionic_log_setup_from_config_json(
        _private.CMarshalUtil.stringToC(configJson),
        _private.CMarshalUtil.stringToC(baseFileWriterPath))

def setup_from_config_file(configFile, baseFileWriterPath=None):
    """!@details
        Sets up logging using the provided JSON formatted configuration file.

        Example:
            ionicsdk.log.setup_from_config_file("config.json", "home/base/path")

        See \ref islogconfig for full documentation on the supported JSON configuration format.
    @param
        configFile (string): The log configuration JSON-formatted file.
    @param
        baseFileWriterPath (string, optional): If specified, this path will be prepended to any relative file paths found
            in the logger configuration. Otherwise, the base path defaults to the current working directory.
        
    @return
        None
    """
    _private.cLib.ionic_log_setup_from_config_file(
        _private.CMarshalUtil.stringToC(configFile),
        _private.CMarshalUtil.stringToC(baseFileWriterPath))


class CustomLogger(object):
    """!Logger Custom Class for capturing some portion (or all) logging in the Python code. You can either simply 
    create a simple logger, which sends all logs at or above a severity to your derived custom logger instance.
    Or, you can register this instance with the logger library and then completely config things using a JSON 
    file.  With this method, you can create multiple Python instances and separate log output by channel.
    
    To use this class, you must derive your own version in which you implement the log(self, logText, severity)
    method.
    """
    
    def __init__(self):
        """!Base class constructor for a custom logger.
        """
        self._logCallback = None
    
    def register(self, loggerName):
        """! Register this logger instance with the logging library and make it available to JSON configured setups.
        
        @param
            loggerName (unicode string): The reference name of the logger that will be used in the JSON configuration file.

        @return
            None
        """
        if self._logCallback is None:
            self._createCallback()
        
        cLogLabel = _private.CMarshalUtil.stringToC(loggerName)
        _private.cLib.ionic_log_register_logger_from_callback(self._logCallback, cLogLabel)

    def createSimpleLogger(self, severity):
        """! Sets up logging to call the log() method of this instance with any log message of severity or greater.
            
        @param
            severity (int): Minimum severity for this logger. Log messages with a lower severity are filtered out.

        @return
            None
        """
        if self._logCallback is None:
            self._createCallback()

        _private.cLib.ionic_log_setup_from_callback(self._logCallback, severity)

    def _createCallback(self):
        """!Call this to enable callbacks to the SyncKeys method.  If this is called from a class implementation
            without a SyncKeys override, then the base class will raise an exception on the first call to Sync()
            
            @return
            None
            """
        def cb_log(cSeverity, cLogText):
            try:
                logText = _private.CMarshalUtil.stringFromC(cLogText)
                self.log(cSeverity, logText)
                return 0
            except AttributeError:
                return -1

        self._logCallback = _private.LogCallback(cb_log)

    def log(self, severity, logtext):
        """!Called whenever this logger gets a new log line.  You must sub class and override this method to use this.

        @param
            severity (int): Specifies how detailed the logging will be - SEV_TRACE and SEV_FATAL are the most
                detailed and the least detailed levels, respectively.
        
        @param
            logtext (unicode string): Formatted text of the log line to record.
        
        @return
        (int) 0 if the log text is recorded, -1 if it is filtered out (possibly due to severity too low).
        """
        raise Exception("You must sub-class and implement this method!")


def is_setup():
    """!Determines if the Ionic logger has been set up.
        
    @return
        True if the Ionic logger is set up and ready to use. Otherwise, returns false.
    """
    return _private.cLib.ionic_log_is_setup()

def shutdown():
    """!Shuts down the Ionic logger.
                 If the logger is not already set up, then this function does nothing.
                 Otherwise, it shuts down the logger and releases all associated resources (file handles, memory).
                 
    @return
        None
    """
    _private.cLib.ionic_log_shutdown()

def log(severity, channelName, lineNumber, fileName, message):
    """!@details
        Writes the specified message to the Ionic logger.

        Available severity levels:
        - SEV_INVALID                     -1
        - SEV_TRACE                       0
        - SEV_DEBUG                       1
        - SEV_INFO                        2
        - SEV_WARN                        3
        - SEV_ERROR                       4
        - SEV_FATAL                       5
    
    @param
        severity (int): Specifies how detailed the logging will be - SEV_TRACE and SEV_FATAL are the most 
                 detailed and the least detailed levels, respectively.
    @param
        channelName (string): The channel name is an arbitrary string that may be used by the logger
                 to perform custom/configurable message routing.
    @param
        lineNumber (int): The line number in the source file associated with the log message.
    @param
        fileName (string, optional): The source file name associated with the log message.
                 This parameter is optional so the empty string "" is an acceptable input.
    @param
        message (string): The log message string.

    @return
        None
    """
    _private.cLib.ionic_log(severity,
        _private.CMarshalUtil.stringToC(channelName),
        lineNumber,
        _private.CMarshalUtil.stringToC(fileName),
        _private.CMarshalUtil.stringToC(message))
