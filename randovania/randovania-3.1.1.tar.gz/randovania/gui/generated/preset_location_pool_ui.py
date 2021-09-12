# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preset_location_pool.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_PresetLocationPool(object):
    def setupUi(self, PresetLocationPool):
        if not PresetLocationPool.objectName():
            PresetLocationPool.setObjectName(u"PresetLocationPool")
        PresetLocationPool.resize(505, 463)
        self.centralWidget = QWidget(PresetLocationPool)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.randomization_mode_group = QGroupBox(self.centralWidget)
        self.randomization_mode_group.setObjectName(u"randomization_mode_group")
        self.verticalLayout_2 = QVBoxLayout(self.randomization_mode_group)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.randomization_mode_label = QLabel(self.randomization_mode_group)
        self.randomization_mode_label.setObjectName(u"randomization_mode_label")
        self.randomization_mode_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.randomization_mode_label)

        self.randomization_mode_combo = QComboBox(self.randomization_mode_group)
        self.randomization_mode_combo.addItem("")
        self.randomization_mode_combo.addItem("")
        self.randomization_mode_combo.setObjectName(u"randomization_mode_combo")

        self.verticalLayout_2.addWidget(self.randomization_mode_combo)


        self.verticalLayout.addWidget(self.randomization_mode_group)

        self.excluded_locations_group = QGroupBox(self.centralWidget)
        self.excluded_locations_group.setObjectName(u"excluded_locations_group")
        self.verticalLayout_5 = QVBoxLayout(self.excluded_locations_group)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(2, 3, 2, 0)
        self.excluded_locations_label = QLabel(self.excluded_locations_group)
        self.excluded_locations_label.setObjectName(u"excluded_locations_label")

        self.verticalLayout_5.addWidget(self.excluded_locations_label)

        self.excluded_locations_area = QScrollArea(self.excluded_locations_group)
        self.excluded_locations_area.setObjectName(u"excluded_locations_area")
        self.excluded_locations_area.setWidgetResizable(True)
        self.excluded_locations_area_contents = QWidget()
        self.excluded_locations_area_contents.setObjectName(u"excluded_locations_area_contents")
        self.excluded_locations_area_contents.setGeometry(QRect(0, 0, 489, 244))
        self.excluded_locations_area_layout = QHBoxLayout(self.excluded_locations_area_contents)
        self.excluded_locations_area_layout.setSpacing(6)
        self.excluded_locations_area_layout.setContentsMargins(11, 11, 11, 11)
        self.excluded_locations_area_layout.setObjectName(u"excluded_locations_area_layout")
        self.excluded_locations_area_layout.setContentsMargins(0, 0, 0, 0)
        self.excluded_locations_area.setWidget(self.excluded_locations_area_contents)

        self.verticalLayout_5.addWidget(self.excluded_locations_area)


        self.verticalLayout.addWidget(self.excluded_locations_group)

        PresetLocationPool.setCentralWidget(self.centralWidget)

        self.retranslateUi(PresetLocationPool)

        QMetaObject.connectSlotsByName(PresetLocationPool)
    # setupUi

    def retranslateUi(self, PresetLocationPool):
        PresetLocationPool.setWindowTitle(QCoreApplication.translate("PresetLocationPool", u"Location Pool", None))
        self.randomization_mode_group.setTitle(QCoreApplication.translate("PresetLocationPool", u"Randomization Mode", None))
        self.randomization_mode_label.setText(QCoreApplication.translate("PresetLocationPool", u"<html><head/><body><p>This setting controls how Randovania will shuffle items.</p><p><span style=\" font-weight:600;\">Full:</span> All items can be placed in any location.</p><p><span style=\" font-weight:600;\">Major/minor split:</span> Major items (i.e., major upgrades, Energy Tanks, Dark Temple Keys, and Energy Transfer Modules) and minor items (i.e, expansions) will be shuffled separately. Major items in excess of the number of major locations will be placed in minor locations, and vice versa.</p></body></html>", None))
        self.randomization_mode_combo.setItemText(0, QCoreApplication.translate("PresetLocationPool", u"Full", None))
        self.randomization_mode_combo.setItemText(1, QCoreApplication.translate("PresetLocationPool", u"Major/minor split", None))

        self.excluded_locations_group.setTitle(QCoreApplication.translate("PresetLocationPool", u"Available Locations", None))
        self.excluded_locations_label.setText(QCoreApplication.translate("PresetLocationPool", u"<html><head/><body><p>Choose which locations are considered for placing items.</p></body></html>", None))
    # retranslateUi

