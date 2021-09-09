from cnvrg.charts import Heatmap, MatrixHeatmap, Scatterplot, Bar, CategoricalScatterplot
try:
    import pandas as pd
    import numpy as np
    pandas_available = True
except ImportError as e:
    pandas_available = False


class PandasAnalyzer(object):
    def __init__(self, data, experiment=None):
        if not pandas_available: raise ImportError("Can't analyze dataframe, please install pandas first.")
        self.__data = data
        self.__categorical_columns = []
        self.__numeric_columns = []
        self.__experiment = experiment
        self.__generate_charts()

    def __generate_charts(self):
        self.__find_correlations()
        self.__categorical_counts()
        self.__null_values()
        self.__correlation_scatter()

    def __categorical_counts(self):
        print("Creating charts of per categorical values.")
        self.__categorical_columns = self.__data.select_dtypes(exclude=["number", "bool_", "object_"]).columns
        for cat_col in self.__categorical_columns:
            counts = self.__data[cat_col].value_counts()
            self.__experiment.log_chart("{}_categorical_counts".format(cat_col),
                                        [Bar(x=counts.index.tolist(), y=counts.values.tolist(), name=cat_col)],
                                        title="Categorical count {col}".format(col=cat_col))

    def __find_correlations(self):
        print("Logging correlation matrix")
        correlation = self.__data.corr()
        self.__experiment.log_chart("correlation", [MatrixHeatmap(np.round(correlation.values, 2))], x_ticks=correlation.index.tolist(), y_ticks=correlation.index.tolist())

    def __null_values(self):
        print("Finding null values")
        null_values = self.__data.isnull().sum()
        self.__experiment.log_chart("null_values", [Bar(x=null_values.index.tolist(), y=null_values.values.tolist())], title="Null values in the dataframe")


    def __correlation_scatter(self):
        indexes = self.__data.select_dtypes(include=["number"]).columns
        corr = self.__data.corr()
        for idx, i in enumerate(indexes):
            for jdx, j in enumerate(indexes):
                if i == j: continue
                if jdx < idx: continue
                corr_val = abs(corr[i][j])
                if 1 ==  corr_val or corr_val < 0.5: continue
                print("create", i, "against", j, "scatter chart")
                droplines = self.__data[[i,j]].notnull().all(1)
                x,y = self.__data[droplines][[i,j]].values.transpose()
                self.__experiment.log_chart("{i}_against_{j}".format(i=i, j=j),
                                            [Scatterplot(x=x.tolist(), y=y.tolist())],
                                            title="{i} against {j}".format(i=i, j=j))





