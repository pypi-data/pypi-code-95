# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preset_logic_damage.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_PresetLogicDamage(object):
    def setupUi(self, PresetLogicDamage):
        if not PresetLogicDamage.objectName():
            PresetLogicDamage.setObjectName(u"PresetLogicDamage")
        PresetLogicDamage.resize(505, 463)
        self.centralWidget = QWidget(PresetLogicDamage)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.damage_strictness_group = QGroupBox(self.centralWidget)
        self.damage_strictness_group.setObjectName(u"damage_strictness_group")
        self.damage_strictness_layout = QVBoxLayout(self.damage_strictness_group)
        self.damage_strictness_layout.setSpacing(6)
        self.damage_strictness_layout.setContentsMargins(11, 11, 11, 11)
        self.damage_strictness_layout.setObjectName(u"damage_strictness_layout")
        self.damage_strictness_label = QLabel(self.damage_strictness_group)
        self.damage_strictness_label.setObjectName(u"damage_strictness_label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.damage_strictness_label.sizePolicy().hasHeightForWidth())
        self.damage_strictness_label.setSizePolicy(sizePolicy)
        self.damage_strictness_label.setWordWrap(True)

        self.damage_strictness_layout.addWidget(self.damage_strictness_label)

        self.damage_strictness_spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.damage_strictness_layout.addItem(self.damage_strictness_spacer)

        self.damage_strictness_combo = QComboBox(self.damage_strictness_group)
        self.damage_strictness_combo.addItem("")
        self.damage_strictness_combo.addItem("")
        self.damage_strictness_combo.addItem("")
        self.damage_strictness_combo.setObjectName(u"damage_strictness_combo")

        self.damage_strictness_layout.addWidget(self.damage_strictness_combo)


        self.verticalLayout.addWidget(self.damage_strictness_group)

        self.damage_strictness_spacer_2 = QSpacerItem(20, 302, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.damage_strictness_spacer_2)

        PresetLogicDamage.setCentralWidget(self.centralWidget)

        self.retranslateUi(PresetLogicDamage)

        QMetaObject.connectSlotsByName(PresetLogicDamage)
    # setupUi

    def retranslateUi(self, PresetLogicDamage):
        PresetLogicDamage.setWindowTitle(QCoreApplication.translate("PresetLogicDamage", u"Damage", None))
        self.damage_strictness_group.setTitle(QCoreApplication.translate("PresetLogicDamage", u"Logic damage strictness", None))
        self.damage_strictness_label.setText(QCoreApplication.translate("PresetLogicDamage", u"<html><head/><body><p>Certain locations, such as rooms without safe zones in Dark Aether or bosses, requires a certain number of energy tanks (or suits).</p><p>This setting controls how much energy the logic will expect you to have to reach these locations.</p></body></html>", None))
        self.damage_strictness_combo.setItemText(0, QCoreApplication.translate("PresetLogicDamage", u"Strict (1\u00d7)", None))
        self.damage_strictness_combo.setItemText(1, QCoreApplication.translate("PresetLogicDamage", u"Medium (1.5\u00d7)", None))
        self.damage_strictness_combo.setItemText(2, QCoreApplication.translate("PresetLogicDamage", u"Lenient (2\u00d7)", None))

        self.damage_strictness_combo.setCurrentText(QCoreApplication.translate("PresetLogicDamage", u"Strict (1\u00d7)", None))
    # retranslateUi

