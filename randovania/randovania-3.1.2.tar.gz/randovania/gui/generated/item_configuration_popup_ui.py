# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'item_configuration_popup.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from randovania.gui.lib.scroll_protected import ScrollProtectedSpinBox


class Ui_ItemConfigurationPopup(object):
    def setupUi(self, ItemConfigurationPopup):
        if not ItemConfigurationPopup.objectName():
            ItemConfigurationPopup.setObjectName(u"ItemConfigurationPopup")
        ItemConfigurationPopup.resize(534, 99)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ItemConfigurationPopup.sizePolicy().hasHeightForWidth())
        ItemConfigurationPopup.setSizePolicy(sizePolicy)
        ItemConfigurationPopup.setMaximumSize(QSize(16777215, 16777215))
        self.gridLayout_2 = QGridLayout(ItemConfigurationPopup)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.line = QFrame(ItemConfigurationPopup)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 0, 0, 1, 6)

        self.shuffled_radio = QRadioButton(ItemConfigurationPopup)
        self.shuffled_radio.setObjectName(u"shuffled_radio")

        self.gridLayout_2.addWidget(self.shuffled_radio, 1, 4, 1, 1)

        self.starting_radio = QRadioButton(ItemConfigurationPopup)
        self.starting_radio.setObjectName(u"starting_radio")

        self.gridLayout_2.addWidget(self.starting_radio, 1, 3, 1, 1)

        self.item_name_label = QLabel(ItemConfigurationPopup)
        self.item_name_label.setObjectName(u"item_name_label")

        self.gridLayout_2.addWidget(self.item_name_label, 1, 0, 1, 1)

        self.vanilla_radio = QRadioButton(ItemConfigurationPopup)
        self.vanilla_radio.setObjectName(u"vanilla_radio")

        self.gridLayout_2.addWidget(self.vanilla_radio, 1, 2, 1, 1)

        self.provided_ammo_spinbox = ScrollProtectedSpinBox(ItemConfigurationPopup)
        self.provided_ammo_spinbox.setObjectName(u"provided_ammo_spinbox")

        self.gridLayout_2.addWidget(self.provided_ammo_spinbox, 2, 4, 1, 2)

        self.provided_ammo_label = QLabel(ItemConfigurationPopup)
        self.provided_ammo_label.setObjectName(u"provided_ammo_label")
        self.provided_ammo_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.provided_ammo_label.setWordWrap(True)

        self.gridLayout_2.addWidget(self.provided_ammo_label, 2, 0, 1, 4)

        self.shuffled_spinbox = ScrollProtectedSpinBox(ItemConfigurationPopup)
        self.shuffled_spinbox.setObjectName(u"shuffled_spinbox")
        self.shuffled_spinbox.setMinimum(1)
        self.shuffled_spinbox.setMaximum(99)

        self.gridLayout_2.addWidget(self.shuffled_spinbox, 1, 5, 1, 1)

        self.excluded_radio = QRadioButton(ItemConfigurationPopup)
        self.excluded_radio.setObjectName(u"excluded_radio")

        self.gridLayout_2.addWidget(self.excluded_radio, 1, 1, 1, 1)

        self.warning_label = QLabel(ItemConfigurationPopup)
        self.warning_label.setObjectName(u"warning_label")
        self.warning_label.setWordWrap(True)

        self.gridLayout_2.addWidget(self.warning_label, 3, 0, 1, 6)


        self.retranslateUi(ItemConfigurationPopup)

        QMetaObject.connectSlotsByName(ItemConfigurationPopup)
    # setupUi

    def retranslateUi(self, ItemConfigurationPopup):
        ItemConfigurationPopup.setWindowTitle(QCoreApplication.translate("ItemConfigurationPopup", u"Item Configuration", None))
        self.shuffled_radio.setText(QCoreApplication.translate("ItemConfigurationPopup", u"Shuffled", None))
        self.starting_radio.setText(QCoreApplication.translate("ItemConfigurationPopup", u"Starting", None))
        self.item_name_label.setText(QCoreApplication.translate("ItemConfigurationPopup", u"TextLabel", None))
        self.vanilla_radio.setText(QCoreApplication.translate("ItemConfigurationPopup", u"Vanilla", None))
#if QT_CONFIG(tooltip)
        self.provided_ammo_label.setToolTip(QCoreApplication.translate("ItemConfigurationPopup", u"<html><head/><body><p>When this item is collected, it also gives this amount of the given ammos.</p><p>This is included in the calculation of how much each pickup of this ammo gives.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.provided_ammo_label.setText(QCoreApplication.translate("ItemConfigurationPopup", u"<html><head/><body><p>Provided Ammo (XXXX and YYYY)</p></body></html>", None))
        self.excluded_radio.setText(QCoreApplication.translate("ItemConfigurationPopup", u"Excluded", None))
        self.warning_label.setText("")
    # retranslateUi

