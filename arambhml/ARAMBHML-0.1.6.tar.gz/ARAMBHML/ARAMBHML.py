
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import  BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import AdaBoostClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)
import plotly.graph_objects as go
class arambhNet:
    def __init__(self,path,target):
        self.path= path
        self.target = target
    def get_dataframe(self,path):
        df = pd.read_csv(self.path)
        
        
        return df.head()
    def get_features(self,path):
        df = pd.read_csv(self.path)
        return df.columns
    def get_shape(self,path):
        df = pd.read_csv(self.path)
        return df.shape
    def get_information(self,path):
        df = pd.read_csv(self.path)
        return df.describe()
    def get_info_null(self,path):
        df = pd.read_csv(self.path)
        features_with_na=[features for features in df.columns if df[features].isnull().sum()>1]
        if len(features_with_na)==0:
            print('No Null Values Present')
        else:
            for feature in features_with_na:
                print( feature, np.round(df[feature].isnull().mean(), 4),  '% missing values')
    def get_numerical_features(self,path):
        df = pd.read_csv(self.path)
        numerical_features = [feature for feature in df.columns if df[feature].dtypes != 'O']
        print("The number of numerical features are:", len(numerical_features))
        if len(numerical_features)==0:
            print("Nothing to print")
        else:
            for feature in numerical_features:
                print(feature,end = '\n')

    def get_discrete_features(self,path):
        df = pd.read_csv(self.path)
        numerical_features = [feature for feature in df.columns if df[feature].dtypes != 'O']
        discrete_features=[feature for feature in numerical_features if len(df[feature].unique())<25]
        print("The number of discrete features are :",len(discrete_features))

        if len(discrete_features)==0:
            print("No features to print")
        else:
            for feature in numerical_features:
                print(feature,end = '\n')
    def get_continuous_features(self,path):
        df = pd.read_csv(self.path)
        numerical_features = [feature for feature in df.columns if df[feature].dtypes != 'O']
        discrete_features=[feature for feature in numerical_features if len(df[feature].unique())<25] 
        continuous_features=[feature for feature in numerical_features if feature not in discrete_features]

        if len(continuous_features)==0:
            print("No features to print")
        else:

            print("The features are :")
            for feature in continuous_features:
                print(feature,end = '\n')
    def plot_distribution_of_continuous_features(self,path):
        df = pd.read_csv(self.path)
        numerical_features = [feature for feature in df.columns if df[feature].dtypes != 'O']
        discrete_features=[feature for feature in numerical_features if len(df[feature].unique())<25] 
        continuous_features=[feature for feature in numerical_features if feature not in discrete_features]
        if(len(continuous_features)>=20):
            print("Too many features to print! Please Reduce the features")
        else:
            for feature in continuous_features:
                data=df.copy()
                data[feature].hist(bins=25)
                plt.xlabel(feature)
                plt.ylabel("Count")
                plt.title(feature)
                plt.show()
    def get_correlation_heatmap(self,path):
        df = pd.read_csv(self.path)
        fig, ax = plt.subplots(figsize=(10,8))
        sns.heatmap(df.corr(),annot=True,ax=ax)
    def plot_continuous_feature_with_target(self,path,target):
        df = pd.read_csv(self.path)
        numerical_features = [feature for feature in df.columns if df[feature].dtypes != 'O']
        discrete_features=[feature for feature in numerical_features if len(df[feature].unique())<25] 
        continuous_features=[feature for feature in numerical_features if feature not in discrete_features]
        for feature in continuous_features:
            sns.displot(x=feature, hue=self.target, data=df, alpha=0.6)
    def get_categorical_features(self,path):
        df = pd.read_csv(self.path)
        categorical_features = [feature for feature in df.columns if df[feature].dtypes == 'O']
        if(len(categorical_features)==0):
            print("No Categorical_features!")
        else:
            print("The number of categorical variables are : ", len(categorical_features))
            print("The features are : ",end='\n')
            for feature in categorical_features:
                print(feature,end = '\n')


    
    def get_model_details(self,path,target):
        df = pd.read_csv(self.path)
        flag=0
        flag2=0
        if df[self.target].dtypes == 'O':
            flag=1
            flag2 =1
            print("This is a Classification Problem",end='\n')
        else:
            if(len(df[self.target].unique())<30):
                flag=1
                print("This is a Classification Problem",end='\n')
            else:
                print("This is a Regression Problem",end='\n')
        if flag==1:
            print("Starting to process the data for Classification......")
            print("Checking if the target variable is of Object type....")
            if(flag2==1):
                print("The target variable is of Object type")
                print("Label encoding it into numerical feature...")
                labelencoder = LabelEncoder()
                df['Target2'] = labelencoder.fit_transform(df[self.target])
                df = df.drop(df[target],axis=1)
                self.target = 'Target2'
                print("Label Encoding done!")
            else:
                print("The target variable is of numeric type: ")
                print("The number of categories in the target variable ",len(df[self.target].unique()))
                y= df[self.target]
                X= df.drop([self.target],axis=1)
                scaler = StandardScaler()
                categorical_vars = [feature for feature in X.columns if X[feature].dtypes == 'O']
                print("SEARCHING FOR MISSING VALUES .....")
                features_with_na=[features for features in X.columns if X[features].isnull().sum()>1]
                if(len(features_with_na)==0):
                    
                    print("Missing values not found!")
                else:
                    
                    print("Missing Values Found!")
                    print("Treating Missing Values.....")
                    for feature in features_with_na:
                        if np.round(X[feature].isnull().mean())>0.5:
                                
                            X=X.drop([feature],axis=1)
                        
                        elif X[feature].dtypes == 'O':
                            most_frequent_category=X[feature].mode()[0]
                            X[feature+"_Imputed"] =X[feature]
                            X[feature + "_Imputed"].fillna(most_frequent_category,inplace=True)
                            X= X.drop([feature],axis=1) 
                        
                        elif X[feature].dtypes !='O' and len(X[feature].unique())<25 :
                            most_frequent_category=X[feature].mode()[0]
                            X[feature+"_Imputed"] =X[feature]
                            X[feature + "_Imputed"].fillna(most_frequent_category,inplace=True)
                            X= X.drop([feature],axis=1) 
                        
                        elif X[feature].dtypes !='O' and len(X[feature].unique())>25:
                            X[feature].fillna(X[feature].mean(),inplace=True)
                            
                            
                            
                                
                                
                                
                                
                                
                                
                            
                            
                                
                              
                              
                            
                            
                            
                            
                            
                        
                
                #Fill categorical nans with something
                #Fill continuous nans with mean 
                #Drop columns with more than 50% nans
#                 for feature in categorical_vars:
#                     most_frequent_category=X[feature].mode()[0]
#                     X[feature+"_Imputed"] =X[feature]
#                     X[feature + "_Imputed"].fillna(most_frequent_category,inplace=True)
                    
#                 X= X.drop([categorical_vars],axis=1) 





                    
                
                
                
                numerical_features = [feature for feature in df.columns if df[feature].dtypes != 'O']
                discrete_features=[feature for feature in numerical_features if len(df[feature].unique())<25] 
                continuous_vars=[feature for feature in numerical_features if feature not in discrete_features]
                X = pd.get_dummies(X, columns = categorical_vars, drop_first = True)
                X[continuous_vars] = scaler.fit_transform(X[continuous_vars])
                print("STARTING TO TRAIN......")
                print("TRAIN_TEST_SPLIT = 20%")
                X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2)
                lr = LogisticRegression(random_state=42)

                knn = KNeighborsClassifier()
                para_knn = {'n_neighbors':np.arange(1, 50)}

                grid_knn = GridSearchCV(knn, param_grid=para_knn, cv=5)

                dt = DecisionTreeClassifier()
                para_dt = {'criterion':['gini','entropy'],'max_depth':np.arange(1, 100), 'min_samples_leaf':[1,2,4,5,10,20,30,40,80,100]}
                grid_dt = GridSearchCV(dt, param_grid=para_dt, cv=5)

                rf = RandomForestClassifier()

                # Define the dictionary 'params_rf'
                params_rf = {
                    'n_estimators':[100, 350, 500],
                    'min_samples_leaf':[2, 10, 30]
                }
                grid_rf = GridSearchCV(rf, param_grid=params_rf, cv=5)
                dt = DecisionTreeClassifier(criterion='gini', max_depth=30, min_samples_leaf=5, random_state=42)
                knn = KNeighborsClassifier(n_neighbors=2)
                rf = RandomForestClassifier(n_estimators=1000, min_samples_leaf=2, random_state=42)
                classifiers = [('Logistic Regression', lr), ('K Nearest Neighbours', knn), ('Classification Tree', dt), ('Random Forest', rf)]
                model_names =[]
                accuracy_scores=[]
                for clf_name, clf in classifiers:    

                    # Fit clf to the training set
                    clf.fit(X_train, y_train)    

                    # Predict y_pred
                    y_pred = clf.predict(X_test)

                    # Calculate accuracy
                    accuracy = accuracy_score(y_pred, y_test) 
                    model_names.append(clf_name)
                    accuracy_scores.append(accuracy)

                    # Evaluate clf's accuracy on the test set
                    print('{:s} : {:.3f}'.format(clf_name, accuracy))


                ada = AdaBoostClassifier(base_estimator=rf, n_estimators=100, random_state=1)

                ada.fit(X_train, y_train)

                y_pred = ada.predict(X_test)
                model_names.append("Adaboost")

                accuracy_scores.append(accuracy_score(y_pred, y_test))
                print("Adaboost Accuracy: ",accuracy_score(y_pred, y_test))

                classifier = XGBClassifier(n_estimators = 10000,learning_rate = 0.0001,max_depth=29,max_leaves = 31,eval_metric = 'auc',verbosity = 0,use_label_encoder=False)
                classifier.fit(X,y)
                y_pred=classifier.predict(X_test)
                y_test=np.array(y_test)
                print("accuracy_score_XGBOOST: ",accuracy_score(y_test,y_pred))
                model_names.append('XGBoost')
                accuracy_scores.append(accuracy_score(y_test,y_pred))
                plt.bar(x=model_names,height=accuracy_scores)
               # fig = px.bar(y=accuracy_scores, x=model_names)
                # Put bar total value above bars with 2 values of precision
    #             fig.update_traces(texttemplate='%{text:.1s}', textposition='outside')
                # Set fontsize and uniformtext_mode='hide' says to hide the text if it won't fit
               # fig.update_layout(uniformtext_minsize=8)
                # Rotate labels 45 degrees
               # fig.update_layout(xaxis_tickangle=-45)
                #fig.show();
                print("IMPORTANCE OF EACH FEATURES: ")
                importances = pd.Series(data=rf.feature_importances_,
                            index= X_train.columns)

                # Sort importances
                importances_sorted = importances.sort_values()

                # Draw a horizontal barplot of importances_sorted
                plt.figure(figsize=(10, 10))
                importances_sorted.plot(kind='bar',color='orange')
                plt.title('Features Importances')
                plt.show()
          
