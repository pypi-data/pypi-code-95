def knn(df):
    import pandas as pd
    from sklearn.impute import KNNImputer
    imputer = KNNImputer()
    data = imputer.fit_transform(X)
    return pd.DataFrame(data, index=df.index, columns=df.columns)

def minimum(df):
    df = df.T
    mins = df.min().to_dict()
    return df.fillna(mins).T

def median(df):
    df = df.T
    medians = df.median().to_dict()
    return df.fillna(medians).T

def mean(df):
    df = df.T
    means = df.mean().to_dict()
    return df.fillna(means).T

def none(df):
    return df