# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_editor.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DataEditorWindow(object):
    def setupUi(self, DataEditorWindow):
        if not DataEditorWindow.objectName():
            DataEditorWindow.setObjectName(u"DataEditorWindow")
        DataEditorWindow.resize(802, 471)
        self.centralWidget = QWidget(DataEditorWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 16777215))
        self.gridLayout_2 = QGridLayout(self.centralWidget)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.points_of_interest_group = QGroupBox(self.centralWidget)
        self.points_of_interest_group.setObjectName(u"points_of_interest_group")
        self.points_of_interest_group.setMaximumSize(QSize(250, 16777215))
        self.verticalLayout = QVBoxLayout(self.points_of_interest_group)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.delete_node_button = QPushButton(self.points_of_interest_group)
        self.delete_node_button.setObjectName(u"delete_node_button")

        self.verticalLayout.addWidget(self.delete_node_button)

        self.new_node_button = QPushButton(self.points_of_interest_group)
        self.new_node_button.setObjectName(u"new_node_button")

        self.verticalLayout.addWidget(self.new_node_button)


        self.gridLayout_2.addWidget(self.points_of_interest_group, 1, 0, 2, 1)

        self.save_database_button = QPushButton(self.centralWidget)
        self.save_database_button.setObjectName(u"save_database_button")

        self.gridLayout_2.addWidget(self.save_database_button, 3, 0, 1, 1)

        self.connections_group = QGroupBox(self.centralWidget)
        self.connections_group.setObjectName(u"connections_group")
        self.connections_group.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.gridLayout = QGridLayout(self.connections_group)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setObjectName(u"gridLayout")
        self.other_node_connection_combo = QComboBox(self.connections_group)
        self.other_node_connection_combo.setObjectName(u"other_node_connection_combo")
        self.other_node_connection_combo.setEnabled(False)

        self.gridLayout.addWidget(self.other_node_connection_combo, 0, 0, 1, 1)

        self.other_node_connection_edit_button = QPushButton(self.connections_group)
        self.other_node_connection_edit_button.setObjectName(u"other_node_connection_edit_button")

        self.gridLayout.addWidget(self.other_node_connection_edit_button, 0, 1, 1, 1)

        self.other_node_alternatives_scroll_area = QScrollArea(self.connections_group)
        self.other_node_alternatives_scroll_area.setObjectName(u"other_node_alternatives_scroll_area")
        self.other_node_alternatives_scroll_area.setLineWidth(4)
        self.other_node_alternatives_scroll_area.setWidgetResizable(True)
        self.other_node_alternatives_contents = QWidget()
        self.other_node_alternatives_contents.setObjectName(u"other_node_alternatives_contents")
        self.other_node_alternatives_contents.setGeometry(QRect(0, 0, 487, 140))
        self.other_node_alternatives_scroll_area.setWidget(self.other_node_alternatives_contents)

        self.gridLayout.addWidget(self.other_node_alternatives_scroll_area, 1, 0, 1, 2)


        self.gridLayout_2.addWidget(self.connections_group, 2, 1, 2, 1)

        self.world_selection_group = QGroupBox(self.centralWidget)
        self.world_selection_group.setObjectName(u"world_selection_group")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.world_selection_group.sizePolicy().hasHeightForWidth())
        self.world_selection_group.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.world_selection_group)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.world_selector_box = QComboBox(self.world_selection_group)
        self.world_selector_box.setObjectName(u"world_selector_box")

        self.horizontalLayout.addWidget(self.world_selector_box)

        self.area_selector_box = QComboBox(self.world_selection_group)
        self.area_selector_box.setObjectName(u"area_selector_box")
        self.area_selector_box.setEnabled(False)

        self.horizontalLayout.addWidget(self.area_selector_box)


        self.gridLayout_2.addWidget(self.world_selection_group, 0, 0, 1, 2)

        self.node_info_group = QGroupBox(self.centralWidget)
        self.node_info_group.setObjectName(u"node_info_group")
        sizePolicy.setHeightForWidth(self.node_info_group.sizePolicy().hasHeightForWidth())
        self.node_info_group.setSizePolicy(sizePolicy)
        self.gridLayout_4 = QGridLayout(self.node_info_group)
        self.gridLayout_4.setSpacing(6)
        self.gridLayout_4.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.node_name_label = QLabel(self.node_info_group)
        self.node_name_label.setObjectName(u"node_name_label")

        self.gridLayout_4.addWidget(self.node_name_label, 0, 0, 1, 1)

        self.node_heals_check = QCheckBox(self.node_info_group)
        self.node_heals_check.setObjectName(u"node_heals_check")
        self.node_heals_check.setMaximumSize(QSize(100, 16777215))

        self.gridLayout_4.addWidget(self.node_heals_check, 0, 1, 1, 1)

        self.node_edit_button = QPushButton(self.node_info_group)
        self.node_edit_button.setObjectName(u"node_edit_button")
        self.node_edit_button.setMaximumSize(QSize(100, 16777215))

        self.gridLayout_4.addWidget(self.node_edit_button, 0, 2, 1, 1)

        self.node_details_label = QLabel(self.node_info_group)
        self.node_details_label.setObjectName(u"node_details_label")

        self.gridLayout_4.addWidget(self.node_details_label, 1, 0, 1, 2)

        self.area_spawn_check = QCheckBox(self.node_info_group)
        self.area_spawn_check.setObjectName(u"area_spawn_check")

        self.gridLayout_4.addWidget(self.area_spawn_check, 1, 2, 1, 1)


        self.gridLayout_2.addWidget(self.node_info_group, 1, 1, 1, 1)

        DataEditorWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(DataEditorWindow)

        QMetaObject.connectSlotsByName(DataEditorWindow)
    # setupUi

    def retranslateUi(self, DataEditorWindow):
        DataEditorWindow.setWindowTitle(QCoreApplication.translate("DataEditorWindow", u"Data Visualizer", None))
        self.points_of_interest_group.setTitle(QCoreApplication.translate("DataEditorWindow", u"Nodes", None))
        self.delete_node_button.setText(QCoreApplication.translate("DataEditorWindow", u"Delete Node", None))
        self.new_node_button.setText(QCoreApplication.translate("DataEditorWindow", u"New Node", None))
        self.save_database_button.setText(QCoreApplication.translate("DataEditorWindow", u"Save as database", None))
        self.connections_group.setTitle(QCoreApplication.translate("DataEditorWindow", u"Connections", None))
        self.other_node_connection_edit_button.setText(QCoreApplication.translate("DataEditorWindow", u"Edit", None))
        self.world_selection_group.setTitle(QCoreApplication.translate("DataEditorWindow", u"World/Area Selection", None))
        self.node_info_group.setTitle(QCoreApplication.translate("DataEditorWindow", u"Node Info", None))
        self.node_name_label.setText(QCoreApplication.translate("DataEditorWindow", u"TextLabel", None))
        self.node_heals_check.setText(QCoreApplication.translate("DataEditorWindow", u"Heals?", None))
        self.node_edit_button.setText(QCoreApplication.translate("DataEditorWindow", u"Edit", None))
        self.node_details_label.setText(QCoreApplication.translate("DataEditorWindow", u"TextLabel", None))
        self.area_spawn_check.setText(QCoreApplication.translate("DataEditorWindow", u"Area spawn", None))
    # retranslateUi

