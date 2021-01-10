#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import random, sys, os, math, time, numpy, json

from lib import Utils, PaintUtils, Geometry

class ControlsMenu(QtWidgets.QWidget,Utils.FilePaths):

    def __init__(self,logger,screen_width,screen_height):
        super().__init__()
        uic.loadUi(f'{self.user_path}ui/controls_window.ui',self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle('Keyboard Controls')

        self.logger = logger
        self.return_to_menu_flag = False

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.width = 600
        self.height = 400.0        

        self.offset_x = int((self.screen_width-self.width)/2.0)
        self.offset_y = int((self.screen_height-self.height)/2.0)

        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

        self.set_default_map()
        self.update_lists()

        # PyQt signal connections
        self.key_listwidget.itemClicked.connect(self.key_selected)
        self.action_listwidget.itemClicked.connect(self.key_selected)

    def showEvent(self,event):
        self.setGeometry(QtCore.QRect(self.offset_x,self.offset_y,self.width,self.height))

    def closeEvent(self, event):
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def set_default_map(self):
        self.key_map = {
            'Drive right': {'text':'D','code':Qt.Key_D,'row':None},
            'Drive left': {'text':'A','code':Qt.Key_A,'row':None},
            'Drive up': {'text':'W','code':Qt.Key_W,'row':None},
            'Drive down': {'text':'S','code':Qt.Key_S,'row':None},
            'Increase cannon power': {'text':'Up arrow','code':Qt.Key_Up,'row':None},
            'Lower cannon power': {'text':'Down arrow','code':Qt.Key_Down,'row':None},
            'Rotate cannon counter clockwise': {'text':'Right arrow','code':Qt.Key_Left,'row':None},
            'Rotate cannon clockwise': {'text':'Left arrow','code':Qt.Key_Right,'row':None},
            'Fire cannon': {'text':'F','code':Qt.Key_F,'row':None},
            'Switch shell': {'text':'T','code':Qt.Key_T,'row':None},
            'Next turn': {'text':'N','code':Qt.Key_N,'row':None},
            'Advance frame': {'text':'I','code':Qt.Key_I,'row':None},
            'Pause game': {'text':'Esc','code':Qt.Key_Escape,'row':None}
        }

    def key_selected(self,item):
        selection = item.text()
        if selection in self.key_map.keys():
            idx = self.key_map[selection]['row']
        else:
            for key,val in self.key_map.items():
                if val['text'] == selection:
                    idx = val['row']
                    break

        self.action_listwidget.setCurrentRow(idx)
        self.key_listwidget.setCurrentRow(idx)

    def update_lists(self):
        self.action_listwidget.clear()
        self.key_listwidget.clear()
        idx = 0
        for key,val in self.key_map.items():
            self.action_listwidget.addItem(key)
            self.key_listwidget.addItem(val['text'])
            self.key_map[key]['row'] = idx
            idx += 1