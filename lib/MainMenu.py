#!/usr/bin/env python3

from PyQt5 import QtCore, QtWidgets, uic
from lib import Utils, KeyControls
import os

class MainMenu(QtWidgets.QWidget,Utils.FilePaths):

    def __init__(self,logger,screen_width,screen_height):
        super().__init__()
        self.logger = logger
        self.screen_width = screen_width
        self.screen_height = screen_height
        uic.loadUi(f'{self.user_path}ui/welcome_screen.ui',self)

        self.delete_game_button.clicked.connect(self.delete_save_file)
        self.player_count_spinbox.valueChanged.connect(self.update_player_tank_count)
        self.number_of_tanks_spinbox.valueChanged.connect(self.update_player_tank_count)

        self.control_window = KeyControls.ControlsMenu(self.logger,self.screen_width,self.screen_height)
        self.keyboard_controls_button.clicked.connect(self.show_controls_window)

        self.list_save_games()
        self.list_maps()
        self.list_shells()
        self.list_tanks()

    def show_controls_window(self):
        self.control_window.show()

    def update_player_tank_count(self):
        player_val = self.player_count_spinbox.value()
        tank_val = self.number_of_tanks_spinbox.value()
        
        if player_val > tank_val:
            self.number_of_tanks_spinbox.setValue(player_val)
        
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def delete_save_file(self):
        file_name = self.save_files_combobox.currentText()
        if file_name == '':
            return
        os.remove(f'{self.saves_path}{file_name}')
        self.list_save_games()

    def list_save_games(self):
        try:
            self.save_files_combobox.clear()
            save_files = os.listdir(f'{self.saves_path}')
            self.logger.log(f'Save files found: {save_files}')

            if len(save_files) > 0:
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
        data = os.listdir(f'{self.shells_path}')
        shell_files = []
        for file_name in data:
            if '.shell' in file_name:
                shell_files.append(file_name)
        
        self.logger.log(f'Shell files found: {shell_files}')
        self.shell_files = shell_files

        if len(shell_files) == 0:
            self.shell_type_combobox.addItem('None')
        else:
            self.shell_type_combobox.addItems(shell_files)

    def list_tanks(self):
        tank_files = os.listdir(f'{self.tanks_path}')
        self.logger.log(f'Tank files found: {tank_files}')

        if len(tank_files) == 0:
            self.tank_type_combobox.addItem('None')
        else:
            self.tank_type_combobox.addItems(tank_files)