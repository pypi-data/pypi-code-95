# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'logic_settings_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_LogicSettingsWindow(object):
    def setupUi(self, LogicSettingsWindow):
        if not LogicSettingsWindow.objectName():
            LogicSettingsWindow.setObjectName(u"LogicSettingsWindow")
        LogicSettingsWindow.resize(697, 737)
        self.verticalLayout = QVBoxLayout(LogicSettingsWindow)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 4, 0, 0)
        self.menuBar = QMenuBar(LogicSettingsWindow)
        self.menuBar.setObjectName(u"menuBar")

        self.verticalLayout.addWidget(self.menuBar)

        self.name_layout = QHBoxLayout()
        self.name_layout.setSpacing(6)
        self.name_layout.setObjectName(u"name_layout")
        self.name_label = QLabel(LogicSettingsWindow)
        self.name_label.setObjectName(u"name_label")

        self.name_layout.addWidget(self.name_label)

        self.name_edit = QLineEdit(LogicSettingsWindow)
        self.name_edit.setObjectName(u"name_edit")

        self.name_layout.addWidget(self.name_edit)


        self.verticalLayout.addLayout(self.name_layout)

        self.main_tab_widget = QTabWidget(LogicSettingsWindow)
        self.main_tab_widget.setObjectName(u"main_tab_widget")
        self.logic_tab = QWidget()
        self.logic_tab.setObjectName(u"logic_tab")
        self.logic_tab_layout = QVBoxLayout(self.logic_tab)
        self.logic_tab_layout.setSpacing(6)
        self.logic_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.logic_tab_layout.setObjectName(u"logic_tab_layout")
        self.logic_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.logic_tab_widget = QTabWidget(self.logic_tab)
        self.logic_tab_widget.setObjectName(u"logic_tab_widget")

        self.logic_tab_layout.addWidget(self.logic_tab_widget)

        self.main_tab_widget.addTab(self.logic_tab, "")
        self.patches_tab = QWidget()
        self.patches_tab.setObjectName(u"patches_tab")
        self.patches_tab_layout = QVBoxLayout(self.patches_tab)
        self.patches_tab_layout.setSpacing(6)
        self.patches_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.patches_tab_layout.setObjectName(u"patches_tab_layout")
        self.patches_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.patches_tab_widget = QTabWidget(self.patches_tab)
        self.patches_tab_widget.setObjectName(u"patches_tab_widget")

        self.patches_tab_layout.addWidget(self.patches_tab_widget)

        self.main_tab_widget.addTab(self.patches_tab, "")

        self.verticalLayout.addWidget(self.main_tab_widget)

        self.button_box = QDialogButtonBox(LogicSettingsWindow)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(LogicSettingsWindow)

        self.main_tab_widget.setCurrentIndex(0)
        self.logic_tab_widget.setCurrentIndex(-1)
        self.patches_tab_widget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(LogicSettingsWindow)
    # setupUi

    def retranslateUi(self, LogicSettingsWindow):
        LogicSettingsWindow.setWindowTitle(QCoreApplication.translate("LogicSettingsWindow", u"Customize Preset", None))
        self.name_label.setText(QCoreApplication.translate("LogicSettingsWindow", u"Name:", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.logic_tab), QCoreApplication.translate("LogicSettingsWindow", u"Randomizer Logic", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.patches_tab), QCoreApplication.translate("LogicSettingsWindow", u"Game Modifications", None))
    # retranslateUi

