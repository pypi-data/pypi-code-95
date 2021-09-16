#!/usr/bin/env python
# -*- coding: utf-8 -*-

import auditok
import math


class Overtalk(object):
    """Computes duration of overtalk in a stereo WAV file.

    Attributes
        kwargs (dict, optional): keyword arguments passed on to auditok.
        aw (float, optional): 'analysis_window' argument of auditok,
            defaults to 0.05.
        regionobj (AudioRegion): AudioRegion object of auditok.
        _bools (list): list of two lists containig booleans for each
            analysis_window indicating whether the analysis_window
            carried audio event or not.
    """
    def __init__(self, **kwargs):
        """Computes duration of overtalk, silence and talk time of channels in a
        stereo WAV file. It also accepts two mono WAV files. Overtalk occurs
        when both channels carry audio event.

        Args:
            kwargs (dict, optional): keyword arguments passed on to auditok.
        """
        self.kwargs = kwargs
        self.aw = kwargs.get("analysis_window", 0.05)
        self.regionobj = None
        self._bools = []

    def load(self, *wavfiles):
        """Loads one stereo or two mono WAV files.

        Args:
            wavfiles (str): path to wavfile(s).

        Returns:
            None.
        """
        if len(wavfiles) > 2:
            raise ValueError("Number of input WAV files is greater than 2.")

        if self._bools:
            del self._bools[:]

        for wavfile in wavfiles:
            if len(self._bools) == 2:
                continue

            self.regionobj = regionobj = auditok.load(wavfile)
            for ch in range(regionobj.channels):
                if len(self._bools) == 2:
                    continue

                bools = []
                offset = 0
                top = self.roundup(regionobj.duration)
                regions = auditok.split(
                    regionobj, use_channel=ch, **self.kwargs
                )

                for r in regions:
                    bottom = self.rounddown(r.meta.start)
                    top = self.roundup(r.meta.end)
                    bools.extend(
                        [False for x in range(int((bottom - offset) / self.aw))]
                    )
                    bools.extend(
                        [True for x in range(int((top - bottom) / self.aw))]
                    )
                    offset = top

                end = self.roundup(regionobj.duration)
                bools.extend([False for x in range(int((end - top) / self.aw))])
                self._bools.append(bools)

    @property
    def bools(self):
        """Returns a list of two lists containig booleans for each
            analysis_window indicating whether the analysis_window
            carried audio event or not.

        Returns:
            list: list of audio event types for each channel.
        """
        return self._bools

    @property
    def overtalk(self):
        """Returns the total overtalk time in seconds.

        Returns:
            float: sum of analisys_windows when both channels carried
            audio event.
        """
        if len(self.bools) == 1:
            return 0.
        awsum = sum(1 for c1, c2 in zip(*self.bools) if c1 and c2)
        return awsum * self.aw

    @property
    def silence(self):
        """Returns the total silence time in seconds.

        Returns:
            float: sum of analisys_windows when neither channel carried
            audio event.
        """
        if len(self.bools) == 1:
            awsum = sum(1 for c in self.bools[0] if not c)
        else:
            awsum = sum(1 for c1, c2 in zip(*self.bools) if not c1 and not c2)
        return awsum * self.aw

    @property
    def talktime(self):
        """Returns the total talk time in seconds for each channel.

        Returns:
            tuple(float, float or None): sum of analisys_windows with
            audio event for each channel.
        """
        c1 = sum(1 for x in self.bools[0] if x) * self.aw
        if len(self.bools) == 2:
            c2 = sum(1 for x in self.bools[1] if x) * self.aw
        else:
            c2 = None
        return c1, c2

    @property
    def sr(self):
        """Returns the sampling rate in Hz.

        Returns:
            int: sampling rate.
        """
        return self.regionobj.sampling_rate

    @property
    def duration(self):
        """Returns the duration of (the last) WAV file in seconds.

        Returns:
            float or None: duration of last loaded WAV file.
        """
        return self.regionobj.duration if self.regionobj else None

    def rounddown(self, x):
        """Rounds x down to the nearest multiple of analysis_window.

        Args:
            x (int): number to be rounded down.

        Returns:
            int: rounded down number.
        """
        return math.floor(x / self.aw) * self.aw

    def roundup(self, x):
        """Rounds x up to the nearest multiple of analysis_window.

        Args:
            x (int): number to be rounded up.

        Returns:
            int: rounded up number.
        """
        return math.ceil(x / self.aw) * self.aw


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Need at least one WAV file as argument.")
        sys.exit(1)
    overtalk = Overtalk(
        energy_threshold=50,
        analysis_window=0.1,
        min_dur=0.2,
        max_dur=10,
        max_silence=0.2
    )
    overtalk.load(*sys.argv[1:])
    print(overtalk.overtalk)
