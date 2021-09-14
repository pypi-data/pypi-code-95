import librosa
import soundfile
import os
from scipy import signal
import os
import soundfile as sf
import numpy as np
import random
from rs4 import pathtool
from ..video.ffmpeg import run_process
import matplotlib.pyplot as plt
from matplotlib import cm
import skimage
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def resampling (audioFilePath, targetFilePath, sampling_rate = 16000):
    y, sr = librosa.load (audioFilePath, sr = 22050, mono = True)
    with open (targetFilePath, "wb") as f:
       soundfile.write (f, y, sampling_rate)

def resample_dir (directory, target = None, recusive = False):
    if taget is None:
        target  = os.path.join (directory, "AIMDV")
    pathtool.mkdir (target)

    for each in os.listdir (directory):
        if each == "AIMDV":
            continue

        path = os.path.join (directory, each)
        if os.path.isdir (path):
            if recusive:
                resample_dir (path, target, True)
            else:
                continue

        try:
            resampling (path, target)
        except:
            raise

def convert2mp3 (input, output, quality = 7):
    try:
        int (quality)
    except ValueError:
        assert quality.endswith ("k")
        q = "-b:a {}".format (quality)
    else:
        q = "-q:a {}".format (quality)
    os.path.isfile (output) and os.remove (output)
    cmd = 'ffmpeg -i "{}" -codec:a libmp3lame {} "{}"'.format (input, q, output)
    r = run_process (cmd)
    assert os.path.isfile (output)
    return output

def convert2wav (input, output, sample_rate = 44050):
    os.path.isfile (output) and os.remove (output)
    cmd = 'ffmpeg -i "{}" -acodec pcm_s16le -ar {} "{}"'.format (input, sample_rate, output)
    r = run_process (cmd)
    #r = run_process ('ffmpeg -i "{}" "{}"'.format (input, output))
    assert os.path.isfile (output)
    return output


def read_wav(path, sr, duration=None, mono=True):
    wav, _ = librosa.load(path, mono=mono, sr=sr, duration=duration)
    return wav

def write_wav(wav, sr, path, format='wav', subtype='PCM_16'):
    sf.write(path, wav, sr, format=format, subtype=subtype)


def read_mfcc(prefix):
    filename = '{}.mfcc.npy'.format(prefix)
    mfcc = np.load(filename)
    return mfcc

def write_mfcc(prefix, mfcc):
    filename = '{}.mfcc'.format(prefix)
    np.save(filename, mfcc)


def read_spectrogram(prefix):
    filename = '{}.spec.npy'.format(prefix)
    spec = np.load(filename)
    return spec


def write_spectrogram(prefix, spec):
    filename = '{}.spec'.format(prefix)
    np.save(filename, spec)


def read_wav_from_arr(path):
    import pyarrow

    with open(path, 'rb') as rb:
        return pyarrow.deserialize(rb.read())


def split_wav(wav, top_db):
    intervals = librosa.effects.split(wav, top_db=top_db)
    wavs = map(lambda i: wav[i[0]: i[1]], intervals)
    return wavs


def trim_wav(wav):
    wav, _ = librosa.effects.trim(wav)
    return wav


def fix_length(wav, length):
    if len(wav) != length:
        wav = librosa.util.fix_length(wav, length)
    return wav


def crop_random_wav(wav, length=None):
    if not length:
        return wav
    assert (wav.ndim <= 2)
    assert (type(length) == int)
    wav_len = wav.shape[-1]
    start = np.random.randint(0, np.maximum(1, wav_len - length))
    end = start + length
    if wav.ndim == 1:
        wav = wav[start:end]
    else:
        wav = wav[:, start:end]
    return wav


def mp3_to_wav(src_path, tar_path):
    from pydub import AudioSegment

    basepath, filename = os.path.split(src_path)
    os.chdir(basepath)
    AudioSegment.from_mp3(src_path).export(tar_path, format='wav')


def prepro_audio(source_path, target_path, format=None, sr=None, db=None):
    from pydub import AudioSegment

    sound = AudioSegment.from_file(source_path, format)
    if sr:
        sound = sound.set_frame_rate(sr)
    if db:
        change_dBFS = db - sound.dBFS
        sound = sound.apply_gain(change_dBFS)
    sound.export(target_path, 'wav')

def wav2spec(wav, n_fft, win_length, hop_length, time_first=True):
    stft = librosa.stft(y=wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length)
    mag = np.abs(stft)
    phase = np.angle(stft)
    if time_first:
        mag = mag.T
        phase = phase.T
    return mag, phase

def spec2wav(mag, n_fft, win_length, hop_length, num_iters=30, phase=None):
    assert (num_iters > 0)
    if phase is None:
        phase = np.pi * np.random.rand(*mag.shape)
    stft = mag * np.exp(1.j * phase)
    wav = None
    for i in range(num_iters):
        wav = librosa.istft(stft, win_length=win_length, hop_length=hop_length)
        if i != num_iters - 1:
            stft = librosa.stft(wav, n_fft=n_fft, win_length=win_length, hop_length=hop_length)
            _, phase = librosa.magphase(stft)
            phase = np.angle(phase)
            stft = mag * np.exp(1.j * phase)
    return wav

def preemphasis(wav, coeff=0.97):
    assert coeff <= 1.0
    preem_wav = signal.lfilter([1, -coeff], [1], wav)
    return preem_wav

def inv_preemphasis(preem_wav, coeff=0.97):
    wav = signal.lfilter([1], [1, -coeff], preem_wav)
    return wav


def linear_to_mel(linear, sr, n_fft, n_mels, **kwargs):
    mel_basis = librosa.filters.mel(sr, n_fft, n_mels, **kwargs)  # (n_mels, 1+n_fft//2)
    mel = np.dot(mel_basis, linear)  # (n_mels, t) # mel spectrogram
    return mel

def amp2db(amp):
    return librosa.amplitude_to_db(amp)

def db2amp(db):
    return librosa.db_to_amplitude(db)

def normalize_db_0_1(db, max_db, min_db):
    norm_db = np.clip((db - min_db) / (max_db - min_db), 0, 1)
    return norm_db

def denormalize_db_0_1(norm_db, max_db, min_db):
    db = np.clip(norm_db, 0, 1) * (max_db - min_db) + min_db
    return db

def normalize_db(db, max_db, min_db): # -1 ~ 1
    return (normalize_db_0_1(db, max_db, min_db) - 0.5) * 2

def denormalize_db(norm_db, max_db, min_db):
    return denormalize_db_0_1(norm_db / 2 + 0.5, max_db, min_db)

def directional_dynamic_range_compression(db, threshold_db, ratio = 0.2, method='downward'):
    if method is 'downward':
        db[db > -threshold_db] = (db[db > -threshold_db] + threshold_db) * ratio - threshold_db
    elif method is 'upward':
        db[db < -threshold_db] = (threshold_db + db[db < -threshold_db]) * ratio - threshold_db
    return db

def dynamic_range_compression(db, min_db, max_db, ratio = 0.2):
    db = directional_dynamic_range_compression (db, min_db, ratio)
    return directional_dynamic_range_compression (db, max_db, ratio, 'upward')


def emphasize_magnitude(mag, power=1.2):
    emphasized_mag = np.power(mag, power)
    return emphasized_mag

def wav2melspec(wav, sr, n_fft, win_length, hop_length, n_mels, time_first=True, **kwargs):
    # Linear spectrogram
    mag_spec, phase_spec = wav2spec(wav, n_fft, win_length, hop_length, time_first=False)
    # Mel-spectrogram
    mel_spec = linear_to_mel(mag_spec, sr, n_fft, n_mels, **kwargs)
    # Time-axis first
    if time_first:
        mel_spec = mel_spec.T  # (t, n_mels)
    return mel_spec

def wav2melspec_db(wav, sr, n_fft, win_length, hop_length, n_mels, max_db=None, min_db=None,
                   time_first=True, **kwargs):
    mel_spec = wav2melspec(wav, sr, n_fft, win_length, hop_length, n_mels, time_first=False, **kwargs)
    # Decibel
    mel_db = librosa.amplitude_to_db(mel_spec)
    # Normalization
    mel_db = normalize_db(mel_db, max_db, min_db) if max_db and min_db else mel_db
    # Time-axis first
    if time_first:
        mel_db = mel_db.T  # (t, n_mels)
    return mel_db

def wav2mfcc(wav, sr, n_fft, win_length, hop_length, n_mels, n_mfccs, preemphasis_coeff=0.97, time_first=True,
             **kwargs):
    # Pre-emphasis
    wav_preem = preemphasis(wav, coeff=preemphasis_coeff)
    # Decibel-scaled mel-spectrogram
    mel_db = wav2melspec_db(wav_preem, sr, n_fft, win_length, hop_length, n_mels, time_first=False, **kwargs)
    # MFCCs
    mfccs = np.dot(librosa.filters.dct(n_mfccs, mel_db.shape[0]), mel_db)
    # Time-axis first
    if time_first:
        mfccs = mfccs.T  # (t, n_mfccs)
    return mfccs


def scale_minmax(X, min=-1.0, max=1.0):
    X_std = (X - X.min()) / (X.max() - X.min())
    X_scaled = X_std * (max - min) + min
    return X_scaled
