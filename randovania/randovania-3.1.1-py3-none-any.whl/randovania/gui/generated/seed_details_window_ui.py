# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'seed_details_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SeedDetailsWindow(object):
    def setupUi(self, SeedDetailsWindow):
        if not SeedDetailsWindow.objectName():
            SeedDetailsWindow.setObjectName(u"SeedDetailsWindow")
        SeedDetailsWindow.resize(624, 471)
        self.centralWidget = QWidget(SeedDetailsWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 16777215))
        self.centralWidget.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.layout_info_tab = QTabWidget(self.centralWidget)
        self.layout_info_tab.setObjectName(u"layout_info_tab")
        self.details_tab = QWidget()
        self.details_tab.setObjectName(u"details_tab")
        self.details_tab_layout = QGridLayout(self.details_tab)
        self.details_tab_layout.setSpacing(6)
        self.details_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.details_tab_layout.setObjectName(u"details_tab_layout")
        self.details_tab_layout.setContentsMargins(4, 8, 4, 0)
        self.customize_user_preferences_button = QPushButton(self.details_tab)
        self.customize_user_preferences_button.setObjectName(u"customize_user_preferences_button")

        self.details_tab_layout.addWidget(self.customize_user_preferences_button, 2, 4, 1, 2)

        self.progress_box = QGroupBox(self.details_tab)
        self.progress_box.setObjectName(u"progress_box")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_box.sizePolicy().hasHeightForWidth())
        self.progress_box.setSizePolicy(sizePolicy)
        self.progress_box_layout = QGridLayout(self.progress_box)
        self.progress_box_layout.setSpacing(6)
        self.progress_box_layout.setContentsMargins(11, 11, 11, 11)
        self.progress_box_layout.setObjectName(u"progress_box_layout")
        self.progress_box_layout.setContentsMargins(2, 4, 2, 4)
        self.stop_background_process_button = QPushButton(self.progress_box)
        self.stop_background_process_button.setObjectName(u"stop_background_process_button")
        self.stop_background_process_button.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.stop_background_process_button.sizePolicy().hasHeightForWidth())
        self.stop_background_process_button.setSizePolicy(sizePolicy1)
        self.stop_background_process_button.setMaximumSize(QSize(75, 16777215))
        self.stop_background_process_button.setCheckable(False)
        self.stop_background_process_button.setFlat(False)

        self.progress_box_layout.addWidget(self.stop_background_process_button, 0, 3, 1, 1)

        self.progress_label = QLabel(self.progress_box)
        self.progress_label.setObjectName(u"progress_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.progress_label.sizePolicy().hasHeightForWidth())
        self.progress_label.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setPointSize(7)
        self.progress_label.setFont(font)
        self.progress_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.progress_label.setWordWrap(True)

        self.progress_box_layout.addWidget(self.progress_label, 0, 2, 1, 1)

        self.progress_bar = QProgressBar(self.progress_box)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setMinimumSize(QSize(150, 0))
        self.progress_bar.setMaximumSize(QSize(150, 16777215))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setInvertedAppearance(False)

        self.progress_box_layout.addWidget(self.progress_bar, 0, 0, 1, 2)


        self.details_tab_layout.addWidget(self.progress_box, 4, 0, 1, 7)

        self.layout_description_left_label = QLabel(self.details_tab)
        self.layout_description_left_label.setObjectName(u"layout_description_left_label")
        self.layout_description_left_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.layout_description_left_label.setWordWrap(True)

        self.details_tab_layout.addWidget(self.layout_description_left_label, 3, 0, 1, 3)

        self.layout_description_right_label = QLabel(self.details_tab)
        self.layout_description_right_label.setObjectName(u"layout_description_right_label")
        self.layout_description_right_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.layout_description_right_label.setWordWrap(True)

        self.details_tab_layout.addWidget(self.layout_description_right_label, 3, 3, 1, 4)

        self.player_index_combo = QComboBox(self.details_tab)
        self.player_index_combo.setObjectName(u"player_index_combo")

        self.details_tab_layout.addWidget(self.player_index_combo, 2, 0, 1, 4)

        self.export_iso_button = QPushButton(self.details_tab)
        self.export_iso_button.setObjectName(u"export_iso_button")

        self.details_tab_layout.addWidget(self.export_iso_button, 1, 4, 1, 1)

        self.export_log_button = QPushButton(self.details_tab)
        self.export_log_button.setObjectName(u"export_log_button")

        self.details_tab_layout.addWidget(self.export_log_button, 1, 5, 1, 1)

        self.layout_title_label = QLabel(self.details_tab)
        self.layout_title_label.setObjectName(u"layout_title_label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.layout_title_label.sizePolicy().hasHeightForWidth())
        self.layout_title_label.setSizePolicy(sizePolicy3)
        self.layout_title_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.details_tab_layout.addWidget(self.layout_title_label, 1, 0, 1, 4)

        self.tool_button = QToolButton(self.details_tab)
        self.tool_button.setObjectName(u"tool_button")
        self.tool_button.setPopupMode(QToolButton.InstantPopup)

        self.details_tab_layout.addWidget(self.tool_button, 1, 6, 1, 1)

        self.permalink_edit = QLineEdit(self.details_tab)
        self.permalink_edit.setObjectName(u"permalink_edit")
        self.permalink_edit.setReadOnly(True)

        self.details_tab_layout.addWidget(self.permalink_edit, 0, 1, 1, 3)

        self.permalink_label = QLabel(self.details_tab)
        self.permalink_label.setObjectName(u"permalink_label")

        self.details_tab_layout.addWidget(self.permalink_label, 0, 0, 1, 1)

        self.layout_info_tab.addTab(self.details_tab, "")
        self.pickup_tab = QWidget()
        self.pickup_tab.setObjectName(u"pickup_tab")
        self.spoiler_pickup_layout = QGridLayout(self.pickup_tab)
        self.spoiler_pickup_layout.setSpacing(6)
        self.spoiler_pickup_layout.setContentsMargins(11, 11, 11, 11)
        self.spoiler_pickup_layout.setObjectName(u"spoiler_pickup_layout")
        self.spoiler_pickup_layout.setContentsMargins(4, 8, 0, 0)
        self.pickup_spoiler_pickup_combobox = QComboBox(self.pickup_tab)
        self.pickup_spoiler_pickup_combobox.addItem("")
        self.pickup_spoiler_pickup_combobox.setObjectName(u"pickup_spoiler_pickup_combobox")

        self.spoiler_pickup_layout.addWidget(self.pickup_spoiler_pickup_combobox, 2, 2, 1, 1)

        self.pickup_spoiler_label = QLabel(self.pickup_tab)
        self.pickup_spoiler_label.setObjectName(u"pickup_spoiler_label")

        self.spoiler_pickup_layout.addWidget(self.pickup_spoiler_label, 2, 0, 1, 1)

        self.pickup_spoiler_show_all_button = QPushButton(self.pickup_tab)
        self.pickup_spoiler_show_all_button.setObjectName(u"pickup_spoiler_show_all_button")

        self.spoiler_pickup_layout.addWidget(self.pickup_spoiler_show_all_button, 2, 1, 1, 1)

        self.pickup_spoiler_scroll_area = QScrollArea(self.pickup_tab)
        self.pickup_spoiler_scroll_area.setObjectName(u"pickup_spoiler_scroll_area")
        self.pickup_spoiler_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.pickup_spoiler_scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.pickup_spoiler_scroll_area.setWidgetResizable(True)
        self.pickup_spoiler_scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.pickup_spoiler_scroll_contents = QWidget()
        self.pickup_spoiler_scroll_contents.setObjectName(u"pickup_spoiler_scroll_contents")
        self.pickup_spoiler_scroll_contents.setGeometry(QRect(0, 0, 600, 345))
        self.verticalLayout_3 = QVBoxLayout(self.pickup_spoiler_scroll_contents)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(3, 0, 3, -1)
        self.pickup_spoiler_scroll_content_layout = QVBoxLayout()
        self.pickup_spoiler_scroll_content_layout.setSpacing(6)
        self.pickup_spoiler_scroll_content_layout.setObjectName(u"pickup_spoiler_scroll_content_layout")

        self.verticalLayout_3.addLayout(self.pickup_spoiler_scroll_content_layout)

        self.pickup_spoiler_scroll_area.setWidget(self.pickup_spoiler_scroll_contents)

        self.spoiler_pickup_layout.addWidget(self.pickup_spoiler_scroll_area, 4, 0, 1, 3)

        self.spoiler_starting_location_label = QLabel(self.pickup_tab)
        self.spoiler_starting_location_label.setObjectName(u"spoiler_starting_location_label")

        self.spoiler_pickup_layout.addWidget(self.spoiler_starting_location_label, 0, 0, 1, 3)

        self.spoiler_starting_items_label = QLabel(self.pickup_tab)
        self.spoiler_starting_items_label.setObjectName(u"spoiler_starting_items_label")

        self.spoiler_pickup_layout.addWidget(self.spoiler_starting_items_label, 1, 0, 1, 3)

        self.layout_info_tab.addTab(self.pickup_tab, "")

        self.verticalLayout.addWidget(self.layout_info_tab)

        SeedDetailsWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(SeedDetailsWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 624, 21))
        SeedDetailsWindow.setMenuBar(self.menuBar)

        self.retranslateUi(SeedDetailsWindow)

        self.layout_info_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SeedDetailsWindow)
    # setupUi

    def retranslateUi(self, SeedDetailsWindow):
        SeedDetailsWindow.setWindowTitle(QCoreApplication.translate("SeedDetailsWindow", u"Seed Details", None))
        self.customize_user_preferences_button.setText(QCoreApplication.translate("SeedDetailsWindow", u"Customize cosmetic options", None))
        self.progress_box.setTitle(QCoreApplication.translate("SeedDetailsWindow", u"Progress", None))
        self.stop_background_process_button.setText(QCoreApplication.translate("SeedDetailsWindow", u"Stop", None))
        self.progress_label.setText("")
        self.layout_description_left_label.setText(QCoreApplication.translate("SeedDetailsWindow", u"<html><head/><body><p>This content should have been replaced by code.</p></body></html>", None))
        self.layout_description_right_label.setText(QCoreApplication.translate("SeedDetailsWindow", u"<html><head/><body><p>This content should have been replaced by code.</p></body></html>", None))
        self.export_iso_button.setText(QCoreApplication.translate("SeedDetailsWindow", u"Save ISO", None))
        self.export_log_button.setText(QCoreApplication.translate("SeedDetailsWindow", u"Save Spoiler", None))
        self.layout_title_label.setText(QCoreApplication.translate("SeedDetailsWindow", u"<html><head/><body><p>Seed Hash: ????<br/>Preset Name: ???</p></body></html>", None))
        self.tool_button.setText(QCoreApplication.translate("SeedDetailsWindow", u"...", None))
        self.permalink_edit.setText(QCoreApplication.translate("SeedDetailsWindow", u"<insert permalink here>", None))
        self.permalink_label.setText(QCoreApplication.translate("SeedDetailsWindow", u"Permalink:", None))
        self.layout_info_tab.setTabText(self.layout_info_tab.indexOf(self.details_tab), QCoreApplication.translate("SeedDetailsWindow", u"Summary", None))
        self.pickup_spoiler_pickup_combobox.setItemText(0, QCoreApplication.translate("SeedDetailsWindow", u"None", None))

#if QT_CONFIG(tooltip)
        self.pickup_spoiler_label.setToolTip(QCoreApplication.translate("SeedDetailsWindow", u"Enter text to the right to filter the list below", None))
#endif // QT_CONFIG(tooltip)
        self.pickup_spoiler_label.setText(QCoreApplication.translate("SeedDetailsWindow", u"Search Pickup", None))
        self.pickup_spoiler_show_all_button.setText(QCoreApplication.translate("SeedDetailsWindow", u"Show All", None))
        self.spoiler_starting_location_label.setText(QCoreApplication.translate("SeedDetailsWindow", u"Starting Location", None))
        self.spoiler_starting_items_label.setText(QCoreApplication.translate("SeedDetailsWindow", u"Starting Items", None))
        self.layout_info_tab.setTabText(self.layout_info_tab.indexOf(self.pickup_tab), QCoreApplication.translate("SeedDetailsWindow", u"Spoiler: Pickups", None))
    # retranslateUi

