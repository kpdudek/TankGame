#!/usr/bin/env python3

from lib.Utils import FilePaths, initialize_logger, set_logging_level
from lib.Scene import Scene, SceneData
from PyQt5.QtWidgets import QWidget
from ui.Settings import Ui_Settings
from PyQt5.QtCore import pyqtSignal
from lib.Camera import Camera

class Settings(QWidget):
    set_debug_mode_signal = pyqtSignal(bool)
    toggle_fps_log_signal = pyqtSignal(bool)
    reset_simulation_signal = pyqtSignal()

    def __init__(self,scene:Scene,camera:Camera,debug_mode):
        super().__init__()
        self.logger = initialize_logger()
        self.file_paths = FilePaths()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.camera = camera
        self.scene = scene

        if debug_mode:
            self.ui.debug_mode_checkbox.setChecked(True)
        
        self.ui.log_fps_checkbox.stateChanged.connect(self.toggle_fps_log)
        self.ui.debug_mode_checkbox.stateChanged.connect(self.toggle_debug_mode)
        self.ui.reset_button.clicked.connect(self.reset_simulation)
        self.ui.power_down_button.clicked.connect(self.power_down)
        self.ui.power_up_button.clicked.connect(self.power_up)
        self.ui.drive_left_button.clicked.connect(self.drive_left)
        self.ui.drive_right_button.clicked.connect(self.drive_right)
        self.ui.barrel_up_button.clicked.connect(self.barrel_up)
        self.ui.barrel_down_button.clicked.connect(self.barrel_down)
        self.ui.fire_button.clicked.connect(self.fire_shell)

    def fire_shell(self):
        if len(self.scene.tanks) <= 0:
            return
        self.scene.tanks[self.scene.current_player_idx].fire_shell()

    def barrel_up(self):
        if len(self.scene.tanks) <= 0:
            return
        self.scene.tanks[self.scene.current_player_idx].rotate_barrel(-1)

    def barrel_down(self):
        if len(self.scene.tanks) <= 0:
            return
        self.scene.tanks[self.scene.current_player_idx].rotate_barrel(1)

    def drive_left(self):
        if len(self.scene.tanks) <= 0:
            return
        self.scene.tanks[self.scene.current_player_idx].drive(-1)
    
    def drive_right(self):
        if len(self.scene.tanks) <= 0:
            return
        self.scene.tanks[self.scene.current_player_idx].drive(1)

    def power_up(self):
        if len(self.scene.tanks) <= 0:
            return
        self.scene.tanks[self.scene.current_player_idx].set_power(1)

    def power_down(self):
        if len(self.scene.tanks) <= 0:
            return
        self.scene.tanks[self.scene.current_player_idx].set_power(-1)

    def update_scene_data(self,scene_data:SceneData):
        self.ui.tank_count_label.setText(str(scene_data.tank_count))
        self.ui.shell_count_label.setText(str(scene_data.shell_count))
        self.ui.current_player_label.setText(str(scene_data.current_player))
        
    def toggle_debug_mode(self):
        if self.ui.debug_mode_checkbox.isChecked():
            self.set_debug_mode_signal.emit(True)
            set_logging_level("DEBUG")
        else:
            self.set_debug_mode_signal.emit(False)
            set_logging_level("INFO")

        self.camera.setFocus()

    def toggle_fps_log(self):
        if self.ui.log_fps_checkbox.isChecked():
            self.toggle_fps_log_signal.emit(True)
        else:
            self.toggle_fps_log_signal.emit(False)
        
        self.camera.setFocus()

    def reset_simulation(self):
        num_tanks = self.ui.tank_count_spinbox.value()
        max_vel = self.ui.max_speed_spinbox.value()
        self.scene.initialize_scene(num_tanks,max_vel)
        self.toggle_debug_mode()
        self.toggle_fps_log()

        self.scene.tanks[0].set_current_player(True)
        self.reset_simulation_signal.emit()

        self.camera.setFocus()
