import os
import time
import glob

from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import (
    FileCreatedEvent,
    FileModifiedEvent
)


class FITSWriteHandler(PatternMatchingEventHandler):
    """
    Class to handle FITS write events.abs

    Upon write events to the current run, we send offset to
    the telescope, schedule callbacks to see if the
    offset is complete, and then send a trigger to the
    sequencer to continue with the observation.

    Arguments
    ----------
    path : str
        location of fits files to monitor
    """
    patterns = ['*.fits']

    def __init__(self, path, on_modified_callback, *args, **kwargs):
        super(FITSWriteHandler, self).__init__()
        self.path = path
        self.on_modified_callback = on_modified_callback
        try:
            pattern = os.path.abspath(os.path.join(self.path, self.patterns[0]))
            self.existing_runs = glob.glob(pattern)
        except Exception:
            self.existing_runs = []

        # used to avoid responding to very recent
        # events which may be duplicates.
        self.debounce_time = 0.1
        self.last_event = 0

    def check_debounce(self):
        """
        Avoid handling very closely occurring filesystem events.abs

        Sometimes there are two or more rapid filesystem events when
        a frame is written. This routine checks if another event
        as happened recently, and returns False if so.
        """
        first_event = False
        if time.time() - self.last_event > self.debounce_time:
            self.last_event = time.time()
            first_event = True
        else:
            self.last_event = time.time()
        return first_event

    def on_modified(self, event):
        if self.check_debounce():
            if os.path.abspath(event.src_path) == self.existing_runs[-1]:
                # latest file has just been written to
                self.on_modified_callback()

    def on_created(self, event):
        self.check_debounce()
        # if we don't know about this, it's a new run.
        if os.path.abspath(event.src_path) not in self.existing_runs:
            self.existing_runs.append(event.src_path)
            # log to window
            run_file = os.path.split(event.src_path)[-1]
            run_name = os.path.splitext(run_file)[0]
            print('HiPERCAM is observing new run: {}'.format(run_name))


class FITSWatcher(object):

    def __init__(self, path, on_modified_callback):
        self.path = path
        self.handler = FITSWriteHandler(self.path, on_modified_callback)
        self._snapshot = self.take_snapshot()

    def take_snapshot(self):
        return DirectorySnapshot(self.path, recursive=False)

    def poll(self):
        new_snapshot = self.take_snapshot()
        events = DirectorySnapshotDiff(self._snapshot, new_snapshot)
        self._snapshot = new_snapshot

        # process file creation and modified events only
        for src_path in events.files_created:
            self.queue_event(FileCreatedEvent(src_path))
        for src_path in events.files_modified:
            self.queue_event(FileModifiedEvent(src_path))

    def queue_event(self, event):
        self.handler.dispatch(event)
