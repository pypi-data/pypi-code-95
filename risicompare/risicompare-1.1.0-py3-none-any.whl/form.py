# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.1.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_Risicompare(object):
    def setupUi(self, Risicompare):
        if not Risicompare.objectName():
            Risicompare.setObjectName(u"Risicompare")
        Risicompare.resize(1114, 801)
        self.bulkFileButton = QAction(Risicompare)
        self.bulkFileButton.setObjectName(u"bulkFileButton")
        self.identifierFileButton = QAction(Risicompare)
        self.identifierFileButton.setObjectName(u"identifierFileButton")
        self.beginningButton = QAction(Risicompare)
        self.beginningButton.setObjectName(u"beginningButton")
        self.quitButton = QAction(Risicompare)
        self.quitButton.setObjectName(u"quitButton")
        self.helpButton = QAction(Risicompare)
        self.helpButton.setObjectName(u"helpButton")
        self.showImagesButton = QAction(Risicompare)
        self.showImagesButton.setObjectName(u"showImagesButton")
        self.showImagesButton.setCheckable(True)
        self.showImagesButton.setChecked(True)
        self.numParagraphButton = QAction(Risicompare)
        self.numParagraphButton.setObjectName(u"numParagraphButton")
        self.versionButton = QAction(Risicompare)
        self.versionButton.setObjectName(u"versionButton")
        self.centralwidget = QWidget(Risicompare)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.leftButton = QPushButton(self.centralwidget)
        self.leftButton.setObjectName(u"leftButton")

        self.verticalLayout.addWidget(self.leftButton)

        self.rightButton = QPushButton(self.centralwidget)
        self.rightButton.setObjectName(u"rightButton")

        self.verticalLayout.addWidget(self.rightButton)


        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)

        self.htmlButton = QPushButton(self.centralwidget)
        self.htmlButton.setObjectName(u"htmlButton")

        self.gridLayout.addWidget(self.htmlButton, 2, 0, 1, 4)

        self.identifierList = QListWidget(self.centralwidget)
        self.identifierList.setObjectName(u"identifierList")

        self.gridLayout.addWidget(self.identifierList, 0, 2, 1, 1)

        self.bulkList = QListWidget(self.centralwidget)
        self.bulkList.setObjectName(u"bulkList")

        self.gridLayout.addWidget(self.bulkList, 0, 0, 1, 1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.upButton = QPushButton(self.centralwidget)
        self.upButton.setObjectName(u"upButton")

        self.verticalLayout_2.addWidget(self.upButton)

        self.downButton = QPushButton(self.centralwidget)
        self.downButton.setObjectName(u"downButton")

        self.verticalLayout_2.addWidget(self.downButton)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 3, 1, 1)

        self.outputButton = QPushButton(self.centralwidget)
        self.outputButton.setObjectName(u"outputButton")

        self.gridLayout.addWidget(self.outputButton, 1, 0, 1, 4)

        Risicompare.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Risicompare)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1114, 19))
        self.menuSave = QMenu(self.menubar)
        self.menuSave.setObjectName(u"menuSave")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        Risicompare.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Risicompare)
        self.statusbar.setObjectName(u"statusbar")
        Risicompare.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.identifierList, self.bulkList)
        QWidget.setTabOrder(self.bulkList, self.upButton)
        QWidget.setTabOrder(self.upButton, self.downButton)
        QWidget.setTabOrder(self.downButton, self.leftButton)
        QWidget.setTabOrder(self.leftButton, self.rightButton)
        QWidget.setTabOrder(self.rightButton, self.outputButton)
        QWidget.setTabOrder(self.outputButton, self.htmlButton)

        self.menubar.addAction(self.menuSave.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuSave.addAction(self.bulkFileButton)
        self.menuSave.addAction(self.identifierFileButton)
        self.menuSave.addAction(self.showImagesButton)
        self.menuSave.addAction(self.numParagraphButton)
        self.menuSave.addAction(self.quitButton)
        self.menuHelp.addAction(self.helpButton)
        self.menuHelp.addAction(self.versionButton)

        self.retranslateUi(Risicompare)

        QMetaObject.connectSlotsByName(Risicompare)
    # setupUi

    def retranslateUi(self, Risicompare):
        Risicompare.setWindowTitle(QCoreApplication.translate("Risicompare", u"Risicompare", None))
        self.bulkFileButton.setText(QCoreApplication.translate("Risicompare", u"Bulk file", None))
        self.identifierFileButton.setText(QCoreApplication.translate("Risicompare", u"Identifier file", None))
        self.beginningButton.setText(QCoreApplication.translate("Risicompare", u"Go back to Beginning", None))
        self.quitButton.setText(QCoreApplication.translate("Risicompare", u"Quit", None))
#if QT_CONFIG(shortcut)
        self.quitButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.helpButton.setText(QCoreApplication.translate("Risicompare", u"Help", None))
#if QT_CONFIG(shortcut)
        self.helpButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+H", None))
#endif // QT_CONFIG(shortcut)
        self.showImagesButton.setText(QCoreApplication.translate("Risicompare", u"Show images", None))
        self.numParagraphButton.setText(QCoreApplication.translate("Risicompare", u"Number of  paragraph to show", None))
        self.versionButton.setText(QCoreApplication.translate("Risicompare", u"Version", None))
        self.leftButton.setText(QCoreApplication.translate("Risicompare", u"Move left", None))
#if QT_CONFIG(shortcut)
        self.leftButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+Left", None))
#endif // QT_CONFIG(shortcut)
        self.rightButton.setText(QCoreApplication.translate("Risicompare", u"Move right", None))
#if QT_CONFIG(shortcut)
        self.rightButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+Right", None))
#endif // QT_CONFIG(shortcut)
        self.htmlButton.setText(QCoreApplication.translate("Risicompare", u"Produce HTML", None))
#if QT_CONFIG(shortcut)
        self.htmlButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.upButton.setText(QCoreApplication.translate("Risicompare", u"Move up", None))
#if QT_CONFIG(shortcut)
        self.upButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+Up", None))
#endif // QT_CONFIG(shortcut)
        self.downButton.setText(QCoreApplication.translate("Risicompare", u"Move down", None))
#if QT_CONFIG(shortcut)
        self.downButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+Down", None))
#endif // QT_CONFIG(shortcut)
        self.outputButton.setText(QCoreApplication.translate("Risicompare", u"Write HTML file to...", None))
#if QT_CONFIG(shortcut)
        self.outputButton.setShortcut(QCoreApplication.translate("Risicompare", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.menuSave.setTitle(QCoreApplication.translate("Risicompare", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("Risicompare", u"About", None))
    # retranslateUi

