import numpy as np

def qc(df, obs=0.3):
    '''Filt data by observed rate (obs_num / all_num)'''
    if obs=='none' or obs==0:
        obs=0.01
    df = df.replace(0, np.nan)
    count_s = df.count()/len(df.index)
    count_s = count_s[count_s>=obs]
    return df[count_s.index]