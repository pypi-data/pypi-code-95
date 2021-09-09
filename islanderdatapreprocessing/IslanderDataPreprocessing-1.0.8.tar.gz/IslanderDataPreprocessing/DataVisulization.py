import matplotlib.pyplot as plt
import pandas as pd
from PyQt5 import QtWidgets
import math
import sys

class NotAnOpption(Exception):
    pass
class NeedsToBeATuple(Exception):
    pass
class MissingColumnNames(Exception):
    pass

class DataVisulization:
    def __init__(self, data = None,type_of_plot = "", column_values_for_x = None, column_values_for_y = None,alpha = None):
        self.data = data
        self.alpha = alpha
        self.x = column_values_for_x
        self.y = column_values_for_y
        self.type_of_plot = type_of_plot
        plt.rcParams["figure.figsize"]= self.FindingScreenSize_()
        if type_of_plot.upper() == "HIST":
            self.Hist()
        elif(self.x is not None and self.y is not None):
            if type_of_plot.upper() == "LINE":
                self.Line()
            elif type_of_plot.upper() == "SCATTER":
                self.Scatter()
        elif(self.x is None or self.y is None):
            raise MissingColumnNames(column_values_for_x and column_values_for_y)
        else:
            raise NotAnOpption
    def FindingScreenSize_(self):
        app = QtWidgets.QApplication(sys.argv)
        screen = app.primaryScreen()
        size = screen.size()
        Screensize = (size.width()/96, size.height()/96)
        return Screensize
    def ByeByeText(self,df,varlist):
        copy = df.copy()
        count= 0
        if (isinstance(varlist,str)):
            if(copy[varlist].dtype == "object"):
                print("that will cause an error")
        else:
            for i in varlist:
                if (copy[i].dtype == "object"):
                    varlist.pop(count)
                    copy.drop(columns= i, inplace=True)
                count+=1
        return (copy)
    def Hist(self):
        final_size = self.FindingScreenSize_()
        self.data.hist(figsize= final_size)
        plt.show()
    def Line(self):
        if (isinstance(self.y, list)):
            self.DfLine()
        else:
            plt.plot(self.x,self.y)
    def DfLine(self):
        count = 1
        if (isinstance(self.y,list)):
            copy = self.ByeByeText(self.data,self.y)
            for i in self.y:
                if (math.sqrt(len(self.y)).is_integer()):
                    plt.subplot(round(math.sqrt(len(self.y))),round(math.sqrt(len(self.y))),count)
                else:
                    plt.subplot(round(math.sqrt(len(self.y))) + 1, round(math.sqrt(len(self.y))), count)

                plt.plot(copy[self.x], copy[i])
                count += 1
        elif (isinstance(self.x, list)):
            copy = self.ByeByeText(self.data, self.x)
            for i in self.x:
                if math.sqrt(len(self.x)).is_integer():
                    plt.subplot(round(math.sqrt(len(self.x))), round(math.sqrt(len(self.x))), count)
                else:
                    plt.subplot(round(math.sqrt(len(self.x))) + 1, round(math.sqrt(len(self.x))), count)

                plt.plot(copy[i], copy[self.y])
                count += 1
        else:
            plt.plot(self.data[self.x], y=self.data[self.y])

        plt.show()
    def Scatter(self):
        if (isinstance(self.data, pd.DataFrame)):
            self.Dfscatter()
        else:
            plt.scatter(x=self.x, y=self.y, alpha=self.alpha)

    def Dfscatter(self):
        count = 1
        if (isinstance(self.y, list)):
            copy = self.ByeByeText(self.data, self.y)
            for i in self.y:
                if (math.sqrt(len(self.y)).is_integer()):
                    plt.subplot(round(math.sqrt(len(self.y))), round(math.sqrt(len(self.y))), count)
                else:
                    plt.subplot(round(math.sqrt(len(self.y))) + 1, round(math.sqrt(len(self.y))), count)

                plt.scatter(copy[self.x], copy[i], alpha=self.alpha)
                count += 1
        elif (isinstance(self.x, list)):
            copy = self.ByeByeText(self.data, self.x)
            for i in self.x:
                if (math.sqrt(len(self.x)).is_integer()):
                    plt.subplot(round(math.sqrt(len(self.x))), round(math.sqrt(len(self.x))), count)
                else:
                    plt.subplot(round(math.sqrt(len(self.x))) + 1, round(math.sqrt(len(self.x))), count)

                plt.scatter(copy[i], copy[self.y], alpha=self.alpha)
                count += 1
        else:
            plt.scatter(self.data[self.x], y=self.data[self.y])

        plt.show()