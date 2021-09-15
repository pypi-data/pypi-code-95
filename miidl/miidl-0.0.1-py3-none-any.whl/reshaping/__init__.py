import miidl
from .methods import auto, none

def reshape(df, method='auto'):
    return getattr(miidl.reshaping, method)(df)

call = {
    'auto': auto,
    # 'custom': custom,
    'none': none
}