#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy

from lib import Utils, PaintUtils, Game, WelcomeScreen


class WelcomeScreen(QtWidgets.QWidget,Utils.FilePaths):

    def __init__(self,logger):
        super().__init__()
        self.logger = logger
        uic.loadUi(f'{self.user_path}ui/welcome_screen.ui',self)

        self.list_save_games()
        self.list_maps()

    def list_save_games(self):
        save_files = os.listdir(f'{self.saves_path}')
        self.logger.log(f'Save files found: {save_files}')

        if len(save_files) == 0:
            self.save_files_combobox.addItem('None')
        else:
            self.save_files_combobox.addItems(save_files)

    def list_maps(self):
        map_files = os.listdir(f'{self.maps_path}')
        self.logger.log(f'Map files found: {map_files}')

        if len(map_files) == 0:
            self.map_files_combobox.addItem('None')
        else:
            self.map_files_combobox.addItems(map_files)