# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from randovania.gui.lib.preset_tree_widget import PresetTreeWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(645, 613)
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        self.menu_action_existing_seed_details = QAction(MainWindow)
        self.menu_action_existing_seed_details.setObjectName(u"menu_action_existing_seed_details")
        self.menu_action_edit_existing_database = QAction(MainWindow)
        self.menu_action_edit_existing_database.setObjectName(u"menu_action_edit_existing_database")
        self.menu_action_load_iso = QAction(MainWindow)
        self.menu_action_load_iso.setObjectName(u"menu_action_load_iso")
        self.menu_action_validate_seed_after = QAction(MainWindow)
        self.menu_action_validate_seed_after.setObjectName(u"menu_action_validate_seed_after")
        self.menu_action_validate_seed_after.setCheckable(True)
        self.menu_action_validate_seed_after.setChecked(True)
        self.menu_action_timeout_generation_after_a_time_limit = QAction(MainWindow)
        self.menu_action_timeout_generation_after_a_time_limit.setObjectName(u"menu_action_timeout_generation_after_a_time_limit")
        self.menu_action_timeout_generation_after_a_time_limit.setCheckable(True)
        self.menu_action_timeout_generation_after_a_time_limit.setChecked(True)
        self.menu_action_delete_loaded_game = QAction(MainWindow)
        self.menu_action_delete_loaded_game.setObjectName(u"menu_action_delete_loaded_game")
        self.menu_action_item_tracker = QAction(MainWindow)
        self.menu_action_item_tracker.setObjectName(u"menu_action_item_tracker")
        self.menu_action_open_auto_tracker = QAction(MainWindow)
        self.menu_action_open_auto_tracker.setObjectName(u"menu_action_open_auto_tracker")
        self.action_login_window = QAction(MainWindow)
        self.action_login_window.setObjectName(u"action_login_window")
        self.action_login_as_guest = QAction(MainWindow)
        self.action_login_as_guest.setObjectName(u"action_login_as_guest")
        self.actionLogged_in_as = QAction(MainWindow)
        self.actionLogged_in_as.setObjectName(u"actionLogged_in_as")
        self.actionLogged_in_as.setEnabled(False)
        self.menu_action_edit_prime_1 = QAction(MainWindow)
        self.menu_action_edit_prime_1.setObjectName(u"menu_action_edit_prime_1")
        self.menu_action_edit_prime_2 = QAction(MainWindow)
        self.menu_action_edit_prime_2.setObjectName(u"menu_action_edit_prime_2")
        self.menu_action_edit_prime_3 = QAction(MainWindow)
        self.menu_action_edit_prime_3.setObjectName(u"menu_action_edit_prime_3")
        self.menu_action_visualize_prime_1 = QAction(MainWindow)
        self.menu_action_visualize_prime_1.setObjectName(u"menu_action_visualize_prime_1")
        self.menu_action_visualize_prime_2 = QAction(MainWindow)
        self.menu_action_visualize_prime_2.setObjectName(u"menu_action_visualize_prime_2")
        self.menu_action_visualize_prime_3 = QAction(MainWindow)
        self.menu_action_visualize_prime_3.setObjectName(u"menu_action_visualize_prime_3")
        self.menu_action_dark_mode = QAction(MainWindow)
        self.menu_action_dark_mode.setObjectName(u"menu_action_dark_mode")
        self.menu_action_dark_mode.setCheckable(True)
        self.menu_action_previously_generated_games = QAction(MainWindow)
        self.menu_action_previously_generated_games.setObjectName(u"menu_action_previously_generated_games")
        self.menu_action_layout_editor = QAction(MainWindow)
        self.menu_action_layout_editor.setObjectName(u"menu_action_layout_editor")
        self.menu_action_map_tracker = QAction(MainWindow)
        self.menu_action_map_tracker.setObjectName(u"menu_action_map_tracker")
        self.menu_action_prime_3_data_visualizer = QAction(MainWindow)
        self.menu_action_prime_3_data_visualizer.setObjectName(u"menu_action_prime_3_data_visualizer")
        self.actionasdf = QAction(MainWindow)
        self.actionasdf.setObjectName(u"actionasdf")
        self.menu_action_prime_2_data_visualizer = QAction(MainWindow)
        self.menu_action_prime_2_data_visualizer.setObjectName(u"menu_action_prime_2_data_visualizer")
        self.actionasdf_2 = QAction(MainWindow)
        self.actionasdf_2.setObjectName(u"actionasdf_2")
        self.menu_action_prime_1_data_visualizer = QAction(MainWindow)
        self.menu_action_prime_1_data_visualizer.setObjectName(u"menu_action_prime_1_data_visualizer")
        self.actionasdf_3 = QAction(MainWindow)
        self.actionasdf_3.setObjectName(u"actionasdf_3")
        self.menu_action_log_files_directory = QAction(MainWindow)
        self.menu_action_log_files_directory.setObjectName(u"menu_action_log_files_directory")
        self.menu_action_experimental_games = QAction(MainWindow)
        self.menu_action_experimental_games.setObjectName(u"menu_action_experimental_games")
        self.menu_action_experimental_games.setCheckable(True)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.centralWidget)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.main_tab_widget = QTabWidget(self.centralWidget)
        self.main_tab_widget.setObjectName(u"main_tab_widget")
        self.welcome_tab = QWidget()
        self.welcome_tab.setObjectName(u"welcome_tab")
        self.welcome_layout = QGridLayout(self.welcome_tab)
        self.welcome_layout.setSpacing(6)
        self.welcome_layout.setContentsMargins(11, 11, 11, 11)
        self.welcome_layout.setObjectName(u"welcome_layout")
        self.welcome_layout.setContentsMargins(0, 4, 0, 0)
        self.open_database_viewer_button = QPushButton(self.welcome_tab)
        self.open_database_viewer_button.setObjectName(u"open_database_viewer_button")

        self.welcome_layout.addWidget(self.open_database_viewer_button, 5, 2, 1, 1)

        self.intro_vertical_spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.welcome_layout.addItem(self.intro_vertical_spacer, 1, 1, 1, 1)

        self.intro_bottom_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.welcome_layout.addItem(self.intro_bottom_spacer, 6, 1, 1, 1)

        self.intro_top_spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.welcome_layout.addItem(self.intro_top_spacer, 3, 1, 1, 1)

        self.open_faq_button = QPushButton(self.welcome_tab)
        self.open_faq_button.setObjectName(u"open_faq_button")

        self.welcome_layout.addWidget(self.open_faq_button, 5, 0, 1, 1)

        self.help_offer_label = QLabel(self.welcome_tab)
        self.help_offer_label.setObjectName(u"help_offer_label")
        self.help_offer_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.help_offer_label.setWordWrap(True)

        self.welcome_layout.addWidget(self.help_offer_label, 4, 0, 1, 3)

        self.intro_play_now_button = QPushButton(self.welcome_tab)
        self.intro_play_now_button.setObjectName(u"intro_play_now_button")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.intro_play_now_button.setFont(font)

        self.welcome_layout.addWidget(self.intro_play_now_button, 2, 1, 1, 1)

        self.intro_label = QLabel(self.welcome_tab)
        self.intro_label.setObjectName(u"intro_label")
        self.intro_label.setScaledContents(False)
        self.intro_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.intro_label.setWordWrap(True)
        self.intro_label.setMargin(7)
        self.intro_label.setIndent(-1)
        self.intro_label.setOpenExternalLinks(False)

        self.welcome_layout.addWidget(self.intro_label, 0, 0, 1, 3)

        self.main_tab_widget.addTab(self.welcome_tab, "")
        self.tab_play = QWidget()
        self.tab_play.setObjectName(u"tab_play")
        self.play_layout = QVBoxLayout(self.tab_play)
        self.play_layout.setSpacing(6)
        self.play_layout.setContentsMargins(11, 11, 11, 11)
        self.play_layout.setObjectName(u"play_layout")
        self.play_layout.setContentsMargins(4, 0, 0, 0)
        self.play_top_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.play_layout.addItem(self.play_top_spacer)

        self.play_existing_permalink_group = QGroupBox(self.tab_play)
        self.play_existing_permalink_group.setObjectName(u"play_existing_permalink_group")
        self.play_existing_permalink_layout = QGridLayout(self.play_existing_permalink_group)
        self.play_existing_permalink_layout.setSpacing(6)
        self.play_existing_permalink_layout.setContentsMargins(11, 11, 11, 11)
        self.play_existing_permalink_layout.setObjectName(u"play_existing_permalink_layout")
        self.import_permalink_button = QPushButton(self.play_existing_permalink_group)
        self.import_permalink_button.setObjectName(u"import_permalink_button")

        self.play_existing_permalink_layout.addWidget(self.import_permalink_button, 1, 0, 1, 1)

        self.browse_sessions_button = QPushButton(self.play_existing_permalink_group)
        self.browse_sessions_button.setObjectName(u"browse_sessions_button")

        self.play_existing_permalink_layout.addWidget(self.browse_sessions_button, 3, 1, 1, 1)

        self.import_permalink_label = QLabel(self.play_existing_permalink_group)
        self.import_permalink_label.setObjectName(u"import_permalink_label")
        self.import_permalink_label.setWordWrap(True)

        self.play_existing_permalink_layout.addWidget(self.import_permalink_label, 0, 0, 1, 1)

        self.import_game_file_label = QLabel(self.play_existing_permalink_group)
        self.import_game_file_label.setObjectName(u"import_game_file_label")
        self.import_game_file_label.setWordWrap(True)

        self.play_existing_permalink_layout.addWidget(self.import_game_file_label, 2, 0, 1, 1)

        self.browse_racetime_label = QLabel(self.play_existing_permalink_group)
        self.browse_racetime_label.setObjectName(u"browse_racetime_label")
        self.browse_racetime_label.setTextFormat(Qt.AutoText)
        self.browse_racetime_label.setWordWrap(True)
        self.browse_racetime_label.setOpenExternalLinks(True)

        self.play_existing_permalink_layout.addWidget(self.browse_racetime_label, 0, 1, 1, 1)

        self.import_game_file_button = QPushButton(self.play_existing_permalink_group)
        self.import_game_file_button.setObjectName(u"import_game_file_button")

        self.play_existing_permalink_layout.addWidget(self.import_game_file_button, 3, 0, 1, 1)

        self.browse_racetime_button = QPushButton(self.play_existing_permalink_group)
        self.browse_racetime_button.setObjectName(u"browse_racetime_button")

        self.play_existing_permalink_layout.addWidget(self.browse_racetime_button, 1, 1, 1, 1)

        self.browse_sessions_label = QLabel(self.play_existing_permalink_group)
        self.browse_sessions_label.setObjectName(u"browse_sessions_label")
        self.browse_sessions_label.setWordWrap(True)

        self.play_existing_permalink_layout.addWidget(self.browse_sessions_label, 2, 1, 1, 1)


        self.play_layout.addWidget(self.play_existing_permalink_group)

        self.play_middle_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.play_layout.addItem(self.play_middle_spacer)

        self.play_new_game_group = QGroupBox(self.tab_play)
        self.play_new_game_group.setObjectName(u"play_new_game_group")
        self.play_new_permalink_layout = QGridLayout(self.play_new_game_group)
        self.play_new_permalink_layout.setSpacing(6)
        self.play_new_permalink_layout.setContentsMargins(11, 11, 11, 11)
        self.play_new_permalink_layout.setObjectName(u"play_new_permalink_layout")
        self.host_new_game_label = QLabel(self.play_new_game_group)
        self.host_new_game_label.setObjectName(u"host_new_game_label")
        self.host_new_game_label.setWordWrap(True)

        self.play_new_permalink_layout.addWidget(self.host_new_game_label, 2, 0, 1, 1)

        self.create_new_seed_label = QLabel(self.play_new_game_group)
        self.create_new_seed_label.setObjectName(u"create_new_seed_label")

        self.play_new_permalink_layout.addWidget(self.create_new_seed_label, 0, 0, 1, 1)

        self.create_new_seed_button = QPushButton(self.play_new_game_group)
        self.create_new_seed_button.setObjectName(u"create_new_seed_button")

        self.play_new_permalink_layout.addWidget(self.create_new_seed_button, 1, 0, 1, 1)

        self.host_new_game_button = QPushButton(self.play_new_game_group)
        self.host_new_game_button.setObjectName(u"host_new_game_button")

        self.play_new_permalink_layout.addWidget(self.host_new_game_button, 3, 0, 1, 1)


        self.play_layout.addWidget(self.play_new_game_group)

        self.play_bottom_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.play_layout.addItem(self.play_bottom_spacer)

        self.main_tab_widget.addTab(self.tab_play, "")
        self.tab_create_seed = QWidget()
        self.tab_create_seed.setObjectName(u"tab_create_seed")
        self.create_layout = QGridLayout(self.tab_create_seed)
        self.create_layout.setSpacing(6)
        self.create_layout.setContentsMargins(11, 11, 11, 11)
        self.create_layout.setObjectName(u"create_layout")
        self.create_layout.setContentsMargins(4, 4, 4, 0)
        self.create_generate_no_retry_button = QPushButton(self.tab_create_seed)
        self.create_generate_no_retry_button.setObjectName(u"create_generate_no_retry_button")

        self.create_layout.addWidget(self.create_generate_no_retry_button, 4, 0, 1, 1)

        self.create_generate_race_button = QPushButton(self.tab_create_seed)
        self.create_generate_race_button.setObjectName(u"create_generate_race_button")

        self.create_layout.addWidget(self.create_generate_race_button, 4, 2, 1, 1)

        self.create_generate_button = QPushButton(self.tab_create_seed)
        self.create_generate_button.setObjectName(u"create_generate_button")

        self.create_layout.addWidget(self.create_generate_button, 4, 1, 1, 1)

        self.num_players_spin_box = QSpinBox(self.tab_create_seed)
        self.num_players_spin_box.setObjectName(u"num_players_spin_box")
        self.num_players_spin_box.setCursor(QCursor(Qt.ArrowCursor))
        self.num_players_spin_box.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.num_players_spin_box.setMinimum(1)

        self.create_layout.addWidget(self.num_players_spin_box, 4, 3, 1, 1)

        self.create_preset_tree = PresetTreeWidget(self.tab_create_seed)
        __qtreewidgetitem = QTreeWidgetItem(self.create_preset_tree)
        __qtreewidgetitem1 = QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(self.create_preset_tree)
        self.create_preset_tree.setObjectName(u"create_preset_tree")
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_preset_tree.sizePolicy().hasHeightForWidth())
        self.create_preset_tree.setSizePolicy(sizePolicy)
        self.create_preset_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.create_preset_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.create_preset_tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.create_preset_tree.setAlternatingRowColors(False)
        self.create_preset_tree.setRootIsDecorated(False)

        self.create_layout.addWidget(self.create_preset_tree, 2, 0, 1, 2)

        self.progress_box = QGroupBox(self.tab_create_seed)
        self.progress_box.setObjectName(u"progress_box")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.progress_box.sizePolicy().hasHeightForWidth())
        self.progress_box.setSizePolicy(sizePolicy1)
        self.progress_box_layout = QGridLayout(self.progress_box)
        self.progress_box_layout.setSpacing(6)
        self.progress_box_layout.setContentsMargins(11, 11, 11, 11)
        self.progress_box_layout.setObjectName(u"progress_box_layout")
        self.progress_box_layout.setContentsMargins(2, 4, 2, 4)
        self.stop_background_process_button = QPushButton(self.progress_box)
        self.stop_background_process_button.setObjectName(u"stop_background_process_button")
        self.stop_background_process_button.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.stop_background_process_button.sizePolicy().hasHeightForWidth())
        self.stop_background_process_button.setSizePolicy(sizePolicy2)
        self.stop_background_process_button.setMaximumSize(QSize(75, 16777215))
        self.stop_background_process_button.setCheckable(False)
        self.stop_background_process_button.setFlat(False)

        self.progress_box_layout.addWidget(self.stop_background_process_button, 0, 3, 1, 1)

        self.progress_bar = QProgressBar(self.progress_box)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setMinimumSize(QSize(150, 0))
        self.progress_bar.setMaximumSize(QSize(150, 16777215))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setInvertedAppearance(False)

        self.progress_box_layout.addWidget(self.progress_bar, 0, 0, 1, 2)

        self.progress_label = QLabel(self.progress_box)
        self.progress_label.setObjectName(u"progress_label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.progress_label.sizePolicy().hasHeightForWidth())
        self.progress_label.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(7)
        self.progress_label.setFont(font1)
        self.progress_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.progress_label.setWordWrap(True)

        self.progress_box_layout.addWidget(self.progress_label, 0, 2, 1, 1)


        self.create_layout.addWidget(self.progress_box, 5, 0, 1, 4)

        self.create_scroll_area = QScrollArea(self.tab_create_seed)
        self.create_scroll_area.setObjectName(u"create_scroll_area")
        self.create_scroll_area.setWidgetResizable(True)
        self.create_scroll_area_contents = QWidget()
        self.create_scroll_area_contents.setObjectName(u"create_scroll_area_contents")
        self.create_scroll_area_contents.setGeometry(QRect(0, 0, 302, 442))
        self.create_scroll_area_layout = QVBoxLayout(self.create_scroll_area_contents)
        self.create_scroll_area_layout.setSpacing(6)
        self.create_scroll_area_layout.setContentsMargins(11, 11, 11, 11)
        self.create_scroll_area_layout.setObjectName(u"create_scroll_area_layout")
        self.create_scroll_area_layout.setContentsMargins(4, 4, 4, 4)
        self.create_preset_description = QLabel(self.create_scroll_area_contents)
        self.create_preset_description.setObjectName(u"create_preset_description")
        sizePolicy4 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.create_preset_description.sizePolicy().hasHeightForWidth())
        self.create_preset_description.setSizePolicy(sizePolicy4)
        self.create_preset_description.setMinimumSize(QSize(0, 40))
        self.create_preset_description.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.create_preset_description.setWordWrap(True)

        self.create_scroll_area_layout.addWidget(self.create_preset_description)

        self.create_scroll_area.setWidget(self.create_scroll_area_contents)

        self.create_layout.addWidget(self.create_scroll_area, 2, 2, 1, 2)

        self.main_tab_widget.addTab(self.tab_create_seed, "")
        self.help_tab = QWidget()
        self.help_tab.setObjectName(u"help_tab")
        self.help_layout = QVBoxLayout(self.help_tab)
        self.help_layout.setSpacing(6)
        self.help_layout.setContentsMargins(11, 11, 11, 11)
        self.help_layout.setObjectName(u"help_layout")
        self.help_layout.setContentsMargins(0, 4, 0, 0)
        self.help_tab_widget = QTabWidget(self.help_tab)
        self.help_tab_widget.setObjectName(u"help_tab_widget")
        self.tab_multiworld = QWidget()
        self.tab_multiworld.setObjectName(u"tab_multiworld")
        self.verticalLayout = QVBoxLayout(self.tab_multiworld)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.multiworld_scroll_area = QScrollArea(self.tab_multiworld)
        self.multiworld_scroll_area.setObjectName(u"multiworld_scroll_area")
        self.multiworld_scroll_area.setWidgetResizable(True)
        self.multiworld_scroll_area_contents = QWidget()
        self.multiworld_scroll_area_contents.setObjectName(u"multiworld_scroll_area_contents")
        self.multiworld_scroll_area_contents.setGeometry(QRect(0, 0, 603, 615))
        self.multiworld_scroll_contents_layout = QGridLayout(self.multiworld_scroll_area_contents)
        self.multiworld_scroll_contents_layout.setSpacing(6)
        self.multiworld_scroll_contents_layout.setContentsMargins(11, 11, 11, 11)
        self.multiworld_scroll_contents_layout.setObjectName(u"multiworld_scroll_contents_layout")
        self.multiworld_label = QLabel(self.multiworld_scroll_area_contents)
        self.multiworld_label.setObjectName(u"multiworld_label")
        self.multiworld_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.multiworld_label.setWordWrap(True)

        self.multiworld_scroll_contents_layout.addWidget(self.multiworld_label, 0, 0, 1, 1)

        self.multiworld_scroll_area.setWidget(self.multiworld_scroll_area_contents)

        self.verticalLayout.addWidget(self.multiworld_scroll_area)

        self.help_tab_widget.addTab(self.tab_multiworld, "")
        self.tab_tracker = QWidget()
        self.tab_tracker.setObjectName(u"tab_tracker")
        self.tracker_tab_layout = QVBoxLayout(self.tab_tracker)
        self.tracker_tab_layout.setSpacing(6)
        self.tracker_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.tracker_tab_layout.setObjectName(u"tracker_tab_layout")
        self.tracker_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tracker_scroll_area = QScrollArea(self.tab_tracker)
        self.tracker_scroll_area.setObjectName(u"tracker_scroll_area")
        self.tracker_scroll_area.setWidgetResizable(True)
        self.tracker_scroll_area_contents = QWidget()
        self.tracker_scroll_area_contents.setObjectName(u"tracker_scroll_area_contents")
        self.tracker_scroll_area_contents.setGeometry(QRect(0, 0, 98, 1296))
        self.tracker_scroll_area_layout = QVBoxLayout(self.tracker_scroll_area_contents)
        self.tracker_scroll_area_layout.setSpacing(6)
        self.tracker_scroll_area_layout.setContentsMargins(11, 11, 11, 11)
        self.tracker_scroll_area_layout.setObjectName(u"tracker_scroll_area_layout")
        self.tracker_label = QLabel(self.tracker_scroll_area_contents)
        self.tracker_label.setObjectName(u"tracker_label")
        self.tracker_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.tracker_label.setWordWrap(True)

        self.tracker_scroll_area_layout.addWidget(self.tracker_label)

        self.tracker_scroll_area.setWidget(self.tracker_scroll_area_contents)

        self.tracker_tab_layout.addWidget(self.tracker_scroll_area)

        self.help_tab_widget.addTab(self.tab_tracker, "")
        self.database_viewer_tab = QWidget()
        self.database_viewer_tab.setObjectName(u"database_viewer_tab")
        self.verticalLayout_3 = QVBoxLayout(self.database_viewer_tab)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.database_viewer_scroll_area = QScrollArea(self.database_viewer_tab)
        self.database_viewer_scroll_area.setObjectName(u"database_viewer_scroll_area")
        self.database_viewer_scroll_area.setWidgetResizable(True)
        self.database_viewer_scroll_area_contents = QWidget()
        self.database_viewer_scroll_area_contents.setObjectName(u"database_viewer_scroll_area_contents")
        self.database_viewer_scroll_area_contents.setGeometry(QRect(0, 0, 123, 2169))
        self.verticalLayout_2 = QVBoxLayout(self.database_viewer_scroll_area_contents)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(9, -1, -1, -1)
        self.database_viewer_label = QLabel(self.database_viewer_scroll_area_contents)
        self.database_viewer_label.setObjectName(u"database_viewer_label")
        self.database_viewer_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.database_viewer_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.database_viewer_label)

        self.database_viewer_scroll_area.setWidget(self.database_viewer_scroll_area_contents)

        self.verticalLayout_3.addWidget(self.database_viewer_scroll_area)

        self.help_tab_widget.addTab(self.database_viewer_tab, "")

        self.help_layout.addWidget(self.help_tab_widget)

        self.main_tab_widget.addTab(self.help_tab, "")
        self.games_tab = QWidget()
        self.games_tab.setObjectName(u"games_tab")
        self.games_tab_layout = QVBoxLayout(self.games_tab)
        self.games_tab_layout.setSpacing(0)
        self.games_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.games_tab_layout.setObjectName(u"games_tab_layout")
        self.games_tab_layout.setContentsMargins(0, 4, 0, 0)
        self.games_tab_widget = QTabWidget(self.games_tab)
        self.games_tab_widget.setObjectName(u"games_tab_widget")
        self.help_prime_tab = QWidget()
        self.help_prime_tab.setObjectName(u"help_prime_tab")
        self.prime_tab_layout = QVBoxLayout(self.help_prime_tab)
        self.prime_tab_layout.setSpacing(6)
        self.prime_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.prime_tab_layout.setObjectName(u"prime_tab_layout")
        self.prime_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.help_prime_tab_widget = QTabWidget(self.help_prime_tab)
        self.help_prime_tab_widget.setObjectName(u"help_prime_tab_widget")
        self.prime_faq_tab = QWidget()
        self.prime_faq_tab.setObjectName(u"prime_faq_tab")
        self.faq_layout_4 = QGridLayout(self.prime_faq_tab)
        self.faq_layout_4.setSpacing(6)
        self.faq_layout_4.setContentsMargins(11, 11, 11, 11)
        self.faq_layout_4.setObjectName(u"faq_layout_4")
        self.faq_layout_4.setContentsMargins(0, 0, 0, 0)
        self.prime_faq_scroll_area = QScrollArea(self.prime_faq_tab)
        self.prime_faq_scroll_area.setObjectName(u"prime_faq_scroll_area")
        self.prime_faq_scroll_area.setWidgetResizable(True)
        self.prime_faq_scroll_area_contents = QWidget()
        self.prime_faq_scroll_area_contents.setObjectName(u"prime_faq_scroll_area_contents")
        self.prime_faq_scroll_area_contents.setGeometry(QRect(0, 0, 613, 477))
        self.gridLayout_10 = QGridLayout(self.prime_faq_scroll_area_contents)
        self.gridLayout_10.setSpacing(6)
        self.gridLayout_10.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.prime_faq_label = QLabel(self.prime_faq_scroll_area_contents)
        self.prime_faq_label.setObjectName(u"prime_faq_label")
        self.prime_faq_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.prime_faq_label.setWordWrap(True)

        self.gridLayout_10.addWidget(self.prime_faq_label, 0, 0, 1, 1)

        self.prime_faq_scroll_area.setWidget(self.prime_faq_scroll_area_contents)

        self.faq_layout_4.addWidget(self.prime_faq_scroll_area, 0, 0, 1, 1)

        self.help_prime_tab_widget.addTab(self.prime_faq_tab, "")
        self.prime_differences_tab = QWidget()
        self.prime_differences_tab.setObjectName(u"prime_differences_tab")
        self.differences_tab_layout_4 = QVBoxLayout(self.prime_differences_tab)
        self.differences_tab_layout_4.setSpacing(6)
        self.differences_tab_layout_4.setContentsMargins(11, 11, 11, 11)
        self.differences_tab_layout_4.setObjectName(u"differences_tab_layout_4")
        self.differences_tab_layout_4.setContentsMargins(0, 0, 0, 0)
        self.prime_differences_scroll_area = QScrollArea(self.prime_differences_tab)
        self.prime_differences_scroll_area.setObjectName(u"prime_differences_scroll_area")
        self.prime_differences_scroll_area.setWidgetResizable(True)
        self.prime_differences_scroll_contents = QWidget()
        self.prime_differences_scroll_contents.setObjectName(u"prime_differences_scroll_contents")
        self.prime_differences_scroll_contents.setGeometry(QRect(0, 0, 98, 35))
        self.differences_scroll_layout_5 = QVBoxLayout(self.prime_differences_scroll_contents)
        self.differences_scroll_layout_5.setSpacing(6)
        self.differences_scroll_layout_5.setContentsMargins(11, 11, 11, 11)
        self.differences_scroll_layout_5.setObjectName(u"differences_scroll_layout_5")
        self.prime_differences_label = QLabel(self.prime_differences_scroll_contents)
        self.prime_differences_label.setObjectName(u"prime_differences_label")
        self.prime_differences_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.prime_differences_label.setWordWrap(True)

        self.differences_scroll_layout_5.addWidget(self.prime_differences_label)

        self.prime_differences_scroll_area.setWidget(self.prime_differences_scroll_contents)

        self.differences_tab_layout_4.addWidget(self.prime_differences_scroll_area)

        self.help_prime_tab_widget.addTab(self.prime_differences_tab, "")
        self.prime_hints_tab = QWidget()
        self.prime_hints_tab.setObjectName(u"prime_hints_tab")
        self.hints_tab_layout_4 = QVBoxLayout(self.prime_hints_tab)
        self.hints_tab_layout_4.setSpacing(0)
        self.hints_tab_layout_4.setContentsMargins(11, 11, 11, 11)
        self.hints_tab_layout_4.setObjectName(u"hints_tab_layout_4")
        self.hints_tab_layout_4.setContentsMargins(0, 0, 0, 0)
        self.prime_hints_scroll_area = QScrollArea(self.prime_hints_tab)
        self.prime_hints_scroll_area.setObjectName(u"prime_hints_scroll_area")
        self.prime_hints_scroll_area.setWidgetResizable(True)
        self.prime_hints_scroll_area_contents = QWidget()
        self.prime_hints_scroll_area_contents.setObjectName(u"prime_hints_scroll_area_contents")
        self.prime_hints_scroll_area_contents.setGeometry(QRect(0, 0, 98, 268))
        self.hints_scroll_layout_4 = QVBoxLayout(self.prime_hints_scroll_area_contents)
        self.hints_scroll_layout_4.setSpacing(6)
        self.hints_scroll_layout_4.setContentsMargins(11, 11, 11, 11)
        self.hints_scroll_layout_4.setObjectName(u"hints_scroll_layout_4")
        self.prime_hints_label = QLabel(self.prime_hints_scroll_area_contents)
        self.prime_hints_label.setObjectName(u"prime_hints_label")
        self.prime_hints_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.prime_hints_label.setWordWrap(True)

        self.hints_scroll_layout_4.addWidget(self.prime_hints_label)

        self.prime_hints_scroll_area.setWidget(self.prime_hints_scroll_area_contents)

        self.hints_tab_layout_4.addWidget(self.prime_hints_scroll_area)

        self.help_prime_tab_widget.addTab(self.prime_hints_tab, "")
        self.prime_hint_item_names_tab = QWidget()
        self.prime_hint_item_names_tab.setObjectName(u"prime_hint_item_names_tab")
        self.hint_item_names_layout_4 = QVBoxLayout(self.prime_hint_item_names_tab)
        self.hint_item_names_layout_4.setSpacing(0)
        self.hint_item_names_layout_4.setContentsMargins(11, 11, 11, 11)
        self.hint_item_names_layout_4.setObjectName(u"hint_item_names_layout_4")
        self.hint_item_names_layout_4.setContentsMargins(0, 0, 0, 0)
        self.prime_hint_item_names_scroll_area = QScrollArea(self.prime_hint_item_names_tab)
        self.prime_hint_item_names_scroll_area.setObjectName(u"prime_hint_item_names_scroll_area")
        self.prime_hint_item_names_scroll_area.setWidgetResizable(True)
        self.prime_hint_item_names_scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.prime_hint_item_names_scroll_contents = QWidget()
        self.prime_hint_item_names_scroll_contents.setObjectName(u"prime_hint_item_names_scroll_contents")
        self.prime_hint_item_names_scroll_contents.setGeometry(QRect(0, 0, 98, 386))
        self.hint_item_names_scroll_layout_4 = QVBoxLayout(self.prime_hint_item_names_scroll_contents)
        self.hint_item_names_scroll_layout_4.setSpacing(6)
        self.hint_item_names_scroll_layout_4.setContentsMargins(11, 11, 11, 11)
        self.hint_item_names_scroll_layout_4.setObjectName(u"hint_item_names_scroll_layout_4")
        self.prime_hint_item_names_label = QLabel(self.prime_hint_item_names_scroll_contents)
        self.prime_hint_item_names_label.setObjectName(u"prime_hint_item_names_label")
        self.prime_hint_item_names_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.prime_hint_item_names_label.setWordWrap(True)

        self.hint_item_names_scroll_layout_4.addWidget(self.prime_hint_item_names_label)

        self.prime_hint_item_names_tree_widget = QTableWidget(self.prime_hint_item_names_scroll_contents)
        if (self.prime_hint_item_names_tree_widget.columnCount() < 4):
            self.prime_hint_item_names_tree_widget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.prime_hint_item_names_tree_widget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.prime_hint_item_names_tree_widget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.prime_hint_item_names_tree_widget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.prime_hint_item_names_tree_widget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.prime_hint_item_names_tree_widget.setObjectName(u"prime_hint_item_names_tree_widget")
        self.prime_hint_item_names_tree_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.prime_hint_item_names_tree_widget.setSortingEnabled(True)

        self.hint_item_names_scroll_layout_4.addWidget(self.prime_hint_item_names_tree_widget)

        self.prime_hint_item_names_scroll_area.setWidget(self.prime_hint_item_names_scroll_contents)

        self.hint_item_names_layout_4.addWidget(self.prime_hint_item_names_scroll_area)

        self.help_prime_tab_widget.addTab(self.prime_hint_item_names_tab, "")
        self.prime_hint_locations_tab = QWidget()
        self.prime_hint_locations_tab.setObjectName(u"prime_hint_locations_tab")
        self.hint_tab_layout_4 = QVBoxLayout(self.prime_hint_locations_tab)
        self.hint_tab_layout_4.setSpacing(6)
        self.hint_tab_layout_4.setContentsMargins(11, 11, 11, 11)
        self.hint_tab_layout_4.setObjectName(u"hint_tab_layout_4")
        self.hint_tab_layout_4.setContentsMargins(0, 0, 0, 0)
        self.prime_hint_locations_scroll_area = QScrollArea(self.prime_hint_locations_tab)
        self.prime_hint_locations_scroll_area.setObjectName(u"prime_hint_locations_scroll_area")
        self.prime_hint_locations_scroll_area.setWidgetResizable(True)
        self.prime_hint_locations_scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.prime_hint_locations_scroll_contents = QWidget()
        self.prime_hint_locations_scroll_contents.setObjectName(u"prime_hint_locations_scroll_contents")
        self.prime_hint_locations_scroll_contents.setGeometry(QRect(0, 0, 98, 352))
        self.hint_scroll_layout_4 = QVBoxLayout(self.prime_hint_locations_scroll_contents)
        self.hint_scroll_layout_4.setSpacing(6)
        self.hint_scroll_layout_4.setContentsMargins(11, 11, 11, 11)
        self.hint_scroll_layout_4.setObjectName(u"hint_scroll_layout_4")
        self.prime_hint_locations_label = QLabel(self.prime_hint_locations_scroll_contents)
        self.prime_hint_locations_label.setObjectName(u"prime_hint_locations_label")
        self.prime_hint_locations_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.prime_hint_locations_label.setWordWrap(True)

        self.hint_scroll_layout_4.addWidget(self.prime_hint_locations_label)

        self.prime_hint_locations_tree_widget = QTreeWidget(self.prime_hint_locations_scroll_contents)
        self.prime_hint_locations_tree_widget.setObjectName(u"prime_hint_locations_tree_widget")

        self.hint_scroll_layout_4.addWidget(self.prime_hint_locations_tree_widget)

        self.prime_hint_locations_scroll_area.setWidget(self.prime_hint_locations_scroll_contents)

        self.hint_tab_layout_4.addWidget(self.prime_hint_locations_scroll_area)

        self.help_prime_tab_widget.addTab(self.prime_hint_locations_tab, "")

        self.prime_tab_layout.addWidget(self.help_prime_tab_widget)

        self.games_tab_widget.addTab(self.help_prime_tab, "")
        self.help_echoes_tab = QWidget()
        self.help_echoes_tab.setObjectName(u"help_echoes_tab")
        self.echoes_tab_layout = QVBoxLayout(self.help_echoes_tab)
        self.echoes_tab_layout.setSpacing(6)
        self.echoes_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_tab_layout.setObjectName(u"echoes_tab_layout")
        self.echoes_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.help_echoes_tab_widget = QTabWidget(self.help_echoes_tab)
        self.help_echoes_tab_widget.setObjectName(u"help_echoes_tab_widget")
        self.echoes_faq_tab = QWidget()
        self.echoes_faq_tab.setObjectName(u"echoes_faq_tab")
        self.echoes_faq_layout = QGridLayout(self.echoes_faq_tab)
        self.echoes_faq_layout.setSpacing(6)
        self.echoes_faq_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_faq_layout.setObjectName(u"echoes_faq_layout")
        self.echoes_faq_layout.setContentsMargins(0, 0, 0, 0)
        self.echoes_faq_scroll_area = QScrollArea(self.echoes_faq_tab)
        self.echoes_faq_scroll_area.setObjectName(u"echoes_faq_scroll_area")
        self.echoes_faq_scroll_area.setWidgetResizable(True)
        self.echoes_faq_scroll_area_contents = QWidget()
        self.echoes_faq_scroll_area_contents.setObjectName(u"echoes_faq_scroll_area_contents")
        self.echoes_faq_scroll_area_contents.setGeometry(QRect(0, 0, 108, 2718))
        self.gridLayout_8 = QGridLayout(self.echoes_faq_scroll_area_contents)
        self.gridLayout_8.setSpacing(6)
        self.gridLayout_8.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.echoes_faq_label = QLabel(self.echoes_faq_scroll_area_contents)
        self.echoes_faq_label.setObjectName(u"echoes_faq_label")
        self.echoes_faq_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.echoes_faq_label.setWordWrap(True)

        self.gridLayout_8.addWidget(self.echoes_faq_label, 0, 0, 1, 1)

        self.echoes_faq_scroll_area.setWidget(self.echoes_faq_scroll_area_contents)

        self.echoes_faq_layout.addWidget(self.echoes_faq_scroll_area, 0, 0, 1, 1)

        self.help_echoes_tab_widget.addTab(self.echoes_faq_tab, "")
        self.echoes_differences_tab = QWidget()
        self.echoes_differences_tab.setObjectName(u"echoes_differences_tab")
        self.echoes_differences_tab_layout = QVBoxLayout(self.echoes_differences_tab)
        self.echoes_differences_tab_layout.setSpacing(6)
        self.echoes_differences_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_differences_tab_layout.setObjectName(u"echoes_differences_tab_layout")
        self.echoes_differences_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.echoes_differences_scroll_area = QScrollArea(self.echoes_differences_tab)
        self.echoes_differences_scroll_area.setObjectName(u"echoes_differences_scroll_area")
        self.echoes_differences_scroll_area.setWidgetResizable(True)
        self.echoes_differences_scroll_contents = QWidget()
        self.echoes_differences_scroll_contents.setObjectName(u"echoes_differences_scroll_contents")
        self.echoes_differences_scroll_contents.setGeometry(QRect(0, 0, 123, 3942))
        self.differences_scroll_layout_3 = QVBoxLayout(self.echoes_differences_scroll_contents)
        self.differences_scroll_layout_3.setSpacing(6)
        self.differences_scroll_layout_3.setContentsMargins(11, 11, 11, 11)
        self.differences_scroll_layout_3.setObjectName(u"differences_scroll_layout_3")
        self.echoes_differences_label = QLabel(self.echoes_differences_scroll_contents)
        self.echoes_differences_label.setObjectName(u"echoes_differences_label")
        self.echoes_differences_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.echoes_differences_label.setWordWrap(True)

        self.differences_scroll_layout_3.addWidget(self.echoes_differences_label)

        self.echoes_differences_scroll_area.setWidget(self.echoes_differences_scroll_contents)

        self.echoes_differences_tab_layout.addWidget(self.echoes_differences_scroll_area)

        self.help_echoes_tab_widget.addTab(self.echoes_differences_tab, "")
        self.echoes_hints_tab = QWidget()
        self.echoes_hints_tab.setObjectName(u"echoes_hints_tab")
        self.echoes_hints_tab_layout = QVBoxLayout(self.echoes_hints_tab)
        self.echoes_hints_tab_layout.setSpacing(0)
        self.echoes_hints_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_hints_tab_layout.setObjectName(u"echoes_hints_tab_layout")
        self.echoes_hints_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.echoes_hints_scroll_area = QScrollArea(self.echoes_hints_tab)
        self.echoes_hints_scroll_area.setObjectName(u"echoes_hints_scroll_area")
        self.echoes_hints_scroll_area.setWidgetResizable(True)
        self.echoes_hints_scroll_area_contents = QWidget()
        self.echoes_hints_scroll_area_contents.setObjectName(u"echoes_hints_scroll_area_contents")
        self.echoes_hints_scroll_area_contents.setGeometry(QRect(0, 0, 98, 3486))
        self.echoes_hints_scroll_layout = QVBoxLayout(self.echoes_hints_scroll_area_contents)
        self.echoes_hints_scroll_layout.setSpacing(6)
        self.echoes_hints_scroll_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_hints_scroll_layout.setObjectName(u"echoes_hints_scroll_layout")
        self.echoes_hints_label = QLabel(self.echoes_hints_scroll_area_contents)
        self.echoes_hints_label.setObjectName(u"echoes_hints_label")
        self.echoes_hints_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.echoes_hints_label.setWordWrap(True)

        self.echoes_hints_scroll_layout.addWidget(self.echoes_hints_label)

        self.echoes_hints_scroll_area.setWidget(self.echoes_hints_scroll_area_contents)

        self.echoes_hints_tab_layout.addWidget(self.echoes_hints_scroll_area)

        self.help_echoes_tab_widget.addTab(self.echoes_hints_tab, "")
        self.echoes_hint_item_names_tab = QWidget()
        self.echoes_hint_item_names_tab.setObjectName(u"echoes_hint_item_names_tab")
        self.echoes_hint_item_names_layout = QVBoxLayout(self.echoes_hint_item_names_tab)
        self.echoes_hint_item_names_layout.setSpacing(0)
        self.echoes_hint_item_names_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_hint_item_names_layout.setObjectName(u"echoes_hint_item_names_layout")
        self.echoes_hint_item_names_layout.setContentsMargins(0, 0, 0, 0)
        self.echoes_hint_item_names_scroll_area = QScrollArea(self.echoes_hint_item_names_tab)
        self.echoes_hint_item_names_scroll_area.setObjectName(u"echoes_hint_item_names_scroll_area")
        self.echoes_hint_item_names_scroll_area.setWidgetResizable(True)
        self.echoes_hint_item_names_scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.echoes_hint_item_names_scroll_contents = QWidget()
        self.echoes_hint_item_names_scroll_contents.setObjectName(u"echoes_hint_item_names_scroll_contents")
        self.echoes_hint_item_names_scroll_contents.setGeometry(QRect(0, 0, 98, 386))
        self.echoes_hint_item_names_scroll_layout = QVBoxLayout(self.echoes_hint_item_names_scroll_contents)
        self.echoes_hint_item_names_scroll_layout.setSpacing(6)
        self.echoes_hint_item_names_scroll_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_hint_item_names_scroll_layout.setObjectName(u"echoes_hint_item_names_scroll_layout")
        self.echoes_hint_item_names_label = QLabel(self.echoes_hint_item_names_scroll_contents)
        self.echoes_hint_item_names_label.setObjectName(u"echoes_hint_item_names_label")
        self.echoes_hint_item_names_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.echoes_hint_item_names_label.setWordWrap(True)

        self.echoes_hint_item_names_scroll_layout.addWidget(self.echoes_hint_item_names_label)

        self.echoes_hint_item_names_tree_widget = QTableWidget(self.echoes_hint_item_names_scroll_contents)
        if (self.echoes_hint_item_names_tree_widget.columnCount() < 4):
            self.echoes_hint_item_names_tree_widget.setColumnCount(4)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.echoes_hint_item_names_tree_widget.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.echoes_hint_item_names_tree_widget.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.echoes_hint_item_names_tree_widget.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.echoes_hint_item_names_tree_widget.setHorizontalHeaderItem(3, __qtablewidgetitem7)
        self.echoes_hint_item_names_tree_widget.setObjectName(u"echoes_hint_item_names_tree_widget")
        self.echoes_hint_item_names_tree_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.echoes_hint_item_names_tree_widget.setSortingEnabled(True)

        self.echoes_hint_item_names_scroll_layout.addWidget(self.echoes_hint_item_names_tree_widget)

        self.echoes_hint_item_names_scroll_area.setWidget(self.echoes_hint_item_names_scroll_contents)

        self.echoes_hint_item_names_layout.addWidget(self.echoes_hint_item_names_scroll_area)

        self.help_echoes_tab_widget.addTab(self.echoes_hint_item_names_tab, "")
        self.echoes_hint_locations_tab = QWidget()
        self.echoes_hint_locations_tab.setObjectName(u"echoes_hint_locations_tab")
        self.echoes_hint_tab_layout = QVBoxLayout(self.echoes_hint_locations_tab)
        self.echoes_hint_tab_layout.setSpacing(6)
        self.echoes_hint_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_hint_tab_layout.setObjectName(u"echoes_hint_tab_layout")
        self.echoes_hint_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.echoes_hint_locations_scroll_area = QScrollArea(self.echoes_hint_locations_tab)
        self.echoes_hint_locations_scroll_area.setObjectName(u"echoes_hint_locations_scroll_area")
        self.echoes_hint_locations_scroll_area.setWidgetResizable(True)
        self.echoes_hint_locations_scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.echoes_hint_locations_scroll_contents = QWidget()
        self.echoes_hint_locations_scroll_contents.setObjectName(u"echoes_hint_locations_scroll_contents")
        self.echoes_hint_locations_scroll_contents.setGeometry(QRect(0, 0, 98, 352))
        self.echoes_hint_scroll_layout = QVBoxLayout(self.echoes_hint_locations_scroll_contents)
        self.echoes_hint_scroll_layout.setSpacing(6)
        self.echoes_hint_scroll_layout.setContentsMargins(11, 11, 11, 11)
        self.echoes_hint_scroll_layout.setObjectName(u"echoes_hint_scroll_layout")
        self.echoes_hint_locations_label = QLabel(self.echoes_hint_locations_scroll_contents)
        self.echoes_hint_locations_label.setObjectName(u"echoes_hint_locations_label")
        self.echoes_hint_locations_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.echoes_hint_locations_label.setWordWrap(True)

        self.echoes_hint_scroll_layout.addWidget(self.echoes_hint_locations_label)

        self.echoes_hint_locations_tree_widget = QTreeWidget(self.echoes_hint_locations_scroll_contents)
        self.echoes_hint_locations_tree_widget.setObjectName(u"echoes_hint_locations_tree_widget")

        self.echoes_hint_scroll_layout.addWidget(self.echoes_hint_locations_tree_widget)

        self.echoes_hint_locations_scroll_area.setWidget(self.echoes_hint_locations_scroll_contents)

        self.echoes_hint_tab_layout.addWidget(self.echoes_hint_locations_scroll_area)

        self.help_echoes_tab_widget.addTab(self.echoes_hint_locations_tab, "")

        self.echoes_tab_layout.addWidget(self.help_echoes_tab_widget)

        self.games_tab_widget.addTab(self.help_echoes_tab, "")
        self.help_corruption_tab = QWidget()
        self.help_corruption_tab.setObjectName(u"help_corruption_tab")
        self.corruption_tab_layout = QVBoxLayout(self.help_corruption_tab)
        self.corruption_tab_layout.setSpacing(6)
        self.corruption_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_tab_layout.setObjectName(u"corruption_tab_layout")
        self.corruption_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.help_corruption_tab_widget = QTabWidget(self.help_corruption_tab)
        self.help_corruption_tab_widget.setObjectName(u"help_corruption_tab_widget")
        self.corruption_faq_tab = QWidget()
        self.corruption_faq_tab.setObjectName(u"corruption_faq_tab")
        self.faq_layout_3 = QGridLayout(self.corruption_faq_tab)
        self.faq_layout_3.setSpacing(6)
        self.faq_layout_3.setContentsMargins(11, 11, 11, 11)
        self.faq_layout_3.setObjectName(u"faq_layout_3")
        self.faq_layout_3.setContentsMargins(0, 0, 0, 0)
        self.corruption_faq_scroll_area = QScrollArea(self.corruption_faq_tab)
        self.corruption_faq_scroll_area.setObjectName(u"corruption_faq_scroll_area")
        self.corruption_faq_scroll_area.setWidgetResizable(True)
        self.corruption_faq_scroll_area_contents = QWidget()
        self.corruption_faq_scroll_area_contents.setObjectName(u"corruption_faq_scroll_area_contents")
        self.corruption_faq_scroll_area_contents.setGeometry(QRect(0, 0, 98, 86))
        self.gridLayout_9 = QGridLayout(self.corruption_faq_scroll_area_contents)
        self.gridLayout_9.setSpacing(6)
        self.gridLayout_9.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.corruption_faq_label = QLabel(self.corruption_faq_scroll_area_contents)
        self.corruption_faq_label.setObjectName(u"corruption_faq_label")
        self.corruption_faq_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.corruption_faq_label.setWordWrap(True)

        self.gridLayout_9.addWidget(self.corruption_faq_label, 0, 0, 1, 1)

        self.corruption_faq_scroll_area.setWidget(self.corruption_faq_scroll_area_contents)

        self.faq_layout_3.addWidget(self.corruption_faq_scroll_area, 0, 0, 1, 1)

        self.help_corruption_tab_widget.addTab(self.corruption_faq_tab, "")
        self.corruption_differences_tab = QWidget()
        self.corruption_differences_tab.setObjectName(u"corruption_differences_tab")
        self.corruption_differences_tab_layout = QVBoxLayout(self.corruption_differences_tab)
        self.corruption_differences_tab_layout.setSpacing(6)
        self.corruption_differences_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_differences_tab_layout.setObjectName(u"corruption_differences_tab_layout")
        self.corruption_differences_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.corruption_differences_scroll_area = QScrollArea(self.corruption_differences_tab)
        self.corruption_differences_scroll_area.setObjectName(u"corruption_differences_scroll_area")
        self.corruption_differences_scroll_area.setWidgetResizable(True)
        self.corruption_differences_scroll_contents = QWidget()
        self.corruption_differences_scroll_contents.setObjectName(u"corruption_differences_scroll_contents")
        self.corruption_differences_scroll_contents.setGeometry(QRect(0, 0, 98, 35))
        self.differences_scroll_layout_4 = QVBoxLayout(self.corruption_differences_scroll_contents)
        self.differences_scroll_layout_4.setSpacing(6)
        self.differences_scroll_layout_4.setContentsMargins(11, 11, 11, 11)
        self.differences_scroll_layout_4.setObjectName(u"differences_scroll_layout_4")
        self.corruption_differences_label = QLabel(self.corruption_differences_scroll_contents)
        self.corruption_differences_label.setObjectName(u"corruption_differences_label")
        self.corruption_differences_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.corruption_differences_label.setWordWrap(True)

        self.differences_scroll_layout_4.addWidget(self.corruption_differences_label)

        self.corruption_differences_scroll_area.setWidget(self.corruption_differences_scroll_contents)

        self.corruption_differences_tab_layout.addWidget(self.corruption_differences_scroll_area)

        self.help_corruption_tab_widget.addTab(self.corruption_differences_tab, "")
        self.corruption_hints_tab = QWidget()
        self.corruption_hints_tab.setObjectName(u"corruption_hints_tab")
        self.corruption_hints_tab_layout = QVBoxLayout(self.corruption_hints_tab)
        self.corruption_hints_tab_layout.setSpacing(0)
        self.corruption_hints_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_hints_tab_layout.setObjectName(u"corruption_hints_tab_layout")
        self.corruption_hints_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.corruption_hints_scroll_area = QScrollArea(self.corruption_hints_tab)
        self.corruption_hints_scroll_area.setObjectName(u"corruption_hints_scroll_area")
        self.corruption_hints_scroll_area.setWidgetResizable(True)
        self.corruption_hints_scroll_area_contents = QWidget()
        self.corruption_hints_scroll_area_contents.setObjectName(u"corruption_hints_scroll_area_contents")
        self.corruption_hints_scroll_area_contents.setGeometry(QRect(0, 0, 98, 285))
        self.corruption_hints_scroll_layout = QVBoxLayout(self.corruption_hints_scroll_area_contents)
        self.corruption_hints_scroll_layout.setSpacing(6)
        self.corruption_hints_scroll_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_hints_scroll_layout.setObjectName(u"corruption_hints_scroll_layout")
        self.corruption_hints_label = QLabel(self.corruption_hints_scroll_area_contents)
        self.corruption_hints_label.setObjectName(u"corruption_hints_label")
        self.corruption_hints_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.corruption_hints_label.setWordWrap(True)

        self.corruption_hints_scroll_layout.addWidget(self.corruption_hints_label)

        self.corruption_hints_scroll_area.setWidget(self.corruption_hints_scroll_area_contents)

        self.corruption_hints_tab_layout.addWidget(self.corruption_hints_scroll_area)

        self.help_corruption_tab_widget.addTab(self.corruption_hints_tab, "")
        self.corruption_hint_item_names_tab = QWidget()
        self.corruption_hint_item_names_tab.setObjectName(u"corruption_hint_item_names_tab")
        self.corruption_hint_item_names_layout = QVBoxLayout(self.corruption_hint_item_names_tab)
        self.corruption_hint_item_names_layout.setSpacing(0)
        self.corruption_hint_item_names_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_hint_item_names_layout.setObjectName(u"corruption_hint_item_names_layout")
        self.corruption_hint_item_names_layout.setContentsMargins(0, 0, 0, 0)
        self.corruption_hint_item_names_scroll_area = QScrollArea(self.corruption_hint_item_names_tab)
        self.corruption_hint_item_names_scroll_area.setObjectName(u"corruption_hint_item_names_scroll_area")
        self.corruption_hint_item_names_scroll_area.setWidgetResizable(True)
        self.corruption_hint_item_names_scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.corruption_hint_item_names_scroll_contents = QWidget()
        self.corruption_hint_item_names_scroll_contents.setObjectName(u"corruption_hint_item_names_scroll_contents")
        self.corruption_hint_item_names_scroll_contents.setGeometry(QRect(0, 0, 98, 386))
        self.corruption_hint_item_names_scroll_layout = QVBoxLayout(self.corruption_hint_item_names_scroll_contents)
        self.corruption_hint_item_names_scroll_layout.setSpacing(6)
        self.corruption_hint_item_names_scroll_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_hint_item_names_scroll_layout.setObjectName(u"corruption_hint_item_names_scroll_layout")
        self.corruption_hint_item_names_label = QLabel(self.corruption_hint_item_names_scroll_contents)
        self.corruption_hint_item_names_label.setObjectName(u"corruption_hint_item_names_label")
        self.corruption_hint_item_names_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.corruption_hint_item_names_label.setWordWrap(True)

        self.corruption_hint_item_names_scroll_layout.addWidget(self.corruption_hint_item_names_label)

        self.corruption_hint_item_names_tree_widget = QTableWidget(self.corruption_hint_item_names_scroll_contents)
        if (self.corruption_hint_item_names_tree_widget.columnCount() < 4):
            self.corruption_hint_item_names_tree_widget.setColumnCount(4)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.corruption_hint_item_names_tree_widget.setHorizontalHeaderItem(0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.corruption_hint_item_names_tree_widget.setHorizontalHeaderItem(1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.corruption_hint_item_names_tree_widget.setHorizontalHeaderItem(2, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.corruption_hint_item_names_tree_widget.setHorizontalHeaderItem(3, __qtablewidgetitem11)
        self.corruption_hint_item_names_tree_widget.setObjectName(u"corruption_hint_item_names_tree_widget")
        self.corruption_hint_item_names_tree_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.corruption_hint_item_names_tree_widget.setSortingEnabled(True)

        self.corruption_hint_item_names_scroll_layout.addWidget(self.corruption_hint_item_names_tree_widget)

        self.corruption_hint_item_names_scroll_area.setWidget(self.corruption_hint_item_names_scroll_contents)

        self.corruption_hint_item_names_layout.addWidget(self.corruption_hint_item_names_scroll_area)

        self.help_corruption_tab_widget.addTab(self.corruption_hint_item_names_tab, "")
        self.corruption_hint_locations_tab = QWidget()
        self.corruption_hint_locations_tab.setObjectName(u"corruption_hint_locations_tab")
        self.corruption_hint_tab_layout = QVBoxLayout(self.corruption_hint_locations_tab)
        self.corruption_hint_tab_layout.setSpacing(6)
        self.corruption_hint_tab_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_hint_tab_layout.setObjectName(u"corruption_hint_tab_layout")
        self.corruption_hint_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.corruption_hint_locations_scroll_area = QScrollArea(self.corruption_hint_locations_tab)
        self.corruption_hint_locations_scroll_area.setObjectName(u"corruption_hint_locations_scroll_area")
        self.corruption_hint_locations_scroll_area.setWidgetResizable(True)
        self.corruption_hint_locations_scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.corruption_hint_locations_scroll_contents = QWidget()
        self.corruption_hint_locations_scroll_contents.setObjectName(u"corruption_hint_locations_scroll_contents")
        self.corruption_hint_locations_scroll_contents.setGeometry(QRect(0, 0, 98, 352))
        self.corruption_hint_scroll_layout = QVBoxLayout(self.corruption_hint_locations_scroll_contents)
        self.corruption_hint_scroll_layout.setSpacing(6)
        self.corruption_hint_scroll_layout.setContentsMargins(11, 11, 11, 11)
        self.corruption_hint_scroll_layout.setObjectName(u"corruption_hint_scroll_layout")
        self.corruption_hint_locations_label = QLabel(self.corruption_hint_locations_scroll_contents)
        self.corruption_hint_locations_label.setObjectName(u"corruption_hint_locations_label")
        self.corruption_hint_locations_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.corruption_hint_locations_label.setWordWrap(True)

        self.corruption_hint_scroll_layout.addWidget(self.corruption_hint_locations_label)

        self.corruption_hint_locations_tree_widget = QTreeWidget(self.corruption_hint_locations_scroll_contents)
        self.corruption_hint_locations_tree_widget.setObjectName(u"corruption_hint_locations_tree_widget")

        self.corruption_hint_scroll_layout.addWidget(self.corruption_hint_locations_tree_widget)

        self.corruption_hint_locations_scroll_area.setWidget(self.corruption_hint_locations_scroll_contents)

        self.corruption_hint_tab_layout.addWidget(self.corruption_hint_locations_scroll_area)

        self.help_corruption_tab_widget.addTab(self.corruption_hint_locations_tab, "")

        self.corruption_tab_layout.addWidget(self.help_corruption_tab_widget)

        self.games_tab_widget.addTab(self.help_corruption_tab, "")

        self.games_tab_layout.addWidget(self.games_tab_widget)

        self.main_tab_widget.addTab(self.games_tab, "")
        self.about_tab = QWidget()
        self.about_tab.setObjectName(u"about_tab")
        self.about_layout = QGridLayout(self.about_tab)
        self.about_layout.setSpacing(6)
        self.about_layout.setContentsMargins(11, 11, 11, 11)
        self.about_layout.setObjectName(u"about_layout")
        self.about_layout.setContentsMargins(0, 0, 0, 0)
        self.about_text_browser = QTextBrowser(self.about_tab)
        self.about_text_browser.setObjectName(u"about_text_browser")
        self.about_text_browser.setFrameShape(QFrame.NoFrame)
        self.about_text_browser.setOpenExternalLinks(True)

        self.about_layout.addWidget(self.about_text_browser, 0, 0, 1, 1)

        self.main_tab_widget.addTab(self.about_tab, "")

        self.verticalLayout_4.addWidget(self.main_tab_widget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menu_bar = QMenuBar(MainWindow)
        self.menu_bar.setObjectName(u"menu_bar")
        self.menu_bar.setGeometry(QRect(0, 0, 645, 22))
        self.menu_open = QMenu(self.menu_bar)
        self.menu_open.setObjectName(u"menu_open")
        self.menu_edit = QMenu(self.menu_bar)
        self.menu_edit.setObjectName(u"menu_edit")
        self.menu_database = QMenu(self.menu_edit)
        self.menu_database.setObjectName(u"menu_database")
        self.menu_internal = QMenu(self.menu_database)
        self.menu_internal.setObjectName(u"menu_internal")
        self.menu_advanced = QMenu(self.menu_bar)
        self.menu_advanced.setObjectName(u"menu_advanced")
        MainWindow.setMenuBar(self.menu_bar)

        self.menu_bar.addAction(self.menu_open.menuAction())
        self.menu_bar.addAction(self.menu_edit.menuAction())
        self.menu_bar.addAction(self.menu_advanced.menuAction())
        self.menu_open.addAction(self.menu_action_previously_generated_games)
        self.menu_open.addAction(self.menu_action_log_files_directory)
        self.menu_open.addSeparator()
        self.menu_open.addAction(self.menu_action_item_tracker)
        self.menu_open.addAction(self.menu_action_open_auto_tracker)
        self.menu_open.addSeparator()
        self.menu_open.addSeparator()
        self.menu_edit.addAction(self.menu_database.menuAction())
        self.menu_database.addAction(self.menu_internal.menuAction())
        self.menu_database.addAction(self.menu_action_edit_existing_database)
        self.menu_advanced.addAction(self.menu_action_validate_seed_after)
        self.menu_advanced.addAction(self.menu_action_timeout_generation_after_a_time_limit)
        self.menu_advanced.addAction(self.menu_action_dark_mode)
        self.menu_advanced.addAction(self.menu_action_experimental_games)
        self.menu_advanced.addSeparator()
        self.menu_advanced.addAction(self.action_login_window)
        self.menu_advanced.addSeparator()
        self.menu_advanced.addAction(self.menu_action_layout_editor)

        self.retranslateUi(MainWindow)

        self.main_tab_widget.setCurrentIndex(0)
        self.help_tab_widget.setCurrentIndex(0)
        self.games_tab_widget.setCurrentIndex(0)
        self.help_prime_tab_widget.setCurrentIndex(0)
        self.help_echoes_tab_widget.setCurrentIndex(0)
        self.help_corruption_tab_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Randovania", None))
        self.menu_action_existing_seed_details.setText(QCoreApplication.translate("MainWindow", u"Existing Seed Details", None))
        self.menu_action_edit_existing_database.setText(QCoreApplication.translate("MainWindow", u"External file", None))
        self.menu_action_load_iso.setText(QCoreApplication.translate("MainWindow", u"Load vanilla game ISO", None))
        self.menu_action_validate_seed_after.setText(QCoreApplication.translate("MainWindow", u"Validate if seed is possible after generation", None))
        self.menu_action_timeout_generation_after_a_time_limit.setText(QCoreApplication.translate("MainWindow", u"Timeout generation after a time limit", None))
        self.menu_action_delete_loaded_game.setText(QCoreApplication.translate("MainWindow", u"Delete loaded game", None))
        self.menu_action_item_tracker.setText(QCoreApplication.translate("MainWindow", u"STB's Echoes Item Tracker", None))
        self.menu_action_open_auto_tracker.setText(QCoreApplication.translate("MainWindow", u"Automatic Item Tracker", None))
        self.action_login_window.setText(QCoreApplication.translate("MainWindow", u"Login window", None))
        self.action_login_as_guest.setText(QCoreApplication.translate("MainWindow", u"Login as guest", None))
        self.actionLogged_in_as.setText(QCoreApplication.translate("MainWindow", u"Logged in as {}", None))
        self.menu_action_edit_prime_1.setText(QCoreApplication.translate("MainWindow", u"Prime 1", None))
        self.menu_action_edit_prime_2.setText(QCoreApplication.translate("MainWindow", u"Prime 2", None))
        self.menu_action_edit_prime_3.setText(QCoreApplication.translate("MainWindow", u"Prime 3", None))
        self.menu_action_visualize_prime_1.setText(QCoreApplication.translate("MainWindow", u"Prime 1", None))
        self.menu_action_visualize_prime_2.setText(QCoreApplication.translate("MainWindow", u"Prime 2", None))
        self.menu_action_visualize_prime_3.setText(QCoreApplication.translate("MainWindow", u"Prime 3", None))
        self.menu_action_dark_mode.setText(QCoreApplication.translate("MainWindow", u"Dark Mode", None))
        self.menu_action_previously_generated_games.setText(QCoreApplication.translate("MainWindow", u"Previously generated games", None))
        self.menu_action_layout_editor.setText(QCoreApplication.translate("MainWindow", u"Corruption Layout Editor", None))
        self.menu_action_map_tracker.setText(QCoreApplication.translate("MainWindow", u"Map Tracker", None))
        self.menu_action_prime_3_data_visualizer.setText(QCoreApplication.translate("MainWindow", u"Data Visualizer", None))
        self.actionasdf.setText(QCoreApplication.translate("MainWindow", u"asdf", None))
        self.menu_action_prime_2_data_visualizer.setText(QCoreApplication.translate("MainWindow", u"Data Visualizer", None))
        self.actionasdf_2.setText(QCoreApplication.translate("MainWindow", u"asdf", None))
        self.menu_action_prime_1_data_visualizer.setText(QCoreApplication.translate("MainWindow", u"Data Visualizer", None))
        self.actionasdf_3.setText(QCoreApplication.translate("MainWindow", u"asdf", None))
        self.menu_action_log_files_directory.setText(QCoreApplication.translate("MainWindow", u"Log files folder", None))
        self.menu_action_experimental_games.setText(QCoreApplication.translate("MainWindow", u"Experimental games", None))
#if QT_CONFIG(tooltip)
        self.menu_action_experimental_games.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>These games aren't fully integrated into Randovania and might have any number of issues.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.open_database_viewer_button.setText(QCoreApplication.translate("MainWindow", u"Open Database Viewer", None))
        self.open_faq_button.setText(QCoreApplication.translate("MainWindow", u"Open FAQ", None))
        self.help_offer_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><hr/><p>Want to learn more about the randomizer?</p><p>Check out the <span style=\" font-weight:600;\">FAQ </span>for surprising behaviour of the game.<br/>Check the Database to check what's required to progress in each room.</p></body></html>", None))
        self.intro_play_now_button.setText(QCoreApplication.translate("MainWindow", u"Play Now", None))
        self.intro_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Welcome to Randovania {version}, a randomizer for Metroid Prime and Metroid Prime 2: Echoes.</p><p>Here you will be able to randomize many aspects of either game, while still being ensured it's possible to finish without any trick or glitch! What can be randomized?</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Randomize what can be found in each pickup location, including major upgrades, expansions, keys and artifacts.</li><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Play with multiple people, via multiworld sessions. Your pickups will be shuffled among the games of everyone involved, no matter what game they're playing!</li><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                        "text-indent:0px;\">Randomize where each teleporter goes, or what you need to unlock a translator gate. In either case, there's advanced options for how they're shuffled.</li><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The location you start the game in as well as the items you start with. If you're feeling brave, you can even shuffle items you normally start with, like the Power Beam and Scan Visor.</li></ul><p>So have fun and start randomizing.</p></body></html>", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.welcome_tab), QCoreApplication.translate("MainWindow", u"Welcome", None))
        self.play_existing_permalink_group.setTitle(QCoreApplication.translate("MainWindow", u"Existing games", None))
        self.import_permalink_button.setText(QCoreApplication.translate("MainWindow", u"Import permalink", None))
        self.browse_sessions_button.setText(QCoreApplication.translate("MainWindow", u"Browse for a multiworld session", None))
        self.import_permalink_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Are you playing with others?</p><p>Ask them for a permalink and import it here. You'll create the same game as them.</p></body></html>", None))
        self.import_game_file_label.setText(QCoreApplication.translate("MainWindow", u"If they've shared a spoiler file instead, you can import it directly. This skips the generation step.", None))
        self.browse_racetime_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Are you joining a race hosted in <a href=\"https://racetime.gg/\"><span style=\" text-decoration: underline; color:#0000ff;\">racetime.gg</span></a>?</p><p>Select the race from Randovania and automatically import the permalink!</p></body></html>", None))
        self.import_game_file_button.setText(QCoreApplication.translate("MainWindow", u"Import game file", None))
        self.browse_racetime_button.setText(QCoreApplication.translate("MainWindow", u"Browse races in racetime.gg", None))
        self.browse_sessions_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Joining a multiworld that someone else created? Browse all existing sessions here!</p></body></html>", None))
        self.play_new_game_group.setTitle(QCoreApplication.translate("MainWindow", u"Creating a new game", None))
        self.host_new_game_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Want to play multiworld?</p><p>Host a new online session and invite people!</p></body></html>", None))
        self.create_new_seed_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Playing alone? Hosting a race?</p><p>Create a new game here and then share the permalink!</p></body></html>", None))
        self.create_new_seed_button.setText(QCoreApplication.translate("MainWindow", u"Create new game", None))
        self.host_new_game_button.setText(QCoreApplication.translate("MainWindow", u"Host new multiworld session", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.tab_play), QCoreApplication.translate("MainWindow", u"Play", None))
        self.create_generate_no_retry_button.setText(QCoreApplication.translate("MainWindow", u"Generate without retry", None))
        self.create_generate_race_button.setText(QCoreApplication.translate("MainWindow", u"Generate for Race", None))
        self.create_generate_button.setText(QCoreApplication.translate("MainWindow", u"Generate", None))
        self.num_players_spin_box.setSuffix(QCoreApplication.translate("MainWindow", u" players", None))
        ___qtreewidgetitem = self.create_preset_tree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Presets (Right click for actions)", None));

        __sortingEnabled = self.create_preset_tree.isSortingEnabled()
        self.create_preset_tree.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.create_preset_tree.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Metroid Prime", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"Default Preset", None));
        ___qtreewidgetitem3 = ___qtreewidgetitem2.child(0)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("MainWindow", u"Your Custom Preset", None));
        ___qtreewidgetitem4 = self.create_preset_tree.topLevelItem(1)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("MainWindow", u"Metroid Prime 2", None));
        self.create_preset_tree.setSortingEnabled(__sortingEnabled)

        self.progress_box.setTitle(QCoreApplication.translate("MainWindow", u"Progress", None))
        self.stop_background_process_button.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.progress_label.setText("")
        self.create_preset_description.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>This content should have been replaced by code.</p></body></html>", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.tab_create_seed), QCoreApplication.translate("MainWindow", u"Generate Game", None))
        self.multiworld_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Multiworld is a co-op multiplayer game mode for the randomizer.</p><p>In a multiworld game, each player has their own unique world filled with items destined for an specific player. When you collect an item, it is instantly delivered to the owner.</p><p><span style=\" font-weight:600;\">How do I play multiworld?</span></p><p>In the Play tab, either join a session or host a new one. Create one row for each player, customize their presets and then generate a game. Double check if the presets are correct and then start the session.</p><p>Each player exports their own ISO and opens it in Dolphin or Nintendont and keeps Randovania open.</p><p><span style=\" font-weight:600;\">How do I send an item to someone else?</span></p><p>Certain items in your game will belong to some other player. After collected, you receive an alert that it was sent to someone else.</p><p>You must make sure that Randovania is connected to the game and the game session window is open. The History tab in the session can "
                        "be used to confirm the item was detected and sent correctly.</p><p>WARNING: Collecting multiple items for other players in quick succession (less than 5s) will prevent Randovania from detecting either item, causing both to be lost until you reload a save file. Using Infinite Speed to collect multiple items at once will hit this limitation.</p><p><span style=\" font-weight:600;\">What happens if I die, reload a save or crash?</span></p><p>All received items you've lost are automatically re-delivered. Collecting some item you've already sent someone else has no effect and is perfectly safe.</p><p><span style=\" font-weight:600;\">What happens if I disconnect from the server?</span></p><p>Randovania keeps track of everything you've collected and will send to the server as soon as it regains connection, even if restarted.</p><p><span style=\" font-weight:600;\">What happens if Randovania disconnects from the game?</span></p><p>Do <span style=\" font-style:italic;\">not</span> collect any item if Randovania is not "
                        "connected to your game (closed, error in connection) as it will be lost forever. </p><p><span style=\" font-weight:600;\">Do all players have to play at the same time?</span></p><p>No. All comunication between players is managed by Randovania's server.</p><p><span style=\" font-weight:600;\">Can I play on a Wii?</span></p><p>Yes. Connect your Wii to the same Wifi as your computer and open Homebrew Channel. Press the &quot;Upload Nintendont to Homebrew Channel&quot; button found in the <span style=\" font-style:italic;\">Configure backend</span> menu of the Game Session window.</p><p><span style=\" font-weight:600;\">Can different games be mixed in a session?</span></p><p>Yes. Items for another game will be appear using an equivalent model for your game, or the generic model (Nothing for Prime 1, Energy Transfer Module for Prime 2).</p></body></html>", None))
        self.help_tab_widget.setTabText(self.help_tab_widget.indexOf(self.tab_multiworld), QCoreApplication.translate("MainWindow", u"Multiworld", None))
        self.tracker_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Randovania includes a simple &quot;map&quot; tracker.</p><p>To open, click the <span style=\" font-weight:600;\">Generate Game</span> tab and right-click the preset under the game you will use to generate a seed.</p><p><img src=\"data/gui_assets/tracker-open.png\"/></p><p>The tracker uses the logic and game modifications configuration from the selected preset. It shows where you can go depending on where you are in the game, as well as which items you've picked up and events you've triggered.</p><p>To use the tracker, simply select the items on the left that you have. This will open up new locations on the right side. Click events and pickups as you progress for more locations to show up. If you make a mistake, click the <span style=\" font-weight:600;\">Actions</span> tab to undo the latest action you made.</p><p>If you randomized the elevators, click the <span style=\" font-weight:600;\">Elevators</span> tab to configure how the elevators are setup. If you shuffled the translator gates "
                        "in Prime 2, you can configure those as well via the <span style=\" font-weight:600;\">Translator Gate</span> tab.</p><p>Random starting location is also accounted for if enabled for your settings, so make sure you set the correct starting room when opening the tracker.</p></body></html>", None))
        self.help_tab_widget.setTabText(self.help_tab_widget.indexOf(self.tab_tracker), QCoreApplication.translate("MainWindow", u"Tracker", None))
        self.database_viewer_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Randovania has an extensive database with many tricks and paths that are configurable in a given preset. This is where all the logic is stored and determines what is required of a player in a seed given certain trick difficulties.</p><p>To open the database, click the <span style=\" font-weight:600;\">Open</span> menu and select a game from the dropdown. From here you can view each individual trick or click the <span style=\" font-weight:600;\">Data Visualizer</span> option.</p><p><img src=\"data/gui_assets/database-open.png\"/></p><p>Using the database might take some time to get used to, but it is highly recommended to get familiar with it in case you need to figure out what tricks you might want to play with and how to get from point A to point B.</p><p><span style=\" font-weight:600;\">How to Read the Database</span></p><p><img src=\"data/gui_assets/database-example.png\"/></p><p>The left dropdown lists the areas for the respective game, and the right dropdown is the list of rooms in "
                        "the area selected.</p><p>Once you have a room selected, click a Node from the <span style=\" font-style:italic;\">Nodes</span> box. This is your starting point.</p><p>In the <span style=\" font-style:italic;\">Connections</span> box, select a node from the dropdown menu. These are your destinations. This is where you can view what tricks are required on a path from node to node. </p><p>Nodes that are bolded have a path to the selected node.</p><p><span style=\" font-weight:600;\">List of Nodes</span></p><p>These are the relevant locations in a room. These include:</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Doors</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Blast Shields</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; "
                        "margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Elevators (Prime 1/2)</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Teleporters (Prime 3)</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Portals (Prime 2)</li><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Pickups</li></ul><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Events</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Helper Nodes: general nodes that other nodes link up for database simplification)</li></ul><p><span style=\" font-weight:600;\">Node Info<"
                        "/span></p><p>This box tells important information about a specific node.</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Door/Blast Shield/Portal: Mentions what is needed to open it and what room it connects to.</li></ul><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Elevator/Telporter: Mentions what room it connects to.</li></ul><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Pickup: Mentions what number it is and if it's a major item or not.</li><li style=\" marg"
                        "in-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Events: Specific one-time events that must be completed in order to progress on certain paths.</li></ul></body></html>", None))
        self.help_tab_widget.setTabText(self.help_tab_widget.indexOf(self.database_viewer_tab), QCoreApplication.translate("MainWindow", u"Database Viewer", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.help_tab), QCoreApplication.translate("MainWindow", u"Randovania Help", None))
        self.prime_faq_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Nothing right now. Please suggest questions!</span></p></body></html>", None))
        self.help_prime_tab_widget.setTabText(self.help_prime_tab_widget.indexOf(self.prime_faq_tab), QCoreApplication.translate("MainWindow", u"FAQ", None))
        self.prime_differences_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>TODO</p></body></html>", None))
        self.help_prime_tab_widget.setTabText(self.help_prime_tab_widget.indexOf(self.prime_differences_tab), QCoreApplication.translate("MainWindow", u"Differences", None))
        self.prime_hints_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"justify\">In Metroid Prime, you can find hints from the following sources:</p><p align=\"justify\"><span style=\" font-weight:600;\">Artifact Temple</span>: Hints for where each of your 12 Artifacts are located. In a Multiworld, describes which player has the artifacts as well.</p></body></html>", None))
        self.help_prime_tab_widget.setTabText(self.help_prime_tab_widget.indexOf(self.prime_hints_tab), QCoreApplication.translate("MainWindow", u"Hints", None))
        self.prime_hint_item_names_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>When items are referenced in a hint, multiple names can be used depending on how precise the hint is. The names each item can use are the following:</p></body></html>", None))
        ___qtablewidgetitem = self.prime_hint_item_names_tree_widget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Item", None));
        ___qtablewidgetitem1 = self.prime_hint_item_names_tree_widget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Precise Category", None));
        ___qtablewidgetitem2 = self.prime_hint_item_names_tree_widget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"General Category", None));
        ___qtablewidgetitem3 = self.prime_hint_item_names_tree_widget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Broad Category", None));
        self.help_prime_tab_widget.setTabText(self.help_prime_tab_widget.indexOf(self.prime_hint_item_names_tab), QCoreApplication.translate("MainWindow", u"Hint Item Names", None))
        self.prime_hint_locations_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Hints are placed in the game by replacing Logbook scans. The following are the scans that may have a hint added to them:</p></body></html>", None))
        ___qtreewidgetitem5 = self.prime_hint_locations_tree_widget.headerItem()
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("MainWindow", u"Location", None));
        self.help_prime_tab_widget.setTabText(self.help_prime_tab_widget.indexOf(self.prime_hint_locations_tab), QCoreApplication.translate("MainWindow", u"Hints Locations", None))
        self.games_tab_widget.setTabText(self.games_tab_widget.indexOf(self.help_prime_tab), QCoreApplication.translate("MainWindow", u"Metroid Prime", None))
        self.echoes_faq_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">I can't use this spider track, even though I have Spider Ball!</span></p><p>The following rooms have surprising vanilla behaviour about their spider tracks:</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Main Reactor (Agon Wastes)</li><p>The spider tracks only works after you beat Dark Samus 1 <span style=\" font-style:italic;\">and reload the room</span>. When playing with no tricks, this means you need Dark Beam to escape the room.</p><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Dynamo Works (Sanctuary Fortress)</li><p>The spider tracks only works after you beat Spider Guardian. When playing with no tricks, you can't leave this way until you do that.</p><li style=\" margin-top:12px; margin-b"
                        "ottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Spider Guardian fight (Sanctuary Fortress)</li><p>During the fight, the spider tracks only works in the first and last phases. After the fight, they all work normally.<br/>This means you need Boost Ball to fight Spider Guardian.</p></ul><p><span style=\" font-weight:600;\">Where is the Flying Ing Cache inside Dark Oasis?</span></p><p>The Flying Ing Cache in this room appears only after you collect the item that appears after defeating Power Bomb Guardian.</p><p><span style=\" font-weight:600;\">When causes the Dark Missile Trooper to spawn?</span></p><p>Defeating the Bomb Guardian.</p><p><span style=\" font-weight:600;\">What causes the Missile Expansion on top of the GFMC Compound to spawn?</span></p><p>Collecting the item that appears after defeating the Jump Guardian.</p><p><span style=\" font-weight:600;\">Why isn't the elevator in Torvus Temple working?</span></p><p>In order to open the elevator, you also need to pick th"
                        "e item in Torvus Energy Controller.</p><p><span style=\" font-weight:600;\">Why can't I see the echo locks in Mining Plaza even when using the Echo Visor?</span></p><p>You need to beat Amorbis and then return the Agon Energy in order for these echo locks to appear.</p><p><span style=\" font-weight:600;\">Why can't I cross the door between Underground Transport and Torvus Temple?</span></p><p>The energy gate that disappears after the pirate fight in Torvus Temple blocks this door.</p><p><span style=\" font-weight:600;\">While scanning a hint, weird categories show up in the UI. Is something wrong?</span></p><p>This is a known issue with the randomizer. The correct categories show up in the logbook.</p></body></html>", None))
        self.help_echoes_tab_widget.setTabText(self.help_echoes_tab_widget.indexOf(self.echoes_faq_tab), QCoreApplication.translate("MainWindow", u"FAQ", None))
        self.echoes_differences_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Randovania makes some changes to the original game in order to improve the game experience or to simply fix bugs in the original game.</p><p>Many of these changes are optional and can be disabled in the many options Randovania provides, but the following are <span style=\" font-weight:600;\">always</span> there:</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The item loss cutscene in Hive Chamber B is disabled.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Instead of acquiring the translators by scanning the hologram, there is now an item pickup in the Energy Controllers. This item is thus randomized.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px"
                        ";\">All cutscenes are skippable by default.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Hard Mode and the Image gallery are unlocked by default.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Starting the Dark Samus 1 fight disables adjacent rooms from loading automatically (fixes a potential crash).</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Beating Dark Samus 1 will now turn off the first pass pirates layer in Biostorage Station (fixes a potential crash).</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Agon Temple's first door no longer stays locked after Bomb Guardian until you get the Agon Energy Controller item.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px;"
                        " margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Leaving during the Grapple Guardian fight no longer causes Grapple Guardian to not drop an item if you come back and fight it again.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Luminoth barriers that appear on certain doors after collecting or returning a world's energy have been removed.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Removed some instances in Main Research, to decrease the chance of a crash coming from Central Area Transport West. Also fixed leaving the room midway through destroying the echo locks making it impossible to complete.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Power Bombs no longer instantly kill either Alpha Splinter's first phase or Spider Guardian (doing so would not ac"
                        "tually end the fight, leaving you stuck).</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Getting the Torvus Energy Controller item will no longer block you from getting the Torvus Temple item.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Fixed the door lock in Bioenergy Production, so that it doesn't stay locked if you beat the Aerotroopers before triggering the lock.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Altered a few rooms (Transport A Access, Venomous Pond) so that the PAL version matches NTSC requirements.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Fixed the message when collecting the item in Mining Station B while in the wrong layer.</li><li style=\" margin-top:12px; marg"
                        "in-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Added a warning when going on top of the ship in GFMC Compound before beating Jump Guardian.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The in-game Hint System has been removed. The option for it remains, but does nothing.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The logbook entries that contains hints are now named after the room they're in, with the categories being about which kind of hint they are.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Agon, Torvus and Sanctuary Energy Controllers are alwyas visible in the map, to allow warping with the light beams.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text"
                        "-indent:0px;\">When a crash happens, the game now displays an error screen instead of just stopping.</li></ul></body></html>", None))
        self.help_echoes_tab_widget.setTabText(self.help_echoes_tab_widget.indexOf(self.echoes_differences_tab), QCoreApplication.translate("MainWindow", u"Differences", None))
        self.echoes_hints_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"justify\">In Metroid Prime 2: Echoes, you can find hints from the following sources:</p><p align=\"justify\"><span style=\" font-weight:600;\">Sky Temple Gateway</span>: Hints for where each of your 9 Sky Temple Keys are located. In a Multiworld, describes which player has the keys as well.</p><p align=\"justify\"><span style=\" font-weight:600;\">Keybearer Corpse</span>: Contains a hint for the Flying Ing Cache in the associated room for the corpse. This hint will use the Broad Category, as described in Hint Item Names.</p><p align=\"justify\"><span style=\" font-weight:600;\">Luminoth Lore</span>: Contains the guaranteed hints and item hints, as described next.</p><hr/><p align=\"justify\">In each game, each of the following guaranteed hints are placed on a luminoth lore scan, placed randomly - this means they can be locked behind what they hint for. The hints are:</p><p align=\"justify\"><span style=\" font-weight:600;\">U-Mos 2</span>: The detailed item name of what would be L"
                        "ight Suit in the vanilla game.</p><p align=\"justify\"><span style=\" font-weight:600;\">Dark Temple Bosses</span>: The detailed item name which is dropped by each of the three temple bosses: Amorbis, Chykka and Quadraxis. There's one hint for each boss.</p><p align=\"justify\"><span style=\" font-weight:600;\">Dark Temple Keys</span>: The areas where the temple keys can be located, listed in alphabetical order. In multiworld, the area listed might be someone else's, but the hint is refering to your keys.</p><p align=\"justify\"><span style=\" font-weight:600;\">Joke Hints</span>: A joke. Uses green text and is a waste of space. There are 2 joke hints per game.</p><hr/><p align=\"justify\">The remaining Luminoth Lores are filled with item hints. These hints are placed in three step:</p><p align=\"justify\"><span style=\" font-weight:600;\">During Generator</span>: Whenever an item is logically placed (see Item Order in the spoiler), a hint for that item is placed in a compatible lore location - the item locati"
                        "on wasn't in logic when the given lore was first in logic.</p><p align=\"justify\"><span style=\" font-weight:600;\">Post Generator</span>: When the generator finishes (placed enough items to reach credits), lore locations without hints are filled in order, starting from these unlocked last. These hints will be for items from the Item Order that don't have a hint yet, favoring these that have less compatible lore locations (should bias for later items in the order).</p><p align=\"justify\"><span style=\" font-weight:600;\">Last Resort</span>: At this point, lore locations without a hint get one for a random item location.</p><p align=\"justify\">A same location can't receive more than one hint from this process, ignoring the guaranteed hints.<br/>These hints can be in many different formats:</p><p align=\"justify\">* Detailed item name with detailed room name (x5).<br/>* Precise category with detailed room name (x2).<br/>* General category with detailed room name (x1).<br/>* Detailed item name with only area n"
                        "ame (x2).<br/>* Precise category with only area name (x1).<br/>* Detailed item name, relative to a room with exact distance (x1).<br/>* Detailed item name, relative to a room with up to distance (x1).<br/>* Detailed item name, relative to another precise item name (x1).</p><p align=\"justify\">With relative hints, distance is measured using the map, not considering portals, and is always the shortest path.<br/>For hints with two items, the item being hinted is the first one.</p></body></html>", None))
        self.help_echoes_tab_widget.setTabText(self.help_echoes_tab_widget.indexOf(self.echoes_hints_tab), QCoreApplication.translate("MainWindow", u"Hints", None))
        self.echoes_hint_item_names_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>When items are referenced in a hint, multiple names can be used depending on how precise the hint is. The names each item can use are the following:</p></body></html>", None))
        ___qtablewidgetitem4 = self.echoes_hint_item_names_tree_widget.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Item", None));
        ___qtablewidgetitem5 = self.echoes_hint_item_names_tree_widget.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Precise Category", None));
        ___qtablewidgetitem6 = self.echoes_hint_item_names_tree_widget.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"General Category", None));
        ___qtablewidgetitem7 = self.echoes_hint_item_names_tree_widget.horizontalHeaderItem(3)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Broad Category", None));
        self.help_echoes_tab_widget.setTabText(self.help_echoes_tab_widget.indexOf(self.echoes_hint_item_names_tab), QCoreApplication.translate("MainWindow", u"Hint Item Names", None))
        self.echoes_hint_locations_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Hints are placed in the game by replacing Logbook scans. The following are the scans that may have a hint added to them:</p></body></html>", None))
        ___qtreewidgetitem6 = self.echoes_hint_locations_tree_widget.headerItem()
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("MainWindow", u"Location", None));
        self.help_echoes_tab_widget.setTabText(self.help_echoes_tab_widget.indexOf(self.echoes_hint_locations_tab), QCoreApplication.translate("MainWindow", u"Hints Locations", None))
        self.games_tab_widget.setTabText(self.games_tab_widget.indexOf(self.help_echoes_tab), QCoreApplication.translate("MainWindow", u"Metroid Prime 2: Echoes", None))
        self.corruption_faq_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Nothing right now. Please suggest questions!</span></p></body></html>", None))
        self.help_corruption_tab_widget.setTabText(self.help_corruption_tab_widget.indexOf(self.corruption_faq_tab), QCoreApplication.translate("MainWindow", u"FAQ", None))
        self.corruption_differences_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>TODO</p></body></html>", None))
        self.help_corruption_tab_widget.setTabText(self.help_corruption_tab_widget.indexOf(self.corruption_differences_tab), QCoreApplication.translate("MainWindow", u"Differences", None))
        self.corruption_hints_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"justify\">In Metroid Prime 3: Corruption, you can find hints from the following sources:</p><p align=\"justify\"><span style=\" font-weight:600;\">Valhalla Scanbots</span>: Two specific scan bots will hint in which planet the Hyper Missile and Hyper Grapple can be found.</p></body></html>", None))
        self.help_corruption_tab_widget.setTabText(self.help_corruption_tab_widget.indexOf(self.corruption_hints_tab), QCoreApplication.translate("MainWindow", u"Hints", None))
        self.corruption_hint_item_names_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>When items are referenced in a hint, multiple names can be used depending on how precise the hint is. The names each item can use are the following:</p></body></html>", None))
        ___qtablewidgetitem8 = self.corruption_hint_item_names_tree_widget.horizontalHeaderItem(0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"Item", None));
        ___qtablewidgetitem9 = self.corruption_hint_item_names_tree_widget.horizontalHeaderItem(1)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"Precise Category", None));
        ___qtablewidgetitem10 = self.corruption_hint_item_names_tree_widget.horizontalHeaderItem(2)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"General Category", None));
        ___qtablewidgetitem11 = self.corruption_hint_item_names_tree_widget.horizontalHeaderItem(3)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"Broad Category", None));
        self.help_corruption_tab_widget.setTabText(self.help_corruption_tab_widget.indexOf(self.corruption_hint_item_names_tab), QCoreApplication.translate("MainWindow", u"Hint Item Names", None))
        self.corruption_hint_locations_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Hints are placed in the game by replacing Logbook scans. The following are the scans that may have a hint added to them:</p></body></html>", None))
        ___qtreewidgetitem7 = self.corruption_hint_locations_tree_widget.headerItem()
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("MainWindow", u"Location", None));
        self.help_corruption_tab_widget.setTabText(self.help_corruption_tab_widget.indexOf(self.corruption_hint_locations_tab), QCoreApplication.translate("MainWindow", u"Hints Locations", None))
        self.games_tab_widget.setTabText(self.games_tab_widget.indexOf(self.help_corruption_tab), QCoreApplication.translate("MainWindow", u"Metroid Prime 3: Corruption", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.games_tab), QCoreApplication.translate("MainWindow", u"Games", None))
        self.about_text_browser.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Titillium Web'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:14pt;\">Randovania</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/randovania/randovania\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">https://github.com/randovania/randovania</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"><br />This software is covered by the </span><a href=\"https://www.gnu.org/li"
                        "censes/gpl-3.0.en.html\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">GNU General Public License v3 (GPLv3)</span></a></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:14pt;\">Community</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">Make sure to visit the Metroid Prime Randomizer Discord server!<br /></span><a href=\"https://discordapp.com/invite/gymstUz\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">https://discordapp.com/invite/gymstUz</span></a></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'"
                        "MS Shell Dlg 2'; font-size:14pt;\">Credits</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">GUI and logic written by </span><a href=\"https://github.com/henriquegemignani\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">Henrique Gemignani</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">, with contributions by </span><a href=\"https://www.twitch.tv/spaghettitoastbook\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">SpaghettiToastBook</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">, </span><a href=\"https://github.com/gollop\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">gollop</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-"
                        "size:10pt;\"> and </span><a href=\"https://www.twitch.tv/dyceron\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">Dyceron</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://www.twitch.tv/bashprime\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">BashPrime</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">, </span><a href=\"https://github.com/Pwootage/\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">Pwootage</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">, and </span><a href=\"https://github.com/aprilwade\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">"
                        "April Wade</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"> made </span><a href=\"https://randomizer.metroidprime.run/\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">https://randomizer.metroidprime.run/</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">, from which the GUI was based.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">Auto Tracker</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">Classic theme uses assets derived from </span><a href=\"https://www.spriters-resource.com/custom_edited/metroidcustoms/sheet/23198/\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: unde"
                        "rline; color:#0000ff;\">this spritesheet</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"> from ChaosMiles07 and Ridleymaster, with edits from SpaghettiToastBook.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">Game theme assets were provided by </span><a href=\"https://twitter.com/MaskedKirby\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">MaskedTAS</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">Multiworld</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span styl"
                        "e=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">Server and logic written by Henrique, including Dolphin and Nintendont integrations. These were based on </span><a href=\"https://github.com/aldelaro5/Dolphin-memory-engine\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">Dolphin Memory Engine</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"> and Pwootage's Nintendont fork, respectively. In-game message alert initially written by </span><a href=\"https://github.com/encounter\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">encounter</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">Metroid Prime 1</span><span style=\" font-family:'MS Shell Dlg 2';"
                        " font-size:10pt;\"><br />* Game patching via </span><a href=\"https://github.com/aprilwade/randomprime\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">randomprime</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"> from April Wade, with contributions from </span><a href=\"https://github.com/UltiNaruto\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">UltiNaruto</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">, BashPrime and </span><a href=\"https://github.com/toasterparty/\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">toasterparty</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">.<br />* Room data collected by UltiNaruto, </span><a href=\"https://github.com/EthanArmbrust\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; col"
                        "or:#0000ff;\">EthanArmbrust</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"> and </span><a href=\"https://github.com/samuelroy21\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">samuelroy21</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">Metroid Prime 2: Echoes</span><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"><br />* Game patching written by </span><a href=\"https://www.twitch.tv/claris\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">Claris</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">.<br />* Room data initially collected by Claris, revamped by Dyceron.</span></p>\n"
"<p style=\" margin-top:12px; "
                        "margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:12pt;\">Metroid Prime 3: Corruption</span><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\"><br />* Game patching written by gollop.<br />* Room data collected by Dyceron and </span><a href=\"https://www.twitch.tv/kirbymastah\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt; text-decoration: underline; color:#0000ff;\">KirbymastaH</span></a><span style=\" font-family:'MS Shell Dlg 2'; font-size:10pt;\">.</span></p></body></html>", None))
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.about_tab), QCoreApplication.translate("MainWindow", u"About", None))
        self.menu_open.setTitle(QCoreApplication.translate("MainWindow", u"Open", None))
        self.menu_edit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menu_database.setTitle(QCoreApplication.translate("MainWindow", u"Database", None))
        self.menu_internal.setTitle(QCoreApplication.translate("MainWindow", u"Internal", None))
        self.menu_advanced.setTitle(QCoreApplication.translate("MainWindow", u"Advanced", None))
    # retranslateUi

