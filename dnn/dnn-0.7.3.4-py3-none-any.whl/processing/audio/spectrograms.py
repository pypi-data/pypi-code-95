import numpy as np
import librosa
from . import utils
import matplotlib.pyplot as plt
from matplotlib import cm
import skimage
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def buf_to_int(x, n_bytes=2):
    scale = float(1 << ((8 * n_bytes) - 1))
    fmt = '<i{:d}'.format(n_bytes)
    return (x * scale).astype(fmt)

def ms_to_len (frame_ms, frame_stride, sample_rate):
    frame_length, frame_step = (frame_ms * sample_rate) // 1000, (frame_stride * sample_rate) // 1000  # Convert from seconds to samples
    return frame_length, frame_step

def mel_spec (y, sample_rate = 16000, n_mels = 40, frame_ms = 32, frame_stride = 8):
    y = utils.scale_minmax (y, -1, 1)
    frame_length, frame_step = ms_to_len (frame_ms, frame_stride, sample_rate)
    S = librosa.feature.melspectrogram (y=y, sr=sample_rate, n_mels = n_mels, n_fft = frame_length, hop_length = frame_step, fmax=8000)
    db = librosa.power_to_db (S, ref=np.max)
    return db

def stft_spec (y, sample_rate = 16000, n_fft = None, frame_ms = 32, frame_stride = 8):
    y = utils.scale_minmax (y, -1, 1)
    frame_length, frame_step = ms_to_len (frame_ms, frame_stride, sample_rate)
    nfft = n_fft or frame_length
    magnitude = abs (librosa.stft(y, n_fft = nfft, win_length = frame_length, hop_length = frame_step))
    db = librosa.amplitude_to_db (magnitude, ref=np.max, top_db = 80)
    return db

def save (db, out, size = None, scale = 'log'):
    if size is None:
        size = (db.shape [1], db.shape [0])
    fig = plt.Figure(figsize=size, dpi = 1)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.axis('off')
    p = librosa.display.specshow(db, ax=ax, y_axis=scale, x_axis='time', cmap = cm.jet)
    fig.tight_layout()
    fig.savefig(out)
save_spectrogram = save


if __name__ == "__main__":
    sig, rate = librosa.load('ravdess/audio_speech_actors_01-24/Actor_01/03-01-07-01-01-01-01.wav', sr = 16000)
    sig = buf_to_int(sig [16000:32000], n_bytes=2)
    spectrogram = sig2spec(sig, rate)
