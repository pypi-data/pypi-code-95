import pandas as pd
import random

class nanDealer:
    def fillNanWithMeanColumnWise(self,dataframe):
        try:
            ## We exclude the categorical data here
            dataframe_numerical = dataframe.select_dtypes(exclude='object')

            ## Finding the mean of the each feature/column
            df = dataframe_numerical.columns[dataframe_numerical.isnull().any()]

            ## Replacing nan values with their column mean
            for i in df:
                mean=dataframe_numerical[i].mean()
                dataframe_numerical[i].fillna(mean,inplace=True)

            return dataframe_numerical
        except Exception as e:
            raise Exception("Error occured while filling Nan values with mean of the data\n",str(e))

    def fillNanWithMedianColumnWise(self,dataframe):
        try:
            ## We exclude the categorical data here
            dataframe_numerical = dataframe.select_dtypes(exclude='object')

            ## Finding the median of the each feature/column
            df = dataframe_numerical.columns[dataframe_numerical.isnull().any()]

            ## Replacing nan values with their column median
            for i in df:
                median = dataframe_numerical[i].median()
                dataframe_numerical[i].fillna(median, inplace=True)

            ## adding the categorical column of dataframe and returning it back as orginal dataframe
            # dataframe_categorical=dataframe.select_dtypes(include='object')

            return dataframe_numerical

        except Exception as e:
            raise Exception("Error occured while filling Nan values with mean of the data\n", str(e))



    def fillNanWithRandomValuesFromColumn(self, dataframe):
        try:
            ## We exclude the categorical data here
            dataframe_numerical = dataframe.select_dtypes(exclude='object')

            ## Finding the median of the each feature/column
            df = dataframe_numerical.columns[dataframe_numerical.isnull().any()]

            ## Replacing nan values with their column median
            for i in df:
                random_num = random.randrange(dataframe_numerical[i].min(),dataframe_numerical[i].max())
                dataframe_numerical[i].fillna(random_num, inplace=True)

            # ## adding the categorical column of dataframe and returning it back as orginal dataframe
            # dataframe_categorical = dataframe.select_dtypes(include='object')

            return dataframe_numerical
        except Exception as e:
            raise Exception("Error occured while filling Nan values with random value from the column\n", str(e))

    def fillNanWithMeanRowWise(self,dataframe):
        try:
            ## We exclude the categorical data here
            dataframe_numerical = dataframe.select_dtypes(exclude='object')

            ##Finding the mean row wise
            mean=dataframe_numerical.mean(axis=1)

            ##Enumertating the dataframe and filling the mean value in the Nan values
            for i,column in enumerate(dataframe_numerical):
                dataframe_numerical.iloc[:,i].fillna(mean,inplace=True)

            return dataframe_numerical
        except Exception as e:
            raise Exception("Error occured while filling the Nan values with mean of their respective rows\n,str(e)")


    def fillNanWithMedianRowWise(self,dataframe):
        try:
            ## We exclude the categorical data here
            dataframe_numerical = dataframe.select_dtypes(exclude='object')

            ##Finding the mean row wise
            median=dataframe_numerical.median(axis=1)

            ##Enumertating the dataframe and filling the mean value in the Nan values
            for i,column in enumerate(dataframe_numerical):
                dataframe_numerical.iloc[:,i].fillna(median,inplace=True)

            return dataframe_numerical
        except Exception as e:
            raise Exception("Error occured while filling the Nan values with mean of their respective rows\n,str(e)")




if __name__=="__main__":
    test = nanDealer()
    t = pd.read_csv("C://Users//atulkumarrai//Batsmen_data.csv")

    df = test.fillNanWithMeanColumnWise(t)
    df1 = test.fillNanWithMedianColumnWise(t)
    df2 = test.fillNanWithRandomValuesFromColumn(t)
    df3 = test.fillNanWithMeanRowWise(t)
    df4 = test.fillNanWithMedianRowWise(t)
    print(df)
    print(df1)
    print(df2)
    print(df3)
    print(df4)
