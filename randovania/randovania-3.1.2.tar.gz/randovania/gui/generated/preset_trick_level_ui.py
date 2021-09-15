# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preset_trick_level.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_PresetTrickLevel(object):
    def setupUi(self, PresetTrickLevel):
        if not PresetTrickLevel.objectName():
            PresetTrickLevel.setObjectName(u"PresetTrickLevel")
        PresetTrickLevel.resize(539, 516)
        self.centralWidget = QWidget(PresetTrickLevel)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.trick_level_scroll = QScrollArea(self.centralWidget)
        self.trick_level_scroll.setObjectName(u"trick_level_scroll")
        self.trick_level_scroll.setFrameShape(QFrame.NoFrame)
        self.trick_level_scroll.setFrameShadow(QFrame.Plain)
        self.trick_level_scroll.setWidgetResizable(True)
        self.trick_level_scroll_contents = QWidget()
        self.trick_level_scroll_contents.setObjectName(u"trick_level_scroll_contents")
        self.trick_level_scroll_contents.setGeometry(QRect(0, 0, 525, 729))
        self.trick_level_layout = QVBoxLayout(self.trick_level_scroll_contents)
        self.trick_level_layout.setSpacing(6)
        self.trick_level_layout.setContentsMargins(11, 11, 11, 11)
        self.trick_level_layout.setObjectName(u"trick_level_layout")
        self.trick_level_layout.setContentsMargins(4, 8, 4, 0)
        self.logic_description_label = QLabel(self.trick_level_scroll_contents)
        self.logic_description_label.setObjectName(u"logic_description_label")
        self.logic_description_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.logic_description_label.setWordWrap(True)

        self.trick_level_layout.addWidget(self.logic_description_label)

        self.trick_level_line_1 = QFrame(self.trick_level_scroll_contents)
        self.trick_level_line_1.setObjectName(u"trick_level_line_1")
        self.trick_level_line_1.setFrameShape(QFrame.HLine)
        self.trick_level_line_1.setFrameShadow(QFrame.Sunken)

        self.trick_level_layout.addWidget(self.trick_level_line_1)

        self.dangerous_actions_group = QGroupBox(self.trick_level_scroll_contents)
        self.dangerous_actions_group.setObjectName(u"dangerous_actions_group")
        self.verticalLayout_5 = QVBoxLayout(self.dangerous_actions_group)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.dangerous_combo = QComboBox(self.dangerous_actions_group)
        self.dangerous_combo.addItem("")
        self.dangerous_combo.addItem("")
        self.dangerous_combo.setObjectName(u"dangerous_combo")

        self.verticalLayout_5.addWidget(self.dangerous_combo)

        self.cutscene_label = QLabel(self.dangerous_actions_group)
        self.cutscene_label.setObjectName(u"cutscene_label")
        self.cutscene_label.setWordWrap(True)

        self.verticalLayout_5.addWidget(self.cutscene_label)


        self.trick_level_layout.addWidget(self.dangerous_actions_group)

        self.trick_level_line_2 = QFrame(self.trick_level_scroll_contents)
        self.trick_level_line_2.setObjectName(u"trick_level_line_2")
        self.trick_level_line_2.setFrameShape(QFrame.HLine)
        self.trick_level_line_2.setFrameShadow(QFrame.Sunken)

        self.trick_level_layout.addWidget(self.trick_level_line_2)

        self.trick_level_minimal_logic_check = QCheckBox(self.trick_level_scroll_contents)
        self.trick_level_minimal_logic_check.setObjectName(u"trick_level_minimal_logic_check")

        self.trick_level_layout.addWidget(self.trick_level_minimal_logic_check)

        self.trick_level_minimal_logic_label = QLabel(self.trick_level_scroll_contents)
        self.trick_level_minimal_logic_label.setObjectName(u"trick_level_minimal_logic_label")
        self.trick_level_minimal_logic_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.trick_level_minimal_logic_label.setWordWrap(True)

        self.trick_level_layout.addWidget(self.trick_level_minimal_logic_label)

        self.underwater_abuse_check = QCheckBox(self.trick_level_scroll_contents)
        self.underwater_abuse_check.setObjectName(u"underwater_abuse_check")

        self.trick_level_layout.addWidget(self.underwater_abuse_check)

        self.underwater_abuse_label = QLabel(self.trick_level_scroll_contents)
        self.underwater_abuse_label.setObjectName(u"underwater_abuse_label")
        self.underwater_abuse_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.underwater_abuse_label.setWordWrap(True)

        self.trick_level_layout.addWidget(self.underwater_abuse_label)

        self.trick_level_line_3 = QFrame(self.trick_level_scroll_contents)
        self.trick_level_line_3.setObjectName(u"trick_level_line_3")
        self.trick_level_line_3.setFrameShape(QFrame.HLine)
        self.trick_level_line_3.setFrameShadow(QFrame.Sunken)

        self.trick_level_layout.addWidget(self.trick_level_line_3)

        self.trick_level_help_label = QLabel(self.trick_level_scroll_contents)
        self.trick_level_help_label.setObjectName(u"trick_level_help_label")
        self.trick_level_help_label.setWordWrap(True)

        self.trick_level_layout.addWidget(self.trick_level_help_label)

        self.trick_level_scroll.setWidget(self.trick_level_scroll_contents)

        self.verticalLayout.addWidget(self.trick_level_scroll)

        PresetTrickLevel.setCentralWidget(self.centralWidget)

        self.retranslateUi(PresetTrickLevel)

        QMetaObject.connectSlotsByName(PresetTrickLevel)
    # setupUi

    def retranslateUi(self, PresetTrickLevel):
        PresetTrickLevel.setWindowTitle(QCoreApplication.translate("PresetTrickLevel", u"Trick Level", None))
        self.logic_description_label.setText(QCoreApplication.translate("PresetTrickLevel", u"<html><head/><body><p align=\"justify\">Randovania has rules in place which guarantees that the game is completable regardless of the modifications made to the game. Here you can also configure which kind of game knowledge or skill it expects you to have, allowing for even more varied games.</p><p align=\"justify\">No matter the level, it is always possible to softlock when you enter a room or area that you're unable to leave. For example, vanilla beam rooms without the necessary beam to escape, Dark World without Light Beam/Anihhilator Beam, Torvus Bog without Super Missile.</p><p align=\"justify\">However, it may be <span style=\" font-style:italic;\">necessary</span> to enter Dark World without a way to escape if that item is located in the Dark World.</p></body></html>", None))
        self.dangerous_actions_group.setTitle(QCoreApplication.translate("PresetTrickLevel", u"Allow dangerous actions", None))
        self.dangerous_combo.setItemText(0, QCoreApplication.translate("PresetTrickLevel", u"Randomly", None))
        self.dangerous_combo.setItemText(1, QCoreApplication.translate("PresetTrickLevel", u"Last Resort", None))

        self.cutscene_label.setText(QCoreApplication.translate("PresetTrickLevel", u"<html><head/><body><p>A dangerous action is the act of moving past a lock without the appropriate items needed to head backwards, or doing an action that can only be done once.</p><p><span style=\" font-weight:600;\">Randomly</span>: Dangerous actions might be required by logic.</p><p><span style=\" font-weight:600;\">Last Resort</span>: Only allows dangerous actions to be required if no other option is available for progression.<br/>Warning: Due to how item placement works, certain locations will have progression extremely less often or even never.</p></body></html>", None))
        self.trick_level_minimal_logic_check.setText(QCoreApplication.translate("PresetTrickLevel", u"Use minimal logic instead", None))
        self.trick_level_minimal_logic_label.setText(QCoreApplication.translate("PresetTrickLevel", u"<html><head/><body><p>Randovania will only check that Screw Attack, Dark Visor and Light Suit won't all be behind Ing Caches and Dark Water, removing the biggest reasons for a pure random layout to be impossible.</p><p>There are no guarantees that a seed will be possible in this case.</p><p><br/></p></body></html>", None))
        self.underwater_abuse_check.setText(QCoreApplication.translate("PresetTrickLevel", u"Allow abuse of underwater movement without Gravity Suit", None))
        self.underwater_abuse_label.setText(QCoreApplication.translate("PresetTrickLevel", u"<html><head/><body><p>Movement while not having Gravity Suit has different physics, which causes different item requirements. <a href=\"resource-details://misc/gravity\"><span style=\" text-decoration: underline; color:#0000ff;\">Click here</span></a> to see which rooms are affected.</p><p>Enabling this option adds these alternatives to logic. Be careful that this means collecting Gravity Suit can cause items to be permanently inacessible!</p></body></html>", None))
        self.trick_level_help_label.setText(QCoreApplication.translate("PresetTrickLevel", u"<html><head/><body><p>If you want to tweak the knowledge or skill needed expected in a game, you can configure the level used for each of the tweaks listed below by moving the slider to the apropriate level.</p><p>Press the ? button to see which rooms use that trick on the selected level.</p></body></html>", None))
    # retranslateUi

