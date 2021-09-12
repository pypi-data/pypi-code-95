import pandas as pd
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import numpy as np
from datetime import date, timedelta
import re
from sklearn.impute import KNNImputer
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn import preprocessing
from sklearn.metrics import roc_curve, auc

class RiskDataframe():
    """
    The class is used to extend the properties of Dataframes to a prticular
    type of Dataframes in the Risk Indistry. 
    It provides the end user with both general and specific cleaning functions, 
    though they never reference a specific VARIABLE NAME.
    
    It facilitates the End User to perform some Date Feature Engineering,
    Scaling, Encoding, etc. to avoid code repetition.
    """
    #Initializing the inherited pd.DataFrame
    def __init__(self,target,data, *args, **kwargs):
        self.target = target
        self.data = data
        super().__init__(*args,**kwargs)

    @property
    def _constructor(self,target,data):
        def func_(target,data,*args,**kwargs):
            df = RiskDataframe(target,data,*args,**kwargs)
            return df
        return func_

 #-----------------------------------------------------------------------------
                        # EDA - MNAR
#-----------------------------------------------------------------------------
    def binarize_target(self):
        """Turns the selected target variable into boolean by transforming the values > 0 into 1."""
        self.data[self.target] = np.where(self.data[self.target] > 0, 1, self.data[self.target])
        return self.data.value_counts(self.target)
    def missing_values_percentage(self):
        """Return the % of missing values for each pd.series inside the Dataframe."""
        missing_values_percentage = 100*self.data.isnull().sum()/self.data.isnull().count()
        return (missing_values_percentage[missing_values_percentage > 0])   
    def missing_values(self):
        """Return the features that have missing values and the number of those."""
        missing_values = self.data.isnull().sum()
        return (missing_values[missing_values > 0])
    def visualize_MNAR(self):
        """Plot the correlation between missing values inside the dataframe"""
        null_data = self.data[self.data.isnull().any(axis=1)]
        #Replace all non-Nan entries with 1 and all NaN with O
        null_data_zeros_and_ones = null_data.notnull().astype('int')
        plt.figure(figsize=(16, 6))
        heatmap = sns.heatmap(null_data_zeros_and_ones.corr(), vmin=-1, vmax=1, annot=True)
        heatmap.set_title('Correlation Heatmap', fontdict={'fontsize':20}, pad=20);
    def missing_not_at_random(self,input_vars=[]): 
        """MNAR or Missing Not At Random method performs a customize analysis on the correlation between the missing values inside the variables that we select with the argument input_vars.
        Correlation threshold = above 0.5 or below -0.5.
        If the function was run correctly, it will return a MNAR report."""
        null_data = self.data[self.data.isnull().any(axis=1)]
        null_data_zeros_and_ones = null_data.notnull().astype('int') #Replace all non-Nan entries with 1 and all NaN with O
        if input_vars ==[]: 
            input_vars = list(self.data.columns.values)
        try:        
            MNAR_correlation = null_data_zeros_and_ones[input_vars].corr()      
            MNAR =[]
            pos_corr = 0.50
            neg_corr = -0.50
            for i in range(len(MNAR_correlation.columns)):
                for j in range(i):
                    if abs(MNAR_correlation.iloc[i,j]) > pos_corr or (MNAR_correlation.iloc[i,j])<neg_corr:
                        colname_i = MNAR_correlation.columns[j]
                        colname_j = MNAR_correlation.columns[i]
                        MNAR.append(colname_i)
                        MNAR.append(colname_j)
            MNAR = list(set(MNAR))
            if MNAR == []:
                if len(input_vars) == 1:
                    print('Just included one variable. C´mon... include at least two.')
                if len(input_vars) > 1:
                    print('There is not correlation between the chosen variables.')
            else:
                print('MNAR Variables found: {}'.format(MNAR))
                features = list(self.data.columns)
                File_Segment = [x for x in features if x not in MNAR] #List Comprehensions are perfectly suited to making this sort of thing 
                print('Missing Not At Random Report - {} variables seem Missing Not at Random.Therefore, we recomend: \n'.format(MNAR)),
                print('Thin File Segment Variables: {}\n'.format(File_Segment))
                print('Full File Segment Variables: {}\n'.format(features))   
        except:
            print('Not valid "input_vars" argument, include a list with variables that are inside the dataframe.')
 

 #-----------------------------------------------------------------------------
                        # DATA PREPARATION - FEATURE ENGINEERING
 #-----------------------------------------------------------------------------
    def numerical_features(self):
        """Numerical_variables function separates the numerical features except the target one."""
        numerical_features = set(self.data.select_dtypes(include=['number'])) - set([self.target]) #not include the target one
        return numerical_features
    def categorical_features(self):
        """Categorical_variables function separates the non-numerical features except the target one."""
        categorical_features = set(self.data.select_dtypes(exclude=['number'])) - set([self.target]) #not include the target one
        return categorical_features
    def incomplete_features(self):
        """Get the features with nulls inside."""
        incomplete_features = []  # Create an empty array
        for column_name in self.data.columns:
            if self.data[column_name].isna().any():
                incomplete_features.append(column_name)  
        return incomplete_features
    def numerical_features_na (self):
        """Numerical features with missing values."""
        numerical_features_na = self.numerical_features().intersection(self.incomplete_features())
        return numerical_features_na
    def categorical_features_na (self):
        """Categorical features with missing values."""
        categorical_features_na = self.categorical_features().intersection(self.incomplete_features())
        return categorical_features_na
    def cat_imputer (self):
        """Missing categorical values are imputed with SimpleImputer from sklearn (univariable - most frequent)."""
        imputer = SimpleImputer(missing_values=np.nan, strategy ='most_frequent')
        imputed = imputer.fit_transform(self.data[self.categorical_features_na()].values)
        categorical_imputed = pd.DataFrame(imputed, columns=self.categorical_features_na())
        return categorical_imputed
    def num_imputer (self):
        """Missing numerical values are imputed with KNN Imputer from sklearn (multivariable - 5 neighbors)."""
        imputer = KNNImputer(n_neighbors=5, weights='uniform', metric='nan_euclidean')
        imputed = imputer.fit_transform(self.data[self.numerical_features_na()].values)
        numerical_imputed = pd.DataFrame(imputed, columns=self.numerical_features_na())
        return numerical_imputed
    def cat_num_imputer_concat (self):
        """Missing categorical values are imputed with SimpleImputer from sklearn (univariable - most frequent)
        Missing numerical values are imputed with KNN Imputer from sklearn (multivariable - 5 neighbors)
        Place the numerical & categorical NOT imputed in a separate dataframe and concatenate all in the next step."""
        imputer = SimpleImputer(missing_values=np.nan, strategy ='most_frequent')
        imputed = imputer.fit_transform(self.data[self.categorical_features_na()].values)
        categorical_imputed = pd.DataFrame(imputed, columns=self.categorical_features_na())
        
        imputer = KNNImputer(n_neighbors=5, weights='uniform', metric='nan_euclidean')
        imputed = imputer.fit_transform(self.data[self.numerical_features_na()].values)
        numerical_imputed = pd.DataFrame(imputed, columns=self.numerical_features_na())
        
        numerical_complete = pd.DataFrame(self.data[list(self.numerical_features().difference(self.numerical_features_na()))])
        categorical_complete = pd.DataFrame(self.data[list(self.categorical_features().difference(self.categorical_features_na()))])
        
        data = pd.concat([numerical_imputed.reset_index(drop=True),
                   numerical_complete.reset_index(drop=True),
                   categorical_imputed.reset_index(drop=True),
                   categorical_complete.reset_index(drop=True),
                   pd.DataFrame(self.data[self.target].values, columns=[self.target])], axis =1)
        return data
    def scaling(self):
        """Scaling numerical features with MinMaxScaler from sklearn."""
        mm_scaler = preprocessing.MinMaxScaler()
        self.data[list(self.numerical_features)] = mm_scaler.fit_transform(self.data[list(self.numerical_features)])
    def dates_to_days(self,new_column,date_1,date_2,drop_columns=[]):
        """Transform the date columns into days
          - new_column: Name of the column to be created.
          - date_1: Column that represents the minuend, it has datetime[64s] format.
          - date_2: Column that represents the sustraend, it has datetime[64s] format.
          - drop_columns: List of columns to be dropped from the dataframe.
          (When date_1=1, it pops up an error but still the code has run correctly.)"""
        if date_1=='today':
            self.data[new_column] = (np.datetime64(date_1) - self.data[date_2]).dt.days
            self.data.drop(columns = (drop_columns), inplace = True)
        if date_2=='today':
            self.data[new_column] = (self.data[date_1] - np.datetime64(date_2)).dt.days
            self.data.drop(columns = (drop_columns), inplace = True)
        else:
            self.data[new_column] = (self.data[date_1] - self.data[date_2]).dt.days
            self.data.drop(columns = (drop_columns), inplace = True)
        return self.data

  def anova_2tailed(self,target,feature_names):

    print('Null hypothesis:\n The statistical mean of all the groups/categories of the variables is the same.\nAlternate Hypothesis:\n The statistical mean of all the groups/categories of the variables is not the same.')

    for x in feature_names:
        model = ols(target + '~' + x, data = self.data).fit() #Oridnary least square method
        result_anova = sm.stats.anova_lm(model) # ANOVA Test
        print(result_anova)

#-----------------------------------------------------------------------------
                        # MODEL - FIND_SEGMENT_SPLIT
#-----------------------------------------------------------------------------    
    def categorical_split(self):
        """Categorical variables Splitted through decision tree model and mean_encoding with the target variable"""
        categorical_features = list(set(self.data.select_dtypes(exclude=['number'])) - set([self.target]))
        for column in self.data [categorical_features]:
            new = self.data[[column,self.target]].copy()
            mean_encoded_subject = new.groupby([column])[self.target].mean().to_dict()
            new['SubjectName'] =  new[column].map(mean_encoded_subject)
            X = new['SubjectName']
            Y = new[self.target]
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=1) 
            X_train= X_train.values.reshape(-1, 1)
            Y_train= Y_train.values.reshape(-1, 1)
            X_test = X_test.values.reshape(-1, 1)
            clf = DecisionTreeClassifier(max_depth=1)
            clf.fit(X_train, Y_train)
            threshold = clf.tree_.threshold
            group1 = new.loc[new['SubjectName']<=threshold[0],column].unique()
            print(group1)
            group2 = new.loc[new['SubjectName']>threshold[0],column].unique()
            print(group2)
    def find_segment_split(self,candidate,target,input_vars = []):
        """The objective of this function is to compare if a candidate variable performs better when splitted into two segments.
          The arguments are the following ones:
          - candidate: Name of the column to be analyze comparing a full model vs the one segmented.
          - target: As it is a supervised model, should include the name of the target column.
          - input_vars: Should include the variables that the user will include in the model.
          find_segment_split function will use a decision tree algorithm to split between two segments
          find_segment_split function will use GINI and Accuracy as the metrics to measure the results."""
        #Create a list with candidate,target and input_vars
        input_vars.append(candidate)
        input_vars.append(target)
        lista = input_vars
      
        #Isolate the varibles of the dataframe with the created list
        new_dataframe = self.data[lista].copy()
      
        #Categorical and numerical features of our new dataframe, target is out.
        categorical_features = list(set(new_dataframe.select_dtypes(exclude=['number'])) - set([target]))   
        numerical_features = list(set(new_dataframe.select_dtypes(include=['number'])) - set([target]))
      
        #SEGMENTATION STRATEGY : DECISION TREE btw candidate and target variable
        new = new_dataframe[[candidate,target]].copy()
      
        #is it the candidate a categorical_feature?
        result = any(x in candidate for x in categorical_features)
      
        #MEAN ENCODING - PURPOSE IS TO SPLIT CATEGORICAL VARIABLES IN TWO SEGMENTS
        #1. Create a new dataframe. "new".
        #2. Add new variable based on the corresponding target encoding.
        #3. Decision Tree algorithm to split the categorical variable in two.
        if result:
            mean_encoded_subject = new.groupby([candidate])[target].mean().to_dict()
            new['SubjectName'] =  new[candidate].map(mean_encoded_subject)
            X = new['SubjectName']
            Y = new[target]
          #Adequate the dateframe to the shape of a runnable model.
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=1) 
            X_train= X_train.values.reshape(-1, 1)
            Y_train= Y_train.values.reshape(-1, 1)
            X_test = X_test.values.reshape(-1, 1)

          #Find the ideal threshold to split each variable based on their relation to the target.
            clf = DecisionTreeClassifier(max_depth=1)
            clf.fit(X_train, Y_train)   
            threshold = clf.tree_.threshold

          #Complete the two groups of categorical variables.
            group1 = new.loc[new['SubjectName']<=threshold[0],candidate].unique()
            group2 = new.loc[new['SubjectName']>threshold[0],candidate].unique()
      
        else:  
            X = new[candidate]
            Y = new[target]
          #Adequate the dateframe to the shape of a runnable model.
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=1) 
            X_train= X_train.values.reshape(-1, 1)
            Y_train= Y_train.values.reshape(-1, 1)
            X_test = X_test.values.reshape(-1, 1)

          #Find the ideal threshold to split each variable based on their relation to the target.
            clf = DecisionTreeClassifier(max_depth=1)
            clf.fit(X_train, Y_train)   
            threshold = clf.tree_.threshold

          #Complete the two groups of categorical variables.
            group1 = new.loc[new[candidate]<=threshold[0],candidate].unique()
            group2 = new.loc[new[candidate]>threshold[0],candidate].unique()

        #Target encoding the categorical variables except target and candidate
        categorical_features = list(set(new_dataframe.select_dtypes(exclude=['number'])) - set([target,candidate]))
      
        for column in new_dataframe [categorical_features]:
            mean_encoded_subject = new_dataframe.groupby([column])[target].mean().to_dict()
            new_dataframe[column] =  new_dataframe[column].map(mean_encoded_subject)
        
        numerical_features = list(set(new_dataframe.select_dtypes(include=['number'])) - set([target]))   
      
        #Split between test and train.
        data_train, data_test = train_test_split(new_dataframe, test_size = 0.2, random_state = 42)
      
        #Seg 1 and Seg 2.
        data_train_seg1 = data_train[new_dataframe[candidate].isin(group1)]
        data_train_seg2 = data_train[new_dataframe[candidate].isin(group2)]
        data_test_seg1 = data_test[new_dataframe[candidate].isin(group1)]
        data_test_seg2 = data_test[new_dataframe[candidate].isin(group2)]
          
        #Full Model - Numerical_Features
        X_train = data_train[numerical_features]
        y_train = data_train[target]
        X_test = data_test[numerical_features]
        y_test = data_test[target]
        X_train = data_train[numerical_features]
        y_train = data_train[target]
        method = LogisticRegression(random_state=0)
        fitted_full_model = method.fit(X_train, y_train)
        y_pred = fitted_full_model.predict(X_test)

        # Full Model vs Seg 1 on Seg 1
        X_train_seg1 = data_train_seg1[numerical_features]
        y_train_seg1 = data_train_seg1[target]
        X_test_seg1 = data_test_seg1[numerical_features]
        y_test_seg1 = data_test_seg1[target]
        fitted_model_seg1 = method.fit(X_train_seg1, y_train_seg1)
        y_pred_seg1 = fitted_model_seg1.predict(X_test_seg1)
        y_pred_seg1_fullmodel = fitted_full_model.predict(X_test_seg1)
        #Lets try it with the GINI also  
        def GINI(y_test, y_pred_probadbility):
            fpr, tpr, thresholds = roc_curve(y_test, y_pred_probadbility)
            roc_auc = auc(fpr, tpr)
            GINI = (2 * roc_auc) - 1
            return GINI

        y_pred_seg1_proba = fitted_model_seg1.predict_proba(X_test_seg1)[:,1]
        y_pred_seg1_fullmodel_proba = fitted_full_model.predict_proba(X_test_seg1)[:,1]
        print("FEATURE:",candidate,
              "\nSEGMENT:",group1,
              "\nModel Developed on Seg 1 (train sample) applied on Seg 1 (test sample):\n"
              "     ACCURACY: ",accuracy_score(y_test_seg1, y_pred_seg1))
        print("     GINI:{}".format(GINI(y_test_seg1, y_pred_seg1_proba)*100))
        print("")
        print("FEATURE:",candidate,
              "\nSEGMENT:",group1,
              "\nModel Developed on Full Population (train sample) applied on Seg 1 (test sample):\n"
              "     ACCURACY: ",accuracy_score(y_test_seg1, y_pred_seg1_fullmodel))
        print("     GINI:{}".format(GINI(y_test_seg1, y_pred_seg1_fullmodel_proba)*100)),

        #Full Model vs Seg 2 on Seg 2
        X_train_seg2 = data_train_seg2[numerical_features]
        y_train_seg2 = data_train_seg2[target]
        X_test_seg2 = data_test_seg2[numerical_features]
        y_test_seg2 = data_test_seg2[target]
        fitted_model_seg2 = method.fit(X_train_seg2, y_train_seg2)
        y_pred_seg2 = fitted_model_seg2.predict(X_test_seg2)
        y_pred_seg2_fullmodel = fitted_full_model.predict(X_test_seg2)
        #Lets try it with the GINI also  
        y_pred_seg2_proba = fitted_model_seg2.predict_proba(X_test_seg2)[:,1]
        y_pred_seg2_fullmodel_proba = fitted_full_model.predict_proba(X_test_seg2)[:,1]
        print("\n--------------------------------------------------------------------------------")
        print("\nFEATURE:",candidate,
              "\nSEGMENT:",group2,
              "\nModel Developed on Full Population (train sample) applied on Seg 2 (test sample):\n",
              "     ACCURACY: ",accuracy_score(y_test_seg2, y_pred_seg2_fullmodel))
        print("     GINI:{}".format(GINI(y_test_seg2, y_pred_seg2_fullmodel_proba)*100))
        print("")
        print("FEATURE:",candidate,
              "\nSEGMENT:",group2,
              "\nModel Developed on Seg 2 (train sample) applied on Seg 2 (test sample):\n",
              "     ACCURACY: ",accuracy_score(y_test_seg2, y_pred_seg2))
        print("     GINI:{}".format(GINI(y_test_seg2, y_pred_seg2_proba)*100))
