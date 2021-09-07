import math
import os
import pandas as pd
import numpy as np
from datupapi.configure.config import Config
from sklearn.preprocessing import MinMaxScaler
from causalnex.structure.notears import from_pandas

class Relation(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path

    def min_max_scaler(self, data):
        """
        Scales the data with a Min Max scaler.
        
        :param data: Input dataframe used to train the models predictions.
 
        :return scalers: Array with the scalers for each feature.
        :return data_train: Normalized input dataframe.

        """
        scalers={}
        #data_train=data.iloc[:,n_features:].copy()
        data_train=data.copy()
        for j in data_train.columns:
                scaler = MinMaxScaler(feature_range=(-1,1))
                s_s = scaler.fit_transform(data_train[j].values.reshape(-1,1))
                s_s=np.reshape(s_s,len(s_s))
                scalers['scaler_'+ j] = scaler
                data_train[j]=s_s
        return scalers, data_train
    
    
    def correlation(self,data, n_columns=0, list_columns=[]):
        """
        Finds the correlation between the selected variables.
        
        :param data: Normalized input data used to find the correlation of each feature.
        :param n_columns: Number of features used in the input data.
        :param list_columns: List of features defined to find their correlation.

        :return correlation_matrix: Dataframe with the correlation between the selected variables.

        """
        if self.normalization:
            scalers, data=self.min_max_scaler(data)
        heatdata=data.corr()  
        correlation_matrix=pd.DataFrame()

        if n_columns==0:
            if len(list_columns)==0:
                for col in data.columns:
                    col_heat=heatdata[[col]].sort_values(by=col, ascending=False)
                    correlation_matrix=pd.concat([correlation_matrix,col_heat.reset_index()],axis=1)
                return correlation_matrix
            else:
                for col in list_columns:
                    col_heat=heatdata[[col]].sort_values(by=col, ascending=False)
                    correlation_matrix=pd.concat([correlation_matrix,col_heat.reset_index()],axis=1)
                return correlation_matrix
        else:
            for col in data[0:n_columns].columns:
                col_heat=heatdata[[col]].sort_values(by=col, ascending=False)
                correlation_matrix=pd.concat([correlation_matrix,col_heat.reset_index()],axis=1)
            return correlation_matrix   

    def causality(self, data, threshold=0.7, max_iter=120, list_columns=[]):
        """
        Finds the causality between the selected variables.
        
        :param data: Normalized input data used to find the causality of each feature.
        :param threshold: Minimum causality value.
        :param max_iter: Number of iterations used to converge the model.

        :return affects: Dataframe with the features that are affected by the column name variable.
        :return Var_affected: Dataframe with the features that affects the column name variable.

        """
        if self.normalization:
            scalers,data=self.min_max_scaler(data)
        sm = from_pandas(data,max_iter=max_iter, w_threshold=threshold)
        len(sm.edges)

        #affects
        d=np.array(sm.edges)
        df=pd.DataFrame(d)
        df.columns=["affected by","Var affected"]
        uni=df['affected by'].unique()

        lista=[]
        for i in range(len(uni)):
            lista_aux=[]
            df_aux=df[df['affected by']==uni[i]]
            lista_aux.append(uni[i])
            for j in range(len(df_aux)):
                lista_aux.append(df_aux["Var affected"].iloc[j])
            lista.append(lista_aux)  
        affects=pd.DataFrame(lista).T
        affects=affects.rename(columns=affects.iloc[0])
        affects = affects[1:] 

        table = str.maketrans(dict.fromkeys("()"))
        n_col=[]
        for i in range(len(affects.columns)):
            n_col.append(affects.columns[i].translate(table))
        affects.columns=n_col

        #Var affected by
        uni_aff=df['Var affected'].unique()
        lista_aff=[]
        for i in range(len(uni_aff)):
            lista_aux=[]
            df_aux=df[df['Var affected']==uni_aff[i]]
            lista_aux.append(uni_aff[i])
            for j in range(len(df_aux)):
                lista_aux.append(df_aux["affected by"].iloc[j])
            lista_aff.append(lista_aux) 

        Var_affected=pd.DataFrame(lista_aff).T
        Var_affected=Var_affected.rename(columns=Var_affected.iloc[0])
        Var_affected = Var_affected[1:]  

        n_col=[]
        for i in range(len(Var_affected.columns)):
                n_col.append(Var_affected.columns[i].translate(table))
        Var_affected.columns=n_col
       
        return Var_affected

