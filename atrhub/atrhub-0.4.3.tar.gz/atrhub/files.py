import os
from datetime import datetime
from pathlib import Path
from gestionatr.input.messages import message as gestionatr
from collections import namedtuple
import re

FILE_EXTENSION = '.xml'

Queue = namedtuple('Queue', ['incoming', 'outgoing'])
QUEUE_TYPES = Queue('Entrada', 'Salida')
FOLDERS_TO_PROCESS = [
    QUEUE_TYPES.outgoing,
]

# Prepare logging
import logging
execution_date = datetime.now().isoformat()[:19] #2019-01-14T16:12:45
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

loggers = {}

def setup_logger(name, filename, level=logging.INFO, mode="w"):
    """
    Setup a logger!
    """
    assert mode in ["w", "a"], "Provided mode '{}' is not avaiblable: '{}'".format(mode, ["w", "a"])
    l = logging.getLogger(name)
    fileHandler = logging.FileHandler(filename, mode=mode)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)
    return True

def log(path, what, level="info"):
    # Just setup new logger if needed
    if not path in loggers:
        loggers[path] = setup_logger(name=path, filename="{}/{}.log".format(path, execution_date))

    for a_log in ['global', path]:
        logger = logging.getLogger(a_log)
        new_log_entry = {
            "info": logger.info,
            "warn": logger.warn,
            "error": logger.error,
            "debug": logger.debug,
        }.get(level, logger.info)

        # Hide paths except for global log
        if a_log != "global":
            for filename_to_clean in re.findall(r"([^']+\.xml|bad|error)+", what):
                filename_cleaned = '/'.join(Path(filename_to_clean).parts[-3:])
                what = re.sub(filename_to_clean, filename_cleaned, what)

        # Log it!
        new_log_entry(what)


class ATRFile(object):
    def __init__(self, path):
        assert type(path) == str, type(path)
        self._path = Path(path)
        self.content = self._parse()

    def _parse(self):
        try:
            with open(self.path, 'r') as xml_file:
            # with self._path.open('r') as xml_file:
                data = xml_file.read()
                m = gestionatr.Message(data)
                m.parse_xml()
                return m
        except Exception as e:
            # Log the exception
            log(path=str(self._path.parent),
                what="ERROR001 - File '{filename}' can't be parsed: \"{e}\"".format(
                                                       filename=self.path, e=e),
                level="error"
            )
            self.rename("{}.bad".format(self.path))
            return False

    def validate(self):
        """
        Validate file using `gestionatr` lib
        """
        if not self.content:
            return False

        try:
            # Validate that qeueue is enabled
            assert self.qeueue in FOLDERS_TO_PROCESS, "Current folder '{}' is not valid ('{}')".format(self.qeueue, FOLDERS_TO_PROCESS)

            # Validate origin ()
            assert self.owner == self.origin, "is not accepted, file uploaded to '{}' queue, but the defined emitter inside XML is '{}'".format(self.owner, self.origin)
            #assert self.destination in self.destination, "File '{}' is not accepted, wrong destinatary inside XML '{}'".format(self.owner, self.origin)

            return True
        except Exception as e:
            # Log the exception
            log(path=str(self._path.parent),
                what="ERROR002 - File '{filename}' can't be validated: \"{e}\"".format(
                                                       filename=self.path, e=e),
                level="error"
            )
            self.rename("{filename}.error".format(filename=self.path))
            return False

    def rename(self, name):
        self._path.rename(name)

        log(path=str(self._path.parent),
            what="Moving file '{current}' to '{new}'".format(current=self.path,
                                                             new=name),
            level="info"
        )

        return True

    def deliver(self):
        """
        Moves the file to the expected path based on the destination defined
        inside the file

        If validations are not asserted just rename the extension to identify
        the error
        """
        # ../../$destination/$salida
        deliver_path = self._path.parent.parent.parent / self.destination / Path(QUEUE_TYPES.incoming)

        # ../../$destination/$salida/$filename
        destination_file = deliver_path / self._path.name

        # If does not exist, create it
        if not deliver_path.exists():
            log(path=str(self._path.parent),
                what="ERROR003 - File '{}' is not accepted, wrong destinatary inside XML \"{}\"".format(self.path, self.destination),
                level="error"
            )
            self.rename("{filename}.error".format(filename=self.path))
            return False

        try:
            return self.rename(destination_file)
        except:
            log(path=str(self._path.parent),
                what="ERROR004 - File '{}' is accepted, but can't be delivered (probably due to lack of permissions to deliver to queue \"{}\")".format(self.path, self.destination),
                level="error"
            )
            self.rename("{filename}.error".format(filename=self.path))
            return False
            

    def process(self):
        """
        Validate and deliver a file

        If not validates it handles the error:
        - if emitter and queue does not match (from stored path and file contents),
        append ".error" extension
        - if gestionatr lib does not validate it, append ".bad" extension
        """
        validated = self.validate()
        if not validated:
            return False

        delivered = self.deliver()
        if not delivered:
            self.rename("{filename}.error".format(filename=self.path))
            return False

        return True


    @property
    def path(self):
        """
        String version of file path
        """
        return str(self._path)

    @property
    def origin(self):
        """
        The origin defined inside the XML
        """
        return self.content.get_codi_emisor

    @property
    def destination(self):
        """
        The destination defined inside the XML
        """
        return self.content.get_codi_destinatari

    @property
    def owner(self):
        """
        The current owner based on file path
        """
        return self._path.parents[1].parts[-1]

    @property
    def qeueue(self):
        """
        The current qeueue based on file path
        """
        return self._path.parents[0].parts[-1]



class ATRFiles(object):
    def __init__(self, path, follow_links=False, global_log="/home/atrhub/atrhub.log"):
        loggers['global'] = setup_logger(name='global', filename=global_log, mode="a")
        assert type(path) == str
        assert type(follow_links) == bool
        assert os.path.isdir(path), "'{}' does not exist or is not a directory".format(path)
        self.path = path
        self.follow_links = follow_links

    def walk(self, follow_links=None):
        """
        Returns current list of files
        """
        # If follow links is not overrided, use configured value
        if follow_links == None:
            follow_links = self.follow_links

        # All files with FILE_EXTENSION inside an outgoing queue
        files_list = Path(self.path).glob(
            "**/{queue}/*{extension}".format(queue=QUEUE_TYPES.outgoing,
                                             extension=FILE_EXTENSION))

        # Return all string filenames
        res = [str(filename) for filename in files_list]

        files_list = Path(self.path).glob(
                "**/{queue}/*{extension}".format(queue=QUEUE_TYPES.outgoing,
                    extension=FILE_EXTENSION.upper()))
        res2 = [str(filename) for filename in files_list]
        return res + res2

    def deliver(self):
        """
        Deliver files based on their Header definition
        """
        for a_file in self.walk():
            try:
                ATRFile(a_file).process()
            except:
                pass
        return True
