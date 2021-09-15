import numpy as np

CARTO_SIGNAL_FILE_LENGTH = 2500


class Channel:
    def __init__(self, name):
        self._signals = {}
        self._name = name

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start or self.first_sample
            stop = item.stop or self.last_sample
            step = item.step or 1

            if start > stop:
                raise ValueError('Start must be before stop')

            def nan_array(length):
                array = np.empty((length,))
                array[:] = np.nan
                return array

            pos = start
            parts = []
            for itv in self.signal_parts:
                if pos < itv[0]:
                    end = min(itv[0], stop)
                    length = 1 + ((end - pos - 1) // step)
                    parts.append(nan_array(length))
                    pos += length * step

                if itv[0] <= pos < itv[1]:
                    end = min(itv[1], stop)
                    length = 1 + ((end - pos - 1) // step)
                    parts.append(self._signals[itv][(pos  - itv[0]):(end  - itv[0]):step])
                    pos += length * step

                if pos >= stop:
                    break

            # Final NaNs
            if pos < stop:
                length = 1 + ((stop - pos - 1) // step)
                parts.append(nan_array(length))
                pos += length * step

            signal = np.concatenate(parts)
            return signal

    @property
    def first_sample(self):
        return min((start for start, _ in self._signals))

    @property
    def last_sample(self):
        return min((start for start, _ in self._signals))

    @property
    def signal_parts(self):
        return sorted(self._signals)

    def add(self, signal, start_ts: int):
        itv = start_ts, len(signal) + start_ts
        if itv not in self._signals:
            self._signals[itv] = signal

        self.simplify_parts()

    def simplify_parts(self):
        prev_itv = (-1, -1)
        prev_signal = None
        new_parts = {}
        for itv in self.signal_parts:
            if itv[0] <= prev_itv[1]:  # Overlap
                if itv[1] <= prev_itv[1]:  # We can remove this part
                    continue
                new_itv = prev_itv[0], itv[1]
                new_signal = np.concatenate((prev_signal, self._signals[itv][prev_itv[1]-itv[0]:itv[1]]))
                prev_itv = new_itv
                prev_signal = new_signal
                continue
            else:  # No overlap
                if prev_signal is not None:
                    new_parts[prev_itv] = prev_signal
                prev_itv = itv
                prev_signal = self._signals[itv]

        if prev_signal is not None:
            new_parts[prev_itv] = prev_signal

        self._signals = new_parts

    def defined(self, start, stop):
        if start >= stop:
            raise ValueError('Invalid start/stop bounds')
        for begin, end in self.signal_parts:
            if begin <= start and stop <= end:
                return True
        return False

    @property
    def name(self):
        return self._name

    @property
    def total_data_length(self):
        return sum([e-s for s, e in self.signal_parts])

    @property
    def acquisition_time_span(self):
        return self.signal_parts[-1][1] - self.signal_parts[0][0]

    @property
    def num_parts(self):
        return len(self.signal_parts)

    def __repr__(self):
        return f'<Channel {self.name}: {self.total_data_length//1000} s of signal in ' \
               f'{self.num_parts} parts over {self.acquisition_time_span//1000} s>'
