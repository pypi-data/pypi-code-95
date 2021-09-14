from webrtcvad import Vad
from scipy.io import wavfile
from collections import deque

class Frame:
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration

def frame_generator (frame_duration_ms, audio, sample_rate):
    frames = []
    n = int (sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        frames.append (Frame (audio[offset:offset + n], timestamp, duration))
        timestamp += duration
        offset += n
    return frames

def has_voice (wav, activation_threshold = 0.9, sr = 16000, chunk_ms = 30, aggresive_level = 3):
    vad = Vad (aggresive_level)
    padding_duration_ms = int (1500 / chunk_ms)
    sr, samples = wavfile.read (wav)
    frames = frame_generator (chunk_ms, samples, sr)
    activations = deque (maxlen = padding_duration_ms)
    for i, frame in enumerate(frames):
        activations.append (vad.is_speech (frame.bytes, sr))
        if len (activations) != activations.maxlen:
            continue
        if len ([e for e in activations if e]) / len (activations) > activation_threshold:
            return True
    if len (activations) < activations.maxlen: # below 1.5s
        activation_threshold *= 0.5
        return len ([e for e in activations if e]) / len (activations) > activation_threshold
    return False
