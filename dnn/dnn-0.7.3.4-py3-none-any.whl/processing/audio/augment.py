from ..image import augment
from . import augments as augtool
import random
from .noise_composer import NoiseData
import librosa
import numpy as np
import soundfile
import os

class Augment (augment.Augment):
    def __init__ (self, sr = 16000, noise_source_dir = None, difficulty = 1.0, disables = None):
        self.sr = sr
        self._difficulty = difficulty
        self._disables = disables or []
        self._random_multipliers = []
        if not noise_source_dir:
            noise_source_dir = os.path.join (os.path.dirname (__file__), 'noise_waves')
        self._life_noisy_maker = NoiseData (noise_source_dir, sr) or None

        self._augmentation_ranges = {  # (easy, hard)
            'color': (0.001, 0.005),
            'speed': (0.02, 0.2),
            'pitch': (0.1, 2.0),
            'ambient': (0.01, 0.1)
        }

    def write (self, path, y):
        with open (path, 'wb') as f:
            soundfile.write (f, y, self.sr)

    def roll (self, y, factor = None):
        shift = factor or random.randrange (len (y))
        return np.roll(self, y, shift)

    def color_noise (self, y, factor = None):
        noise_gain = factor or self.noisy_value_from_type ('color')
        noise = augtool.gen_noise (random.choice (augtool.COLORS), y.shape [0])
        return (y * (1.0 - noise_gain)) + ((noise * noise_gain).astype ("float32"))

    def pitch_shfit (self, y, factor = None):
        pitch_shfit = factor or self.noisy_value_from_type ('pitch')
        return librosa.effects.pitch_shift (y, self.sr, pitch_shfit * random.choice ([1, -1]), bins_per_octave = 12)

    def stretch (self, y, factor = None):
        speed = factor or self.noisy_value_from_type ('speed')
        return librosa.effects.time_stretch (y, 1.0 + (speed * random.choice ([1, -1])))

    def ambient_noise (self, y):
        if self._life_noisy_maker:
            ambient = self.noisy_value_from_type ('ambient')
            return self._life_noisy_maker.synthesis (y, ambient)
        return y

    def __call__ (self, y, save_path = None):
        if isinstance (y, str):
            y, _ = librosa.load (y, sr = self.sr)

        if y.shape [0] % 2 == 1:
            y = y [:-1] # make even
        if 'color_noise' not in self._disables and random.randrange (2) == 0:
            y = self.color_noise (y)
            if random.randrange (3) == 0:
                y = self.color_noise (y)
        if 'pitch' not in self._disables and random.randrange (2) == 0:
            y = self.pitch_shfit (y)
        if 'stretch' not in self._disables and random.randrange (2) == 0:
            y = self.stretch (y)
        if 'ambient_noise' not in self._disables and random.randrange (2) == 0:
            y = self.ambient_noise (y)
        save_path and self.write (save_path, y)
        return y
