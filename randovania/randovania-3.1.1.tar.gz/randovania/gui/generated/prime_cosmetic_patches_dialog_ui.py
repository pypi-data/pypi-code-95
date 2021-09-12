# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'prime_cosmetic_patches_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_PrimeCosmeticPatchesDialog(object):
    def setupUi(self, PrimeCosmeticPatchesDialog):
        if not PrimeCosmeticPatchesDialog.objectName():
            PrimeCosmeticPatchesDialog.setObjectName(u"PrimeCosmeticPatchesDialog")
        PrimeCosmeticPatchesDialog.resize(424, 203)
        self.gridLayout = QGridLayout(PrimeCosmeticPatchesDialog)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setObjectName(u"gridLayout")
        self.reset_button = QPushButton(PrimeCosmeticPatchesDialog)
        self.reset_button.setObjectName(u"reset_button")

        self.gridLayout.addWidget(self.reset_button, 2, 2, 1, 1)

        self.accept_button = QPushButton(PrimeCosmeticPatchesDialog)
        self.accept_button.setObjectName(u"accept_button")

        self.gridLayout.addWidget(self.accept_button, 2, 0, 1, 1)

        self.cancel_button = QPushButton(PrimeCosmeticPatchesDialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.gridLayout.addWidget(self.cancel_button, 2, 1, 1, 1)

        self.scrollArea = QScrollArea(PrimeCosmeticPatchesDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scroll_area_contents = QWidget()
        self.scroll_area_contents.setObjectName(u"scroll_area_contents")
        self.scroll_area_contents.setGeometry(QRect(0, 0, 404, 155))
        self.verticalLayout = QVBoxLayout(self.scroll_area_contents)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.game_changes_box = QGroupBox(self.scroll_area_contents)
        self.game_changes_box.setObjectName(u"game_changes_box")
        self.game_changes_layout = QVBoxLayout(self.game_changes_box)
        self.game_changes_layout.setSpacing(6)
        self.game_changes_layout.setContentsMargins(11, 11, 11, 11)
        self.game_changes_layout.setObjectName(u"game_changes_layout")
        self.qol_cosmetic_check = QCheckBox(self.game_changes_box)
        self.qol_cosmetic_check.setObjectName(u"qol_cosmetic_check")

        self.game_changes_layout.addWidget(self.qol_cosmetic_check)

        self.open_map_check = QCheckBox(self.game_changes_box)
        self.open_map_check.setObjectName(u"open_map_check")

        self.game_changes_layout.addWidget(self.open_map_check)


        self.verticalLayout.addWidget(self.game_changes_box)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scroll_area_contents)

        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 3)


        self.retranslateUi(PrimeCosmeticPatchesDialog)

        QMetaObject.connectSlotsByName(PrimeCosmeticPatchesDialog)
    # setupUi

    def retranslateUi(self, PrimeCosmeticPatchesDialog):
        PrimeCosmeticPatchesDialog.setWindowTitle(QCoreApplication.translate("PrimeCosmeticPatchesDialog", u"Metroid Prime 1 - Cosmetic Options", None))
        self.reset_button.setText(QCoreApplication.translate("PrimeCosmeticPatchesDialog", u"Reset to Defaults", None))
        self.accept_button.setText(QCoreApplication.translate("PrimeCosmeticPatchesDialog", u"Accept", None))
        self.cancel_button.setText(QCoreApplication.translate("PrimeCosmeticPatchesDialog", u"Cancel", None))
        self.game_changes_box.setTitle(QCoreApplication.translate("PrimeCosmeticPatchesDialog", u"Game Changes", None))
        self.qol_cosmetic_check.setText(QCoreApplication.translate("PrimeCosmeticPatchesDialog", u"Enable QOL Cosmetic", None))
        self.open_map_check.setText(QCoreApplication.translate("PrimeCosmeticPatchesDialog", u"Open map from start", None))
    # retranslateUi

