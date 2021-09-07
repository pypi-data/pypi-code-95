from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
import sys
from .DataVisulization import DataVisulization

class DataCorrelation:
    def __init__(self,df):
        self.df = df
        self.copy = self.ByeByeText(self.df)
        self.high_corr = {}
        self.corr = []

    def ByeByeText(self,df):
        copy = df.copy()

        for  i in copy.columns:
            if (copy[i].dtype == "object"):
                copy.drop(columns = i, inplace=True)
        return (copy)
    def FindingScreenSize_(self):
        app = QtWidgets.QApplication(sys.argv)
        screen = app.primaryScreen()
        size = screen.size()
        screensize = (size.width()/95-2, size.height()/96-2)
        return screensize
    def Correlationmatrix(self):

        for  i in self.copy.columns:
            for  j in self.copy.columns:
                if i == j:
                    pass
                else:
                    # print(j)
                    corr = self.copy[i].corr(self.copy[j])
                    if (corr>=0.5 or corr<=-0.5):
                        # print(corr)
                        if (i not in self.high_corr.keys()):
                            self.high_corr[i] = []
                        self.high_corr[i].extend([j,corr])
                        self.corr.append(corr)
        print("these are correlation values for each column")
        count = 0
        for i in self.high_corr.keys():
            print(f"{count}:{i},{self.high_corr[i]}")
            count += 1
    def LookingAtCorr(self):
        print("with the values you see up above do you with to see a a scatter matrix of them")
        choice = input("enter yes if you do")
        if choice.upper() == "YES":

            column = []
            matrix = []
            for i in self.copy.columns:
                column.append(i)
            print(column)
            while (choice.upper()!="Q"):
                count = 0
                for i in column:
                    print(f"{count}:{i}")
                    count+=1
                try:
                    index = int(input("enter the corresponding number of each column that you would like to see"))
                except:
                    print("seems you picked an option that was not available")
                matrix.append(column[index])
                choice = input("enter q to view the scatter matrix")
                column.pop(index)
            scatter_matrix(self.copy[matrix],figsize=self.FindingScreenSize_())
            plt.show()
        choice = input("enter yes if there is a plot you would like to view in more depth")
        if (choice.upper()=="YES"):
            for i in self.copy.columns:
                print(i)
            x = input("enter the name of the column you would like to be on the x axis")
            y = input("enter the name of the column you would like to be on the y axis")
            single_plot =DataVisulization(data = self.copy, type_of_plot="scatter",column_values_for_x=x,column_values_for_y=y)
            single_plot.driver()
    def combine(self):
        copy_of_copy = self.copy.copy()
        drop = []
        choice = input("enter yes to combine some of the columns")
        if (choice.upper() == "YES"):
            column = []
            for i in self.copy.columns:
                column.append(i)
            while(choice.upper()!="Q"):
                count = 0
                for  i in column:
                    print(f"{count}:{i}")
                    count+=1
                while (True):
                    try:
                        numerator = int(input("enter the number of the corresponding column you would like to be the numerator to be"))
                        if (numerator<= len(column)):

                            break
                        else:
                            print("please enter of of the numbers you see on the screen")
                    except ValueError:
                        print("please enter a number")
                while (True):
                    try:
                        denominator = int(input("enter the number of the corresponding column you would like to be the denominator to be"))
                        if (denominator<= len(column)):

                            break
                        else:
                            print("please enter of of the numbers you see on the screen")
                    except ValueError:
                        print("please enter a number")
                name_of_new_column = input("enter what you would like the new name of the column to be")
                self.copy[name_of_new_column]= self.copy[column[numerator]]/self.copy[column[denominator]]
                drop.append(column[numerator])
                drop.append(column[denominator])
                choice = input("enter q if that is all the columns you would like to combine")
            self.copy.drop(columns= drop, inplace=True)
            # print(self.copy.columns)
            choice = input("enter yes if you would like to view the new correlation matrix scores")
            if (choice.upper()=="YES"):
                self.high_corr.clear()
                self.corr.clear()
                self.Correlationmatrix()
                print("what do you think of those scores?")
                choice = input("enter yes if you would like to keep these new scores"
                               " or enter nothing to revert them back to the original")
                if (choice.upper()!="YES"):
                    self.copy = copy_of_copy
                elif(choice.upper()=="YES"):
                    self.df = self.copy