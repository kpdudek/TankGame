#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry

class PauseMenu(QtWidgets.QWidget,Utils.FilePaths):
    pause_signal = QtCore.pyqtSignal()
    save_game_signal = QtCore.pyqtSignal()
    main_menu_signal = QtCore.pyqtSignal()
    quit_signal = QtCore.pyqtSignal()

    def __init__(self,logger,screen_width,screen_height):
        super().__init__()
        uic.loadUi(f'{self.user_path}ui/pause_menu.ui',self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle('Pause Menu')

        self.logger = logger
        self.return_to_menu_flag = False

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.width = 300.0
        self.height = 400.0        

        self.offset_x = int((self.screen_width-self.width)/2.0)
        self.offset_y = int((self.screen_height-self.height)/2.0)

        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

        # Qt Signal Connections
        self.resume_button.clicked.connect(self.resume_game)
        self.return_to_menu_button.clicked.connect(self.return_to_menu)
        self.save_game_button.clicked.connect(self.save_game)
        self.quit_button.clicked.connect(self.quit_game)

    def showEvent(self,event):
        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

    def closeEvent(self, event):
        if not self.return_to_menu_flag:
            self.pause_signal.emit()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def resume_game(self):
        self.close()

    def save_game(self):
        self.save_game_signal.emit()

    def return_to_menu(self):
        self.return_to_menu_flag = True
        self.main_menu_signal.emit()

    def quit_game(self):
        self.quit_signal.emit()