#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry

class PauseMenu(QtWidgets.QWidget,Utils.FilePaths):
    quit_signal = QtCore.pyqtSignal()
    pause_signal = QtCore.pyqtSignal()

    def __init__(self,logger,screen_width,screen_height):
        super().__init__()
        uic.loadUi(f'{self.user_path}ui/pause_menu.ui',self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle('Pause Menu')

        self.logger = logger

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.width = 300.0
        self.height = 400.0        

        self.offset_x = int((self.screen_width-self.width)/2.0)
        self.offset_y = int((self.screen_height-self.height)/2.0)

        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

        # Qt Signal Connections
        self.quit_button.clicked.connect(self.quit_game)
        self.resume_button.clicked.connect(self.resume_game)

    def quit_game(self):
        self.quit_signal.emit()

    def showEvent(self,event):
        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

    def closeEvent(self, event):
        self.pause_signal.emit()
        event.accept()

    def resume_game(self):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()