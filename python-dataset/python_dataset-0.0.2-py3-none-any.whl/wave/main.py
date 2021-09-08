import math
import numpy as np

from pathlib import Path
from typing import Tuple

import pyworld as pw
import pysptk as ps
import librosa

from ..property import define_property, define_properties


class Wave(object):
    Vector = "np.ndarray[np.float64]"

    # path関連
    wave_name: str
    person_name: str
    path: Path

    # rawの情報
    fs: int
    wave: Vector

    # 音響特徴量を抜くか否か
    ex_base: bool = True
    ex_mc: bool = True
    ex_mfcc: bool = False

    def __init__(
        self,
        wave_name: str,
        person_name: str,
        path: Path,
        folder_path: Path,  # これは保存しない
        fs: int = 22050,
        order: int = 36,
        ex_base: bool = ex_base,
        ex_mc: bool = ex_mc,
        ex_mfcc: bool = ex_mfcc,
    ) -> None:

        self.wave_name = wave_name
        self.person_name = person_name
        self.path = path

        self.fs = fs
        self.wave = self.load_wav(self.fs, folder_path / self.path)

        if ex_base:
            self.extract_base()

        if ex_mc:
            self.extract_mc()

    def load_wav(
        self,
        fs: int,
        path: Path,
        dtype: "np.dtype" = np.float64,
        top_db: int = 50,
    ) -> Vector:
        """
        pathで指定されたwav fileを読み込む
        """
        wave, fs = librosa.load(path, fs, dtype=dtype)
        wave = librosa.effects.remix(
            wave, intervals=librosa.effects.split(wave, top_db=top_db)
        )

        return wave

    def extract_base(self) -> None:
        f0, sp, ap = pw.wav2world(self.wave, self.fs)

        tmp = len(f0) % 4
        if tmp:
            f0 = f0[:-tmp]
            sp = sp[:-tmp]
            ap = ap[:-tmp]

        self.f0, self.sp, self.ap = f0, sp, ap

    def extract_mc(
        self,
        order: int = 35,
        fs: int = 22050,
        alpha: float = 0.46,
    ) -> None:
        self.mc = ps.conversion.sp2mc(powerspec=self.sp, order=order, alpha=alpha)
