from pandas import DataFrame

def ccounts(series):
    '''
    This accepts a PD.Series object and returns a 2 column df showing
    Value_counts and the percent of total
    df['count','percent']
    '''
    df = DataFrame([series.value_counts(),series.value_counts(normalize=True)]).T
    df.columns=['count','percent']
    return df