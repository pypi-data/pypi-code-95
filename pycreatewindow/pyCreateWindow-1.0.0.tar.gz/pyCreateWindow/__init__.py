import sys
import pyfiglet
from colorama import Style,Fore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

def create_window(x,y):

    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl(x))
            self.setCentralWidget(self.browser)
            self.showMaximized()

            # navbar
            navbar = QToolBar()
            self.addToolBar(navbar)

            back_btn = QAction('Back', self)
            back_btn.triggered.connect(self.browser.back)
            navbar.addAction(back_btn)

            forward_btn = QAction('Forward', self)
            forward_btn.triggered.connect(self.browser.forward)
            navbar.addAction(forward_btn)

            reload_btn = QAction('Reload', self)
            reload_btn.triggered.connect(self.browser.reload)
            navbar.addAction(reload_btn)

            home_btn = QAction('Home', self)
            home_btn.triggered.connect(self.navigate_home)
            navbar.addAction(home_btn)

            self.url_bar = QLineEdit()
            self.url_bar.returnPressed.connect(self.navigate_to_url)
            navbar.addWidget(self.url_bar)

            self.browser.urlChanged.connect(self.update_url)

        def navigate_home(self):
            self.browser.setUrl(QUrl(x))

        def navigate_to_url(self):
            url = self.url_bar.text()
            self.browser.setUrl(QUrl(url))

        def update_url(self, q):
            self.url_bar.setText(q.toString())


    app = QApplication(sys.argv)
    QApplication.setApplicationName(y)
    window = MainWindow()
    app.exec_()

def info():
    info_logo = pyfiglet.figlet_format("CreateWindow")
    print(info_logo)

    print("\n---------------------------------------------------------------------------------------------------------------------------------------")
    print(Fore.YELLOW + "Information regarding pyCreateWindow : ")
    print(Style.RESET_ALL)
    print("pyCreateWindow - is used to make a standalone apps from websites urls")
    print("---------------------------------------------------------------------------------------------------------------------------------------")
    print("\n---------------------------------------------------------------------------------------------------------------------------------------")
    print(Fore.YELLOW + "Version details : ")
    print(Style.RESET_ALL)
    print("Name : " + Fore.RED + "pyCreateWindow")
    print(Style.RESET_ALL)
    print("Version : " + Fore.RED + "1.0.0")
    print(Style.RESET_ALL)
    print("Date released : " + Fore.RED + "12-09-2021")
    print(Style.RESET_ALL)
    print("Developer : " + Fore.RED + "Sujith Sourya Yedida")
    print(Style.RESET_ALL)
    print("Producer : " + Fore.RED + "TS³")
    print(Style.RESET_ALL)
    print("---------------------------------------------------------------------------------------------------------------------------------------")
    print(
        "\n---------------------------------------------------------------------------------------------------------------------------------------")
    print(Fore.YELLOW + "Developer's note : ")
    print(Style.RESET_ALL)
    print("Hi Users ! This is Sujith Sourya Yedida - the developer of this package(pyCreateWindow). Hope so that all of you would like to enjoy \nthis package in python. All the best to future programmers! \nHappy Programming !!")
    print("---------------------------------------------------------------------------------------------------------------------------------------\n")
    print(Fore.YELLOW + "@SujithSouryaYedida")
    print(Style.RESET_ALL)
def manuel():
    manuel_logo = pyfiglet.figlet_format("CreateWindow")
    print(manuel_logo)
    print(Fore.YELLOW + "\n------------------------------------------------------------------------------------------------------------")
    print("NOTE : THIS MANUEL IS DEVELOPED BY SUJITH SOURYA YEDIDA")
    print("------------------------------------------------------------------------------------------------------------")
    print(Style.RESET_ALL)
    print(
        Fore.YELLOW + "\n------------------------------------------------------------------------------------------------------------")
    print("************************** pyCreateWindow MANUEL **************************")
    print("------------------------------------------------------------------------------------------------------------")
    print(Style.RESET_ALL)
    print("First of all , we need to install this package : " + Fore.RED + "pip install pyCreateWindow")
    print(Style.RESET_ALL)
    print("pyCreateWindow.info() - this is to know more information regarding the package")
    print("pyCreateWindow.manual() - this is to get the manuel , or a guide book to use this package")
    print("pyCreateWindow.logo() - this is to get the logo of this package")
    print()
    print("pyCreateWindow.create_window(x , y) - this is to create a window")
    print("So for that you need to use the following command : " + Fore.RED + "pyCreateWindow.create_window('url','name of the site')")
    print(Style.RESET_ALL)
    print("------------------------------------------------------------------------------------------------------------------\n")

    print("\n------------------------------------------------------------------------------------------------------------------\n")
    print(Fore.YELLOW + "@SujithSouryaYedida\n")
    print(Style.RESET_ALL)
def logo():
    logo = pyfiglet.figlet_format("CreateWindow")
    print(logo)

    print(Fore.YELLOW + "\n------------------------------------------------------------------------")
    print("This logo is designed by Sujith Sourya Yedida")
    print("Presented by TS³")
    print("------------------------------------------------------------------------")
    print(Style.RESET_ALL)