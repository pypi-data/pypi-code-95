# This class is basically only need that original HepMC readers comply with Reader API

from pyHepMC3 import HepMC3 as hm

class HepMCReader:
    def __init__(self, evt=None, reader_version=3):

        self.event = evt if evt else hm.GenEvent(hm.Units.GEV, hm.Units.MM)
        self.reader_version = reader_version
        self.reader = None

    def open(self, file_name):
        # opens a file with file_name
        if self.reader_version == 2:
            self.reader = hm.ReaderAsciiHepMC2(file_name)
        else:
            self.reader = hm.ReaderAscii(file_name)

    def events(self, nskip: int = 0, ntake: int = 0):

        if self.reader is None:
            raise RuntimeError("HepMCReader file is not opened")

        event_index = 0

        while not self.reader.failed():
            self.event.clear()

            self.reader.read_event(self.event)
            if self.reader.failed():
                break

            # Should we skip the event?
            if nskip <= event_index:

                # Select the event
                yield self.event

                # Should we break?
                if ntake and ntake + nskip == event_index + 1:
                    return

            event_index += 1

    def close(self):
        # closes the file.
        if self.reader is not None:
            self.reader.close()
