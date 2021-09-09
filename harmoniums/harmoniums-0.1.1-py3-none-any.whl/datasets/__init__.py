import pathlib

from numpy import array, logical_xor, ones_like, random
import pandas as pd

from harmoniums.samplers import sample_right_truncated_gamma_distribution


def load_nvalt8() -> pd.DataFrame:
    """
    Load NVALT-8 lung cancer dataset as data frame.

    The NVALT-8 study is a randomised control experiment that evaluated the
    efficacy of the drug nadroparin in lung cancer patients by examining the
    recurrence free survival.

    Reference:
    - Groen et al., Br. J. Cancer 121.5 (2019): 372-377.
    """
    return pd.read_csv(
        pathlib.Path(__file__).parent.absolute() / "nvalt8.csv", index_col=0
    )


def load_nvalt11() -> pd.DataFrame:
    """
    Load NVALT-11 lung cancer dataset as data frame.

    The NVALT-11 study considered the effect of profylactic brain radiation
    versus observation in ($`m`$=174) patients with advanced non-small cell lung
    cancer.

    Reference:
    -  De Ruysscher et al. , J. Clin. Oncol. 36.23 (2018): 2366-2377.
    """
    return pd.read_csv(
        pathlib.Path(__file__).parent.absolute() / "nvalt11.csv", index_col=0
    )


def load_xor(
    a=(14.430703308172536, 114.49126570927656),
    b=(53.72281323269014, 151.32168761236875),
    m: int = 1000,
    censor: bool = False,
) -> pd.DataFrame:
    """
    Load XOR distribution composed of four modes.

    The values `a` and `b` control the mean and variance of the modes. By
    default, the values corresponding to the four modes (with variance ~ 1/200)
    are placed at:
    - (0.25, 0.25)
    - (0.75, 0.25)
    - (0.25, 0.75)
    - (0.75, 0.75)
    """
    x1 = random.randint(2, size=m)
    x2 = random.randint(2, size=m)
    y = logical_xor(x1, x2).astype(int)
    t1 = array([sample_right_truncated_gamma_distribution(a[i], b[i]) for i in x1])
    t2 = array([sample_right_truncated_gamma_distribution(a[i], b[i]) for i in x2])
    event_1 = ones_like(t1)
    event_2 = ones_like(t2)

    if censor:
        # Censor events at 0.75 with 75 % probability.
        censor_1 = (t1 > 0.75) & (random.randint(4, size=m).astype(bool) > 0)
        censor_2 = (t2 > 0.75) & (random.randint(4, size=m).astype(bool) > 0)
        # Replace observations with censor time.
        t1[censor_1] = 0.75
        t2[censor_2] = 0.75
        event_1 = (~censor_1).astype(int)
        event_2 = (~censor_2).astype(int)
    return pd.DataFrame(
        {"y": y, "t1": t1, "t2": t2, "event_1": event_1, "event_2": event_2}
    )
