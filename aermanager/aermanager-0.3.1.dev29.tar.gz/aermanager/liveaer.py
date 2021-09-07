"""
'liveaer' module contains the implementation of Class LiveDv, interfaces with the DV live
datastream.
"""
import multiprocessing as mp
from queue import Full, Empty
import numpy as np
from dv import NetworkFrameInput


class LiveDv:
    """
    Class for interfacing with the DV live datastream. The stream is
    supposed to be broadcasting accumulated frames. An independent
    thread reads the DV stream and saves it in a queue, from which
    batches can be obtained. Events may be dropped if the queue is full.

    :param host: The host transmitting the data.
    :param port: The port from which to read the data.
    :param qlen: The  queue length.
    :param print_qsize: If True, prints the queue length.
    :param check_input_dims: If True, requires the input to be 2-dimensional.
    """

    def __init__(
        self, host="localhost",
        port=7777,
        qlen=256,
        print_qsize=False,
        two_channel_mode=False,
        check_input_dims=True,
    ):
        self.nfi = NetworkFrameInput(address=host, port=port)
        self.q = mp.Queue(maxsize=qlen)
        self.qlen = qlen
        self.print_qsize = print_qsize
        self.two_channel_mode = two_channel_mode
        self.check_input_dims = check_input_dims

        self._start_threads()

    def _start_threads(self):
        t1 = mp.Process(target=self._build_q,)

        t1.daemon = True
        t1.start()

    def _build_q(self):
        while True:
            frame = next(self.nfi).image.squeeze()
            if self.check_input_dims:
                assert len(frame.shape) == 2, "The frame is 3-dimensional. Perhaps deactivate color?"
            try:
                self.q.put_nowait(frame)
            except Full:
                self.q.get()
                self.q.put_nowait(frame)

    def get_batch(self):
        """
        Read a batch from the queue, drop it from the queue and return it.
        The batch includes everything currently in the queue.
        """
        first_frame = self.q.get()
        batch = np.empty((self.qlen, *first_frame.shape))

        batch[0] = first_frame

        i = 0  # necessary if qlen = 1
        for i in range(1, self.qlen):
            try:
                batch[i] = self.q.get()
            except Empty:
                break

        if self.print_qsize:
            print("Queue length:", self.q.qsize())

        batch = batch[: i + 1]

        if self.two_channel_mode:
            idx = batch >= 128
            twochan_batch = np.zeros((len(batch), 2, *first_frame.shape))
            twochan_batch[:, 0][~idx] = 128 - batch[~idx]
            twochan_batch[:, 1][idx] = batch[idx] - 128
            return twochan_batch
        else:
            return batch[:, np.newaxis]
