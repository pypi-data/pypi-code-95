# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preset_prime_patches.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_PresetPrimePatches(object):
    def setupUi(self, PresetPrimePatches):
        if not PresetPrimePatches.objectName():
            PresetPrimePatches.setObjectName(u"PresetPrimePatches")
        PresetPrimePatches.resize(503, 675)
        self.centralWidget = QWidget(PresetPrimePatches)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea(self.centralWidget)
        self.scroll_area.setObjectName(u"scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_contents = QWidget()
        self.scroll_contents.setObjectName(u"scroll_contents")
        self.scroll_contents.setGeometry(QRect(0, 0, 487, 1189))
        self.scroll_layout = QVBoxLayout(self.scroll_contents)
        self.scroll_layout.setSpacing(6)
        self.scroll_layout.setContentsMargins(11, 11, 11, 11)
        self.scroll_layout.setObjectName(u"scroll_layout")
        self.scroll_layout.setContentsMargins(0, 2, 0, 0)
        self.top_spacer = QSpacerItem(20, 8, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.scroll_layout.addItem(self.top_spacer)

        self.warp_to_start_group = QGroupBox(self.scroll_contents)
        self.warp_to_start_group.setObjectName(u"warp_to_start_group")
        self.verticalLayout_6 = QVBoxLayout(self.warp_to_start_group)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.warp_to_start_check = QCheckBox(self.warp_to_start_group)
        self.warp_to_start_check.setObjectName(u"warp_to_start_check")

        self.verticalLayout_6.addWidget(self.warp_to_start_check)

        self.warp_to_start_label = QLabel(self.warp_to_start_group)
        self.warp_to_start_label.setObjectName(u"warp_to_start_label")
        self.warp_to_start_label.setWordWrap(True)

        self.verticalLayout_6.addWidget(self.warp_to_start_label)


        self.scroll_layout.addWidget(self.warp_to_start_group)

        self.qol_group = QGroupBox(self.scroll_contents)
        self.qol_group.setObjectName(u"qol_group")
        self.verticalLayout_2 = QVBoxLayout(self.qol_group)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.description_label = QLabel(self.qol_group)
        self.description_label.setObjectName(u"description_label")
        self.description_label.setWordWrap(True)
        self.description_label.setOpenExternalLinks(True)

        self.verticalLayout_2.addWidget(self.description_label)

        self.groupBox = QGroupBox(self.qol_group)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.main_plaza_door_check = QCheckBox(self.groupBox)
        self.main_plaza_door_check.setObjectName(u"main_plaza_door_check")

        self.verticalLayout_3.addWidget(self.main_plaza_door_check)

        self.main_plaza_door_label = QLabel(self.groupBox)
        self.main_plaza_door_label.setObjectName(u"main_plaza_door_label")

        self.verticalLayout_3.addWidget(self.main_plaza_door_label)

        self.backwards_frigate_check = QCheckBox(self.groupBox)
        self.backwards_frigate_check.setObjectName(u"backwards_frigate_check")

        self.verticalLayout_3.addWidget(self.backwards_frigate_check)

        self.backwards_frigate_label = QLabel(self.groupBox)
        self.backwards_frigate_label.setObjectName(u"backwards_frigate_label")

        self.verticalLayout_3.addWidget(self.backwards_frigate_label)

        self.backwards_labs_check = QCheckBox(self.groupBox)
        self.backwards_labs_check.setObjectName(u"backwards_labs_check")

        self.verticalLayout_3.addWidget(self.backwards_labs_check)

        self.backwards_labs_label = QLabel(self.groupBox)
        self.backwards_labs_label.setObjectName(u"backwards_labs_label")

        self.verticalLayout_3.addWidget(self.backwards_labs_label)

        self.backwards_upper_mines_check = QCheckBox(self.groupBox)
        self.backwards_upper_mines_check.setObjectName(u"backwards_upper_mines_check")

        self.verticalLayout_3.addWidget(self.backwards_upper_mines_check)

        self.backwards_upper_mines_label = QLabel(self.groupBox)
        self.backwards_upper_mines_label.setObjectName(u"backwards_upper_mines_label")

        self.verticalLayout_3.addWidget(self.backwards_upper_mines_label)

        self.backwards_lower_mines_check = QCheckBox(self.groupBox)
        self.backwards_lower_mines_check.setObjectName(u"backwards_lower_mines_check")

        self.verticalLayout_3.addWidget(self.backwards_lower_mines_check)

        self.backwards_lower_mines_label = QLabel(self.groupBox)
        self.backwards_lower_mines_label.setObjectName(u"backwards_lower_mines_label")

        self.verticalLayout_3.addWidget(self.backwards_lower_mines_label)

        self.phazon_elite_without_dynamo_check = QCheckBox(self.groupBox)
        self.phazon_elite_without_dynamo_check.setObjectName(u"phazon_elite_without_dynamo_check")

        self.verticalLayout_3.addWidget(self.phazon_elite_without_dynamo_check)

        self.phazon_elite_without_dynamo_label = QLabel(self.groupBox)
        self.phazon_elite_without_dynamo_label.setObjectName(u"phazon_elite_without_dynamo_label")

        self.verticalLayout_3.addWidget(self.phazon_elite_without_dynamo_label)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.qol_game_breaking_check = QCheckBox(self.qol_group)
        self.qol_game_breaking_check.setObjectName(u"qol_game_breaking_check")
        self.qol_game_breaking_check.setEnabled(True)

        self.verticalLayout_2.addWidget(self.qol_game_breaking_check)

        self.qol_game_breaking_label = QLabel(self.qol_group)
        self.qol_game_breaking_label.setObjectName(u"qol_game_breaking_label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qol_game_breaking_label.sizePolicy().hasHeightForWidth())
        self.qol_game_breaking_label.setSizePolicy(sizePolicy)
        self.qol_game_breaking_label.setMaximumSize(QSize(16777215, 60))
        self.qol_game_breaking_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.qol_game_breaking_label.setWordWrap(True)
        self.qol_game_breaking_label.setOpenExternalLinks(True)

        self.verticalLayout_2.addWidget(self.qol_game_breaking_label)

        self.qol_cosmetic_check = QCheckBox(self.qol_group)
        self.qol_cosmetic_check.setObjectName(u"qol_cosmetic_check")
        self.qol_cosmetic_check.setEnabled(False)
        self.qol_cosmetic_check.setChecked(True)

        self.verticalLayout_2.addWidget(self.qol_cosmetic_check)

        self.qol_cosmetic_label = QLabel(self.qol_group)
        self.qol_cosmetic_label.setObjectName(u"qol_cosmetic_label")
        self.qol_cosmetic_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.qol_cosmetic_label)

        self.qol_pickup_scans_check = QCheckBox(self.qol_group)
        self.qol_pickup_scans_check.setObjectName(u"qol_pickup_scans_check")

        self.verticalLayout_2.addWidget(self.qol_pickup_scans_check)

        self.qol_pickup_scans_label = QLabel(self.qol_group)
        self.qol_pickup_scans_label.setObjectName(u"qol_pickup_scans_label")
        self.qol_pickup_scans_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.qol_pickup_scans_label)


        self.scroll_layout.addWidget(self.qol_group)

        self.cutscene_group = QGroupBox(self.scroll_contents)
        self.cutscene_group.setObjectName(u"cutscene_group")
        self.verticalLayout_5 = QVBoxLayout(self.cutscene_group)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.cutscene_combo = QComboBox(self.cutscene_group)
        self.cutscene_combo.addItem("")
        self.cutscene_combo.addItem("")
        self.cutscene_combo.addItem("")
        self.cutscene_combo.addItem("")
        self.cutscene_combo.setObjectName(u"cutscene_combo")

        self.verticalLayout_5.addWidget(self.cutscene_combo)

        self.cutscene_label = QLabel(self.cutscene_group)
        self.cutscene_label.setObjectName(u"cutscene_label")
        self.cutscene_label.setWordWrap(True)

        self.verticalLayout_5.addWidget(self.cutscene_label)


        self.scroll_layout.addWidget(self.cutscene_group)

        self.small_samus_group = QGroupBox(self.scroll_contents)
        self.small_samus_group.setObjectName(u"small_samus_group")
        self.verticalLayout_4 = QVBoxLayout(self.small_samus_group)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.small_samus_check = QCheckBox(self.small_samus_group)
        self.small_samus_check.setObjectName(u"small_samus_check")

        self.verticalLayout_4.addWidget(self.small_samus_check)

        self.small_samus_label = QLabel(self.small_samus_group)
        self.small_samus_label.setObjectName(u"small_samus_label")
        self.small_samus_label.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.small_samus_label)


        self.scroll_layout.addWidget(self.small_samus_group)

        self.scroll_area.setWidget(self.scroll_contents)

        self.verticalLayout.addWidget(self.scroll_area)

        PresetPrimePatches.setCentralWidget(self.centralWidget)

        self.retranslateUi(PresetPrimePatches)

        QMetaObject.connectSlotsByName(PresetPrimePatches)
    # setupUi

    def retranslateUi(self, PresetPrimePatches):
        PresetPrimePatches.setWindowTitle(QCoreApplication.translate("PresetPrimePatches", u"Other", None))
        self.warp_to_start_group.setTitle(QCoreApplication.translate("PresetPrimePatches", u"Warp to Start", None))
        self.warp_to_start_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Add warping to starting location from save stations", None))
        self.warp_to_start_label.setText(QCoreApplication.translate("PresetPrimePatches", u"<html><head/><body><p>Refusing to save at any Save Station while holding L+R will warp you to the starting location (by default, Samus' ship in Landing Site).</p></body></html>", None))
        self.qol_group.setTitle(QCoreApplication.translate("PresetPrimePatches", u"Quality of life", None))
        self.description_label.setText(QCoreApplication.translate("PresetPrimePatches", u"<html><head/><body><p>In order to improve the game experience, many quality of life changes are provided separated in 5 different groups.</p><p>For in-depth list of changes, see <a href=\"https://github.com/toasterparty/randomprime/blob/randovania/doc/quality_of_life.md\"><span style=\" text-decoration: underline; color:#0000ff;\">Quality of Life</span></a>.</p></body></html>", None))
        self.groupBox.setTitle(QCoreApplication.translate("PresetPrimePatches", u"Logical changes", None))
        self.main_plaza_door_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Main Plaza Vault Door", None))
        self.main_plaza_door_label.setText(QCoreApplication.translate("PresetPrimePatches", u"Allow access to Vault from Main Plaza", None))
        self.backwards_frigate_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Backwards Frigate", None))
        self.backwards_frigate_label.setText(QCoreApplication.translate("PresetPrimePatches", u"Power door in Main Ventilation Shaft Section B when approached from behind", None))
        self.backwards_labs_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Backwards Labs", None))
        self.backwards_labs_label.setText(QCoreApplication.translate("PresetPrimePatches", u"Scan through barrier of Research Lab Hydra when approached from deep labs", None))
        self.backwards_upper_mines_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Backwards Upper Mines", None))
        self.backwards_upper_mines_label.setText(QCoreApplication.translate("PresetPrimePatches", u"Disable Main Quarry barrier automatically when approached from Mine Security Station", None))
        self.backwards_lower_mines_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Backwards Lower Mines", None))
        self.backwards_lower_mines_label.setText(QCoreApplication.translate("PresetPrimePatches", u"Remove PCA locks and allow passing through lower mines scan barriers from the back", None))
        self.phazon_elite_without_dynamo_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Phazon Elite without Dynamo", None))
        self.phazon_elite_without_dynamo_label.setText(QCoreApplication.translate("PresetPrimePatches", u"Removes the Central Dynamo item requirement for activating the Phazon Elite boss fight", None))
        self.qol_game_breaking_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Game Breaking", None))
        self.qol_game_breaking_label.setText(QCoreApplication.translate("PresetPrimePatches", u"<html><head/><body><p>Fixes softlocks and wrong room spawn points. Reverts changes made in later game versions.<br/>Logic always assume this is enabled.</p></body></html>", None))
        self.qol_cosmetic_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Cosmetic", None))
        self.qol_cosmetic_label.setText(QCoreApplication.translate("PresetPrimePatches", u"<html><head/><body><p>Remove or change things that only affect real time, not in-game time.<br/>This group is controlled by an user preference and changing it does not affect the permalink.</p></body></html>", None))
        self.qol_pickup_scans_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Pickup Scans", None))
        self.qol_pickup_scans_label.setText(QCoreApplication.translate("PresetPrimePatches", u"Enable this option to patch various item locations so that they can be scanned. Only locations whose model is visible in combat visor are affected. Note that the new scan may be near the item, not necessarily on top of it.", None))
        self.cutscene_group.setTitle(QCoreApplication.translate("PresetPrimePatches", u"Cutscene removal mode", None))
        self.cutscene_combo.setItemText(0, QCoreApplication.translate("PresetPrimePatches", u"Original", None))
        self.cutscene_combo.setItemText(1, QCoreApplication.translate("PresetPrimePatches", u"Competitive", None))
        self.cutscene_combo.setItemText(2, QCoreApplication.translate("PresetPrimePatches", u"Minor", None))
        self.cutscene_combo.setItemText(3, QCoreApplication.translate("PresetPrimePatches", u"Major", None))

        self.cutscene_label.setText(QCoreApplication.translate("PresetPrimePatches", u"<html><head/><body><p><span style=\" font-weight:600;\">Original</span>: No changes to the cutscenes are made.</p><p><span style=\" font-weight:600;\">Competitive</span>: Similar to minor, but leaves a few rooms alone where skipping cutscenes would be inappropriate for races.</p><p><span style=\" font-weight:600;\">Minor</span>: Removes cutscenes that don't affect the game too much when removed.</p><p><span style=\" font-weight:600;\">Major</span>: Allows you to continue playing the game while cutscenes happen.</p></body></html>", None))
        self.small_samus_group.setTitle(QCoreApplication.translate("PresetPrimePatches", u"Small Samus", None))
        self.small_samus_check.setText(QCoreApplication.translate("PresetPrimePatches", u"Enable Small Samus", None))
        self.small_samus_label.setText(QCoreApplication.translate("PresetPrimePatches", u"<html><head/><body><p>In this mode, Samus is scaled to 30% of her normal size. Expect to be able to fit in many places you weren't before, but also fall down in a lot of holes you didn't before.</p><p><span style=\" font-weight:600;\">Warning:</span> This option has been known to induce motion sickness and nausea in some players. If you are concerned you may suffer from these symptoms, it may be best to avoid playing with this setting enabled.</p></body></html>", None))
    # retranslateUi

