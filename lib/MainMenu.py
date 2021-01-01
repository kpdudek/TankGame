#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import random, sys, os, math, time, numpy

from lib import Utils, PaintUtils, Game


class MainMenu(QtWidgets.QWidget,Utils.FilePaths):

    def __init__(self,logger):
        super().__init__()
        self.logger = logger
        uic.loadUi(f'{self.user_path}ui/welcome_screen.ui',self)

        self.list_save_games()
        self.list_maps()
        self.list_shells()
        self.list_tanks()

    def list_save_games(self):
        try:
            save_files = os.listdir(f'{self.saves_path}')
            self.logger.log(f'Save files found: {save_files}')

            if len(save_files) == 0:
                self.save_files_combobox.addItem('None')
            else:
                self.save_files_combobox.addItems(save_files)
                
        except FileNotFoundError:
            self.logger.log(f'Creating saves folder...')
            os.mkdir(f'{self.saves_path}')
            self.list_save_games()

    def list_maps(self):
        map_files = os.listdir(f'{self.maps_path}')
        self.logger.log(f'Map files found: {map_files}')

        if len(map_files) == 0:
            self.map_files_combobox.addItem('None')
        else:
            self.map_files_combobox.addItems(map_files)

    def list_shells(self):
        shell_files = os.listdir(f'{self.shells_path}')
        self.logger.log(f'Map files found: {shell_files}')

        if len(shell_files) == 0:
            self.shell_type_combobox.addItem('None')
        else:
            self.shell_type_combobox.addItems(shell_files)

    def list_tanks(self):
        tank_files = os.listdir(f'{self.tanks_path}')
        self.logger.log(f'Map files found: {tank_files}')

        if len(tank_files) == 0:
            self.tank_type_combobox.addItem('None')
        else:
            self.tank_type_combobox.addItems(tank_files)