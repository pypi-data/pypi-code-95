import wave
import time
import logging
import threading
import collections

DEFAULT_AUDIO_SAMPLE_RATE = 16000
DEFAULT_AUDIO_SAMPLE_WIDTH = 2
DEFAULT_AUDIO_DEVICE_BLOCK_SIZE = 6400
DEFAULT_AUDIO_DEVICE_FLUSH_SIZE = 25600
DEFAULT_AUDIO_CHANNELS = 1

class WaveSource:
    def __init__(self, fp, sample_rate = DEFAULT_AUDIO_SAMPLE_RATE, sample_width = DEFAULT_AUDIO_SAMPLE_WIDTH, mimic = True, pad_silent = 0):
        self._fp = fp
        try:
            self._wavep = wave.open(self._fp, 'r')
        except wave.Error as e:
            logging.warning('error opening WAV file: %s, '
                            'falling back to RAW format', e)
            self._fp.seek(0)
            self._wavep = None
        self._sample_rate = sample_rate
        self._sample_width = sample_width
        self._sleep_until = 0
        self._mimic = mimic
        self._silence = pad_silent

    def read(self, size):
        now = time.time()
        missing_dt = (self._sleep_until - now)
        if self._mimic and missing_dt > 0:
            time.sleep(missing_dt)
        self._sleep_until = time.time() + self._sleep_time(size)
        data = (self._wavep.readframes(size // self._sample_width)
                if self._wavep
                else self._fp.read(size))

        if not data:
            self._silence -= size
            if self._silence <= 0:
                return b''
            return b'\x00' * size

        if len (data) < size:
            return data + (b'\x00' * (size - len (data)))
        return data

    def write(self, data):
        self._wavep.writeframes(data)

    def close(self):
        if self._wavep:
            self._wavep.close()
        self._fp.close()

    def start (self):
        pass

    def stop(self):
        pass

    def _sleep_time(self, size):
        sample_count = size / float(self._sample_width)
        sample_rate_dt = sample_count / float(self._sample_rate)
        return sample_rate_dt

    def flush(self):
        pass

    @property
    def sample_rate(self):
        return self._sample_rate


try:
    import sounddevice as sd
except ImportError:
    pass

class SoundDeviceStream (WaveSource):
    def __init__(self, sample_rate = DEFAULT_AUDIO_SAMPLE_RATE, sample_width = DEFAULT_AUDIO_SAMPLE_WIDTH, block_size = DEFAULT_AUDIO_DEVICE_BLOCK_SIZE, flush_size = DEFAULT_AUDIO_DEVICE_FLUSH_SIZE, device = None, channels = DEFAULT_AUDIO_CHANNELS):
        try:
            sd
        except NameError:
            raise Exception('sounddevice is not installed, use pip')

        if sample_width == 2:
            audio_format = 'int16'
        else:
            raise Exception('unsupported sample width:', sample_width)
        self._audio_stream = sd.RawStream(
            samplerate=sample_rate, dtype=audio_format, channels=channels, device = device,
            blocksize=int(block_size/2),  # blocksize is in number of frames.
        )
        self._channels = channels
        self._sample_width = sample_width
        self._block_size = block_size
        self._flush_size = flush_size
        self._sample_rate = sample_rate

    def read(self, size):
        size = size // self._sample_width # to bytes length
        buf, overflow = self._audio_stream.read(size)
        if overflow:
            logging.warning('SoundDeviceStream read overflow (%d, %d)', size, len(buf))
        return bytes(buf)

    def write(self, buf):
        underflow = self._audio_stream.write(buf)
        if underflow:
            logging.warning('SoundDeviceStream write underflow (size: %d)', len(buf))
        return len(buf)

    def flush(self):
        if self._audio_stream.active and self._flush_size > 0:
            self._audio_stream.write(b'\x00' * self._flush_size)

    def start(self):
        if not self._audio_stream.active:
            self._audio_stream.start()

    def stop(self):
        if self._audio_stream.active:
            self._audio_stream.stop()

    def close(self):
        if self._audio_stream:
            self.stop()
            self._audio_stream.close()
            self._audio_stream = None


class SoundDeviceInputStream(SoundDeviceStream):
    def __init__(self, sample_rate = DEFAULT_AUDIO_SAMPLE_RATE, sample_width = DEFAULT_AUDIO_SAMPLE_WIDTH, block_size = DEFAULT_AUDIO_DEVICE_BLOCK_SIZE, flush_size = DEFAULT_AUDIO_DEVICE_FLUSH_SIZE, device = None):
        if sample_width == 2:
            audio_format = 'int16'
        else:
            raise Exception('unsupported sample width:', sample_width)
        self._audio_stream = sd.RawInputStream(
            samplerate=sample_rate, dtype=audio_format, channels=1, device = device,
            blocksize=int(block_size/2),  # blocksize is in number of frames.
        )
        self._sample_width = sample_width
        self._block_size = block_size
        self._flush_size = flush_size
        self._sample_rate = sample_rate


class VirtualDevice:
    def __init__ (self, sample_rate, sample_width, block_size):
        self._sample_rate = sample_rate
        self._sample_width = sample_width
        self._block_size = block_size

        self._lock = threading.Condition ()
        self._stopped = False
        self._streams = collections.deque (maxlen = 16)

    def put (self, stream):
        with self._lock:
            self._streams.append (stream)
            self._lock.notify ()

    def read (self, size):
        with self._lock:
            if self._stopped:
                raise IOError ('closed input stream')
            while not self._stopped and (not self._streams or sum ([len (s) for s in self._streams]) < size):
                self._lock.wait ()
            if self._stopped:
                return b''
            data = b''
            while 1:
                first = self._streams.popleft ()
                if len (data) + len (first) < size:
                    data += first
                else:
                    wanted = size - len (data)
                    data += first [:wanted]
                    self._streams.appendleft (first [wanted:])
                    break
            assert len (data) == size
        return data

    def start(self):
        with self._lock:
            self._stopped = False
            self._lock.notify ()

    def stop (self):
        with self._lock:
            self._stopped = True
            self._lock.notify ()

    def close (self):
        self.stop ()

    def write(self, buf): raise AttributeError
    def flush(self): raise AttributeError


class ClonableSoundDeviceInputStream (SoundDeviceInputStream):
    def __init__(self, sample_rate = DEFAULT_AUDIO_SAMPLE_RATE, sample_width = DEFAULT_AUDIO_SAMPLE_WIDTH, block_size = DEFAULT_AUDIO_DEVICE_BLOCK_SIZE, flush_size = DEFAULT_AUDIO_DEVICE_FLUSH_SIZE, device = None):
        super ().__init__(sample_rate, sample_width, block_size, flush_size, device)
        self.linked = []
        self._stopped = False

    def clone (self):
        vd = VirtualDevice (self._sample_rate, self._sample_width, self._block_size)
        self.linked.append (vd)
        return vd

    def _loop (self, size, count = 0):
        loops = 0
        while not self._stopped:
            loops += 1
            if count and loops == count:
                self.close ()
                break
            data = self.read (size)
            for vd in self.linked:
                vd.put (data)

    def stop (self):
        super ().stop ()
        for vd in self.linked:
            vd.stop ()
        self._stopped = True

    def start (self, size = 320, count = 0):
        super ().start ()
        t = threading.Thread (target = self._loop, args = (size, count))
        t.start ()

