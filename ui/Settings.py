# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/Settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(1134, 308)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Settings.sizePolicy().hasHeightForWidth())
        Settings.setSizePolicy(sizePolicy)
        Settings.setMinimumSize(QtCore.QSize(0, 0))
        Settings.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        Settings.setFont(font)
        self.gridLayout = QtWidgets.QGridLayout(Settings)
        self.gridLayout.setContentsMargins(0, 3, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.expand_collapse_settings_button = QtWidgets.QPushButton(Settings)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.expand_collapse_settings_button.setFont(font)
        self.expand_collapse_settings_button.setStyleSheet("text-align: left;\n"
"font:  bold 10pt;")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./ui/icons/expand_down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.expand_collapse_settings_button.setIcon(icon)
        self.expand_collapse_settings_button.setIconSize(QtCore.QSize(16, 16))
        self.expand_collapse_settings_button.setCheckable(True)
        self.expand_collapse_settings_button.setFlat(False)
        self.expand_collapse_settings_button.setObjectName("expand_collapse_settings_button")
        self.gridLayout.addWidget(self.expand_collapse_settings_button, 2, 0, 1, 3)
        self.settings_frame = QtWidgets.QFrame(Settings)
        self.settings_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.settings_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.settings_frame.setObjectName("settings_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.settings_frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(self.settings_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMaximumSize(QtCore.QSize(300, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.frame_6 = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setObjectName("frame_6")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.frame_6)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.tank_count_spinbox = QtWidgets.QSpinBox(self.frame_6)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.tank_count_spinbox.setFont(font)
        self.tank_count_spinbox.setMinimum(1)
        self.tank_count_spinbox.setMaximum(500)
        self.tank_count_spinbox.setProperty("value", 1)
        self.tank_count_spinbox.setObjectName("tank_count_spinbox")
        self.gridLayout_8.addWidget(self.tank_count_spinbox, 0, 1, 1, 1)
        self.gridLayout_6.addWidget(self.frame_6, 2, 1, 1, 1)
        self.frame_5 = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy)
        self.frame_5.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_5.setObjectName("frame_5")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.frame_5)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.max_speed_spinbox = QtWidgets.QDoubleSpinBox(self.frame_5)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.max_speed_spinbox.setFont(font)
        self.max_speed_spinbox.setMinimum(1.0)
        self.max_speed_spinbox.setMaximum(1000.0)
        self.max_speed_spinbox.setSingleStep(10.0)
        self.max_speed_spinbox.setProperty("value", 75.0)
        self.max_speed_spinbox.setObjectName("max_speed_spinbox")
        self.gridLayout_7.addWidget(self.max_speed_spinbox, 0, 1, 1, 1)
        self.gridLayout_6.addWidget(self.frame_5, 4, 1, 1, 1)
        self.log_fps_checkbox = QtWidgets.QCheckBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.log_fps_checkbox.setFont(font)
        self.log_fps_checkbox.setObjectName("log_fps_checkbox")
        self.gridLayout_6.addWidget(self.log_fps_checkbox, 7, 0, 1, 1)
        self.reset_button = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.reset_button.setFont(font)
        self.reset_button.setObjectName("reset_button")
        self.gridLayout_6.addWidget(self.reset_button, 9, 0, 1, 2)
        self.debug_mode_checkbox = QtWidgets.QCheckBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.debug_mode_checkbox.setFont(font)
        self.debug_mode_checkbox.setObjectName("debug_mode_checkbox")
        self.gridLayout_6.addWidget(self.debug_mode_checkbox, 7, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setMinimumSize(QtCore.QSize(0, 20))
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_6.addWidget(self.label_3, 1, 0, 1, 2)
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_6.addWidget(self.line, 8, 0, 1, 2)
        self.label_5 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QtCore.QSize(150, 0))
        self.label_5.setMaximumSize(QtCore.QSize(150, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_6.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QtCore.QSize(150, 0))
        self.label_4.setMaximumSize(QtCore.QSize(150, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_6.addWidget(self.label_4, 2, 0, 1, 1)
        self.ai_difficulty_combobox = QtWidgets.QComboBox(self.frame)
        self.ai_difficulty_combobox.setObjectName("ai_difficulty_combobox")
        self.ai_difficulty_combobox.addItem("")
        self.ai_difficulty_combobox.addItem("")
        self.ai_difficulty_combobox.addItem("")
        self.ai_difficulty_combobox.addItem("")
        self.gridLayout_6.addWidget(self.ai_difficulty_combobox, 5, 0, 1, 2)
        self.map_type_combobox = QtWidgets.QComboBox(self.frame)
        self.map_type_combobox.setObjectName("map_type_combobox")
        self.map_type_combobox.addItem("")
        self.map_type_combobox.addItem("")
        self.map_type_combobox.addItem("")
        self.gridLayout_6.addWidget(self.map_type_combobox, 6, 0, 1, 2)
        self.label_15 = QtWidgets.QLabel(self.frame)
        self.label_15.setObjectName("label_15")
        self.gridLayout_6.addWidget(self.label_15, 3, 0, 1, 1)
        self.ai_count_spinbox = QtWidgets.QSpinBox(self.frame)
        self.ai_count_spinbox.setMaximum(10)
        self.ai_count_spinbox.setProperty("value", 1)
        self.ai_count_spinbox.setObjectName("ai_count_spinbox")
        self.gridLayout_6.addWidget(self.ai_count_spinbox, 3, 1, 1, 1)
        self.horizontalLayout.addWidget(self.frame)
        self.game_details_frame = QtWidgets.QFrame(self.settings_frame)
        self.game_details_frame.setMinimumSize(QtCore.QSize(0, 110))
        self.game_details_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.game_details_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.game_details_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.game_details_frame.setObjectName("game_details_frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.game_details_frame)
        self.gridLayout_2.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_2.setVerticalSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_6 = QtWidgets.QLabel(self.game_details_frame)
        self.label_6.setMinimumSize(QtCore.QSize(0, 20))
        self.label_6.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 2)
        self.tank_count_label = QtWidgets.QLabel(self.game_details_frame)
        self.tank_count_label.setObjectName("tank_count_label")
        self.gridLayout_2.addWidget(self.tank_count_label, 4, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.game_details_frame)
        self.label_2.setMinimumSize(QtCore.QSize(150, 0))
        self.label_2.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)
        self.current_player_label = QtWidgets.QLabel(self.game_details_frame)
        self.current_player_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.current_player_label.setObjectName("current_player_label")
        self.gridLayout_2.addWidget(self.current_player_label, 3, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.game_details_frame)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 4, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.game_details_frame)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 5, 0, 1, 1)
        self.shell_count_label = QtWidgets.QLabel(self.game_details_frame)
        self.shell_count_label.setObjectName("shell_count_label")
        self.gridLayout_2.addWidget(self.shell_count_label, 5, 1, 1, 1)
        self.horizontalLayout.addWidget(self.game_details_frame)
        self.player_details_frame = QtWidgets.QFrame(self.settings_frame)
        self.player_details_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.player_details_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.player_details_frame.setObjectName("player_details_frame")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.player_details_frame)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_11 = QtWidgets.QLabel(self.player_details_frame)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 2, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.player_details_frame)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 2, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.player_details_frame)
        self.label_10.setObjectName("label_10")
        self.gridLayout_4.addWidget(self.label_10, 1, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.player_details_frame)
        self.label_8.setMinimumSize(QtCore.QSize(0, 20))
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.player_details_frame)
        self.label_9.setObjectName("label_9")
        self.gridLayout_4.addWidget(self.label_9, 1, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.player_details_frame)
        self.label_13.setObjectName("label_13")
        self.gridLayout_4.addWidget(self.label_13, 3, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.player_details_frame)
        self.label_14.setObjectName("label_14")
        self.gridLayout_4.addWidget(self.label_14, 3, 1, 1, 1)
        self.horizontalLayout.addWidget(self.player_details_frame)
        self.frame_2 = QtWidgets.QFrame(self.settings_frame)
        self.frame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.fire_button = QtWidgets.QPushButton(self.frame_2)
        self.fire_button.setAutoRepeat(True)
        self.fire_button.setAutoRepeatDelay(10)
        self.fire_button.setAutoRepeatInterval(10)
        self.fire_button.setObjectName("fire_button")
        self.gridLayout_3.addWidget(self.fire_button, 4, 1, 1, 2)
        self.barrel_up_button = QtWidgets.QPushButton(self.frame_2)
        self.barrel_up_button.setAutoRepeat(True)
        self.barrel_up_button.setAutoRepeatDelay(10)
        self.barrel_up_button.setAutoRepeatInterval(10)
        self.barrel_up_button.setObjectName("barrel_up_button")
        self.gridLayout_3.addWidget(self.barrel_up_button, 1, 2, 1, 1)
        self.barrel_down_button = QtWidgets.QPushButton(self.frame_2)
        self.barrel_down_button.setAutoRepeat(True)
        self.barrel_down_button.setAutoRepeatDelay(10)
        self.barrel_down_button.setAutoRepeatInterval(10)
        self.barrel_down_button.setObjectName("barrel_down_button")
        self.gridLayout_3.addWidget(self.barrel_down_button, 1, 1, 1, 1)
        self.power_down_button = QtWidgets.QPushButton(self.frame_2)
        self.power_down_button.setAutoRepeat(True)
        self.power_down_button.setAutoRepeatDelay(250)
        self.power_down_button.setAutoRepeatInterval(100)
        self.power_down_button.setObjectName("power_down_button")
        self.gridLayout_3.addWidget(self.power_down_button, 2, 1, 1, 1)
        self.drive_left_button = QtWidgets.QPushButton(self.frame_2)
        self.drive_left_button.setAutoRepeat(True)
        self.drive_left_button.setAutoRepeatDelay(10)
        self.drive_left_button.setAutoRepeatInterval(10)
        self.drive_left_button.setObjectName("drive_left_button")
        self.gridLayout_3.addWidget(self.drive_left_button, 0, 1, 1, 1)
        self.power_up_button = QtWidgets.QPushButton(self.frame_2)
        self.power_up_button.setAutoRepeat(True)
        self.power_up_button.setAutoRepeatDelay(250)
        self.power_up_button.setAutoRepeatInterval(100)
        self.power_up_button.setObjectName("power_up_button")
        self.gridLayout_3.addWidget(self.power_up_button, 2, 2, 1, 1)
        self.drive_right_button = QtWidgets.QPushButton(self.frame_2)
        self.drive_right_button.setAutoRepeat(True)
        self.drive_right_button.setAutoRepeatDelay(10)
        self.drive_right_button.setAutoRepeatInterval(10)
        self.drive_right_button.setObjectName("drive_right_button")
        self.gridLayout_3.addWidget(self.drive_right_button, 0, 2, 1, 1)
        self.switch_shells_button = QtWidgets.QPushButton(self.frame_2)
        self.switch_shells_button.setObjectName("switch_shells_button")
        self.gridLayout_3.addWidget(self.switch_shells_button, 3, 1, 1, 2)
        self.horizontalLayout.addWidget(self.frame_2)
        self.gridLayout.addWidget(self.settings_frame, 4, 0, 1, 3)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Form"))
        self.expand_collapse_settings_button.setText(_translate("Settings", "Settings"))
        self.log_fps_checkbox.setText(_translate("Settings", "Log FPS"))
        self.reset_button.setText(_translate("Settings", "New Game"))
        self.debug_mode_checkbox.setText(_translate("Settings", "Debug mode"))
        self.label_3.setText(_translate("Settings", "New Game:"))
        self.label_5.setText(_translate("Settings", "Max Speed: "))
        self.label_4.setText(_translate("Settings", "Number of Players: "))
        self.ai_difficulty_combobox.setItemText(0, _translate("Settings", "Easy"))
        self.ai_difficulty_combobox.setItemText(1, _translate("Settings", "Medium"))
        self.ai_difficulty_combobox.setItemText(2, _translate("Settings", "Hard"))
        self.ai_difficulty_combobox.setItemText(3, _translate("Settings", "Impossible"))
        self.map_type_combobox.setItemText(0, _translate("Settings", "Flat"))
        self.map_type_combobox.setItemText(1, _translate("Settings", "Peak"))
        self.map_type_combobox.setItemText(2, _translate("Settings", "Perlin"))
        self.label_15.setText(_translate("Settings", "Number of AI:"))
        self.label_6.setText(_translate("Settings", "Current Game Details:"))
        self.tank_count_label.setText(_translate("Settings", "..."))
        self.label_2.setText(_translate("Settings", "Current Player:"))
        self.current_player_label.setText(_translate("Settings", "..."))
        self.label_7.setText(_translate("Settings", "Number of Tanks:"))
        self.label.setText(_translate("Settings", "Number of Shells:"))
        self.shell_count_label.setText(_translate("Settings", "..."))
        self.label_11.setText(_translate("Settings", "Remaining Shells: "))
        self.label_12.setText(_translate("Settings", "..."))
        self.label_10.setText(_translate("Settings", "..."))
        self.label_8.setText(_translate("Settings", "Current Player Details:"))
        self.label_9.setText(_translate("Settings", "Selected Shell: "))
        self.label_13.setText(_translate("Settings", "Armour Rating:"))
        self.label_14.setText(_translate("Settings", "..."))
        self.fire_button.setText(_translate("Settings", "Fire!"))
        self.barrel_up_button.setText(_translate("Settings", "Barrel Up"))
        self.barrel_down_button.setText(_translate("Settings", "Barrel Down"))
        self.power_down_button.setText(_translate("Settings", "Power Down"))
        self.drive_left_button.setText(_translate("Settings", "Drive Left"))
        self.power_up_button.setText(_translate("Settings", "Power Up"))
        self.drive_right_button.setText(_translate("Settings", "Drive Right"))
        self.switch_shells_button.setText(_translate("Settings", "Switch Shells"))
