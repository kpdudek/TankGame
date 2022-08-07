#!/usr/bin/env python3

from PyQt5 import QtCore, QtWidgets, uic
from lib import Utils

class GameOver(QtWidgets.QWidget,Utils.FilePaths):
    quit_signal = QtCore.pyqtSignal()
    return_to_menu_signal = QtCore.pyqtSignal()

    def __init__(self,logger,screen_width,screen_height):
        super().__init__()
        uic.loadUi(f'{self.user_path}ui/game_over.ui',self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle('Game Over')
    
        self.logger = logger

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.width = 300
        self.height = 200        

        self.offset_x = int((self.screen_width-self.width)/2.0)
        self.offset_y = int((self.screen_height-self.height)/2.0)

        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

        # Qt Signal Connections
        self.quit_button.clicked.connect(self.quit_game)
        self.return_to_menu_button.clicked.connect(self.return_to_menu)

    def quit_game(self):
        self.quit_signal.emit()

    def return_to_menu(self):
        self.return_to_menu_signal.emit()

    def showEvent(self,event):
        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

    def closeEvent(self, event):
        event.accept()
